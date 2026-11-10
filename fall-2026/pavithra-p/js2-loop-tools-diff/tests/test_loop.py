"""The loop against GATE.md: exits, budgets, repeat rule, error policy, trace and state. All boards are CONSTRUCTED."""
import json
import unittest
from datetime import datetime, timezone

from agent import tools
from tests.fakes import BUDGETS, LEVER_404, FakeClock, FakeNet, Project, ashby, greenhouse, lever, url

GH = {"name": "acme", "system": "greenhouse"}
LV = {"name": "beta", "system": "lever"}
AS = {"name": "gamma", "system": "ashby"}
BAD = {"name": "no-such-board", "system": "lever"}
DAY1 = datetime(2026, 11, 9, 12, 0, tzinfo=timezone.utc)
DAY2 = datetime(2026, 11, 10, 12, 0, tzinfo=timezone.utc)


def net_for(**overrides):
    answers = {url("greenhouse", "acme"): [(200, greenhouse(1, 2))], url("lever", "beta"): [(200, lever("a"))],
               url("ashby", "gamma"): [(200, ashby("x"))], url("lever", "no-such-board"): [(404, LEVER_404)]}
    answers.update({url(*k.split(":")): v for k, v in overrides.items()})
    return FakeNet(answers)


class ExitTests(unittest.TestCase):
    def setUp(self):
        self.p = Project(self)

    def test_finished_when_every_board_is_checked(self):
        result, _, _ = self.p.run([GH, LV, AS], net_for())
        self.assertEqual(result.status, "finished")
        self.assertEqual([b["result"] for b in result.boards], ["checked"] * 3)

    def test_first_run_of_a_board_is_a_baseline_with_zero_new(self):
        result, state, _ = self.p.run([GH], net_for())
        self.assertTrue(result.boards[0]["baseline"])
        self.assertEqual(result.new_jobs, [])
        self.assertEqual(state["boards"]["greenhouse:acme"], ["1", "2"])

    def test_second_run_reports_only_unseen_ids(self):
        _, state, _ = self.p.run([GH], net_for(), now=DAY1)
        result, _, _ = self.p.run([GH], net_for(**{"greenhouse:acme": [(200, greenhouse(1, 2, 3))]}), state=state, now=DAY2)
        self.assertEqual([j["id"] for j in result.new_jobs], ["3"])

    def test_wrong_board_name_fails_once_and_the_run_is_incomplete(self):
        net = net_for()
        result, _, _ = self.p.run([GH, BAD, LV], net)
        self.assertEqual(result.status, "incomplete")
        self.assertEqual(net.calls.count(url("lever", "no-such-board")), 1, "a 404 is not retried")
        self.assertIn("lever:no-such-board", result.reason)
        self.assertEqual(result.boards[2]["result"], "checked", "the loop continues after a failed board")

    def test_failed_board_is_not_reported_as_zero_jobs(self):
        result, _, _ = self.p.run([BAD], net_for())
        board = result.boards[0]
        self.assertEqual(board["result"], "failed")
        self.assertIsNone(board["jobs"], "no count is invented for a board that was not read")
        self.assertNotEqual(result.status, "finished")

    def test_invalid_json_is_a_failed_board_not_an_error(self):
        net = net_for(**{"greenhouse:acme": [(200, b"<html>not json</html>")]})
        result, _, _ = self.p.run([GH, LV], net)
        self.assertEqual(result.status, "incomplete")
        self.assertIn("invalid data", result.boards[0]["reason"])
        self.assertEqual(net.calls.count(url("greenhouse", "acme")), 1, "invalid data is not retried")

    def test_loop_crash_is_an_error_with_the_last_action(self):
        net = net_for(**{"ashby:gamma": [RuntimeError("disk full")]})
        result, _, _ = self.p.run([GH, AS], net)
        self.assertEqual(result.status, "error")
        self.assertIn("RuntimeError", result.reason)
        self.assertIn("greenhouse", result.last_action)


class ErrorPolicyTests(unittest.TestCase):
    def setUp(self):
        self.p = Project(self)

    def test_timeout_is_retried_once_after_the_wait(self):
        clock = FakeClock()
        net = net_for(**{"greenhouse:acme": [tools.Timeout("slow"), (200, greenhouse(1))]})
        result, _, _ = self.p.run([GH], net, clock=clock)
        self.assertEqual(result.boards[0]["result"], "checked")
        self.assertEqual(len(result.boards[0]["attempts"]), 2)
        self.assertEqual(clock.slept, [BUDGETS["retry_wait_seconds"]])

    def test_5xx_twice_fails_after_one_retry(self):
        net = net_for(**{"greenhouse:acme": [(503, b"busy"), (503, b"busy")]})
        result, _, _ = self.p.run([GH], net)
        self.assertEqual(net.calls.count(url("greenhouse", "acme")), 2)
        self.assertIn("after one retry", result.boards[0]["reason"])

    def test_429_is_retried(self):
        net = net_for(**{"greenhouse:acme": [(429, b"slow down"), (200, greenhouse(1))]})
        result, _, _ = self.p.run([GH], net)
        self.assertEqual(result.status, "finished")

    def test_any_5xx_is_retried(self):
        net = net_for(**{"greenhouse:acme": [(501, b"not implemented"), (200, greenhouse(1))]})
        result, _, _ = self.p.run([GH], net)
        self.assertEqual(len(result.boards[0]["attempts"]), 2)
        self.assertEqual(result.status, "finished")

    def test_other_4xx_is_not_retried(self):
        net = net_for(**{"greenhouse:acme": [(403, b"no")]})
        self.p.run([GH], net)
        self.assertEqual(net.calls, [url("greenhouse", "acme")])


class BudgetAndRepeatTests(unittest.TestCase):
    def setUp(self):
        self.p = Project(self)

    def test_request_budget_stops_with_budget_exhausted(self):
        net = net_for()
        result, _, _ = self.p.run([GH, LV, AS], net, budgets=BUDGETS | {"max_requests": 2})
        self.assertEqual(result.status, "budget-exhausted")
        self.assertIn("requests", result.reason)
        self.assertEqual(len(net.calls), 2)
        self.assertEqual([b["result"] for b in result.boards], ["checked", "checked"], "the work done is reported")

    def test_board_budget_stops_before_the_extra_board(self):
        net = net_for()
        result, _, _ = self.p.run([GH, LV, AS], net, budgets=BUDGETS | {"max_boards": 2})
        self.assertEqual(result.status, "budget-exhausted")
        self.assertIn("boards", result.reason)
        self.assertNotIn(url("ashby", "gamma"), net.calls)

    def test_seconds_budget_stops_the_run(self):
        result, _, _ = self.p.run([GH, LV, AS], net_for(), clock=FakeClock(step=25))
        self.assertEqual(result.status, "budget-exhausted")
        self.assertIn("seconds", result.reason)

    def test_seconds_budget_counts_the_next_request(self):
        from agent import loop
        clock = FakeClock(step=0)
        r = loop._Run(BUDGETS, self.p.policy, None, {}, self.p.root, "x", None, clock, clock.sleep, loop.Hooks())
        clock.now = r.t0 + 49  # 49 s used + a 10 s timeout = 59 s: still inside 60 s
        r.check_budgets(1)
        clock.now = r.t0 + 51  # 51 s used + 10 s = 61 s: the next request could break the budget
        with self.assertRaisesRegex(loop.BudgetExhausted, "seconds"):
            r.check_budgets(1)

    def test_repeated_board_stops_with_error(self):
        net = net_for()
        result, _, _ = self.p.run([GH, GH], net)
        self.assertEqual(result.status, "error")
        self.assertIn("already made in this run", result.reason)
        self.assertEqual(len(net.calls), 1, "the second identical GET is never sent")

    def test_host_off_allow_list_stops_with_error_before_any_request(self):
        from agent.policy import Policy
        self.p.policy = Policy(root=self.p.root, hosts=["boards-api.greenhouse.io"])
        net = net_for()
        result, _, _ = self.p.run([GH, LV], net)
        self.assertEqual(result.status, "error")
        self.assertNotIn(url("lever", "beta"), net.calls)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.p = Project(self)

    def test_every_attempt_is_in_the_trace_and_every_body_saved(self):
        net = net_for(**{"greenhouse:acme": [(503, b"busy"), (200, greenhouse(1))]})
        result, _, _ = self.p.run([GH, BAD], net)
        attempts = [e for e in result.trace if e.get("action", "").startswith("GET")]
        self.assertEqual(len(attempts), 3)
        for event in attempts:
            self.assertTrue((self.p.root / event["raw"]).exists(), event)
        self.assertEqual(result.trace[-1]["action"], "exit")

    def test_state_is_not_changed_for_a_failed_board(self):
        state = {"boards": {"lever:no-such-board": ["old"]}}
        self.p.run([BAD], net_for(), state=state)
        self.assertEqual(state["boards"]["lever:no-such-board"], ["old"])

    def test_relevant_count_uses_the_written_rule(self):
        _, state, _ = self.p.run([GH], net_for(), now=DAY1)
        net = net_for(**{"greenhouse:acme": [(200, greenhouse(1, 2, 3))]})
        result, _, run_dir = self.p.run([GH], net, state=state, now=DAY2)
        self.assertEqual(result.new_jobs[0]["rule"], "Relevant", "Software Engineer, Remote US, Python and AWS")
        self.assertEqual(json.loads((run_dir / "report.json").read_text())["relevant_all"], 3)


if __name__ == "__main__":
    unittest.main()
