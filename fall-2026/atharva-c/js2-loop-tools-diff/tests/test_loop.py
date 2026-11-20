"""Loop tests: one per WRONG_VERSIONS.md row the loop owns, plus the exits.

WRONG_VERSIONS.md was committed in 459e7b3 before this file existed.
All tests use a scripted fake fetcher, a fake clock and a fake sleep:
no network, no real waiting.
"""

import json
import tempfile
import unittest
from pathlib import Path

from agent.loop import (BUDGET_EXHAUSTED, ERROR, FINISHED, INCOMPLETE, Loop,
                        Response, main)
from agent.policy import Policy

GH = "https://boards-api.greenhouse.io/v1/boards/{}/jobs"
LV = "https://api.lever.co/v0/postings/{}?mode=json"

BUDGET = {"max_boards": 5, "max_requests": 15, "max_seconds": 60,
          "retry_wait_seconds": 2, "request_timeout_seconds": 10}


def gh_jobs(n):
    return json.dumps({"jobs": [{"id": i, "title": f"Job {i}", "location": {"name": "Remote"},
                                 "absolute_url": f"https://example.test/{i}"} for i in range(n)]})


def lv_jobs(n):
    return json.dumps([{"id": f"l{i}", "text": f"Lever job {i}", "categories": {"location": "NYC"},
                        "hostedUrl": f"https://example.test/l{i}"} for i in range(n)])


def gh(name):
    return {"name": name, "ats": "greenhouse", "url": GH.format(name)}


def lv(name):
    return {"name": name, "ats": "lever", "url": LV.format(name)}


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class FakeFetch:
    """Scripted responses per URL. A list is served in order; the last item repeats.
    An item may be a Response, the string "timeout", or a callable(clock) -> Response."""

    def __init__(self, script, clock=None):
        self.script = script
        self.clock = clock
        self.calls = []

    def __call__(self, url, timeout):
        self.calls.append(url)
        items = self.script[url]
        n = sum(1 for c in self.calls if c == url)
        item = items[min(n, len(items)) - 1]
        if callable(item):
            item = item(self.clock)
        if item == "timeout":
            raise TimeoutError(url)
        return item


class LoopTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name).resolve()
        (self.root / "out").mkdir()
        self.policy = Policy(self.root)
        self.clock = FakeClock()
        self.sleeps = []

    def tearDown(self):
        self._tmp.cleanup()

    def run_loop(self, boards, script, budget=BUDGET):
        fetch = FakeFetch(script, self.clock)
        loop = Loop(boards, dict(budget), self.policy, fetch, clock=self.clock,
                    sleep=self.sleeps.append)
        return loop.run(), fetch, loop

    def board(self, report, name):
        return next(r for r in report["boards"] if r["board"] == name)

    # --- exits ------------------------------------------------------------

    def test_finished_when_every_board_has_jobs(self):
        boards = [gh("a"), gh("b"), lv("c")]
        script = {GH.format("a"): [Response(200, gh_jobs(3))],
                  GH.format("b"): [Response(200, gh_jobs(1))],
                  LV.format("c"): [Response(200, lv_jobs(2))]}
        report, _, _ = self.run_loop(boards, script)
        self.assertEqual(report["exit"], FINISHED)
        self.assertEqual([r["jobs"] for r in report["boards"]], [3, 1, 2])

    def test_wv01_empty_board_is_incomplete_not_finished(self):
        boards = [gh("a"), lv("c")]
        script = {GH.format("a"): [Response(200, '{"jobs": []}')],
                  LV.format("c"): [Response(200, "[]")]}
        report, _, _ = self.run_loop(boards, script)
        self.assertEqual(report["exit"], INCOMPLETE)
        for name in ("a", "c"):
            r = self.board(report, name)
            self.assertEqual(r["status"], "flagged")
            self.assertNotIn("jobs", r)

    # --- repeat rule ------------------------------------------------------

    def test_wv02_skipped_duplicate_uses_no_budget(self):
        boards = [gh("a"), gh("a"), gh("b")]
        script = {GH.format("a"): [Response(200, gh_jobs(1))],
                  GH.format("b"): [Response(200, gh_jobs(1))]}
        report, fetch, loop = self.run_loop(boards, script)
        self.assertEqual(report["boards"][1]["status"], "repeat-skipped")
        self.assertEqual(len(fetch.calls), 2)
        self.assertEqual(report["budget"]["used"]["requests"], 2)
        self.assertEqual(report["budget"]["used"]["boards"], 2)
        self.assertTrue(any(e["event"] == "repeat-skipped" for e in loop.trace))

    def test_wv03_url_variants_fetched_once(self):
        upper = dict(gh("a"), name="A-upper", url="https://boards-api.greenhouse.io/v1/boards/A/jobs/")
        boards = [gh("a"), upper]
        script = {GH.format("a"): [Response(200, gh_jobs(1))]}
        report, fetch, _ = self.run_loop(boards, script)
        self.assertEqual(len(fetch.calls), 1)
        self.assertEqual(self.board(report, "A-upper")["status"], "repeat-skipped")

    # --- error policy -----------------------------------------------------

    def test_wv04_404_not_retried(self):
        report, fetch, _ = self.run_loop([gh("bad")], {GH.format("bad"): [Response(404, "{}")]})
        self.assertEqual(len(fetch.calls), 1)
        self.assertEqual(self.board(report, "bad")["status"], "failed")
        self.assertEqual(self.sleeps, [])
        self.assertEqual(report["exit"], INCOMPLETE)

    def test_wv05_persistent_500_tried_exactly_twice(self):
        report, fetch, _ = self.run_loop([gh("a")], {GH.format("a"): [Response(500, "")]})
        self.assertEqual(len(fetch.calls), 2)
        self.assertEqual(self.board(report, "a")["status"], "failed")

    def test_timeout_then_success_retries_once(self):
        report, fetch, _ = self.run_loop(
            [gh("a")], {GH.format("a"): ["timeout", Response(200, gh_jobs(2))]})
        self.assertEqual(len(fetch.calls), 2)
        self.assertEqual(self.board(report, "a")["jobs"], 2)
        self.assertEqual(report["exit"], FINISHED)

    def test_other_4xx_not_retried(self):
        for code in (403, 429):
            report, fetch, _ = self.run_loop([gh("a")], {GH.format("a"): [Response(code, "")]})
            self.assertEqual(len(fetch.calls), 1, code)
            self.assertEqual(self.board(report, "a")["status"], "failed")

    def test_non_json_fails_without_retry(self):
        report, fetch, _ = self.run_loop([gh("a")], {GH.format("a"): [Response(200, "<html>")]})
        self.assertEqual(len(fetch.calls), 1)
        self.assertEqual(self.board(report, "a")["status"], "failed")

    def test_wv10_waits_2_seconds_before_retry(self):
        self.run_loop([gh("a")], {GH.format("a"): [Response(503, ""), Response(200, gh_jobs(1))]})
        self.assertEqual(self.sleeps, [2])

    def test_wv11_failed_board_has_no_job_count(self):
        report, _, _ = self.run_loop([gh("bad")], {GH.format("bad"): [Response(404, "")]})
        r = self.board(report, "bad")
        self.assertEqual(r["status"], "failed")
        self.assertNotIn("jobs", r)
        self.assertNotIn("new", r)

    # --- budgets ----------------------------------------------------------

    def test_wv12_time_budget_checked_between_boards(self):
        def slow(clock):
            clock.now += 65
            return Response(200, gh_jobs(1))
        boards = [gh("a"), gh("b")]
        script = {GH.format("a"): [slow], GH.format("b"): [Response(200, gh_jobs(1))]}
        report, fetch, _ = self.run_loop(boards, script)
        self.assertEqual(report["exit"], BUDGET_EXHAUSTED)
        self.assertEqual(fetch.calls, [GH.format("a")])
        self.assertEqual(self.board(report, "b")["status"], "skipped")

    def test_board_budget(self):
        boards = [gh(n) for n in "abcdef"]
        script = {GH.format(n): [Response(200, gh_jobs(1))] for n in "abcdef"}
        report, fetch, _ = self.run_loop(boards, script)
        self.assertEqual(report["exit"], BUDGET_EXHAUSTED)
        self.assertEqual(len(fetch.calls), 5)
        self.assertEqual(self.board(report, "f")["status"], "skipped")

    def test_request_budget(self):
        tight = dict(BUDGET, max_requests=3)
        boards = [gh("a"), gh("b")]
        script = {GH.format("a"): [Response(500, "")], GH.format("b"): [Response(500, "")]}
        report, fetch, _ = self.run_loop(boards, script, budget=tight)
        self.assertEqual(report["exit"], BUDGET_EXHAUSTED)
        self.assertEqual(len(fetch.calls), 3)
        self.assertIn("stopped mid-board", self.board(report, "b")["reason"])

    def test_request_budget_used_up_between_boards(self):
        # Found in the Nov 9 demo run (run-20261110-025634Z): with 2 requests and
        # 2 boards already fetched, the 3rd board was reported "stopped mid-board"
        # and counted as used, although no request was ever sent to it.
        tight = dict(BUDGET, max_requests=2)
        boards = [gh("a"), gh("b"), lv("c")]
        script = {GH.format("a"): [Response(200, gh_jobs(1))],
                  GH.format("b"): [Response(200, gh_jobs(1))],
                  LV.format("c"): [Response(200, lv_jobs(1))]}
        report, fetch, _ = self.run_loop(boards, script, budget=tight)
        self.assertEqual(report["exit"], BUDGET_EXHAUSTED)
        self.assertNotIn(LV.format("c"), fetch.calls)
        self.assertIn("not reached", self.board(report, "c")["reason"])
        self.assertEqual(report["budget"]["used"]["boards"], 2)

    # --- policy inside the loop (BOUNDARY_TABLE "run exits error") ----------

    def test_off_list_host_ends_run_with_error_before_any_request(self):
        evil = {"name": "evil", "ats": "greenhouse",
                "url": "https://boards-api.greenhouse.io.evil.com/v1/boards/x/jobs"}
        boards = [gh("a"), evil, gh("b")]
        script = {GH.format("a"): [Response(200, gh_jobs(1))],
                  GH.format("b"): [Response(200, gh_jobs(1))]}
        report, fetch, _ = self.run_loop(boards, script)
        self.assertEqual(report["exit"], ERROR)
        self.assertNotIn(evil["url"], fetch.calls)
        self.assertNotIn(GH.format("b"), fetch.calls)   # stops right away

    def test_crash_is_reported_as_error(self):
        def boom(clock):
            raise ValueError("unexpected")
        report, _, _ = self.run_loop([gh("a")], {GH.format("a"): [boom]})
        self.assertEqual(report["exit"], ERROR)
        self.assertIn("crash", report["reason"])

    # --- replay gives the same report --------------------------------------

    def test_replay_reproduces_report(self):
        (self.root / "boards.json").write_text(json.dumps({"boards": [gh("a"), gh("bad")]}))
        (self.root / "budget.json").write_text(json.dumps(BUDGET))
        import agent.loop as L
        script = {GH.format("a"): [Response(200, gh_jobs(2))],
                  GH.format("bad"): [Response(404, "{}")]}
        original = L.live_fetch
        L.live_fetch = FakeFetch(script)
        try:
            import os
            cwd = os.getcwd()
            os.chdir(self.root)
            try:
                main([], root=self.root)
                run_dir = next((self.root / "out").glob("run-*"))
                main(["--replay", str(run_dir.relative_to(self.root))], root=self.root)
            finally:
                os.chdir(cwd)
        finally:
            L.live_fetch = original
        live = json.loads((run_dir / "report.json").read_text())
        rep_dir = next((self.root / "out").glob("replay-*"))
        replay = json.loads((rep_dir / "report.json").read_text())
        for r in (live, replay):
            r.pop("run_id"), r.pop("mode"), r["budget"]["used"].pop("seconds")
        self.assertEqual(live, replay)
        self.assertEqual(live["exit"], INCOMPLETE)


if __name__ == "__main__":
    unittest.main()
