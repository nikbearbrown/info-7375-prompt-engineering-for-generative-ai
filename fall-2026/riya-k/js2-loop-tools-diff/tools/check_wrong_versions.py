"""Plant each GATE.md wrong version into a temporary copy of the real code and show a test catches it.

    python3 tools/check_wrong_versions.py
The clean copy must pass; every mutation must make at least one test fail. Offline, about 2 s.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MUTATIONS = {
    "1 empty board reported as success": (
        "jsagent/loop.py", "    if not postings and empty_guard:", "    if False:"),
    "2 failure turned into a number (0, not null)": (
        "jsagent/loop.py", '"attempts": 0, "http_status": None,\n           "postings": None,',
        '"attempts": 0, "http_status": None,\n           "postings": 0,'),
    "3a wrong exit: finished although a board failed": (
        "jsagent/loop.py", 'exit_status = "incomplete" if bad else "finished"', 'exit_status = "finished"'),
    "3b wrong exit: finished although the budget ran out": (
        "jsagent/loop.py", '        exit_status = "budget_exhausted"', '        exit_status = "finished"'),
    "4a retrying a 404": (
        "jsagent/loop.py", "if 500 <= status < 600 and attempt == 1:", "if status != 200 and attempt == 1:"),
    "4b retrying with no wait": (
        "jsagent/loop.py", "            s.sleep(RETRY_WAIT)", "            pass"),
    "5 budget off by one (11th request)": (
        "jsagent/loop.py", "if self.requests >= MAX_REQUESTS:", "if self.requests > MAX_REQUESTS:"),
    "6 prefix path check (runs-evil passes)": (
        "jsagent/policy.py", "    return real == base or base in real.parents",
        "    return str(real).startswith(str(base))"),
    "7 substring host check (greenhouse.io.evil.com passes)": (
        "jsagent/policy.py", "        if u.hostname not in ALLOWED_HOSTS:",
        "        if not any(h in url for h in ALLOWED_HOSTS):"),
    "8 symlink escape (path text checked, not real path)": (
        "jsagent/policy.py", "real, base = Path(os.path.realpath(path)), Path(os.path.realpath(root))",
        "real, base = Path(os.path.abspath(path)), Path(os.path.abspath(root))"),
}


def run_tests(where):
    p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=where,
                       capture_output=True, text=True)
    failed = [l.split(" ")[1] for l in p.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
    return p.returncode == 0, failed


def main():
    all_ok = True
    with tempfile.TemporaryDirectory() as d:
        for name, (path, old, new) in [("clean copy", (None, None, None))] + list(MUTATIONS.items()):
            work = Path(d) / "copy"
            shutil.rmtree(work, ignore_errors=True)
            shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns("runs", "snapshots", "__pycache__", "review"))
            if path:
                src = (work / path).read_text()
                assert src.count(old) == 1, f"mutation anchor not found exactly once: {name}"
                (work / path).write_text(src.replace(old, new))
            passed, failed = run_tests(work)
            ok = passed == (path is None)
            all_ok &= ok
            print(f"[{'OK' if ok else 'PROBLEM'}] {name}: {'tests pass' if passed else 'caught by ' + ', '.join(failed)}")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
