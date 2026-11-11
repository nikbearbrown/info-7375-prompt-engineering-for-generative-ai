"""Pre-submission audit, 2026-11-10: two places where the code did not do what GATE.md says, plus one
GATE §6 wrong version that had no test. Written BEFORE the fix (see README, "Audit fixes")."""

import unittest
from unittest import mock

from jsagent2 import loop as loop_mod
from jsagent2.loop import normalise_url, run_loop
from jsagent2.policy import Policy
from jsagent2.transport import PolicyRefused
from tests import test_loop
from tests.fakes import BOARDS, BUDGETS, FakeClock, ScriptedTransport, tmp_root
from tests.test_wrong_versions import red_tests


class RepeatRuleNormalisation(unittest.TestCase):
    """GATE §3: 'the same action' = same method + normalised URL (scheme, host, path, sorted query)."""

    def test_scheme_and_host_case_ignored(self):
        self.assertEqual(normalise_url("HTTPS://Boards-API.Greenhouse.io/v1/boards/stripe/jobs"),
                         normalise_url("https://boards-api.greenhouse.io/v1/boards/stripe/jobs"))

    def test_query_order_ignored(self):
        self.assertEqual(normalise_url("https://api.ashbyhq.com/x?b=2&a=1"), normalise_url("https://api.ashbyhq.com/x?a=1&b=2"))

    def test_path_case_kept(self):
        # Ashby board names are case-sensitive (Jasper%20AI works, jasper-ai 404s), so the path is not lowered.
        self.assertNotEqual(normalise_url("https://api.ashbyhq.com/posting-api/job-board/Notion"),
                            normalise_url("https://api.ashbyhq.com/posting-api/job-board/notion"))


class PolicyViolationExit(unittest.TestCase):
    """GATE §1: exit 'error' when the run could not run safely, including a permission-policy violation."""

    def test_redirect_off_allow_list_ends_in_error(self):
        root = tmp_root()
        c = FakeClock()
        script = {"boards/stripe": [PolicyRefused("redirect refused: host 'evil.example' is not on the allow-list")],
                  "boards/figma": [(200, b'{"jobs": [{"id": 1}]}')], "job-board/notion": [(200, b'{"jobs": [{"id": 2}]}')]}
        res = run_loop(BOARDS, BUDGETS, Policy(root), ScriptedTransport(script), now=c.now, sleep=c.sleep, run_id="t")
        self.assertEqual(res.boards["Stripe"]["status"], "policy-refused")
        self.assertEqual(res.exit, "error")
        self.assertEqual(res.state_write, "skipped (exit error)")


def failed_board_as_zero(status, jobs, reason):
    """GATE §6 wrong version 2: a failed board counted as 0 postings instead of no value."""
    e = REAL_ENTRY(status, jobs, reason)
    if e["postings"] is None:
        e["postings"] = 0
    return e


REAL_ENTRY = loop_mod._board_entry


class WrongVersion2(unittest.TestCase):
    def test_failed_board_as_zero_caught(self):
        names = ["Exits.test_one_404_is_incomplete_with_no_count", "ErrorPolicy.test_timeout_twice_gives_up_without_value"]
        with mock.patch.object(loop_mod, "_board_entry", failed_board_as_zero):
            self.assertEqual(red_tests(*names), set(names))


if __name__ == "__main__":
    unittest.main()
