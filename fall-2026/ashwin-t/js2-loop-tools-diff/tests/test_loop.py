"""The loop: exits, budgets, repeat rule, error policy, state (GATE.md sections 1-4). Offline."""
from __future__ import annotations

import json
import unittest
from dataclasses import replace

from jobloop import loop
from tests.helpers import (FakeClock, FakeTransport, Project, ashby_body, gh_body, lever_body, ok,
                           state_for, status, timeout, url)

GH, AS, LV = "greenhouse", "ashby", "lever"
THREE = [(GH, "alpha", "watch"), (AS, "beta", "watch"), (LV, "gamma", "watch")]
SEEN = state_for({"greenhouse/alpha": [1, 2], "ashby/beta": ["b1"], "lever/gamma": ["g1"]})


def happy_script():
    return {url(GH, "alpha"): [ok(gh_body([1, 2, 3]))], url(AS, "beta"): [ok(ashby_body(["b1", "b2"]))],
            url(LV, "gamma"): [ok(lever_body(["g1"]))]}


class LoopCase(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.projects = []

    def tearDown(self):
        for p in self.projects:
            p.cleanup()

    def go(self, boards, script, state=None, **kw):
        project = Project(boards, state)
        self.projects.append(project)
        transport = FakeTransport(self.clock, script)
        before = project.state_bytes()
        report = loop.run(project.root, transport=transport, clock=self.clock, sleep=self.clock.sleep,
                          wall=self.clock.wall, **kw)
        return report, transport, project, before

    @staticmethod
    def board(report, name):
        return next(b for b in report["boards"] if f"{b['provider']}/{b['board']}" == name)


class TestExits(LoopCase):
    def test_three_boards_two_systems_finish_and_report_new_ids(self):
        report, transport, _, _ = self.go(THREE, happy_script(), SEEN)
        self.assertEqual(report["run"]["status"], loop.FINISHED)
        self.assertEqual(report["run"]["exit_code"], 0)
        self.assertEqual([n["key"] for n in self.board(report, "greenhouse/alpha")["new"]], ["greenhouse/alpha/3"])
        self.assertEqual(self.board(report, "lever/gamma")["new"], [])
        self.assertEqual(len(transport.calls), 3)

    def test_one_404_board_makes_the_run_incomplete_and_the_rest_continue(self):
        boards = THREE + [(GH, "nope", "deliberate-failure")]
        script = {**happy_script(), url(GH, "nope"): [status(404)]}
        report, transport, _, _ = self.go(boards, script, SEEN)
        self.assertEqual(report["run"]["status"], loop.INCOMPLETE)
        self.assertEqual(report["run"]["exit_code"], 1)
        nope = self.board(report, "greenhouse/nope")
        self.assertEqual((nope["outcome"], len(nope["attempts"]), nope["postings_observed"]), (loop.FAILED, 1, None))
        self.assertIn("deliberate failure observed and handled", report["run"]["deliberate_failure"][0])
        self.assertEqual(report["attention_required"][0]["board"], "greenhouse/nope")

    def test_deliberate_failure_that_succeeds_is_reported_as_not_achieved(self):
        boards = [(GH, "alpha", "deliberate-failure")]
        report, _, _, _ = self.go(boards, {url(GH, "alpha"): [ok(gh_body([1]))]})
        self.assertIn("NOT achieved", report["run"]["deliberate_failure"][0])

    def test_valid_empty_board_is_empty_needs_review_never_no_new_jobs(self):
        script = {**happy_script(), url(AS, "beta"): [ok(ashby_body([]))]}
        report, transport, _, _ = self.go(THREE, script, SEEN)
        beta = self.board(report, "ashby/beta")
        self.assertEqual(report["run"]["status"], loop.INCOMPLETE)
        self.assertEqual((beta["outcome"], beta["new"], beta["postings_observed"]), (loop.EMPTY, None, 0))
        self.assertEqual(len(transport.calls), 3)      # an empty board is not retried

    def test_first_observation_is_a_labeled_baseline_with_nothing_reported_new(self):
        report, _, _, _ = self.go(THREE, happy_script(), None)
        for b in report["boards"]:
            self.assertTrue(b["baseline"])
            self.assertIsNone(b["new"])

    def test_interrupt_is_incomplete_and_later_boards_are_not_observed(self):
        class Interrupting(FakeTransport):
            def __call__(self, u, t):
                if u == url(AS, "beta"):
                    raise KeyboardInterrupt
                return super().__call__(u, t)
        project = Project(THREE, SEEN)
        self.projects.append(project)
        report = loop.run(project.root, transport=Interrupting(self.clock, happy_script()), clock=self.clock,
                          sleep=self.clock.sleep, wall=self.clock.wall)
        self.assertEqual(report["run"]["status"], loop.INCOMPLETE)
        self.assertEqual([b["outcome"] for b in report["boards"]], [loop.OBSERVED, loop.NOT_OBSERVED, loop.NOT_OBSERVED])


class TestPreflight(LoopCase):
    def test_duplicate_board_is_an_error_before_any_request(self):
        boards = [(GH, "alpha", "watch"), (GH, "alpha", "watch")]
        report, transport, _, _ = self.go(boards, happy_script())
        self.assertEqual((report["run"]["status"], report["run"]["exit_code"]), (loop.ERROR, 3))
        self.assertEqual(transport.calls, [])
        self.assertIn("duplicates are not allowed", report["run"]["reasons"][0])

    def test_seven_boards_exceed_the_board_ceiling(self):
        boards = [(GH, f"b{i}", "watch") for i in range(7)]
        report, transport, _, _ = self.go(boards, {})
        self.assertEqual(report["run"]["status"], loop.ERROR)
        self.assertEqual(transport.calls, [])

    def test_zero_boards_is_an_error(self):
        report, transport, _, _ = self.go([], {})
        self.assertEqual(report["run"]["status"], loop.ERROR)

    def test_corrupt_state_stops_before_the_network(self):
        project = Project(THREE, None)
        self.projects.append(project)
        (project.root / "state").mkdir()
        (project.root / "state" / "seen.json").write_text("{not json")
        transport = FakeTransport(self.clock, happy_script())
        report = loop.run(project.root, transport=transport, clock=self.clock, sleep=self.clock.sleep,
                          wall=self.clock.wall)
        self.assertEqual(report["run"]["status"], loop.ERROR)
        self.assertEqual(transport.calls, [])

    def test_budget_above_the_gate_ceiling_is_refused(self):
        report, transport, _, _ = self.go(THREE, happy_script(), budget=replace(loop.CEILINGS, max_attempts=13))
        self.assertEqual(report["run"]["status"], loop.ERROR)
        self.assertIn("ceiling", report["run"]["reasons"][0])
        self.assertEqual(transport.calls, [])


class TestErrorPolicy(LoopCase):
    def test_503_is_retried_once_after_one_second_and_both_attempts_are_recorded(self):
        script = {**happy_script(), url(GH, "alpha"): [status(503), ok(gh_body([1, 2]))]}
        report, transport, _, _ = self.go(THREE, script, SEEN)
        alpha = self.board(report, "greenhouse/alpha")
        self.assertEqual(alpha["outcome"], loop.OBSERVED)
        self.assertEqual([a["status"] for a in alpha["attempts"]], [503, 200])
        self.assertEqual(self.clock.sleeps, [1.0])
        self.assertEqual(report["run"]["attempts_used"], 4)

    def test_two_timeouts_fail_after_exactly_one_retry(self):
        script = {**happy_script(), url(GH, "alpha"): [timeout(), timeout()]}
        report, transport, _, _ = self.go(THREE, script, SEEN)
        alpha = self.board(report, "greenhouse/alpha")
        self.assertEqual((alpha["outcome"], len(alpha["attempts"])), (loop.FAILED, 2))
        self.assertEqual(alpha["attempts"][0]["response"], "no response received")
        self.assertIsNone(alpha["postings_observed"])

    def test_no_retry_for_404_429_redirect_or_malformed_json(self):
        for resp in (status(404), status(429), status(301, headers={"location": "https://evil.example/"}),
                     ok(b"{not json"), ok(b"")):
            with self.subTest(status=resp.status, body=resp.body[:10]):
                script = {url(GH, "alpha"): [resp]}
                report, transport, _, _ = self.go([(GH, "alpha", "watch")], script)
                self.assertEqual(len(transport.calls), 1)
                self.assertEqual(self.board(report, "greenhouse/alpha")["outcome"], loop.FAILED)

    def test_redirect_target_is_never_requested(self):
        script = {url(GH, "alpha"): [status(302, headers={"location": "https://evil.example/jobs"})]}
        report, transport, _, _ = self.go([(GH, "alpha", "watch")], script)
        self.assertEqual([c[0] for c in transport.calls], [url(GH, "alpha")])
        self.assertIn("refused", self.board(report, "greenhouse/alpha")["reason"])


class TestBudgets(LoopCase):
    def test_request_budget_counts_failures_and_marks_unvisited_boards_not_observed(self):
        script = {url(GH, "alpha"): [timeout(1.0), timeout(1.0)], url(AS, "beta"): [ok(ashby_body(["b1"]))]}
        report, transport, _, _ = self.go(THREE, script, SEEN, budget=replace(loop.CEILINGS, max_attempts=3))
        self.assertEqual((report["run"]["status"], report["run"]["exit_code"]), (loop.BUDGET_EXHAUSTED, 2))
        self.assertEqual(report["run"]["attempts_used"], 3)
        gamma = self.board(report, "lever/gamma")
        self.assertEqual((gamma["outcome"], gamma["new"], gamma["postings_observed"]), (loop.NOT_OBSERVED, None, None))

    def test_retry_that_does_not_fit_the_time_budget_is_not_attempted(self):
        script = {url(GH, "alpha"): [timeout(9.5)]}
        report, transport, _, _ = self.go([(GH, "alpha", "watch")], script,
                                          budget=replace(loop.CEILINGS, max_seconds=10.0))
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(self.clock.sleeps, [])
        self.assertEqual(report["run"]["status"], loop.BUDGET_EXHAUSTED)

    def test_request_timeout_is_reduced_to_the_remaining_run_time(self):
        script = {url(GH, "alpha"): [ok(gh_body([1]), elapsed=6.0)], url(AS, "beta"): [ok(ashby_body(["b1"]))]}
        report, transport, _, _ = self.go(THREE[:2], script, budget=replace(loop.CEILINGS, max_seconds=8.0))
        self.assertEqual([round(c[1], 3) for c in transport.calls], [8.0, 2.0])

    def test_time_budget_spent_marks_remaining_boards_not_observed(self):
        script = {url(GH, "alpha"): [ok(gh_body([1]), elapsed=5.0)]}
        report, transport, _, _ = self.go(THREE, script, budget=replace(loop.CEILINGS, max_seconds=5.0))
        self.assertEqual(report["run"]["status"], loop.BUDGET_EXHAUSTED)
        self.assertEqual(len(transport.calls), 1)
        self.assertNotEqual(self.board(report, "greenhouse/alpha")["outcome"], loop.OBSERVED)


class TestRepeatRule(unittest.TestCase):
    def test_second_attempt_is_allowed_only_as_the_retry_of_a_transient_failure(self):
        ledger, action = loop.Ledger(), (GH, "alpha", "GET", url(GH, "alpha"))
        ledger.authorize(action, is_retry=False)
        ledger.record(action, "transient")
        ledger.authorize(action, is_retry=True)
        ledger.record(action, "transient")
        with self.assertRaises(loop.RepeatViolation):
            ledger.authorize(action, is_retry=True)

    def test_repeat_after_a_non_transient_failure_is_a_violation(self):
        ledger, action = loop.Ledger(), (GH, "alpha", "GET", url(GH, "alpha"))
        ledger.record(action, "failed")
        with self.assertRaises(loop.RepeatViolation):
            ledger.authorize(action, is_retry=True)


class TestState(LoopCase):
    def test_finished_run_without_approval_leaves_state_unchanged(self):
        report, _, project, before = self.go(THREE, happy_script(), SEEN)
        self.assertEqual(report["run"]["status"], loop.FINISHED)
        self.assertTrue(report["run"]["state_update"].startswith("not-approved"))
        self.assertEqual(project.state_bytes(), before)

    def test_finished_run_with_approval_writes_state_keyed_by_board(self):
        report, _, project, _ = self.go(THREE, happy_script(), SEEN, approve_state_write=True)
        self.assertEqual(report["run"]["state_update"], "updated")
        saved = json.loads(project.state_bytes())
        self.assertEqual(saved["boards"]["greenhouse/alpha"]["seen_ids"], ["1", "2", "3"])
        self.assertEqual(saved["boards"]["ashby/beta"]["seen_ids"], ["b1", "b2"])

    def test_incomplete_run_with_approval_does_not_change_state(self):
        script = {**happy_script(), url(LV, "gamma"): [status(404)]}
        report, _, project, before = self.go(THREE, script, SEEN, approve_state_write=True)
        self.assertEqual(report["run"]["status"], loop.INCOMPLETE)
        self.assertTrue(report["run"]["state_update"].startswith("not-allowed"))
        self.assertEqual(project.state_bytes(), before)

    def test_same_id_on_two_boards_is_tracked_separately(self):
        boards = [(GH, "alpha", "watch"), (GH, "other", "watch")]
        state = state_for({"greenhouse/alpha": [7], "greenhouse/other": [8]})
        script = {url(GH, "alpha"): [ok(gh_body([7]))], url(GH, "other"): [ok(gh_body([7, 8]))]}
        report, _, _, _ = self.go(boards, script, state)
        self.assertEqual([n["key"] for n in self.board(report, "greenhouse/other")["new"]], ["greenhouse/other/7"])


class TestEvidence(LoopCase):
    def test_every_attempt_is_in_the_trace_and_raw_files_are_saved(self):
        script = {**happy_script(), url(GH, "alpha"): [status(503), ok(gh_body([1, 2]))]}
        report, _, project, _ = self.go(THREE, script, SEEN)
        run_dir = project.root / report["run"]["run_dir"]
        events = [json.loads(l) for l in (run_dir / "trace.jsonl").read_text().splitlines()]
        self.assertEqual(sum(e["event"] == "attempt" for e in events), 4)
        for b in report["boards"]:
            for a in b["attempts"]:
                self.assertTrue((project.root / a["raw_file"]).exists())
        self.assertTrue((run_dir / "report.md").exists())

    def test_seeded_replay_is_labeled_and_cannot_be_approved_to_write_state(self):
        report, transport, _, _ = self.go(THREE, happy_script(), SEEN, replay="seeded/x", approve_state_write=True)
        self.assertEqual(report["run"]["mode"], loop.SEEDED)
        self.assertEqual(report["run"]["status"], loop.ERROR)
        self.assertEqual(transport.calls, [])


if __name__ == "__main__":
    unittest.main()
