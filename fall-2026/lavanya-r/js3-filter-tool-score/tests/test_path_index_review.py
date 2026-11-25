"""Review of patch 7044eaf: cases found by READING that diff, written before
the revision. Unlike tests/test_path_index.py, these were written AFTER seeing
Claude's patch, so they are a reviewer's tests, not a test-first spec.
Expected values: Claude's, under Lavanya's delegation (2026-11-10).

Patch 7044eaf fails three of these:
- a dict key made of digits ("2025") is now read as a list index, so a field that exists is rejected (it worked before the patch: a regression);
- "00" and a non-ASCII digit ("٠") are accepted as index 0.
"""
import json
import pathlib
import unittest

from agent.claude_judge import path_exists

HERE = pathlib.Path(__file__).resolve().parent.parent
RESUME = json.loads((HERE / "persona/priya-nair.resume.json").read_text())
WITH_YEAR_KEYS = {**RESUME, "by_year": {"2025": {"gpa": "3.9"}}}   # constructed

CASES = [
    (WITH_YEAR_KEYS, "by_year.2025.gpa", True),     # regression in 7044eaf
    (RESUME, "education.00.end_date", False),       # not a canonical index
    (RESUME, "education.٠.end_date", False),   # ARABIC-INDIC DIGIT ZERO
    (RESUME, "education[0][0]", False),             # index into a dict item
    (RESUME, "skills.0", False),                    # still false
    (RESUME, "education.0.end_date", True),         # still true
]


class TestReviewCases(unittest.TestCase):
    def test_cases(self):
        for data, path, expected in CASES:
            with self.subTest(path=path):
                self.assertIs(path_exists(data, path), expected)


if __name__ == "__main__":
    unittest.main()
