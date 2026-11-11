"""The loop's exits, budgets, repeat rule, and error policy (GATE.md sections 2–5)."""
import unittest

from agent2 import loop, policy
from agent2.loop import Budget
from tests.fakes import (BAD, FIGMA, NOT_FOUND, SNOW, SPOTIFY, TIMEOUT, FakeClock, FakeTransport, ashby, gh,
                         lever, no_save)

B = Budget()


def run(boards, script, last_counts=None, budget=B, clock=None):
    t = FakeTransport(script)
    c = clock or FakeClock()
    return loop.run_loop(boards, t, last_counts or {}, budget, no_save, clock=c, sleep=c.sleep), t


class Exits(unittest.TestCase):
    def test_finished_only_when_every_board_ok(self):
        r, _ = run([FIGMA, SPOTIFY, SNOW], {FIGMA.url: [gh(3)], SPOTIFY.url: [lever(2)], SNOW.url: [ashby(1)]})
        self.assertEqual(r.exit, "finished")

    def test_one_failed_board_is_incomplete_not_finished(self):
        r, _ = run([FIGMA, BAD], {FIGMA.url: [gh(3)], BAD.url: [NOT_FOUND]})
        self.assertEqual(r.exit, "incomplete")
        self.assertEqual(r.boards[BAD.key]["outcome"], "failed_not_found")
        self.assertNotIn(BAD.key, r.postings)       # no invented value for the failed board

    def test_every_board_failed_is_error(self):
        r, _ = run([BAD], {BAD.url: [NOT_FOUND]})
        self.assertEqual((r.exit, r.cause), ("error", "every board failed: escalate to a person"))


class ErrorPolicy(unittest.TestCase):
    def test_404_is_not_retried(self):
        r, t = run([BAD], {BAD.url: [NOT_FOUND, NOT_FOUND]})
        self.assertEqual(len(t.calls), 1)

    def test_transient_retried_once_then_failed(self):
        r, t = run([FIGMA, SPOTIFY], {FIGMA.url: [TIMEOUT, TIMEOUT, gh(1)], SPOTIFY.url: [lever(1)]})
        self.assertEqual(t.calls.count(FIGMA.url), 2)
        self.assertEqual(r.boards[FIGMA.key]["outcome"], "failed_transient")
        self.assertEqual(r.requests_used, 3)        # the retry counts against the budget

    def test_transient_then_ok(self):
        r, _ = run([FIGMA], {FIGMA.url: [TIMEOUT, gh(2)]})
        self.assertEqual((r.exit, r.boards[FIGMA.key]["attempts"]), ("finished", 2))

    def test_empty_after_history_is_suspicious_not_ok(self):
        r, _ = run([FIGMA, SPOTIFY], {FIGMA.url: [gh(0)], SPOTIFY.url: [lever(1)]}, last_counts={FIGMA.key: 140})
        self.assertEqual(r.boards[FIGMA.key]["outcome"], "suspicious_empty")
        self.assertEqual(r.exit, "incomplete")

    def test_malformed_is_failed(self):
        from agent2.fetch import Response
        bad = Response("ok", 200, b'{"ok": false, "error": "Document not found"}')
        r, _ = run([SPOTIFY, FIGMA], {SPOTIFY.url: [bad], FIGMA.url: [gh(1)]})
        self.assertEqual(r.boards[SPOTIFY.key]["outcome"], "malformed")


class Budgets(unittest.TestCase):
    def test_request_budget_stops_before_the_request(self):
        r, t = run([FIGMA, SPOTIFY, SNOW], {FIGMA.url: [gh(1)], SPOTIFY.url: [lever(1)], SNOW.url: [ashby(1)]},
                   budget=Budget(max_requests=2))
        self.assertEqual(r.exit, "budget_exhausted")
        self.assertEqual(len(t.calls), 2)
        self.assertEqual(r.not_attempted, [SNOW.key])

    def test_board_budget(self):
        r, _ = run([FIGMA, SPOTIFY], {FIGMA.url: [gh(1)], SPOTIFY.url: [lever(1)]}, budget=Budget(max_boards=1))
        self.assertEqual((r.exit, r.not_attempted), ("budget_exhausted", [SPOTIFY.key]))

    def test_time_budget_checked_before_each_request(self):
        clock = FakeClock()

        class Slow(FakeTransport):          # each request takes 70 simulated seconds
            def get(self, url, timeout):
                clock.sleep(70)
                return super().get(url, timeout)
        t = Slow({FIGMA.url: [gh(1)], SPOTIFY.url: [lever(1)]})
        r = loop.run_loop([FIGMA, SPOTIFY], t, {}, Budget(max_seconds=60), no_save, clock=clock, sleep=clock.sleep)
        self.assertEqual(r.exit, "budget_exhausted")
        self.assertEqual(len(t.calls), 1)


class RepeatRule(unittest.TestCase):
    def test_same_board_twice_is_refused(self):
        r, t = run([FIGMA, FIGMA], {FIGMA.url: [gh(1), gh(1)]})
        self.assertEqual(len(t.calls), 1)
        self.assertIn("repeat_refused", [e["event"] for e in r.trace])
        self.assertEqual(r.exit, "finished")

    def test_url_normalization(self):
        a = loop.action_key("GET", "https://API.lever.co/v0/postings/spotify?mode=json&x=1")
        b = loop.action_key("get", "https://api.lever.co/v0/postings/spotify?x=1&mode=json")
        self.assertEqual(a, b)


class Permission(unittest.TestCase):
    def test_policy_violation_mid_run_is_error(self):
        class Redirecting(FakeTransport):
            def get(self, url, timeout):
                policy.check_request("GET", "https://evil.example.com/")
        r = loop.run_loop([FIGMA], Redirecting({}), {}, B, no_save, clock=FakeClock())
        self.assertEqual(r.exit, "error")
        self.assertIn("permission violation", r.cause)


if __name__ == "__main__":
    unittest.main()
