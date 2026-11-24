"""Plant each FILTER.md wrong version into a temporary copy of the code and show the tests catch it.

    python3 tools/check_wrong_versions.py
The clean copy must pass; every planted wrong version must make at least one test fail. Offline, a few seconds.
(Same method as my JS2 tools/check_wrong_versions.py.)
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MUTATIONS = {
    "W1 substring matching": (
        "js3/text.py",
        '    pattern = r"(?<![A-Za-z0-9])" + r"\\s+".join(map(re.escape, term.split())) + r"(?![A-Za-z0-9])"',
        '    pattern = r"\\s+".join(map(re.escape, term.split()))'),
    "W2 score without the gates": (
        "js3/filter.py", '    rec["gates_failed"] = gate_failures(posting, flt)', '    rec["gates_failed"] = []'),
    "W3 title-blind scoring (gate G5 removed)": (
        "filters/filter-v1.json", '"require_role_word_in_title": true', '"require_role_word_in_title": false'),
    "W4 threshold tuned after looking at held-out labels": (
        "filters/filter-v1.json", '"threshold": 6,', '"threshold": 5,'),
}


def run_tests(where):
    p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=where,
                       capture_output=True, text=True)
    return p.returncode, (p.stderr.strip().splitlines() or [""])[-1]


def main():
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        clean = Path(tmp) / "clean"
        shutil.copytree(ROOT, clean, ignore=shutil.ignore_patterns("out", "__pycache__", "transcripts", "runs"))
        rc, last = run_tests(clean)
        print(f"clean copy: {'PASS' if rc == 0 else 'FAIL'} ({last})")
        ok &= rc == 0
        for name, (rel, old, new) in MUTATIONS.items():
            d = Path(tmp) / name.split()[0]
            shutil.copytree(clean, d)
            f = d / rel
            src = f.read_text()
            if src.count(old) != 1:
                print(f"{name}: could not plant (pattern found {src.count(old)} times)")
                ok = False
                continue
            f.write_text(src.replace(old, new))
            rc, last = run_tests(d)
            caught = rc != 0
            print(f"{name}: {'CAUGHT' if caught else 'NOT CAUGHT'} ({last})")
            ok &= caught
    print("ALL WRONG VERSIONS CAUGHT" if ok else "SOME WRONG VERSION NOT CAUGHT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
