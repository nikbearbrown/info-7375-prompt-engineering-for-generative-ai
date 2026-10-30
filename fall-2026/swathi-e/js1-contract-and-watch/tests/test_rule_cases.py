"""Hand-fixed rule cases from CONTRACT.md: 1-8 before any agent code, 9-12 for Revision 2.

Each expected verdict was decided by hand from the written rule (checks 1(a)/1(b),
2, 3). These tests import rule.judge(title, location), which does not exist yet
when this file is first committed, so they are expected to fail until it does.
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

RELEVANT = "relevant"
NOT_RELEVANT = "not relevant"

CASES = [
    (1, "Data Engineer", "San Francisco, California", RELEVANT),
    (2, "Senior Data Scientist", "Remote - US", NOT_RELEVANT),
    (3, "Machine Learning Engineer", "Amsterdam, Netherlands", NOT_RELEVANT),
    (4, "New Grad Software Engineer", "Mountain View, California", RELEVANT),
    (5, "Business Analyst", "Remote", RELEVANT),
    (6, "AI Research Lead", "New York, NY", NOT_RELEVANT),
    (7, "Analytics Engineer", "Remote - Germany", NOT_RELEVANT),
    (8, "ML Platform Engineer", "Seattle, Washington", RELEVANT),
    # Cases 9-12 added for CONTRACT.md Revision 2 (2026-10-25, after the baseline).
    (9, "Sr Data Engineer", "Remote - US", NOT_RELEVANT),
    (10, "AI Transformation Leader", "San Francisco, California", NOT_RELEVANT),
    (11, "Data Science Intern", "Mountain View, California", NOT_RELEVANT),
    (12, "GenAI Engineer", "Remote - US", RELEVANT),
]


class HandFixedRuleCases(unittest.TestCase):
    def test_hand_fixed_cases(self):
        from rule import judge

        for number, title, location, expected in CASES:
            with self.subTest(case=number, title=title, location=location):
                self.assertEqual(judge(title, location)["verdict"], expected)


if __name__ == "__main__":
    unittest.main()
