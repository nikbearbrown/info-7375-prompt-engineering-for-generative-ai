"""The loop: exits, budgets, repeat rule, error policy (GATE.md 1-4).
All offline: a fake network answers with CONSTRUCTED responses."""

import gzip
import json
import shutil
import unittest

from agent import loop
from agent.policy import always_approve, no_approval
from tests.boundary_cases import sandbox
from tests.loop_fakes import (LIMITS, TIMEOUT, FakeClock, FakeNet, ashby, gh,
                              lever, url)

GH, LV, AS = "greenhouse", "lever", "ashby"
THREE = [{"ats": GH, "board": "acme"}, {"ats": LV, "board": "beta"},
         {"ats": AS, "board": "gamma"}]


def good_answers():
    return {url(GH, "acme"): [(200, gh(1, 2, 3))],
            url(LV, "beta"): [(200, lever(1, 2))],
            url(AS, "gamma"): [(200, ashby(1))]}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp, self.policy, _ = sandbox()
        (self.policy.root / "state" / "greenhouse-databricks.json").unlink()
        self.sleeps = []

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_loop(self, boards, answers, limits=LIMITS, approver=no_approval,
                 clock=None, per_request=0.0, stamp="T1"):
        clock = clock or FakeClock()
        self.net = FakeNet(self.policy, answers, clock, per_request)
        return loop.run(boards, policy=self.policy, get=self.net.get,
                        limits=dict(limits), approver=approver, clock=clock,
                        sleep=self.sleeps.append, stamp=stamp, kind="test")

    def board(self, report, i):
        return report["boards"][i]


class TestExits(Base):
    def test_three_boards_two_ats_finished(self):
        r, trace = self.run_loop(THREE, good_answers())
        self.assertEqual(r["exit"], "finished")
        self.assertEqual(r["exit_code"], 0)
        self.assertEqual([b["jobs"] for b in r["boards"]], [3, 2, 1])
        self.assertTrue(all(b["baseline"] for b in r["boards"]))
        self.assertEqual(r["jobs_total_ok_boards"], 6)

    def test_one_broken_board_is_incomplete_not_finished(self):
        a = good_answers()
        a[url(LV, "beta")] = [(404, b'{"ok":false}')]
        r, _ = self.run_loop(THREE, a)
        self.assertEqual(r["exit"], "incomplete")
        self.assertEqual(r["exit_code"], 2)
        self.assertIn("lever/beta: not_found", r["exit_reason"])
        self.assertEqual(self.board(r, 2)["status"], "ok")   # loop went on

    def test_every_board_failed_is_error(self):
        a = {u: [(404, b"")] for u in good_answers()}
        r, _ = self.run_loop(THREE, a)
        self.assertEqual(r["exit"], "error")
        self.assertEqual(r["exit_code"], 1)

    def test_bad_config_is_error_and_stops(self):
        boards = [{"ats": GH, "board": "../../etc"}] + THREE
        r, _ = self.run_loop(boards, good_answers())
        self.assertEqual(r["exit"], "error")
        self.assertEqual(self.net.calls, [])
        self.assertTrue(all(b["status"] == "not_visited"
                            for b in r["boards"][1:]))

    def test_report_and_trace_written_inside_runs(self):
        r, trace = self.run_loop(THREE, good_answers())
        d = self.policy.root / r["run_dir"]
        self.assertEqual(json.loads((d / "report.json").read_text())["exit"],
                         "finished")
        lines = (d / "trace.jsonl").read_text().splitlines()
        self.assertEqual(len(lines), len(trace))
        self.assertEqual(json.loads(lines[-1])["event"], "run_end")


class TestErrorPolicy(Base):
    def test_404_is_not_retried_and_invents_no_count(self):
        a = good_answers()
        a[url(GH, "acme")] = [(404, b"not found")]
        r, _ = self.run_loop(THREE, a)
        b = self.board(r, 0)
        self.assertEqual((b["status"], b["attempts"]), ("not_found", 1))
        self.assertIsNone(b["jobs"])
        self.assertIsNone(b["new_count"])
        self.assertEqual(self.net.calls.count(url(GH, "acme")), 1)
        self.assertEqual(self.sleeps, [])
        self.assertEqual(r["jobs_total_ok_boards"], 3)      # not 3 + 0

    def test_timeout_retried_once_then_ok(self):
        a = good_answers()
        a[url(GH, "acme")] = [TIMEOUT, (200, gh(1))]
        r, trace = self.run_loop(THREE, a)
        b = self.board(r, 0)
        self.assertEqual((b["status"], b["attempts"]), ("ok", 2))
        self.assertEqual(self.sleeps, [2])
        self.assertEqual(r["exit"], "finished")
        self.assertEqual(sum(e["event"] == "retry" for e in trace), 1)

    def test_timeout_twice_gives_up(self):
        a = good_answers()
        a[url(GH, "acme")] = [TIMEOUT, TIMEOUT]
        r, _ = self.run_loop(THREE, a)
        b = self.board(r, 0)
        self.assertEqual((b["status"], b["attempts"]), ("timeout", 2))
        self.assertIsNone(b["jobs"])
        self.assertEqual(r["exit"], "incomplete")

    def test_5xx_retried_once(self):
        a = good_answers()
        a[url(LV, "beta")] = [(503, b"busy"), (200, lever(9))]
        r, _ = self.run_loop(THREE, a)
        self.assertEqual(self.board(r, 1)["status"], "ok")
        self.assertEqual(self.board(r, 1)["attempts"], 2)

    def test_403_and_bad_body_not_retried(self):
        a = good_answers()
        a[url(GH, "acme")] = [(403, b"no")]
        a[url(LV, "beta")] = [(200, b"<html>maintenance</html>")]
        r, _ = self.run_loop(THREE, a)
        self.assertEqual(self.board(r, 0)["status"], "http_403")
        self.assertEqual(self.board(r, 1)["status"], "bad_body")
        self.assertEqual([b["attempts"] for b in r["boards"][:2]], [1, 1])

    def test_zero_jobs_is_suspicious_not_no_new_jobs(self):
        a = good_answers()
        a[url(AS, "gamma")] = [(200, b'{"jobs": []}')]
        r, _ = self.run_loop(THREE, a)
        b = self.board(r, 2)
        self.assertEqual(b["status"], "suspicious_empty")
        self.assertIsNone(b["new_count"])                # not 0
        self.assertIsNone(b["state_written"])
        self.assertFalse((self.policy.root / "state/ashby-gamma.json")
                         .exists())
        self.assertEqual(r["exit"], "incomplete")
        self.assertIn("ashby/gamma", " ".join(r["escalate"]))

    def test_zero_jobs_after_a_real_baseline_does_not_wipe_state(self):
        self.run_loop(THREE, good_answers(), stamp="T1")
        before = (self.policy.root / "state/greenhouse-acme.json").read_text()
        a = good_answers()
        a[url(GH, "acme")] = [(200, b'{"jobs": []}')]
        r, _ = self.run_loop(THREE, a, approver=always_approve, stamp="T2")
        self.assertEqual(self.board(r, 0)["status"], "suspicious_empty")
        self.assertEqual(
            (self.policy.root / "state/greenhouse-acme.json").read_text(),
            before)

    def test_raw_bodies_saved_byte_for_byte(self):
        a = good_answers()
        a[url(GH, "acme")] = [(404, b"exact 404 body")]
        r, _ = self.run_loop(THREE, a)
        raw = self.policy.root / self.board(r, 0)["raw"][0]
        self.assertEqual(gzip.decompress(raw.read_bytes()), b"exact 404 body")
        raw = self.policy.root / self.board(r, 1)["raw"][0]
        self.assertEqual(gzip.decompress(raw.read_bytes()), lever(1, 2))


class TestRepeatRule(Base):
    def test_same_board_different_case_is_skipped_and_free(self):
        boards = THREE + [{"ats": GH, "board": "ACME"}]
        r, trace = self.run_loop(boards, good_answers())
        self.assertEqual(self.board(r, 3)["status"], "skipped_repeat")
        self.assertEqual(len(self.net.calls), 3)
        self.assertEqual(r["budget_used"]["boards"], 3)
        self.assertEqual(r["exit"], "finished")          # a repeat is not a failure

    def test_same_name_on_another_ats_is_not_a_repeat(self):
        boards = [{"ats": GH, "board": "acme"}, {"ats": LV, "board": "acme"}]
        a = {url(GH, "acme"): [(200, gh(1))],
             url(LV, "acme"): [(200, lever(1))]}
        r, _ = self.run_loop(boards, a)
        self.assertEqual([b["status"] for b in r["boards"]], ["ok", "ok"])


class TestBudgets(Base):
    def test_board_budget(self):
        r, _ = self.run_loop(THREE, good_answers(),
                             limits={**LIMITS, "boards": 2})
        self.assertEqual(r["exit"], "budget_exhausted")
        self.assertEqual(r["exit_code"], 3)
        self.assertEqual(self.board(r, 2)["status"], "not_visited")
        self.assertEqual(len(self.net.calls), 2)

    def test_retries_count_against_request_budget(self):
        a = {url(GH, "acme"): [TIMEOUT, TIMEOUT],
             url(LV, "beta"): [TIMEOUT, TIMEOUT],
             url(AS, "gamma"): [(200, ashby(1))]}
        r, trace = self.run_loop(THREE, a, limits={**LIMITS, "requests": 3})
        self.assertEqual(len(self.net.calls), 3)          # never 4
        self.assertEqual(r["budget_used"]["requests"], 3)
        self.assertEqual(r["exit"], "budget_exhausted")
        self.assertIn("retry skipped", self.board(r, 1)["reason"])
        self.assertEqual(self.board(r, 2)["status"], "not_visited")

    def test_seconds_budget(self):
        r, _ = self.run_loop(THREE, good_answers(), per_request=70)
        self.assertEqual(r["exit"], "budget_exhausted")
        self.assertIn("seconds", r["exit_reason"])
        self.assertEqual(len(self.net.calls), 2)          # 0 s, 70 s; 140 s stops

    def test_budget_exhausted_wins_over_incomplete(self):
        a = good_answers()
        a[url(GH, "acme")] = [(404, b"")]
        r, _ = self.run_loop(THREE, a, limits={**LIMITS, "boards": 2})
        self.assertEqual(r["exit"], "budget_exhausted")


class TestStateAndApproval(Base):
    def test_second_run_reports_only_new_ids(self):
        self.run_loop(THREE, good_answers(), stamp="T1")
        a = good_answers()
        a[url(GH, "acme")] = [(200, gh(1, 2, 3, 4))]
        r, _ = self.run_loop(THREE, a, approver=always_approve, stamp="T2")
        b = self.board(r, 0)
        self.assertEqual((b["baseline"], b["new_count"]), (False, 1))
        self.assertEqual(b["new"][0]["id"], "4")
        self.assertEqual(r["exit"], "finished")

    def test_no_approval_means_state_not_written_and_run_incomplete(self):
        self.run_loop(THREE, good_answers(), stamp="T1")
        path = self.policy.root / "state/greenhouse-acme.json"
        before = path.read_text()
        a = good_answers()
        a[url(GH, "acme")] = [(200, gh(1, 2, 3, 4))]
        r, trace = self.run_loop(THREE, a, approver=no_approval, stamp="T2")
        b = self.board(r, 0)
        self.assertEqual(b["new_count"], 1)                # still reported
        self.assertFalse(b["state_written"])
        self.assertEqual(path.read_text(), before)
        self.assertEqual(r["exit"], "incomplete")
        self.assertTrue(any(e["event"] == "state_not_written" for e in trace))


class TestIndependentCheck(Base):
    def check(self, r):
        import check
        return check.check_js2(self.policy.root / r["run_dir"] /
                               "report.json")

    def test_check_passes_an_honest_run(self):
        a = good_answers()
        a[url(GH, "acme")] = [(404, b"")]
        a[url(AS, "gamma")] = [(200, b'{"jobs": []}')]
        r, _ = self.run_loop(THREE, a)
        fails = [f for f in self.check(r) if f[0] == "FAIL"]
        self.assertEqual(fails, [])

    def test_check_catches_a_doctored_report(self):
        a = good_answers()
        a[url(AS, "gamma")] = [(200, b'{"jobs": []}')]
        r, _ = self.run_loop(THREE, a)
        p = self.policy.root / r["run_dir"] / "report.json"
        doc = json.loads(p.read_text())
        doc["boards"][2].update(status="ok", new_count=0)   # "no new jobs"
        doc["exit"] = "finished"
        p.write_text(json.dumps(doc))
        names = {f[1] for f in self.check(r) if f[0] == "FAIL"}
        self.assertIn("ashby/gamma empty board", names)
        self.assertIn("exit honesty", names)


if __name__ == "__main__":
    unittest.main()
