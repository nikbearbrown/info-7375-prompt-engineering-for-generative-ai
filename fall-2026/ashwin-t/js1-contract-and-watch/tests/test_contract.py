"""The two wrong versions named in CONTRACT.md: the real code passes, the wrong versions are caught."""
import unittest

from jobwatch import rule
from tests.helpers import assert_skill_matches_require_posting_evidence, assert_verdict_stays_with_posting_id
from wrong_versions import w1_positional, w2_substring


class ContractTests(unittest.TestCase):
    def test_verdict_stays_with_posting_id(self):
        assert_verdict_stays_with_posting_id(self, rule.classify_all)

    def test_skill_matches_require_posting_evidence(self):
        assert_skill_matches_require_posting_evidence(self, rule.classify)


class WrongVersionsAreCaught(unittest.TestCase):
    def test_wrong_version_1_positional_verdicts_is_caught(self):
        with self.assertRaises(AssertionError):
            assert_verdict_stays_with_posting_id(self, w1_positional.classify_all)

    def test_wrong_version_2_substring_skills_is_caught(self):
        with self.assertRaises(AssertionError):
            assert_skill_matches_require_posting_evidence(self, w2_substring.classify)


if __name__ == "__main__":
    unittest.main()
