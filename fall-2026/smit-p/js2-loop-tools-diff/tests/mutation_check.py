"""Do the tests catch the wrong versions listed in GATE.md?

    python3 tests/mutation_check.py

For each wrong version, copy the assignment folder to a temporary directory, plant the
wrong code with one exact text replacement, run the offline test suite there, and report
whether the suite failed (caught) or passed (missed). The real code is never modified.
A replacement that does not match exactly is reported as an error, so a stale mutant
cannot pass silently.
"""

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MUTANTS = [
    ("W2 failure becomes zero", "agent/loop.py",
     'reason="board name not found (404)")',
     'reason="board name not found (404)", count=0)'),
    ("W3a prefix check for paths", "agent/policy.py",
     "if os.path.commonpath([root_real, target]) == root_real:",
     "if target.startswith(root_real):"),
    ("W3b path check without resolving symlinks", "agent/policy.py",
     "return os.path.realpath(joined)",
     "return os.path.abspath(joined)"),
    ("W4 suffix check for hosts", "agent/policy.py",
     "if host not in ALLOWED_HOSTS:",
     "if not any(host.endswith(h.split('.', 1)[1]) for h in ALLOWED_HOSTS):"),
    ("W5 retry everything", "agent/loop.py",
     "transient = resp.error is not None or (resp.http_status or 0) >= 500",
     "transient = resp.error is not None or (resp.http_status or 0) >= 400"),
    ("W6 stop means success", "agent/loop.py",
     "        status = BUDGET_EXHAUSTED",
     "        status = FINISHED"),
    ("W7 baseline overwritten by a failure", "agent/loop.py",
     '            if r["status"] == "ok":\n                new_by_board',
     '            if r.setdefault("ids", []) is not None and r.setdefault("titles", {}) is not None:\n'
     '                r["count"] = r["count"] or 0\n                new_by_board'),
    ("W8 Ashby unlisted postings counted", "agent/adapters.py",
     "        if job.get(\"isListed\") is False:  # unlisted postings are not public openings\n"
     "            continue\n",
     ""),
]


def run_suite(folder):
    proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."],
                          cwd=folder, capture_output=True, text=True)
    last = [l for l in proc.stderr.strip().splitlines() if l.strip()][-1]
    return proc.returncode, last


def main():
    rc, last = run_suite(HERE)
    print(f"{'unmutated code':<45} suite {'passes' if rc == 0 else 'FAILS'}  ({last})")
    if rc != 0:
        print("the real code must pass before mutants mean anything")
        return 1
    missed = 0
    for name, rel, old, new in MUTANTS:
        with tempfile.TemporaryDirectory() as tmp:
            copy = os.path.join(tmp, "copy")
            shutil.copytree(HERE, copy, ignore=shutil.ignore_patterns("jobs", "__pycache__", ".git"))
            path = os.path.join(copy, rel)
            src = open(path).read()
            if src.count(old) != 1:
                print(f"{name:<45} ERROR: replacement text found {src.count(old)} times in {rel}")
                missed += 1
                continue
            open(path, "w").write(src.replace(old, new))
            rc, last = run_suite(copy)
            caught = rc != 0
            missed += not caught
            print(f"{name:<45} {'caught' if caught else 'MISSED'}  ({last})")
    print(f"{len(MUTANTS) - missed}/{len(MUTANTS)} wrong versions caught")
    return 1 if missed else 0


if __name__ == "__main__":
    sys.exit(main())
