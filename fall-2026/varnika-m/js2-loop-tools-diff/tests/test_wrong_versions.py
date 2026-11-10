"""Each wrong version in GATE.md section 6 is built here, and a committed test is shown to fail on it.

A test that passes on the real code and also on a wrong version proves nothing.
These tests run the committed test against the wrong version and expect it to fail.
"""

import os
import unittest
from unittest import mock

from agent import loop, policy
from tests import test_check_run, test_loop, test_policy

REAL_CLASSIFY = loop.classify
REAL_SHOULD_RETRY = loop.should_retry
REAL_DECIDE_EXIT = loop.decide_exit


def fails(test_class, test_name):
    result = unittest.TestResult()
    test_class(test_name).run(result)
    return not result.wasSuccessful()


def w1_inside_by_prefix(root, path):
    return str(os.path.abspath(path)).startswith(str(root))


def w2_inside_without_resolving_links(root, path):
    absolute = os.path.normpath(os.path.abspath(path))
    return os.path.commonpath([str(root), absolute]) == str(root)


def w3_inside_without_dot_dot(root, path):
    return str(path).startswith(str(root) + os.sep)


def w4_host_by_suffix(host):
    return next((allowed for allowed in policy.ALLOWED_PATHS if host.endswith(allowed)), None)


def w5_empty_is_ok(system, http_status, body):
    status, reason, postings = REAL_CLASSIFY(system, http_status, body)
    return ("ok", None, []) if (status, reason) == ("suspect", "empty") else (status, reason, postings)


def w7_every_stop_is_finished(boards, not_attempted, error):
    exit_, reason = REAL_DECIDE_EXIT(boards, not_attempted, error)
    return ("finished", None) if exit_ == "budget_exhausted" else (exit_, reason)


def w8_retry_everything(reason, headers, retries_done):
    return 2 if retries_done < 2 else None


def w12_full_timeout_always(seconds_left):
    return loop.LIMITS["seconds_per_request"]


class WrongVersionsAreCaught(unittest.TestCase):
    def test_real_code_passes_the_tests_used_below(self):
        for cls, name in [(test_policy.FileBoundary, "test_B15_prefix_trick_jobs_evil"),
                          (test_policy.FileBoundary, "test_B16_folder_symlink_inside_jobs_pointing_outside"),
                          (test_policy.FileBoundary, "test_B14_dot_dot_escapes_jobs"),
                          (test_policy.NetworkBoundary, "test_B04_subdomain_of_an_allowed_host"),
                          (test_policy.NetworkBoundary, "test_B03_host_off_the_list_with_allowed_name_as_prefix"),
                          (test_loop.FailedBoardsInventNothing, "test_empty_board_is_suspect_not_no_new_jobs"),
                          (test_check_run.IndependentCheck, "test_the_real_agent_on_the_same_responses_passes"),
                          (test_loop.Budgets, "test_request_budget_runs_out_before_every_board"),
                          (test_loop.Retries, "test_not_found_is_requested_exactly_once"),
                          (test_loop.Budgets, "test_a_request_never_gets_more_seconds_than_are_left")]:
            self.assertFalse(fails(cls, name), name)

    def test_w1_prefix_check_is_caught(self):
        with mock.patch.object(policy, "is_inside", w1_inside_by_prefix):
            self.assertTrue(fails(test_policy.FileBoundary, "test_B15_prefix_trick_jobs_evil"))

    def test_w2_unresolved_symlink_is_caught(self):
        with mock.patch.object(policy, "is_inside", w2_inside_without_resolving_links):
            self.assertTrue(fails(test_policy.FileBoundary, "test_B16_folder_symlink_inside_jobs_pointing_outside"))

    def test_w3_unresolved_dot_dot_is_caught(self):
        with mock.patch.object(policy, "is_inside", w3_inside_without_dot_dot):
            self.assertTrue(fails(test_policy.FileBoundary, "test_B14_dot_dot_escapes_jobs"))

    def test_w4_host_by_suffix_is_caught(self):
        with mock.patch.object(policy, "host_allowed", w4_host_by_suffix):
            self.assertTrue(fails(test_policy.NetworkBoundary, "test_B04_subdomain_of_an_allowed_host"))

    def test_w5_empty_board_as_no_new_jobs_is_caught_twice(self):
        with mock.patch.object(loop, "classify", w5_empty_is_ok):
            self.assertTrue(fails(test_loop.FailedBoardsInventNothing, "test_empty_board_is_suspect_not_no_new_jobs"))
            self.assertTrue(fails(test_check_run.IndependentCheck, "test_the_real_agent_on_the_same_responses_passes"))

    def test_w7_every_stop_reported_as_finished_is_caught(self):
        with mock.patch.object(loop, "decide_exit", w7_every_stop_is_finished):
            self.assertTrue(fails(test_loop.Budgets, "test_request_budget_runs_out_before_every_board"))

    def test_w8_retrying_a_not_found_is_caught(self):
        with mock.patch.object(loop, "should_retry", w8_retry_everything):
            self.assertTrue(fails(test_loop.Retries, "test_not_found_is_requested_exactly_once"))

    def test_w12_budget_checked_only_between_boards_is_caught(self):
        with mock.patch.object(loop, "request_timeout", w12_full_timeout_always):
            self.assertTrue(fails(test_loop.Budgets, "test_a_request_never_gets_more_seconds_than_are_left"))


if __name__ == "__main__":
    unittest.main()
