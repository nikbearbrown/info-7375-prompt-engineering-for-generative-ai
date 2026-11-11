"""My time-budget decisions (GATE.md, Decisions, 2026-11-10). Written before the changes.

1. If the time budget is invalid, such as NaN, or cannot be checked reliably, the agent fails
   safely: it must not keep running without a valid time limit.
2. The independent checker enforces the same time budget as the agent: it verifies the total
   time, and that no request was allowed to exceed the remaining budget.
"""

import json
import unittest
from unittest import mock

import check_run
from agent import loop
from agent.tools import Response
from tests.helpers import (ASHBY, GH, LEVER, THREE, FakeClock, ashby_body, ashby_job, gh_body, gh_job, lever_body,
                           lever_job, make_root, ok, run_loop)

BODIES = {GH % "anthropic": gh_body(gh_job(1)), LEVER % "palantir": lever_body(lever_job("a")),
          ASHBY % "linear": ashby_body(ashby_job("x"))}


class BreakableClock(FakeClock):
    """A fake clock that can start giving NaN, the way a broken or unreliable clock would."""

    def __init__(self, broken=False):
        super().__init__()
        self.broken = broken

    def __call__(self):
        return float("nan") if self.broken else self.t


def net(clock, durations=(), break_after=None):
    calls = []

    def transport(url, timeout, max_bytes):
        calls.append({"url": url, "timeout": timeout})
        clock.t += durations[len(calls) - 1] if len(calls) <= len(durations) else 0
        if break_after is not None and len(calls) >= break_after:
            clock.broken = True
        return ok(BODIES[url])
    transport.calls = calls
    return transport


def failed(checks):
    return sorted(c.name for c in checks if not c.passed)


class Decision1InvalidTimeFailsSafely(unittest.TestCase):
    def test_a_clock_that_reads_nan_stops_the_run_before_any_request(self):
        root, clock = make_root(self, THREE), BreakableClock(broken=True)
        transport = net(clock)
        record = run_loop(root, transport, clock)
        self.assertEqual((record["exit"], record["exit_reason"]), ("error", "time_budget_invalid"))
        self.assertEqual(transport.calls, [])
        lines = (root / record["files"]["trace"]).read_text().splitlines()
        self.assertEqual(json.loads(lines[-1])["exit"], "error")

    def test_a_clock_that_breaks_mid_run_stops_before_the_next_request(self):
        root, clock = make_root(self, THREE), BreakableClock()
        transport = net(clock, break_after=1)
        record = run_loop(root, transport, clock)
        self.assertEqual((record["exit"], record["exit_reason"]), ("error", "time_budget_invalid"))
        self.assertEqual(len(transport.calls), 1)
        self.assertIsNone(record["budget"]["used"]["seconds"])  # not NaN, and not a made-up number
        json.loads((root / record["files"]["record"]).read_text(),
                   parse_constant=lambda name: self.fail("the record contains %s" % name))


class Decision2CheckerEnforcesTheSameBudget(unittest.TestCase):
    def test_every_request_records_when_it_started_and_the_seconds_left(self):
        root, clock = make_root(self, THREE), FakeClock()
        record = run_loop(root, net(clock, durations=(100, 5)), clock)
        fetches = [json.loads(line) for line in (root / record["files"]["trace"]).read_text().splitlines()
                   if json.loads(line)["action"] == "fetch"]
        self.assertEqual([f["started_t"] for f in fetches], [0, 100, 105])
        self.assertEqual([f["seconds_left_at_start"] for f in fetches], [120, 20, 15])
        self.assertEqual([f["timeout"] for f in fetches], [30, 20, 15])

    def test_a_late_request_given_exactly_the_seconds_left_passes(self):
        root, clock = make_root(self, THREE), FakeClock()
        record = run_loop(root, net(clock, durations=(100, 5)), clock)
        self.assertEqual(failed(check_run.check(root / record["files"]["record"])), [])

    def test_a_request_given_more_than_the_seconds_left_is_caught_without_slack(self):
        """Wrong version W12 gives 30 s at 93 s into the run: 3 s past the budget, inside the old 5 s slack."""
        root, clock = make_root(self, THREE), FakeClock()
        with mock.patch.object(loop, "request_timeout", lambda seconds_left: 30):
            record = run_loop(root, net(clock, durations=(93,)), clock)
        self.assertIn("budgets_and_hosts", failed(check_run.check(root / record["files"]["record"])))

    def test_a_total_time_that_is_not_a_number_cannot_be_verified(self):
        root, clock = make_root(self, THREE), FakeClock()
        record = run_loop(root, net(clock), clock)
        path = root / record["files"]["record"]
        for bad in (float("nan"), None):
            data = json.loads(path.read_text())
            data["budget"]["used"]["seconds"] = bad
            path.write_text(json.dumps(data))
            self.assertIn("budgets_and_hosts", failed(check_run.check(path)), bad)


if __name__ == "__main__":
    unittest.main()
