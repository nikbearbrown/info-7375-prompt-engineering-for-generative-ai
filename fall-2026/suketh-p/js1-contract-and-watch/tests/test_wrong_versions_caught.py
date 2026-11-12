"""Proof that the suite catches the wrong versions in CONTRACT.md: swap each one into the
agent, rerun the tests aimed at it, and require at least one failure."""

import unittest
from unittest import mock

from tests import wrong_versions

W1_TESTS = ["tests.test_run.VerdictAttachmentTest"]
W2_TESTS = ["tests.test_validator.UnsupportedJustificationTest", "tests.test_run.RejectedResponseTest"]


def run_tests(names, target=None, replacement=None):
    suite = unittest.defaultTestLoader.loadTestsFromNames(names)
    result = unittest.TestResult()
    if target is None:
        suite.run(result)
    else:
        with mock.patch(target, replacement):
            suite.run(result)
    return result


class WrongVersionsAreCaughtTest(unittest.TestCase):
    def assert_caught(self, names, target, replacement):
        self.assertTrue(run_tests(names).wasSuccessful(), "the tests must pass on the real agent first")
        result = run_tests(names, target, replacement)
        self.assertGreater(len(result.failures), 0, "the wrong version passed every test aimed at it")

    def test_w1_verdicts_attached_to_the_wrong_posting_are_caught(self):
        self.assert_caught(W1_TESTS, "jobwatch.run.assess_new", wrong_versions.assess_new_misattached)

    def test_w2a_a_validator_that_ignores_citations_is_caught(self):
        self.assert_caught(W2_TESTS, "jobwatch.judge.validate_response", wrong_versions.validate_response_lenient)

    def test_w2b_a_rejected_reply_turned_into_not_relevant_is_caught(self):
        self.assert_caught(W2_TESTS, "jobwatch.judge.judge_posting", wrong_versions.judge_posting_fail_open)


if __name__ == "__main__":
    unittest.main()
