"""Plant each CONTRACT.md wrong version into a temporary copy of the real code and show the tests catch it.

    python3 tools/check_wrong_versions.py
Each mutation must make at least one test fail or error; the clean copy must pass.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MUTATIONS = {
    "wrong version 1: verdicts attached to the next posting (shifted by one)": (
        "jsagent/watch.py",
        "    for p in postings:\n        v = judge_fn(p)\n        validate_verdict(v, p[\"id\"])\n        out.append(v)",
        "    for i, p in enumerate(postings):\n        v = {**judge_fn(p), \"id\": postings[(i + 1) % len(postings)][\"id\"]}\n        out.append(v)"),
    "wrong version 2: justification cites nothing": (
        "jsagent/rules.py",
        "        \"justification\": \"; \".join(reasons),",
        "        \"justification\": \"Good fit.\","),
    "extra: an already-seen posting is reported as new": (
        "jsagent/watch.py",
        "    return [j for j in jobs if j[\"id\"] not in seen]",
        "    return list(jobs)"),
    "extra: substring skill match ('SQL' inside 'NoSQL')": (
        "jsagent/rules.py",
        "    pattern = r\"(?<![A-Za-z0-9])\" + r\"\\s+\".join(map(re.escape, term.split())) + r\"(?![A-Za-z0-9])\"",
        "    pattern = r\"\\s+\".join(map(re.escape, term.split()))"),
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
            shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns("runs", "snapshots", "__pycache__", "experiments"))
            if path:
                src = (work / path).read_text()
                assert src.count(old) == 1, f"mutation anchor not found once: {name}"
                (work / path).write_text(src.replace(old, new))
            passed, failed = run_tests(work)
            expected = path is None
            ok = passed == expected
            all_ok &= ok
            verdict = "tests pass" if passed else f"caught by {failed}"
            print(f"[{'OK' if ok else 'PROBLEM'}] {name}: {verdict}")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
