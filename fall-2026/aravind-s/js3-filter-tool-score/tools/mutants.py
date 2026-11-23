"""Plant each wrong version from CONTRACT.md in a copy of the code and check that the tests fail.

A suite that still passes when the code is broken proves nothing. Each mutant below swaps one piece
of code for a plausible mistake. The first entries are the contract's "Wrong versions" (W1 to W4);
the ones marked "extra" are further mistakes the tests also have to catch. The entries marked "JS3" are
FILTER.md v1.0's wrong versions (Section 4, W1 to W7) and further mistakes in the JS3 filter; the entries marked
"MCP" are mistakes in the JS3 MCP server (job_agent/mcp_server.py). The copy lives in a temporary folder, so the
repo itself is never touched. A mutant is "caught" when a test fails.

Usage (from the repo root):  python3 tools/mutants.py
Exit 0 when every mutant is caught, 1 when one survives, 2 when the unbroken copy fails or a
mutant's target text is not found exactly once.

The approach (exact text swaps on a copy, one at a time) follows Klaxon's scripts/mutation_check.py.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# runs/: the rule's tests read the real baseline response; labels/ and tools/: the selection and label tests;
# experiment/: the Claude judge's tests copy Claude Code's real init event from a saved call.
# js3/mcp: the MCP client tests run the copied lesson 8 server and read the committed transcripts.
COPIED = ("job_agent", "tests", "persona", "runs", "labels", "tools", "prompts", "experiment", "js3/mcp")
COPIED_FILES = ("GATE.md", "boards.json", "FILTER.md")  # test_gate.py reads GATE.md; the JS3 filter reads FILTER.md

# (label, file, old text, new text)
MUTANTS = [
    ("W1 saves seen ids too early", "job_agent/watch.py",
     "    found = state_mod.diff(previous, jobs)\n",
     "    state_mod.save(state_path, state_mod.next_state(previous, jobs, record))\n"
     "    found = state_mod.diff(state_mod.load(state_path), jobs)\n"),
    ("W2 any 'sponsor' blocks", "job_agent/rule.py",
     'SPONSORSHIP_PHRASES = ("unable to sponsor",', 'SPONSORSHIP_PHRASES = ("sponsor", "unable to sponsor",'),
    ("W3 look-alike host passes (substring)", "job_agent/allowlist.py",
     "    if host not in ALLOWED_HOSTS:", "    if not any(allowed in host for allowed in ALLOWED_HOSTS):"),
    ("W3 look-alike host passes (prefix)", "job_agent/allowlist.py",
     "    if host not in ALLOWED_HOSTS:", "    if not any(host.startswith(allowed) for allowed in ALLOWED_HOSTS):"),
    ("W3 look-alike host passes (suffix)", "job_agent/allowlist.py",
     "    if host not in ALLOWED_HOSTS:", "    if not any(host.endswith(allowed) for allowed in ALLOWED_HOSTS):"),
    ("W4 citation-free answer passes (empty list)", "job_agent/claude_judge.py",
     "        if not isinstance(fields, list) or not fields:", "        if not isinstance(fields, list):"),
    ("W4 citation-free answer passes (field never sent)", "job_agent/claude_judge.py",
     "        unknown = [f for f in fields if not isinstance(f, str) or f not in allowed[key]]",
     "        unknown = [f for f in fields if not isinstance(f, str)]"),
    ("extra: an invented quote passes", "job_agent/claude_judge.py",
     "            if not isinstance(quote, str) or not quote.strip() or not any(_plain(quote) in t for t in texts):",
     "            if not isinstance(quote, str):"),
    ("extra: an extra key passes", "job_agent/claude_judge.py",
     "    if keys != set(ANSWER_KEYS):", "    if not set(ANSWER_KEYS) <= keys:"),
    ("extra: a CLI that loaded tools is trusted", "job_agent/claude_judge.py",
     "    if tools:\n        return", "    if False:\n        return"),
    ("extra: an API-key login is trusted", "job_agent/claude_judge.py",
     '    if init.get("apiKeySource") != SEAT:', "    if False:"),
    ("extra: a reply of several turns is trusted", "job_agent/claude_judge.py",
     '    if result.get("num_turns") != 1:', "    if False:"),
    ("extra: at signs reach the CLI as typed", "job_agent/claude_judge.py",
     '    return kept.replace("@", FULLWIDTH_AT)', "    return kept"),
    ("extra: the API key is passed on to the CLI", "job_agent/claude_judge.py",
     'PASSED_ON = ("HOME",', 'PASSED_ON = ("ANTHROPIC_API_KEY", "HOME",'),
    ("extra: the sentence limit is not checked", "job_agent/claude_judge.py",
     "    elif sentence_count(justification) > MAX_SENTENCES:", "    elif False:"),
    ("extra: a key may appear twice", "job_agent/claude_judge.py",
     "answer = json.loads(text, object_pairs_hook=_each_key_once)", "answer = json.loads(text)"),
    ("extra: an installed plugin is trusted", "job_agent/claude_judge.py",
     "    if unknown:\n        return f\"Claude Code loaded {len(unknown)} plugin(s)",
     "    if False:\n        return f\"Claude Code loaded {len(unknown)} plugin(s)"),
    ("extra: the input-token count is not checked", "job_agent/claude_judge.py",
     "    if tokens > chars_sent / 4 + OVERHEAD_TOKENS:", "    if False:"),
    ("extra: the state is saved before the screen is printed", "job_agent/watch.py",
     "    say(line)  # before the state is saved, so that a screen that fails cannot leave a saved state behind an error\n",
     "    state_mod.save(state_path, state_mod.next_state(previous, jobs, record))\n    say(line)\n"),
    ("extra: the rule reads a singular 'year'", "job_agent/rule.py",
     "\\s*years(?![a-z])\"", "\\s*years?(?![a-z])\""),
    ("extra: a replay records its path as given", "job_agent/watch.py",
     "f\"replay of a saved response ({_shown_path(replay)}), not a live run\"",
     "f\"replay of a saved response ({Path(replay)}), not a live run\""),
    ("extra: redirects are followed", "job_agent/fetch.py",
     "urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirects())",
     "urllib.request.build_opener(urllib.request.ProxyHandler({}))"),
    ("extra: proxy settings from the environment are used", "job_agent/fetch.py",
     "urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirects())",
     "urllib.request.build_opener(NoRedirects())"),
    ("extra: a non-200 answer is used", "job_agent/board.py",
     "    if status != 200:", "    if False:"),
    ("extra: the baseline reports every posting as new", "job_agent/state.py",
     "        return Diff(baseline=True)", "        return Diff(baseline=True, new=list(jobs))"),
    ("extra: ids are forgotten when a posting disappears", "job_agent/state.py",
     '    seen = set(previous["seen_ids"]) if previous else set()\n    order, listed = [], set()',
     "    seen = set()\n    order, listed = [], set()"),
    ("extra: a saved run folder is reused", "job_agent/evidence.py",
     "path.mkdir(parents=True, exist_ok=False)", "path.mkdir(parents=True, exist_ok=True)"),
    ("extra: a resume not marked fictional passes", "job_agent/resume.py",
     '    if data.get("fictional") is not True:', '    if data.get("fictional") is False:'),
    ("extra: any email mentioning example.com passes", "job_agent/resume.py",
     'not re.fullmatch(r"[^@\\s]+@example\\.com", email)', 'not re.search(r"@example\\.com", email)'),
    ("extra: Claude gets the contact fields", "job_agent/resume.py",
     "if key not in CONTACT_FIELDS}", 'if key != "name"}'),
    ("extra: the rule takes the largest number of years", "job_agent/rule.py",
     "    n, quote = min(found, key=lambda pair: pair[0])", "    n, quote = max(found, key=lambda pair: pair[0])"),
    ("extra: a posting that states no years fails", "job_agent/rule.py",
     "    if not found:\n        return _cite(True,", "    if not found:\n        return _cite(False,"),
    ("extra: v0.2 still reads years only in 'experience' sentences", "job_agent/rule.py",
     '        if contract == "0.1" and "experience" not in sentence.lower():\n',
     '        if "experience" not in sentence.lower():\n'),
    ("extra: 'N years ago' is read as a requirement", "job_agent/rule.py",
     "            if contract != \"0.1\" and (_NOT_A_REQUIREMENT_AFTER.match(sentence[match.end():]) or\n",
     "            if contract != \"0.1\" and (False or\n"),
    ("extra: 'the next N years' is read as a requirement", "job_agent/rule.py",
     "                                      _NOT_A_REQUIREMENT_BEFORE.search(sentence[:match.start()])):\n",
     "                                      False):\n"),
    ("extra: team names after the comma trip the role check", "job_agent/rule.py",
     "    part = role_part(title)", "    part = title"),
    ("extra: level words match inside longer words", "job_agent/rule.py",
     "    found = [w for w in LEVEL_WORDS if _has_word(title, w)]",
     "    found = [w for w in LEVEL_WORDS if w.lower() in title.lower()]"),
    ("extra: a listed city counts outside the United States", "job_agent/rule.py",
     '        if country.lower() == "united states" and city.lower() in cities:', "        if city.lower() in cities:"),
    ("extra: the export-control 'may need' sentence blocks", "job_agent/rule.py",
     'US_PERSON_PHRASES = ("U.S. person",', 'US_PERSON_PHRASES = ("export control", "U.S. person",'),
    ("extra: U.S.-person phrases are skipped", "job_agent/rule.py",
     '    if auth["us_person"] is False:', "    if False:"),

    # Layer 2: GATE.md's wrong versions 1, 2 and 4 (3, the path tricks, come with the boundary tests).
    ("G1a a 404 board read as zero postings", "job_agent/providers.py",
     '    if status != 200:\n        raise Unverified(f"the board answered HTTP {status}, not 200")\n',
     '    if status == 404:\n        return []\n    if status != 200:\n'
     '        raise Unverified(f"the board answered HTTP {status}, not 200")\n'),
    ("G1b an empty jobs list read as zero postings", "job_agent/providers.py",
     '    if not jobs:\n        raise Unverified("the board\'s jobs list is empty")\n', ""),
    ("G1c a run with an unverified board reported finished", "job_agent/loop.py",
     '    if any(b.status == "unverified" for b in boards):\n        return gate.INCOMPLETE\n', ""),
    ("G2 a failed board's postings counted as gone", "job_agent/loop.py",
     '        if board.status == "read":\n            board.diff = board_state.diff(board.previous, board.postings)\n',
     '        if board.status in ("read", "unverified"):\n'
     '            board.diff = board_state.diff(board.previous, board.postings or [])\n'),
    ("G4a a retry not counted against the request budget", "job_agent/loop.py",
     '        self.used += 1\n        self.sent[("GET", url)] = times + 1\n',
     '        self.used += 0 if retry else 1\n        self.sent[("GET", url)] = times + 1\n'),
    ("G4b the request budget checked after sending", "job_agent/loop.py",
     '        if self.used >= self.limit:\n'
     '            raise BudgetStop("requests", f"the request budget of {self.limit} was used up")\n'
     '        self.used += 1\n        self.sent[("GET", url)] = times + 1\n        announce(self.used)\n'
     '        return get(url, gate.REQUEST_TIMEOUT)\n',
     '        self.used += 1\n        self.sent[("GET", url)] = times + 1\n        announce(self.used)\n'
     '        answer = get(url, gate.REQUEST_TIMEOUT)\n        if self.used > self.limit:\n'
     '            raise BudgetStop("requests", f"the request budget of {self.limit} was used up")\n'
     '        return answer\n'),
    ("G4c a command-line flag raises a budget", "job_agent/gate.py",
     "            if value > limit:\n", "            if False:\n"),
    ("extra: a 404 is retried", "job_agent/loop.py",
     "        except Unverified as exc:\n",
     "        except Unverified as exc:\n            if not retry:\n"
     "                _wait_for_retry(board, trace, budgets, elapsed, ledger, sleep, str(exc))\n"
     "                continue\n"),
    ("extra: the repeat rule is not enforced", "job_agent/loop.py",
     "        if times and not (retry and times == 1):\n", "        if False:\n"),
    ("extra: an unverified board's state is written", "job_agent/loop.py",
     '        if board.status != "read":\n            trace.add("state_write"',
     '        if board.status == "not visited":\n            trace.add("state_write"'),
    ("extra: a Lever posting's requirements in lists are not read", "job_agent/providers.py",
     '            parts += [item.get("text"), html_text(item.get("content") or "")]\n', '            pass\n'),
    ("G3a the write check compares path strings (runs-evil passes)", "job_agent/policy.py",
     "    try:\n        PurePath(target).relative_to(root)\n        return True\n    except ValueError:\n        return False\n",
     "    return str(target).startswith(str(root))\n"),
    ("G3b the write check does not refuse '..' first", "job_agent/policy.py",
     "        if \"..\" in target.parts:\n            raise Refused(f\"refused: {kind} {path}: a path with '..' is never followed\")\n",
     ""),
    ("G3c the write check follows a symlink", "job_agent/policy.py",
     "                _refuse_symlinks(target, root, kind, path)\n", ""),
    ("extra: a look-alike host passes the policy (prefix)", "job_agent/policy.py",
     "    if host not in HOSTS:\n", "    if not any(host.startswith(h) for h in HOSTS):\n"),
    ("extra: a look-alike host passes the policy (substring)", "job_agent/policy.py",
     "    if host not in HOSTS:\n", "    if not any(h in host for h in HOSTS):\n"),
    ("extra: a user name before @ passes the policy", "job_agent/policy.py",
     "    if parts.username is not None or parts.password is not None:\n", "    if False:\n"),
    ("extra: any path on an allowed host passes", "job_agent/policy.py",
     "    if not path.fullmatch(parts.path) or parts.query != query or parts.fragment:\n", "    if False:\n"),
    ("extra: a method other than GET passes", "job_agent/policy.py",
     "    if method not in METHODS:\n", "    if False:\n"),
    ("extra: deleting a board's state needs no approval", "job_agent/policy.py",
     "        if not approval:\n            raise NeedsApproval(f\"refused: deleting", "        if False:\n            raise NeedsApproval(f\"refused: deleting"),
    ("extra: a redirect is followed as a transient failure", "job_agent/loop.py",
     "            return _unverified(board, trace, str(exc))\n        saved = _save_answer(",
     "            if not retry:\n                continue\n"
     "            return _unverified(board, trace, str(exc))\n        saved = _save_answer("),
    # JS3: FILTER.md v1.0, Section 4's wrong versions W1 to W7, then extra mistakes in the filter (2026-11-21).
    ("JS3 W1 role phrases match inside longer words", "job_agent/filter.py",
     '    included = next((p for p in rules["role_includes"] if _has_word(part, p)), None)',
     '    included = next((p for p in rules["role_includes"] if p.lower() in part.lower()), None)'),
    ("JS3 W2 years read only in sentences with 'experience'", "job_agent/filter.py",
     "    for sentence in sentences:\n        for match in YEARS.finditer(sentence):\n",
     "    for sentence in sentences:\n        if \"experience\" not in sentence.lower():\n            continue\n"
     "        for match in YEARS.finditer(sentence):\n"),
    ("JS3 W3 optional years treated as required", "job_agent/filter.py",
     '            if any(_has_word(sentence, p) for p in rules["years_optional_phrases"]):',
     "            if any(_has_word(sentence, p) for p in []):"),
    ("JS3 W4 one posting with no title refuses its board", "job_agent/providers.py",
     '            posting["title"] = ""\n            posting["_cannot_tell"] = "the posting has no title"\n',
     '            raise Unverified(f"job {index} has no title")\n'),
    ("JS3 W5 ties broken by the order postings arrive", "job_agent/filter.py",
     '    return (-record["score"], 0 if when else 1, -(when.timestamp() if when else 0), str(record["id"]))',
     '    return (-record["score"],)'),
    ("JS3 W6 REST matched in any case", "job_agent/filter.py",
     "                hit = _has_exact_word(sentence, term) if term in exact else _has_word(sentence, term)",
     "                hit = _has_word(sentence, term)"),
    ("JS3 W7 every location outside the person's areas rejected", "job_agent/filter.py",
     '        return _result("R2", "soft", us_seen[0],', '        return _result("R2", "reject", us_seen[0],'),
    ("JS3 extra: the 'Dec.' splitter fix is gone", "job_agent/filter.py",
     '        if out and out[-1][1] == " " and _MONTH_ABBREVIATION_END.search(out[-1][0]) and _YEAR_START.match(piece):',
     "        if False:"),
    ("JS3 extra: the cutoff is exclusive", "job_agent/filter.py",
     '    eligible = [r for r in records if r["fate"] == "kept" and r["score"] >= rank["shortlist_min"]]',
     '    eligible = [r for r in records if r["fate"] == "kept" and r["score"] > rank["shortlist_min"]]'),
    ("JS3 extra: duplicates keep the oldest copy", "job_agent/filter.py",
     "        if key not in newest or _newer(record, newest[key]):",
     "        if key not in newest or _newer(newest[key], record):"),
    ("JS3 extra: a missing employment type passes", "job_agent/filter.py",
     '        return _result("R1", "cannot_tell", None, "the employment type is missing",',
     '        return _result("R1", "pass", None, "the employment type is missing",'),
    ("JS3 extra: topic points are not capped", "job_agent/filter.py",
     '              min(rank["topic_cap"], rank["per_topic_group"] * groups))]',
     '              rank["per_topic_group"] * groups)]'),
    ("JS3 extra: a posting with no description is judged", "job_agent/filter.py",
     '    if not reason and not description.strip():\n        reason = "the posting has no description"\n',
     '    if False:\n        reason = "the posting has no description"\n'),
    ("JS3 extra: the company words are ignored", "job_agent/filter.py",
     '            company = next((w for w in rules["years_company_words"] if _has_word(sentence, w)), None)',
     "            company = None"),
    ("JS3 extra: a season before the earliest start passes", "job_agent/filter.py",
     "    return first > limit[1]", "    return first < limit[1]"),
    # JS3 step 2 item 3: mistakes in the MCP server (2026-11-21).
    ("MCP: ready set on initialize, so the initialized notification is skipped", "job_agent/mcp_server.py",
     "        self.initialized = True\n        # Version negotiation",
     "        self.initialized = True\n        self.ready = True\n        # Version negotiation"),
    ("MCP: a tool error sent with isError false (a failure dressed as a result)", "job_agent/mcp_server.py",
     '    return {"content": [{"type": "text", "text": text}], "isError": True}',
     '    return {"content": [{"type": "text", "text": text}], "isError": False}'),
    ("MCP: an extra argument is accepted (additionalProperties ignored)", "job_agent/mcp_server.py",
     '    if extra:\n        problems.append("not allowed: "', '    if False:\n        problems.append("not allowed: "'),
    ("MCP: the transcript guard compares path strings (a sibling folder passes)", "job_agent/mcp_server.py",
     "    if path.parent.resolve() != root.resolve():",
     "    if not str(path.parent.resolve()).startswith(str(root.resolve())):"),
    ("MCP: a status line on stdout", "job_agent/mcp_server.py",
     "        reason = serve(Server(repo), stdin or sys.stdin.buffer, stdout or sys.stdout.buffer, transcript)",
     '        print("job-search-agent MCP server ready", flush=True)\n'
     "        reason = serve(Server(repo), stdin or sys.stdin.buffer, stdout or sys.stdout.buffer, transcript)"),
    ("MCP: a transcript written without being asked for", "job_agent/mcp_server.py",
     "    transcript = None\n    if args.transcript is not None:",
     '    transcript = None\n    args.transcript = args.transcript or "js3/mcp/transcripts/default.jsonl"\n'
     "    if args.transcript is not None:"),
]


def run_tests(work: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    args = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."]
    try:
        return subprocess.run(args, cwd=work, env=env, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:  # a suite that hangs under a mutant did not pass
        return subprocess.CompletedProcess(args, 1, "", "the tests did not end within 600 s")


def main() -> int:
    work = Path(tempfile.mkdtemp(prefix="job-agent-mutants-"))
    try:
        for item in COPIED:
            shutil.copytree(REPO / item, work / item, ignore=shutil.ignore_patterns("__pycache__"))
        for item in COPIED_FILES:
            shutil.copy2(REPO / item, work / item)
        for label, file, old, new in MUTANTS:
            text = (work / file).read_text(encoding="utf-8")
            if text.count(old) != 1:
                print(f"{label}: the text to break is not found exactly once in {file}")
                return 2
            compile(text.replace(old, new), file, "exec")
        baseline = run_tests(work)
        if baseline.returncode != 0:
            print("the unbroken copy FAILS its tests:\n" + baseline.stderr[-3000:])
            return 2
        print("unbroken copy passes")
        survived = []
        for label, file, old, new in MUTANTS:
            path = work / file
            original = path.read_text(encoding="utf-8")
            path.write_text(original.replace(old, new), encoding="utf-8")
            try:
                result = run_tests(work)
            finally:
                path.write_text(original, encoding="utf-8")
            caught = result.returncode != 0
            failing = [line.split(" (")[0] for line in result.stderr.splitlines() if line.startswith(("FAIL:", "ERROR:"))]
            detail = f"{len(failing)} failing, first {failing[0]}" if failing else ""
            print(f"{'caught  ' if caught else 'SURVIVED'}  {label}   {detail}")
            if not caught:
                survived.append(label)
        print(f"\n{len(MUTANTS) - len(survived)} of {len(MUTANTS)} planted mistakes caught")
        return 1 if survived else 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
