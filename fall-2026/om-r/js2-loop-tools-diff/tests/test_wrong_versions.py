"""The two "Wrong versions" tests from GATE.md, written BEFORE the loop
implementation existed.

The implementation under test is chosen by the JS2_IMPL environment variable
(default: agent.loop). Run against the deliberately wrong stubs with:

    JS2_IMPL=agent.wrong_stub_budget       python3 -m unittest -v tests.test_wrong_versions
    JS2_IMPL=agent.wrong_stub_failed_board python3 -m unittest -v tests.test_wrong_versions

Interface every implementation must provide (fixed here, before the code):

    run(boards, *, root, fetch, budgets=None, approved_new_boards=(),
        sleep=time.sleep, clock=time.monotonic) -> report dict
        report["exit"]            one of finished/incomplete/budget-exhausted/error
        report["requests_made"]   int
        report["budget_hit"]      {"budget": name, "limit": n} or None
        report["not_attempted"]   [board, ...]
        report["boards"][name]    {"board_status": ..., "error": ..., "new": [...]}
    format_report(report) -> str  the human-readable final output

All responses are CONSTRUCTED fixtures (tests/fakes.py); no network.
"""
import importlib
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.fakes import FakeFetch, greenhouse_body, http_error, lever_body

impl = importlib.import_module(os.environ.get("JS2_IMPL", "agent.loop"))

BOARDS = ["gitlab", "stripe", "palantir"]


class _TmpRoot(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="js2_test_"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def _run(self, fetch, **kw):
        return impl.run(BOARDS, root=self.root, fetch=fetch, approved_new_boards=set(BOARDS),
                        sleep=lambda s: None, **kw)


class WrongVersion1BudgetSilentlyIgnored(_TmpRoot):
    """GATE.md wrong version 1: MAX_REQUESTS_PER_RUN = 2, three boards ->
    exactly 2 requests are made (counted by the fake fetcher, not by the
    loop's own report) and the exit is budget-exhausted."""

    def test_request_budget_is_enforced_not_just_logged(self):
        fetch = FakeFetch({
            "/boards/gitlab/": greenhouse_body(1, 2),
            "/boards/stripe/": greenhouse_body(3, 4),
            "/postings/palantir": lever_body("a", "b"),
        })
        report = self._run(fetch, budgets={"max_requests": 2})

        self.assertEqual(len(fetch.calls), 2, f"requests actually made: {fetch.calls}")
        self.assertEqual(report["exit"], "budget-exhausted")
        self.assertEqual(report["requests_made"], 2)
        self.assertEqual(report["budget_hit"], {"budget": "requests", "limit": 2})
        self.assertEqual(report["not_attempted"], ["palantir"])


class WrongVersion2FailedBoardReportedAsNoNewJobs(_TmpRoot):
    """GATE.md wrong version 2: a 404 on one board must surface as
    board_status "failed" with the real error - never as "0 new postings"."""

    def test_404_board_is_failed_not_zero_new(self):
        fetch = FakeFetch({
            "/boards/gitlab/": greenhouse_body(1, 2),
            "/boards/stripe/": http_error("https://boards-api.greenhouse.io/v1/boards/stripe/jobs", 404, "Not Found"),
            "/postings/palantir": lever_body("a", "b"),
        })
        report = self._run(fetch)
        stripe = report["boards"]["stripe"]

        self.assertEqual(stripe["board_status"], "failed")
        self.assertIn("404", stripe["error"])
        self.assertIn("Not Found", stripe["error"])
        self.assertEqual(stripe["new"], [])
        # Not retried: a 404 never resolves by retrying (GATE.md error policy).
        self.assertEqual(sum("/boards/stripe/" in u for u in fetch.calls), 1)
        # The healthy boards are not failed, and one failure is not a run error.
        self.assertNotEqual(report["boards"]["gitlab"]["board_status"], "failed")
        self.assertNotEqual(report["exit"], "error")

        # The final output must not put stripe in the same sentence as "no new".
        stripe_lines = [l for l in impl.format_report(report).splitlines() if "stripe" in l]
        self.assertTrue(stripe_lines, "stripe missing from final output")
        for line in stripe_lines:
            self.assertIn("FAILED", line)
            self.assertNotRegex(line.lower(), r"\b(0|no) new\b")


if __name__ == "__main__":
    unittest.main()
