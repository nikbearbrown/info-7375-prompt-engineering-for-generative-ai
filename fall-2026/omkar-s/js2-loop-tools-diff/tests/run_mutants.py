"""Apply each wrong version (tests/mutants/mutants.py) to a copy of the code and run the suite.

    python3 tests/run_mutants.py            # all mutants
    python3 tests/run_mutants.py W1 W4      # some

CONTROL = the same copy WITHOUT any edit is run first and must pass; otherwise nothing is judged.
KILLED  = at least one test FAILED or raised inside a test on the wrong version (good).
SURVIVED = the suite passed on the wrong version (a test is missing).
INVALID = the copy could not even load a test module (an import error), so a "failure" would
          say nothing about the mutant.
STALE   = the mutant's source text is not in the code any more (fix the mutant, not the test).
Exit code 0 only if the control passes and every selected mutant is KILLED.

Bug fixed 2026-11-09 ~08:2x UTC (found by an independent TA-style review): the copy left out
verify/, so tests.test_independent_check failed to import in every copy and every mutant was
counted KILLED whatever it did. Runs saved before 08:10:59 predate that test module and are valid;
the 08:10:59 run is not.
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "mutants"))
from mutants import MUTANTS  # noqa: E402


COPY_DIRS = ("agent", "verify", "tests", "persona", "config")


def _suite(cwd):
    p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."],
                       cwd=cwd, capture_output=True, text=True, timeout=300)
    failed = [l.split(" (")[0].replace("FAIL: ", "").replace("ERROR: ", "")
              for l in p.stderr.splitlines() if l.startswith(("FAIL: ", "ERROR: "))]
    load_errors = [l for l in p.stderr.splitlines() if "unittest.loader._FailedTest" in l]
    return p.returncode, failed, load_errors


def control():
    tmp = tempfile.mkdtemp(prefix="js2-control-")
    try:
        for d in COPY_DIRS:
            shutil.copytree(os.path.join(ROOT, d), os.path.join(tmp, d),
                            ignore=shutil.ignore_patterns("__pycache__"))
        return _suite(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run_one(m):
    tmp = tempfile.mkdtemp(prefix=f"js2-mutant-{m['id']}-")
    try:
        for d in COPY_DIRS:
            shutil.copytree(os.path.join(ROOT, d), os.path.join(tmp, d),
                            ignore=shutil.ignore_patterns("__pycache__"))
        path = os.path.join(tmp, "agent", m["file"])
        with open(path, encoding="utf-8") as f:
            src = f.read()
        for old, new, count in m["edits"]:
            if src.count(old) != count:
                return "STALE", f"expected {count}x {old.strip()!r}, found {src.count(old)}"
            src = src.replace(old, new)
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
        code, failed, load_errors = _suite(tmp)
        if load_errors:
            return "INVALID", "test module failed to load: " + "; ".join(load_errors)
        return ("KILLED" if code != 0 else "SURVIVED"), ", ".join(failed) or "-"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(ids):
    code, failed, load_errors = control()
    if code != 0:
        print(f"CONTROL FAILED: the unmutated copy does not pass ({', '.join(failed) or load_errors}).")
        print("No mutant can be judged.")
        return 2
    print("CONTROL  passed: the unmutated copy passes every test\n")
    chosen = [m for m in MUTANTS if not ids or m["id"] in ids]
    bad = 0
    for m in chosen:
        verdict, detail = run_one(m)
        bad += verdict != "KILLED"
        print(f"{m['id']:4} {verdict:8} {m['what']}\n       killed by: {detail}")
    print(f"\n{len(chosen) - bad}/{len(chosen)} wrong versions KILLED")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
