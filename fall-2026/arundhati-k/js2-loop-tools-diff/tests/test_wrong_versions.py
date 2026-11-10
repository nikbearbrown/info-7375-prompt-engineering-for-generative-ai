"""GATE.md section 6: each plausible-but-wrong version must turn my tests red.

Each wrong version is swapped in for the real one, then my existing tests are run against it. A wrong version
that passes every test would mean the tests are too weak.
"""

import os
import unittest
from pathlib import Path
from unittest import mock
from urllib.parse import urlsplit

from jsagent2 import loop as loop_mod
from jsagent2.policy import Decision, Policy
from tests import test_loop
from tests.test_policy import failing_cases


# --- wrong policies (GATE §6 items 3, 4, 5) ---------------------------------------------------------

class StartswithPolicy(Policy):
    """Wrong 3: prefix check on the joined string, so out-evil/ counts as inside out/."""

    def _inside(self, path, folder):
        return str(self.root / path).startswith(str(self.root / folder))


class NoSymlinkPolicy(Policy):
    """Wrong 4: normalises .. but does not resolve symlinks."""

    def _inside(self, path, folder):
        full = Path(os.path.normpath(self.root / os.path.expanduser(str(path))))
        base = Path(os.path.normpath(self.root / folder))
        return full == base or base in full.parents

    def _has_symlink(self, path):
        return False


class SubstringHostPolicy(Policy):
    """Wrong 5: host check by substring."""

    def check_request(self, method, url):
        if method == "GET" and urlsplit(url).scheme == "https" and any(h in url for h in self.hosts):
            return Decision("allow", "substring match")
        return Decision("refuse", "no match")


class WrongPolicies(unittest.TestCase):
    def test_startswith_policy_caught(self):
        self.assertIn(9, [c[0] for c in failing_cases(StartswithPolicy)])

    def test_no_symlink_policy_caught(self):
        self.assertIn(10, [c[0] for c in failing_cases(NoSymlinkPolicy)])

    def test_substring_host_policy_caught(self):
        self.assertIn(4, [c[0] for c in failing_cases(SubstringHostPolicy)])


# --- wrong loops (GATE §6 items 1, 2, 6, 7) --------------------------------------------------------

def red_tests(*names):
    """Run the named test_loop tests; return the names that failed or errored."""
    suite = unittest.TestSuite()
    for n in names:
        cls, meth = n.split(".")
        suite.addTest(getattr(test_loop, cls)(meth))
    result = unittest.TestResult()
    suite.run(result)
    return {t.id().split(".", 2)[-1] for t, _ in result.failures + result.errors}


def empty_as_zero(status, body, ats):
    s, jobs = REAL_CLASSIFY(status, body, ats)
    return ("ok", jobs) if s == "empty-unverified" else (s, jobs)


def failed_as_zero_exit(boards, budget_hit):
    # Wrong 2 + 7: failures and budget hits ignored: "it stopped" == "it succeeded"
    return "finished"


def retry_everything(status):
    return status != 200


REAL_CLASSIFY = loop_mod.classify


class WrongLoops(unittest.TestCase):
    def test_empty_as_zero_caught(self):
        with mock.patch.object(loop_mod, "classify", empty_as_zero):
            self.assertIn("Exits.test_empty_board_is_incomplete_not_zero_new", red_tests("Exits.test_empty_board_is_incomplete_not_zero_new"))

    def test_finished_always_caught(self):
        names = ["Exits.test_one_404_is_incomplete_with_no_count", "Budgets.test_budget_never_reported_as_finished"]
        with mock.patch.object(loop_mod, "exit_for", failed_as_zero_exit):
            self.assertEqual(red_tests(*names), set(names))

    def test_retry_404_caught(self):
        with mock.patch.object(loop_mod, "is_retryable", retry_everything):
            self.assertIn("Exits.test_one_404_is_incomplete_with_no_count", red_tests("Exits.test_one_404_is_incomplete_with_no_count"))


if __name__ == "__main__":
    unittest.main()
