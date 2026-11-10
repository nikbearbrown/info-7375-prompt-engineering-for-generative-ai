"""Tests from the independent review of 2026-11-10 (REVIEW-FINDINGS.md), written before the fixes.

Each test is one finding, reproduced. They were committed failing, then the loop and
check_run.py were fixed. Findings about agent/tools.py are not here: that file is the
subject of the review packet, and changes to it wait for my decision on the patch.
"""

import json
import unittest
from unittest import mock

import check_run
from agent import loop
from tests.helpers import (ANTHROPIC, ASHBY, GH, LEVER, THREE, FakeClock, FakeNet, ashby_body, ashby_job, gh_body,
                           gh_job, lever_body, lever_job, make_root, ok, run_loop, status)


def failed(checks):
    return sorted(c.name for c in checks if not c.passed)


def three_ok():
    return {GH % "anthropic": [ok(gh_body(gh_job(1)))], LEVER % "palantir": [ok(lever_body(lever_job("a")))],
            ASHBY % "linear": [ok(ashby_body(ashby_job("x")))]}


class Finding2NanBudget(unittest.TestCase):
    def test_nan_cannot_switch_a_budget_off(self):
        root, clock = make_root(self, THREE), FakeClock()
        for name in ("seconds", "requests", "boards"):
            with self.assertRaises(ValueError, msg=name):
                loop.run(root, transport=FakeNet(clock, three_ok()), clock=clock, sleep=clock.sleep,
                         limits={name: float("nan")})
        self.assertEqual(list((root / "jobs").iterdir()), [])


class Finding4CheckSurvivesBadShape(unittest.TestCase):
    def test_check_run_does_not_crash_on_a_correct_run_with_a_bad_shape_board(self):
        root, clock = make_root(self, THREE), FakeClock()
        script = three_ok()
        script[GH % "anthropic"] = [ok(b"<html>maintenance</html>")]
        script[LEVER % "palantir"] = [ok(b'{"ok": true}')]
        record = run_loop(root, FakeNet(clock, script), clock)
        self.assertEqual(record["exit"], "incomplete")
        self.assertEqual(failed(check_run.check(root / record["files"]["record"])), [])


class Finding3CheckReadsTheConfig(unittest.TestCase):
    def good_run(self):
        root, clock = make_root(self, THREE), FakeClock()
        record = run_loop(root, FakeNet(clock, three_ok()), clock)
        return root, root / record["files"]["record"]

    def edit(self, path, change):
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data))

    def test_a_board_missing_from_the_record_is_caught(self):
        root, path = self.good_run()
        self.edit(path, lambda d: d["boards"].pop())
        self.assertIn("boards_match_config", failed(check_run.check(path)))

    def test_a_board_falsely_labelled_skipped_repeat_is_caught(self):
        root, path = self.good_run()

        def fake_skip(d):
            d["boards"][2].update(status="skipped_repeat", counts=None, attempts=[], requests=0)
        self.edit(path, fake_skip)
        self.assertIn("boards_match_config", failed(check_run.check(path)))


class Finding5CheckUsesTheSecondsBudget(unittest.TestCase):
    def test_a_run_over_the_seconds_budget_is_caught(self):
        root, clock = make_root(self, THREE), FakeClock()
        script = {url: [(100, answers[0])] for url, answers in three_ok().items()}
        with mock.patch.object(loop.Loop, "seconds_left", lambda self: 30):  # a wrong loop that never runs out
            record = run_loop(root, FakeNet(clock, script), clock)
        self.assertEqual(record["exit"], "finished")
        self.assertIn("budgets_and_hosts", failed(check_run.check(root / record["files"]["record"])))


class Finding7GoneSinceLastRun(unittest.TestCase):
    def test_gone_counts_against_the_last_good_run_not_every_id_ever_seen(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        gone = []
        for n, ids in enumerate([(1, 2), (1,), (1,)], start=1):
            record = run_loop(root, FakeNet(clock, {GH % "anthropic": [ok(gh_body(*[gh_job(i) for i in ids]))]}),
                              clock, run_id="run-%d" % n)
            gone.append(record["boards"][0]["counts"]["gone"])
        self.assertEqual(gone, [0, 1, 0])


class Finding7bGoneWithoutLastIds(unittest.TestCase):
    """Found in live run 2 (2026-11-10T214509Z), not by the reviewer: my fix for finding 7 fell back to
    every id ever seen when a state file had no last_ids, and reported Anthropic gone 78 instead of 0."""

    def state_without_last_ids(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        run_loop(root, FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(1), gh_job(2)))]}), clock, run_id="run-1")
        run_loop(root, FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(2), gh_job(3)))]}), clock, run_id="run-2")
        path = root / "jobs" / "state" / "greenhouse-anthropic.json"
        state = json.loads(path.read_text())
        del state["last_ids"]  # as written by the code before 9ab582c
        path.write_text(json.dumps(state))
        return root, clock

    def test_gone_is_unknown_not_invented_when_the_last_ids_are_not_recorded(self):
        root, clock = self.state_without_last_ids()
        record = run_loop(root, FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(2), gh_job(3)))]}), clock,
                          run_id="run-3")
        self.assertIsNone(record["boards"][0]["counts"]["gone"])  # it was 1: ids 1, 2, 3 seen minus 2, 3

    def test_check_run_recomputes_gone_from_the_last_raw_response(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        run_loop(root, FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(1), gh_job(2)))]}), clock, run_id="run-1")
        record = run_loop(root, FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(2)))]}), clock, run_id="run-2")
        path = root / record["files"]["record"]
        self.assertEqual(failed(check_run.check(path)), [])
        data = json.loads(path.read_text())
        data["boards"][0]["counts"]["gone"] = 78
        path.write_text(json.dumps(data))
        self.assertIn("gone_recomputed", failed(check_run.check(path)))


class MissingEarlierRawFile(unittest.TestCase):
    """Found in the final check (2026-11-10): with an earlier raw file missing (the Canvas zip has no JS1 folder),
    check_run must say it cannot recompute, not report a made-up recomputed count."""

    def test_a_missing_earlier_raw_file_is_reported_as_cannot_recompute(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        first = run_loop(root, FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(1)))]}), clock, run_id="run-1")
        record = run_loop(root, FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(1), gh_job(2)))]}), clock,
                          run_id="run-2")
        (root / first["boards"][0]["attempts"][0]["raw_file"]).unlink()
        checks = {c.name: c for c in check_run.check(root / record["files"]["record"])}
        self.assertFalse(checks["new_ids_recomputed"].passed)
        self.assertIn("is missing", checks["new_ids_recomputed"].detail)
        self.assertNotRegex(checks["new_ids_recomputed"].detail, r"recomputed \d")  # no made-up count


class Finding8aRedirectRepeats(unittest.TestCase):
    def test_redirect_to_the_same_url_is_not_sent_again(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        net = FakeNet(clock, {GH % "anthropic": [status(301, headers={"location": GH % "anthropic"}),
                                                 ok(gh_body(gh_job(1)))]})
        record = run_loop(root, net, clock)
        self.assertEqual(len(net.calls), 1)
        self.assertEqual((record["boards"][0]["status"], record["boards"][0]["reason"]),
                         ("failed", "refused_redirect"))

    def test_redirect_without_a_location_is_not_sent_again(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        net = FakeNet(clock, {GH % "anthropic": [status(304)] * 3})
        record = run_loop(root, net, clock)
        self.assertEqual(len(net.calls), 1)
        self.assertEqual(record["boards"][0]["reason"], "refused_redirect")


if __name__ == "__main__":
    unittest.main()
