#!/usr/bin/env python3
"""Plant each GATE.md wrong version in a scratch copy and confirm the tests catch it.

Rerun this after every change to the code or the rules (TA feedback on JS1). It never edits
this folder: each wrong version is planted in a fresh temporary copy.

  baseline  the unchanged code: every test must pass
  WV1       a failed board is reported as an ok board with zero new jobs   (GATE.md section 6)
  WV2       the folder check compares strings, so runs-evil passes as runs  (GATE.md section 6)
  WV3       a retry is not counted against the request budget              (GATE.md section 6)

usage (from this folder):
  python3 wrong_versions.py
exit codes: 0 baseline passes and every wrong version is caught, 1 otherwise
"""
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
COPY = ["agent.py", "policy.py", "providers.py", "record.py", "independent_check.py", "tests", "persona", "config"]
WRONG_VERSIONS = [
    ("WV1 failed board reported as zero new", "agent.py",
     '    res["status"] = kind\n', '    res["status"] = "ok"\n'),
    ("WV2 string-prefix folder check", "policy.py",
     "return Path(path).resolve().is_relative_to(Path(folder).resolve())",
     "return str(Path(path).resolve()).startswith(str(Path(folder).resolve()))"),
    ("WV3 retries not counted", "agent.py",
     "                requests_used += 1\n", "                requests_used += 1 if attempt == 1 else 0\n"),
]


def run_tests(folder):
    p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=folder,
                       capture_output=True, text=True, env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"})
    failed = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \((\S+)\)", p.stderr, re.M)))
    ran = re.search(r"^Ran (\d+) tests?", p.stderr, re.M)
    return p.returncode, failed, int(ran.group(1)) if ran else 0


def scratch_copy(dest):
    for name in COPY:
        src = HERE / name
        if src.is_dir():
            shutil.copytree(src, dest / name, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(src, dest / name)


def main():
    print(f"Wrong-version check, {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    ok = True
    with tempfile.TemporaryDirectory(prefix="js2-wrong-") as tmp:
        base = Path(tmp) / "baseline"
        base.mkdir()
        scratch_copy(base)
        code, failed, ran = run_tests(base)
        print(f"  baseline (unchanged code): {ran} tests, {'PASS' if code == 0 else 'FAIL ' + str(failed)}")
        ok = ok and code == 0
        for name, file, old, new in WRONG_VERSIONS:
            d = Path(tmp) / name.split()[0]
            d.mkdir()
            scratch_copy(d)
            src = (d / file).read_text(encoding="utf-8")
            if src.count(old) != 1:
                print(f"  {name}: CANNOT PLANT (the line to change is not found exactly once in {file})")
                ok = False
                continue
            (d / file).write_text(src.replace(old, new), encoding="utf-8")
            code, failed, ran = run_tests(d)
            caught = code != 0 and failed
            ok = ok and bool(caught)
            print(f"  {name}: {'CAUGHT' if caught else 'NOT CAUGHT'} by {len(failed)} failing test(s)")
            for test, where in failed:          # Python 3.11+ already ends `where` with the test name
                print(f"      {where if where.endswith('.' + test) else where + '.' + test}")
    print("RESULT: every wrong version was caught" if ok else "RESULT: a wrong version survived, or the baseline failed")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
