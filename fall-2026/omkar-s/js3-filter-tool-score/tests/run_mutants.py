"""Apply each wrong version (tests/mutants/wrong_versions.py) to a temp copy and run the full suite.

    python3 tests/run_mutants.py

First a CONTROL run on the unchanged copy must pass; otherwise every KILLED would be meaningless.
Exit 0 only if the control passes and every mutant is KILLED.
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "mutants"))
from wrong_versions import MUTANTS  # noqa: E402

SKIP = {"transcripts", "__pycache__", ".git", "runs"}


def copy_tree(dst):
    for name in os.listdir(BASE):
        if name in SKIP:
            continue
        s, d = os.path.join(BASE, name), os.path.join(dst, name)
        if os.path.isdir(s):
            shutil.copytree(s, d, ignore=shutil.ignore_patterns("__pycache__", "runs", "raw"))
        else:
            shutil.copy2(s, d)


def suite(root):
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."],
                       cwd=root, capture_output=True, text=True, timeout=300)
    last = [l for l in r.stderr.strip().splitlines() if l.strip()][-1:] or ["?"]
    if r.returncode != 0 and os.environ.get("MUTANT_DEBUG"):
        print(r.stderr[-3000:])
    return r.returncode, last[0]


def main():
    with tempfile.TemporaryDirectory() as root:
        copy_tree(root)
        code, last = suite(root)
        print(f"CONTROL (no change): {'passed' if code == 0 else 'FAILED'} ({last})")
        if code != 0:
            print("CONTROL FAILED: the copy is incomplete or the suite is red; no mutant result is valid")
            return 2
    killed, total = 0, 0
    for mid, rel, old, new, what in MUTANTS:
        total += 1
        with tempfile.TemporaryDirectory() as root:
            copy_tree(root)
            path = os.path.join(root, rel)
            with open(path, encoding="utf-8") as f:
                src = f.read()
            if src.count(old) != 1:
                print(f"{mid:5} ERROR  replacement not found exactly once in {rel}: the mutant is stale")
                continue
            with open(path, "w", encoding="utf-8") as f:
                f.write(src.replace(old, new))
            code, last = suite(root)
            status = "KILLED" if code != 0 else "SURVIVED"
            killed += code != 0
            print(f"{mid:5} {status:8} {what} ({last})")
    print(f"{killed}/{total} KILLED")
    return 0 if killed == total else 1


if __name__ == "__main__":
    sys.exit(main())
