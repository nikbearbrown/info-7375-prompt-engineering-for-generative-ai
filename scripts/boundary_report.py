"""Print BOUNDARY_TESTS.md's predictions next to the actual decisions of the current code.

    python3 scripts/boundary_report.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tests.js2_boundary_cases import CASES, run_case  # noqa: E402


def main():
    print(f"{'ID':4} {'predicted':15} {'actual':15} match  case")
    misses = 0
    for case_id, what, predicted, fn in CASES:
        actual = run_case(fn)
        match = actual == predicted
        misses += not match
        print(f"{case_id:4} {predicted:15} {actual:15} {'yes' if match else 'NO':5}  {what}")
    print(f"{len(CASES) - misses}/{len(CASES)} cases match their prediction")
    return 0 if misses == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
