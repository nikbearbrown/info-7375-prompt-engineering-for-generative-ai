"""Plant each CONTRACT.md §5 wrong version into a temporary copy of the real code and confirm the
test suite fails. (Complements tests/faulty_variants.py, which are standalone wrong versions.)

    .venv/bin/python tests/mutation_check.py      # exits 0 only if every mutant is caught
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MUTANTS = {
    "M1 validator ignores posting_id mismatch (wrong version 1, association)": (
        "agent/validate.py",
        '    elif pid != posting.get("id"):\n        err(',
        "    elif False:\n        err(",
    ),
    "M2 watch joins judgments by completion order instead of id (wrong version 1)": (
        "agent/watch.py",
        "        summaries = dict(zip(targets, pool.map(lambda p: judge_one(by_id[p], resume, judge_fn, jdir), targets)))",
        "        from concurrent.futures import as_completed\n"
        "        futs = [pool.submit(judge_one, by_id[p], resume, judge_fn, jdir) for p in targets]\n"
        "        summaries = dict(zip(targets, [f.result() for f in as_completed(futs)]))",
    ),
    "M3 validator skips quote and résumé-evidence checks (wrong version 2)": (
        "agent/validate.py",
        '            elif not contains_phrase(fields[s["posting_field"]], quote):',
        "            elif False:",
    ),
}


def main():
    caught_all = True
    for name, (rel, old, new) in MUTANTS.items():
        with tempfile.TemporaryDirectory() as tmp:
            for d in ("agent", "tests", "resume"):
                shutil.copytree(ROOT / d, Path(tmp) / d, ignore=shutil.ignore_patterns("__pycache__"))
            target = Path(tmp) / rel
            src = target.read_text()
            assert old in src, f"mutation anchor not found for {name}"
            target.write_text(src.replace(old, new))
            proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                                  cwd=tmp, capture_output=True, text=True)
            failed = [line for line in proc.stdout.splitlines() if line.startswith("FAILED")]
            caught = proc.returncode != 0
            caught_all &= caught
            print(f"{'CAUGHT' if caught else 'MISSED'}: {name}")
            for line in failed:
                print("   ", line)
    sys.exit(0 if caught_all else 1)


if __name__ == "__main__":
    main()
