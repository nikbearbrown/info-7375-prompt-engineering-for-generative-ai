"""Offline regression for interrupted request accounting, before the patch.

Drafted on 2026-11-10 using the existing reproduction and test helpers.
No live requests are made; the transport records a simulated sent request
before raising KeyboardInterrupt.
"""
import unittest

import independent_check
from jobloop import loop
from tests.helpers import FakeClock, FakeTransport, Project, url
from tests.test_loop import SEEN, THREE, happy_script


class InterruptAfterSend(FakeTransport):
    def __call__(self, request_url, timeout_s):
        if request_url == url("ashby", "beta"):
            self.calls.append((request_url, timeout_s))
            raise KeyboardInterrupt
        return super().__call__(request_url, timeout_s)


class TestInterruptedRequestAccounting(unittest.TestCase):
    def setUp(self):
        self.project = Project(THREE, SEEN)
        self.addCleanup(self.project.cleanup)
        clock = FakeClock()
        self.transport = InterruptAfterSend(clock, happy_script())
        self.report = loop.run(
            self.project.root, transport=self.transport, clock=clock,
            sleep=clock.sleep, wall=clock.wall,
        )
        # Establish that the scenario sent alpha, then beta, and stopped.
        self.assertEqual(
            [request_url for request_url, _ in self.transport.calls],
            [url("greenhouse", "alpha"), url("ashby", "beta")],
        )
        self.assertEqual(self.report["run"]["status"], "incomplete")

    def test_budget_counts_every_sent_request(self):
        self.assertEqual(
            self.report["run"]["attempts_used"], len(self.transport.calls),
            "An interrupted request still consumes one attempt.",
        )

    def test_interrupted_board_records_one_attempt(self):
        beta = next(
            board for board in self.report["boards"]
            if (board["provider"], board["board"]) == ("ashby", "beta")
        )
        self.assertEqual(
            len(beta["attempts"]), 1,
            "The board report must retain the request sent before interruption.",
        )

    def test_saved_evidence_passes_independent_check(self):
        run_dir = self.project.root / self.report["run"]["run_dir"]
        findings = independent_check.check(run_dir, self.project.root)
        self.assertEqual(findings, [], "The saved report must agree with its trace.")


if __name__ == "__main__":
    unittest.main()
