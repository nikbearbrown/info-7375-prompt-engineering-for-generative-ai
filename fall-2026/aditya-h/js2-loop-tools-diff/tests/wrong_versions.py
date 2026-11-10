"""Plant each GATE.md wrong version into a temporary copy of the code and show the suite fails on it.
The real code is never modified. Usage: python3 tests/wrong_versions.py
"""
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]

PLANTS = {
    "wrong version 1 (stopped = succeeded)": [
        ('exit_status = "finished" if all(e["status"] == "ok" for e in entries) else "incomplete"',
         'exit_status = "finished"'),
        ('"budget-exhausted", "requests"', '"finished", "requests"'),
    ],
    "wrong version 2 (invented value on failure)": [
        ('e.update(status="failed", reason=err or f"HTTP {status}")',
         'e.update(status="failed", reason=err or f"HTTP {status}", fetched=0, new=0, relevant=0)'),
    ],
    "wrong version 3 (retry everything)": [
        ('if transient and e["attempts"] == 1:', 'if status != 200 and e["attempts"] < 3:'),
    ],
}


def run_suite(tree):
    p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=tree,
                       capture_output=True, text=True)
    m = re.search(r"Ran (\d+) tests", p.stderr)
    f = re.search(r"FAILED \((?:failures=(\d+))?(?:, )?(?:errors=(\d+))?", p.stderr)
    bad = sum(int(x) for x in f.groups() if x) if f else 0
    names = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \((\S+)\)", p.stderr, re.M)))
    return int(m.group(1)) if m else 0, bad, [c.split('.', 1)[1] for t, c in names]


def main():
    n, bad, _ = run_suite(ROOT)
    print(f"correct code: {n} tests, {bad} failing")
    ok = bad == 0
    for name, edits in PLANTS.items():
        with tempfile.TemporaryDirectory() as d:
            tree = pathlib.Path(d) / "js2"
            shutil.copytree(ROOT, tree, ignore=shutil.ignore_patterns("runs", "__pycache__"))
            loop = tree / "jobwatch2" / "loop.py"
            src = loop.read_text()
            for old, new in edits:
                assert old in src, f"plant target missing: {old}"
                src = src.replace(old, new)
            loop.write_text(src)
            (tree / "runs").mkdir()
            n, bad, which = run_suite(tree)
        ok &= bad > 0
        print(f"{name}: {bad} of {n} tests fail -> {'CAUGHT' if bad else 'NOT CAUGHT'}")
        for w in which:
            print(f"    {w}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
