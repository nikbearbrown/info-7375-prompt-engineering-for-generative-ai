"""Plant each wrong version from FILTER.md §6 into js3.filter and confirm the test suite catches it.

Run: .venv/bin/python tests/mutation_check.py      (exit 0 only if every mutant is CAUGHT)
Each mutant runs the pytest suite in-process with one seam of js3.filter replaced.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import js3.filter as F  # noqa: E402

MUTANTS = {
    "W1 substring matching": ("phrase_in", lambda norm, phrase: phrase.replace(" ", "") in norm.replace(" ", "")),
    "W2 employer name counts as topic": ("topic_phrase_allowed", lambda phrase, board, cfg: True),
    "W3 raw count, no cap": ("topic_points", lambda groups, cfg: (len(groups), len(groups))),
    "W4 missing description -> reject": ("missing_fields",
                                         lambda norm: [] if norm["title"] else ["posting.title"]),
    "W5 level read from description": ("level_fields", lambda cfg: ["title", "description"]),
}
SUITE = [str(ROOT / "tests" / "test_filter.py")]


def run(label):
    code = pytest.main(["-q", "-x", "-p", "no:cacheprovider", *SUITE])
    return code


def main():
    base = run("baseline")
    if base != 0:
        print("baseline suite FAILS; mutation check is meaningless")
        return 2
    results = {}
    for name, (attr, fn) in MUTANTS.items():
        orig = getattr(F, attr)
        setattr(F, attr, fn)
        try:
            results[name] = run(name) != 0
        finally:
            setattr(F, attr, orig)
    print("\n=== mutation check (FILTER.md §6) ===")
    for name, caught in results.items():
        print(f"{'CAUGHT' if caught else 'MISSED'}  {name}")
    n = sum(results.values())
    print(f"{n}/{len(results)} caught")
    return 0 if n == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
