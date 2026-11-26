"""Build each FILTER.md wrong version as a mutant copy and confirm its named test fails.

Usage: .venv/bin/python tools/check_wrong_versions_js3.py
W1-W5 are FILTER.md section 4; S1-S3 are the server wrong versions in section 7. Each mutant is a copy of the
project in a temp dir with one textual edit; the real code is untouched. A mutant whose anchor text is missing
counts as NOT caught, so a refactor cannot make this pass silently.
"""
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
TESTS = ["tests/test_js3_filter.py", "tests/test_js3_mcp.py"]
FLT, SL, SRV = "jsfilter/filter.py", "jsfilter/shortlist.py", "jsfilter/mcp_server.py"

MUTANTS = [
    ("W1 topic words bypass the role title", "test_topic_cannot_bypass_role_title",
     [(FLT, 'failed = [k for k, v in rules.items() if not v["passed"]]',
       'failed = [k for k, v in rules.items() if not v["passed"] and not (k == "R1" and topics)]')]),
    ("W2 skills matched as substrings", "test_two_distinct_bounded_skills",
     [(FLT, "if key not in seen and contains_sequence(desc_n, key):", "if key not in seen and key in desc_n:")]),
    ("W2 a repeated skill counts again", "test_two_distinct_bounded_skills",
     [(FLT, "                seen.add(key)\n                skills.append(skill)",
       "                seen.add(key)\n                skills.extend([skill] * max(1, desc_n.split().count(key)))")]),
    ("W3 ranking sorts worst first", "test_score_descending_and_stable_ties",
     [(FLT, 'key=lambda r: (-r["total"], r["board"], r["id"])', 'key=lambda r: (r["total"], r["board"], r["id"])')]),
    ("W3 ties broken by insertion order", "test_score_descending_and_stable_ties",
     [(FLT, 'key=lambda r: (-r["total"], r["board"], r["id"])', 'key=lambda r: -r["total"]')]),
    ("W4 empty board reported as zero relevant", "test_missing_board_is_unknown",
     [(FLT, "    if not items:\n", "    if False:\n")]),
    ("W5 draft claims start as supported", "test_score_does_not_entail_claim",
     [(SL, '"label": "not reviewed", "reviewer": None', '"label": "supported", "reviewer": "filter"')]),
    ("W5 shortlist renders unreviewed claims as fact", "test_score_does_not_entail_claim",
     [(SL, "    ok = publishable(claims)\n", "    ok = claims\n")]),
    ("S1 ready set inside initialize", "test_row3_tools_list_after_initialize_before_notification_is_32000",
     [(SRV, "            self.initialized = True\n            return _result(",
       "            self.initialized = True\n            self.ready = True\n            return _result(")]),
    ("S2 tool call appends to a log file", "test_stdio_session_writes_no_files",
     [(SRV, "        board, pid = args[\"board\"], args[\"id\"]\n",
       "        board, pid = args[\"board\"], args[\"id\"]\n"
       "        pathlib.Path(\"score_posting.log\").open(\"a\").write(board + pid + \"\\n\")\n")]),
    ("S3 returned score disagrees with the posting", "test_returned_score_recomputes_from_the_saved_posting",
     [(SRV, '"components": row["components"], "total": row["total"],',
       '"components": row["components"], "total": row["total"] + 1,')]),
]

_FAILED = re.compile(r"^FAILED \S+::(\w+)")


def main():
    all_caught = True
    for name, test, edits in MUTANTS:
        with tempfile.TemporaryDirectory() as tmp:
            copy = pathlib.Path(tmp) / "proj"
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(
                ".venv", ".git", "__pycache__", ".pytest_cache", "evidence", "runs", "state", "experiment",
                "third_party", "*.zip"))
            applied = True
            for rel, old, new in edits:
                target = copy / rel
                source = target.read_text()
                if source.count(old) != 1:
                    print(f"[{name}] MUTATION NOT APPLIED: anchor found {source.count(old)} times in {rel}")
                    applied = False
                    break
                target.write_text(source.replace(old, new, 1))
            if not applied:
                all_caught = False
                continue
            proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *TESTS],
                                  cwd=copy, capture_output=True, text=True)
            failed = sorted({m.group(1) for line in proc.stdout.splitlines() if (m := _FAILED.match(line))})
            caught = test in failed
            all_caught &= caught
            print(f"[{name}] named test {test}: {'FAILED (caught)' if caught else 'PASSED (NOT caught)'}"
                  f"; all failing tests: {', '.join(failed) or 'none'}")
    print(f"\n{len(MUTANTS)} mutants: " + ("all wrong versions caught" if all_caught
                                         else "SOME WRONG VERSION WAS NOT CAUGHT"))
    return 0 if all_caught else 1


if __name__ == "__main__":
    sys.exit(main())
