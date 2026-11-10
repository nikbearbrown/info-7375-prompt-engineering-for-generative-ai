"""Case 14 (Judges and validator). Written by Claude Code from tests/acceptance/ACCEPTANCE_CASES.md on 2026-10-29, before any implementation. Examples are the ones in CONTRACT.md The rule."""
import pytest

CASES = [
    ("ML", "HTML Email Developer", False),
    ("ML", "ML-Ops Engineer", True),
    ("ML", "Senior ML Engineer", True),
    ("C++", "C++", True),
    ("Node.js", "node js", True),
    ("Engineer", "Engineers", False),
    ("New York", "New York City", True),
    ("New York", "NYC", False),
    ("machine learning engineer", "MACHINE LEARNING ENGINEER, Link", True),
]


@pytest.mark.parametrize("term,text,expected", CASES)
def test_ac14_whole_word_matcher(term, text, expected):
    from jobwatch.textmatch import whole_word_match

    assert whole_word_match(term, text) is expected
