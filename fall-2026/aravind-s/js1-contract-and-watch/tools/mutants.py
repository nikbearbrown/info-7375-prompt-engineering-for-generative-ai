"""Plant each wrong version from CONTRACT.md in a copy of the code and check that the tests fail.

A suite that still passes when the code is broken proves nothing. Each mutant below swaps one piece
of code for a plausible mistake. The first entries are the contract's "Wrong versions" (W1 to W4);
the ones marked "extra" are further mistakes the tests also have to catch. The copy lives in a
temporary folder, so the repo itself is never touched. A mutant is "caught" when a test fails.

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
COPIED = ("job_agent", "tests", "persona", "runs", "labels", "tools", "prompts", "experiment")

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
