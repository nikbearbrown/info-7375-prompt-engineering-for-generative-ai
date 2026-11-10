"""Two GATE.md gaps found by a post-submission review on 2026-11-10 (reproduced by Claude Code).

Written by Claude Code BEFORE the fix, and committed failing. Offline: fake clock and fake transport.

1. GATE.md section 2: "check time during response reading and processing ... Never extend the
   work deadline." At dfcf112, slow rule classification let a run end FINISHED after 242.6 s on a
   120 s budget.
2. GATE.md section 1: "Do not mark a job seen before its processing and report succeed." At dfcf112,
   an approved finished run wrote state/seen.json before report.json; when the report write failed,
   state had already advanced.
"""
from __future__ import annotations

import unittest
from unittest import mock

from jobloop import loop, policy, rule
from tests.helpers import FakeClock, FakeTransport, Project
from tests.test_loop import SEEN, THREE, happy_script


class TestProcessingDeadline(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.project = Project(THREE, SEEN)
        self.addCleanup(self.project.cleanup)
        self.calls = 0
        real = rule.classify

        def slow(posting, resume):
            self.calls += 1
            self.clock.t += 121.0                 # one classification longer than the whole budget
            return real(posting, resume)

        before = self.project.state_bytes()
        with mock.patch.object(rule, "classify", slow):
            self.report = loop.run(self.project.root, transport=FakeTransport(self.clock, happy_script()),
                                   clock=self.clock, sleep=self.clock.sleep, wall=self.clock.wall,
                                   approve_state_write=True)
        self.state_changed = self.project.state_bytes() != before

    def test_a_run_past_its_deadline_is_not_finished(self):
        self.assertEqual(self.report["run"]["status"], loop.BUDGET_EXHAUSTED)
        self.assertEqual(self.report["run"]["exit_code"], 2)

    def test_work_stops_once_the_deadline_has_passed(self):
        self.assertEqual(self.calls, 1, "classification must not start after the deadline")

    def test_state_is_not_written_by_an_over_budget_run(self):
        self.assertFalse(self.state_changed)


class TestReportBeforeState(unittest.TestCase):
    def test_a_failed_report_write_leaves_state_unchanged(self):
        clock = FakeClock()
        project = Project(THREE, SEEN)
        self.addCleanup(project.cleanup)
        before = project.state_bytes()
        real_write = policy.write_new_file

        def failing(path, data, **kw):
            if str(path).endswith("/report.json"):
                raise OSError("simulated disk error writing report.json")
            return real_write(path, data, **kw)

        with mock.patch.object(policy, "write_new_file", failing):
            with self.assertRaises(OSError):
                loop.run(project.root, transport=FakeTransport(clock, happy_script()), clock=clock,
                         sleep=clock.sleep, wall=clock.wall, approve_state_write=True)
        self.assertEqual(project.state_bytes(), before, "state advanced although no report was saved")

    def test_an_approved_finished_run_still_writes_state_after_its_report(self):
        clock = FakeClock()
        project = Project(THREE, SEEN)
        self.addCleanup(project.cleanup)
        order = []
        real_write, real_replace = policy.write_new_file, policy.replace_state

        def write(path, data, **kw):
            order.append(str(path).rsplit("/", 1)[-1])
            return real_write(path, data, **kw)

        def replace(data, **kw):
            order.append("state/seen.json")
            return real_replace(data, **kw)

        with mock.patch.object(policy, "write_new_file", write), mock.patch.object(policy, "replace_state", replace):
            report = loop.run(project.root, transport=FakeTransport(clock, happy_script()), clock=clock,
                              sleep=clock.sleep, wall=clock.wall, approve_state_write=True)
        self.assertEqual(report["run"]["state_update"], "updated")
        self.assertLess(order.index("report.json"), order.index("state/seen.json"), order)

    def test_cli_names_the_report_failure_not_the_run_folder(self):
        with mock.patch.object(loop, "run", side_effect=loop.ReportWriteError("disk full")):
            with mock.patch("sys.stderr") as err:
                code = loop.main([])
        self.assertEqual(code, 3)
        written = "".join(c.args[0] for c in err.write.call_args_list)
        self.assertIn("report", written)
        self.assertNotIn("no run folder could be created", written)


if __name__ == "__main__":
    unittest.main()
