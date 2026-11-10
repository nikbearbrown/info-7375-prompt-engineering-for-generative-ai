"""Loop tests: exits, budgets, repeat rule, error policy (GATE.md sections 1-4). Offline, constructed responses."""

import unittest

from jsagent2.loop import run_loop
from jsagent2.policy import Policy
from tests.fakes import BOARDS, BUDGETS, FakeClock, ScriptedTransport, ashby_body, gh_body, timeout, tmp_root

OK = {"boards/stripe": [(200, gh_body(3))], "boards/figma": [(200, gh_body(2, start=100))],
      "job-board/notion": [(200, ashby_body(4))]}


def run(boards=BOARDS, script=None, budgets=None, clock=None, approve=False):
    root = tmp_root()
    t = ScriptedTransport(script or OK)
    c = clock or FakeClock()
    res = run_loop(boards, budgets or BUDGETS, Policy(root, approve_state_write=approve), t, now=c.now, sleep=c.sleep, run_id="test")
    return res, t, c, root


class Exits(unittest.TestCase):
    def test_all_ok_is_finished(self):
        res, t, _, _ = run()
        self.assertEqual(res.exit, "finished")
        self.assertEqual({b: r["postings"] for b, r in res.boards.items()}, {"Stripe": 3, "Figma": 2, "Notion": 4})
        self.assertEqual(len(t.calls), 3)

    def test_one_404_is_incomplete_with_no_count(self):
        boards = BOARDS + [{"name": "Bad", "ats": "greenhouse", "slug": "nope"}]
        res, t, _, _ = run(boards, dict(OK, **{"boards/nope": [(404, b'{"error":"not found"}')]}))
        self.assertEqual(res.exit, "incomplete")
        self.assertEqual(res.boards["Bad"]["status"], "not-found")
        self.assertIsNone(res.boards["Bad"]["postings"])
        self.assertEqual(sum("boards/nope" in u for u in t.calls), 1, "a 404 must not be retried")

    def test_empty_board_is_incomplete_not_zero_new(self):
        res, _, _, _ = run(script=dict(OK, **{"boards/figma": [(200, gh_body(0))]}))
        self.assertEqual(res.exit, "incomplete")
        self.assertEqual(res.boards["Figma"]["status"], "empty-unverified")
        self.assertIsNone(res.boards["Figma"]["new"])

    def test_all_boards_fail_is_error(self):
        res, _, _, _ = run(script={"boards/": [(404, b"{}")], "job-board/": [(404, b"{}")]})
        self.assertEqual(res.exit, "error")

    def test_unknown_ats_is_error_and_nothing_fetched(self):
        res, t, _, _ = run(boards=[{"name": "X", "ats": "workday", "slug": "x"}])
        self.assertEqual(res.exit, "error")
        self.assertEqual(t.calls, [])


class ErrorPolicy(unittest.TestCase):
    def test_timeout_retried_once_then_ok(self):
        res, t, c, _ = run(script=dict(OK, **{"boards/figma": [timeout(), (200, gh_body(2))]}))
        self.assertEqual(res.exit, "finished")
        self.assertEqual(sum("boards/figma" in u for u in t.calls), 2)
        self.assertEqual(c.slept, [2])

    def test_timeout_twice_gives_up_without_value(self):
        res, t, _, _ = run(script=dict(OK, **{"boards/figma": [timeout(), timeout()]}))
        self.assertEqual(res.exit, "incomplete")
        self.assertEqual(res.boards["Figma"]["status"], "transient-failed")
        self.assertIsNone(res.boards["Figma"]["postings"])
        self.assertEqual(sum("boards/figma" in u for u in t.calls), 2, "exactly one retry")

    def test_5xx_retried_once(self):
        res, t, _, _ = run(script=dict(OK, **{"boards/figma": [(503, b""), (200, gh_body(2))]}))
        self.assertEqual(res.exit, "finished")
        self.assertEqual(sum("boards/figma" in u for u in t.calls), 2)

    def test_not_json_is_bad_shape_no_retry(self):
        res, t, _, _ = run(script=dict(OK, **{"boards/figma": [(200, b"<html>maintenance</html>")]}))
        self.assertEqual(res.boards["Figma"]["status"], "bad-shape")
        self.assertEqual(sum("boards/figma" in u for u in t.calls), 1)

    def test_other_4xx_no_retry(self):
        res, t, _, _ = run(script=dict(OK, **{"boards/figma": [(429, b"")]}))
        self.assertEqual(res.boards["Figma"]["status"], "client-error")
        self.assertEqual(sum("boards/figma" in u for u in t.calls), 1)


class Budgets(unittest.TestCase):
    def test_board_budget_leaves_rest_unvisited(self):
        res, t, _, _ = run(budgets=dict(BUDGETS, max_boards=2))
        self.assertEqual(res.exit, "budget-exhausted")
        self.assertEqual(res.budget_hit, "boards")
        self.assertEqual(res.unvisited, ["Notion"])
        self.assertEqual(len(t.calls), 2)

    def test_request_budget_counts_retries(self):
        script = {"boards/stripe": [timeout(), timeout()], "boards/figma": [timeout(), timeout()], "job-board/notion": [(200, ashby_body(1))]}
        res, t, _, _ = run(script=script, budgets=dict(BUDGETS, max_requests=3))
        self.assertEqual(res.exit, "budget-exhausted")
        self.assertEqual(res.budget_hit, "requests")
        self.assertLessEqual(len(t.calls), 3)
        self.assertIn("Notion", res.unvisited)

    def test_seconds_budget(self):
        res, _, _, _ = run(clock=FakeClock(step=50), budgets=dict(BUDGETS, max_seconds=120))
        self.assertEqual(res.exit, "budget-exhausted")
        self.assertEqual(res.budget_hit, "seconds")
        self.assertTrue(res.unvisited)

    def test_budget_never_reported_as_finished(self):
        res, _, _, _ = run(budgets=dict(BUDGETS, max_boards=1))
        self.assertNotEqual(res.exit, "finished")


class RepeatRule(unittest.TestCase):
    def test_board_listed_twice_fetched_once(self):
        res, t, _, _ = run(boards=BOARDS + [dict(BOARDS[0], name="Stripe again")])
        self.assertEqual(sum("boards/stripe" in u for u in t.calls), 1)
        self.assertTrue(any(o["event"] == "repeat-skipped" for o in res.observations))
        self.assertEqual(res.exit, "finished")


class Trace(unittest.TestCase):
    def test_every_request_is_an_observation_and_raw_saved(self):
        res, t, _, root = run(script=dict(OK, **{"boards/figma": [timeout(), (200, gh_body(2))]}))
        fetches = [o for o in res.observations if o["event"] == "response" or o["event"] == "transport-error"]
        self.assertEqual(len(fetches), len(t.calls))
        for o in res.observations:
            if o["event"] == "response":
                self.assertTrue((root / o["raw_file"]).exists())
                self.assertEqual(len(o["sha256"]), 64)


class State(unittest.TestCase):
    def test_first_run_is_baseline_and_state_held_without_approval(self):
        res, _, _, root = run()
        self.assertEqual(res.state_write, "held-for-approval")
        self.assertFalse((root / "out" / "state" / "seen.json").exists())

    def test_state_written_with_approval_and_second_run_finds_new(self):
        root = tmp_root()
        c = FakeClock()
        run_loop(BOARDS, BUDGETS, Policy(root, approve_state_write=True), ScriptedTransport(OK), now=c.now, sleep=c.sleep, run_id="r1")
        script2 = dict(OK, **{"boards/stripe": [(200, gh_body(4))]})  # id 4 is new
        res = run_loop(BOARDS, BUDGETS, Policy(root, approve_state_write=True), ScriptedTransport(script2), now=c.now, sleep=c.sleep, run_id="r2")
        self.assertEqual(res.boards["Stripe"]["new"], [4])
        self.assertEqual(res.boards["Figma"]["new"], [])

    def test_failed_board_ids_not_marked_seen(self):
        root = tmp_root()
        c = FakeClock()
        bad = dict(OK, **{"boards/figma": [(404, b"{}")]})
        run_loop(BOARDS, BUDGETS, Policy(root, approve_state_write=True), ScriptedTransport(bad), now=c.now, sleep=c.sleep, run_id="r1")
        res = run_loop(BOARDS, BUDGETS, Policy(root, approve_state_write=True), ScriptedTransport(OK), now=c.now, sleep=c.sleep, run_id="r2")
        self.assertEqual(res.boards["Figma"]["baseline"], True, "Figma was never seen, so run 2 is its baseline")


if __name__ == "__main__":
    unittest.main()
