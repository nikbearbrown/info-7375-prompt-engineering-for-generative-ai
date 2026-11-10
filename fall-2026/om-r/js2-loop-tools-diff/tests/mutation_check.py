"""Mutation check for agent/permissions.py (FRICTIONAL.md entry 6).

Copies agent/ and tests/ into a fresh temp directory (the project tree is
never modified), applies one mutation at a time to the copied
agent/permissions.py, runs tests/test_permissions.py against it, and reports
whether the tests CAUGHT the mutation (at least one test failed) or let it
SURVIVE (all tests passed).

Before any mutation, the unmutated copy must pass; otherwise the check
aborts, because a "caught" would mean nothing. Each mutation's original text
must occur exactly once, so a mutation that no longer applies is an error,
not a silent "caught".

    python3 tests/mutation_check.py        # exit 0 only if every mutation is caught
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = "agent/permissions.py"

MUTATIONS = [
    ("re-add api.anthropic.com to the host allow-list",
     'ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.lever.co"})',
     'ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.lever.co", "api.anthropic.com"})'),
    ("drop the port check",
     " or port not in (None, 443)",
     ""),
    ("disable new-board approval",
     "if not real.exists() and board not in self.approved_new_boards:",
     "if False:"),
    ("resolve paths with abspath instead of realpath (stop following symlinks)",
     "return Path(os.path.realpath(p))",
     "return Path(os.path.abspath(p))"),
    ("string-prefix containment instead of path-component containment",
     "real != d and real.is_relative_to(d)",
     "real != d and str(real).startswith(str(d))"),
]


def run_tests(tree):
    proc = subprocess.run([sys.executable, "-m", "unittest", "-v", "tests.test_permissions"],
                          cwd=tree, capture_output=True, text=True)
    failed = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\w+)", proc.stderr, re.M)))
    summary = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "(no output)"
    return proc.returncode == 0, failed, summary


def fresh_copy(dest):
    for d in ("agent", "tests"):
        shutil.copytree(ROOT / d, dest / d, ignore=shutil.ignore_patterns("__pycache__"))


def main():
    original = (ROOT / TARGET).read_text()
    with tempfile.TemporaryDirectory(prefix="js2_mutation_") as tmp:
        tmp = Path(tmp)
        base = tmp / "unmutated"
        fresh_copy(base)
        ok, failed, summary = run_tests(base)
        print(f"unmutated {TARGET}: {'PASS' if ok else 'FAIL'} ({summary})")
        if not ok:
            print(f"ABORT: tests fail without any mutation: {failed}")
            return 2

        survived = 0
        for i, (name, old, new) in enumerate(MUTATIONS, 1):
            n = original.count(old)
            if n != 1:
                print(f"ABORT: mutation {i} ({name}) expected its text exactly once, found {n}: {old!r}")
                return 2
            tree = tmp / f"m{i}"
            fresh_copy(tree)
            (tree / TARGET).write_text(original.replace(old, new))
            passed, failed, summary = run_tests(tree)
            verdict = "SURVIVED" if passed else "CAUGHT"
            survived += passed
            print(f"\n[{i}] {verdict:<8} {name}")
            print(f"    - {old}\n    + {new}" if new else f"    - {old}\n    + (deleted)")
            print(f"    result: {summary}")
            for t in failed:
                print(f"    failed: {t}")

        print(f"\n{len(MUTATIONS) - survived}/{len(MUTATIONS)} mutations caught, {survived} survived")
        print(f"project tree unchanged: {(ROOT / TARGET).read_text() == original}")
        return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
