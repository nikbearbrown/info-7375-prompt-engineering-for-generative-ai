"""The independent checker catches reports that disagree with their own saved evidence. Offline."""
from __future__ import annotations

import json
import unittest

import independent_check
from jobloop import loop
from tests.helpers import FakeClock, FakeTransport, Project, ashby_body, gh_body, ok, state_for, status, url

BOARDS = [("greenhouse", "alpha", "watch"), ("ashby", "beta", "watch")]
SEEN = state_for({"greenhouse/alpha": [1], "ashby/beta": ["b1"]})


class TestIndependentCheck(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.project = Project(BOARDS, SEEN)

    def tearDown(self):
        self.project.cleanup()

    def run_loop(self, script):
        report = loop.run(self.project.root, transport=FakeTransport(self.clock, script), clock=self.clock,
                          sleep=self.clock.sleep, wall=self.clock.wall)
        return report, self.project.root / report["run"]["run_dir"]

    def check(self, run_dir):
        return {f["invariant"] for f in independent_check.check(run_dir, self.project.root)}

    def edit_report(self, run_dir, change):
        path = run_dir / "report.json"
        report = json.loads(path.read_text())
        change(report)
        path.write_text(json.dumps(report))

    def test_a_correct_finished_run_passes(self):
        _, run_dir = self.run_loop({url("greenhouse", "alpha"): [ok(gh_body([1]))],
                                    url("ashby", "beta"): [ok(ashby_body(["b1"]))]})
        self.assertEqual(self.check(run_dir), set())

    def test_a_correct_incomplete_run_passes(self):
        _, run_dir = self.run_loop({url("greenhouse", "alpha"): [status(404)],
                                    url("ashby", "beta"): [ok(ashby_body([]))]})
        self.assertEqual(self.check(run_dir), set())

    def test_empty_board_reported_as_finished_with_no_new_jobs_is_caught(self):
        _, run_dir = self.run_loop({url("greenhouse", "alpha"): [ok(gh_body([1]))],
                                    url("ashby", "beta"): [ok(ashby_body([]))]})

        def lie(r):
            r["run"].update(status="finished", exit_code=0)
            beta = r["boards"][1]
            beta.update(outcome="observed", new=[], baseline=False, previously_seen=1)
        self.edit_report(run_dir, lie)
        self.assertTrue({"C4", "C5", "C6"} <= self.check(run_dir))

    def test_wrong_posting_count_and_tampered_raw_file_are_caught(self):
        report, run_dir = self.run_loop({url("greenhouse", "alpha"): [ok(gh_body([1, 2]))],
                                         url("ashby", "beta"): [ok(ashby_body(["b1"]))]})
        self.edit_report(run_dir, lambda r: r["boards"][0].update(postings_observed=5))
        raw = self.project.root / report["boards"][1]["attempts"][0]["raw_file"]
        raw.write_bytes(ashby_body(["b1", "b2"]))
        self.assertTrue({"C4", "C3"} <= self.check(run_dir))

    def test_hidden_attempts_and_state_write_after_incomplete_are_caught(self):
        _, run_dir = self.run_loop({url("greenhouse", "alpha"): [status(404)],
                                    url("ashby", "beta"): [ok(ashby_body(["b1"]))]})
        self.edit_report(run_dir, lambda r: r["run"].update(attempts_used=1, state_update="updated"))
        self.assertTrue({"C7", "C9"} <= self.check(run_dir))

    def test_replay_labeled_live_is_caught(self):
        _, run_dir = self.run_loop({url("greenhouse", "alpha"): [ok(gh_body([1]))],
                                    url("ashby", "beta"): [ok(ashby_body(["b1"]))]})
        self.edit_report(run_dir, lambda r: r["run"].update(replay_source="seeded/x"))
        self.assertIn("C10", self.check(run_dir))


if __name__ == "__main__":
    unittest.main()
