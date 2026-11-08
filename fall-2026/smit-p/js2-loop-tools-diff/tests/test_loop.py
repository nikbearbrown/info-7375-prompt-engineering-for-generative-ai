"""Loop tests: exits, budgets, repeat rule, error policy. Offline; a fake transport stands in
for the network. "W<n>" names the wrong version from GATE.md that a test is there to catch."""

import json
import os
import tempfile
import unittest

from agent import fetch, loop, policy

BUDGETS = {"max_boards": 5, "max_requests": 12, "max_seconds": 60, "retries_per_board": 1}
GH = "https://boards-api.greenhouse.io/v1/boards/{}/jobs"
LV = "https://api.lever.co/v0/postings/{}?mode=json"
AB = "https://api.ashbyhq.com/posting-api/job-board/{}"


def gh_body(ids):
    return {"jobs": [{"id": i, "title": f"Job {i}", "location": {"name": "Remote"},
                      "absolute_url": f"https://x/{i}"} for i in ids], "meta": {"total": len(ids)}}


def lv_body(ids):
    return [{"id": i, "text": f"Job {i}", "categories": {"location": "NYC"},
             "hostedUrl": f"https://x/{i}"} for i in ids]


def ab_body(ids, unlisted=()):
    jobs = [{"id": i, "title": f"Job {i}", "isListed": True, "jobUrl": f"https://x/{i}"} for i in ids]
    jobs += [{"id": i, "title": f"Hidden {i}", "isListed": False} for i in unlisted]
    return {"jobs": jobs}


class FakeTransport:
    seeded = True

    def __init__(self, script):
        self.script = {u: list(v) for u, v in script.items()}
        self.calls = []

    def get(self, url, headers):
        self.calls.append(url)
        queue = self.script[url]
        status, body = queue.pop(0) if len(queue) > 1 else queue[0]
        if status == "timeout":
            return fetch.Response(None, b"", "timeout", 0, True)
        raw = body if isinstance(body, bytes) else json.dumps(body).encode()
        return fetch.Response(status, raw, None, 0, True)


class Clock:
    def __init__(self, step=0.0):
        self.t, self.step = 0.0, step

    def __call__(self):
        self.t += self.step
        return self.t


BOARDS = [{"name": "a", "ats": "greenhouse", "slug": "a"},
          {"name": "b", "ats": "lever", "slug": "b"},
          {"name": "c", "ats": "ashby", "slug": "c"}]


class LoopCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = self.tmp.name
        self.sleeps = []
        self.n = 0
        self.state_dir = loop.state_dir_for("seeded-t-1", seeded=True)

    def tearDown(self):
        self.tmp.cleanup()

    def go(self, script, boards=BOARDS, budgets=BUDGETS, clock=None):
        self.n += 1
        self.transport = FakeTransport(script)
        fetcher = fetch.GuardedFetcher(self.transport, sleep=self.sleeps.append)
        return loop.run(self.base, boards, budgets, fetcher, f"seeded-t-{self.n}",
                        clock=clock or Clock(), sleep=self.sleeps.append, seeded=True)

    def healthy(self, a=("1", "2"), b=("x",), c=("p",)):
        return {GH.format("a"): [(200, gh_body(a))], LV.format("b"): [(200, lv_body(b))],
                AB.format("c"): [(200, ab_body(c))]}

    def board(self, summary, name):
        return next(b for b in summary["boards"] if b["name"] == name)


class Exits(LoopCase):
    def test_finished_when_every_board_ok(self):
        s = self.go(self.healthy())
        self.assertEqual((s["exit"], s["exit_code"]), ("finished", 0))

    def test_first_run_is_baseline_second_reports_only_new(self):
        self.go(self.healthy(a=("1", "2")))
        s = self.go(self.healthy(a=("1", "2", "3")))
        a = self.board(s, "a")
        self.assertEqual((a["baseline"], a["new_ids"]), (False, ["3"]))

    def test_W2_not_found_is_null_not_zero(self):
        script = self.healthy()
        script[GH.format("a")] = [(404, {"status": 404})]
        s = self.go(script)
        a = self.board(s, "a")
        self.assertEqual((s["exit"], a["status"], a["count"]), ("incomplete", "failed:not_found", None))

    def test_W5_404_is_not_retried(self):
        script = self.healthy()
        script[GH.format("a")] = [(404, {})]
        self.go(script)
        self.assertEqual(self.transport.calls.count(GH.format("a")), 1)
        self.assertNotIn(2.0, self.sleeps)

    def test_timeout_retried_once_then_succeeds(self):
        script = self.healthy()
        script[GH.format("a")] = [("timeout", None), (200, gh_body(["1"]))]
        s = self.go(script)
        a = self.board(s, "a")
        self.assertEqual((a["status"], a["attempts"], s["exit"]), ("ok", 2, "finished"))
        self.assertIn(2.0, self.sleeps)

    def test_timeout_twice_is_unreachable_null(self):
        script = self.healthy()
        script[GH.format("a")] = [("timeout", None)]
        s = self.go(script)
        a = self.board(s, "a")
        self.assertEqual((a["status"], a["count"], a["attempts"]), ("failed:unreachable", None, 2))

    def test_bad_json_is_bad_response_not_retried(self):
        script = self.healthy()
        script[LV.format("b")] = [(200, b"<html>maintenance</html>")]
        s = self.go(script)
        b = self.board(s, "b")
        self.assertEqual((b["status"], b["count"], b["attempts"]), ("failed:bad_response", None, 1))

    def test_403_not_retried(self):
        script = self.healthy()
        script[AB.format("c")] = [(403, b"Forbidden")]
        s = self.go(script)
        self.assertEqual(self.board(s, "c")["status"], "failed:http_403")
        self.assertEqual(self.transport.calls.count(AB.format("c")), 1)

    def test_every_board_failed_is_error(self):
        s = self.go({GH.format("a"): [(404, {})], LV.format("b"): [(404, {})],
                     AB.format("c"): [(404, {})]})
        self.assertEqual((s["exit"], s["exit_code"]), ("error", 1))

    def test_W7_failed_board_keeps_its_baseline(self):
        self.go(self.healthy(a=("1", "2")))
        script = self.healthy()
        script[GH.format("a")] = [(404, {})]
        self.go(script)
        state = loop.load_state(self.base, "a", self.state_dir)
        self.assertEqual(state["ids"], ["1", "2"])
        s = self.go(self.healthy(a=("1", "2")))
        self.assertEqual(self.board(s, "a")["new_ids"], [])

    def test_invalid_config_is_error_with_no_requests(self):
        s = self.go(self.healthy(), boards=[{"name": "z", "ats": "workday", "slug": "z"}])
        self.assertEqual((s["exit"], s["requests"]), ("error", 0))


class Budgets(LoopCase):
    def test_W6_board_budget_stop_is_not_finished(self):
        s = self.go(self.healthy(), budgets={**BUDGETS, "max_boards": 2})
        self.assertEqual(s["exit"], "budget_exhausted")
        self.assertEqual(s["budget_stop"]["not_attempted"], ["c"])

    def test_request_budget_counts_retries(self):
        script = self.healthy()
        script[GH.format("a")] = [("timeout", None)]
        s = self.go(script, budgets={**BUDGETS, "max_requests": 2})
        self.assertEqual(s["exit"], "budget_exhausted")
        self.assertEqual(s["requests"], 2)
        self.assertEqual(s["budget_stop"]["budget"], "max_requests")

    def test_seconds_budget(self):
        s = self.go(self.healthy(), budgets={**BUDGETS, "max_seconds": 5}, clock=Clock(step=2.0))
        self.assertEqual((s["exit"], s["budget_stop"]["budget"]), ("budget_exhausted", "max_seconds"))

    def test_budget_stop_writes_no_state_for_unattempted(self):
        self.go(self.healthy(), budgets={**BUDGETS, "max_boards": 1})
        self.assertIsNone(loop.load_state(self.base, "b", self.state_dir))


class Repeats(LoopCase):
    def test_duplicate_board_in_config_requested_once(self):
        s = self.go(self.healthy(), boards=BOARDS + [{"name": "a2", "ats": "greenhouse", "slug": "A"}])
        self.assertEqual(self.transport.calls.count(GH.format("a")), 1)
        self.assertEqual(s["exit"], "finished")

    def test_third_identical_request_blocked(self):
        script = self.healthy()
        script[GH.format("a")] = [("timeout", None)]
        s = self.go(script, budgets={**BUDGETS, "retries_per_board": 5})
        self.assertEqual(self.transport.calls.count(GH.format("a")), 2)
        self.assertEqual(self.board(s, "a")["status"], "failed:repeat_blocked")

    def test_duplicate_posting_ids_counted_once(self):
        s = self.go(self.healthy(a=("1", "1", "2")))
        a = self.board(s, "a")
        self.assertEqual((a["count"], a["duplicate_ids"]), (2, 1))


class SeededIsolation(LoopCase):
    def test_seeded_run_never_touches_live_state(self):
        self.go(self.healthy())
        self.assertFalse(os.path.exists(os.path.join(self.base, "jobs", "state")))
        self.assertIsNotNone(loop.load_state(self.base, "a", self.state_dir))

    def test_live_and_seeded_state_dirs_differ(self):
        self.assertEqual(loop.state_dir_for("2026-11-08T00-00-00Z", seeded=False),
                         os.path.join("jobs", "state"))
        self.assertEqual(loop.state_dir_for("seeded-vanish-2", seeded=True),
                         os.path.join("jobs", "seeded-state", "seeded-vanish"))


class Parsing(LoopCase):
    def test_W8_ashby_unlisted_not_counted(self):
        script = self.healthy()
        script[AB.format("c")] = [(200, ab_body(["p", "q"], unlisted=["hidden"]))]
        s = self.go(script)
        self.assertEqual(self.board(s, "c")["count"], 2)


class PolicyInTheLoop(LoopCase):
    def test_off_list_host_ends_run_in_error_without_request(self):
        class Evil(fetch.GuardedFetcher):
            pass
        transport = FakeTransport(self.healthy())
        fetcher = Evil(transport, sleep=self.sleeps.append)
        real_url = loop.adapters.board_url
        loop.adapters.board_url = lambda ats, slug: "https://evil.example.com/jobs"
        try:
            s = loop.run(self.base, BOARDS, BUDGETS, fetcher, "seeded-evil", clock=Clock(),
                         sleep=self.sleeps.append, seeded=True)
        finally:
            loop.adapters.board_url = real_url
        self.assertEqual(s["exit"], "error")
        self.assertEqual(transport.calls, [])

    def test_all_writes_stay_in_jobs(self):
        self.go(self.healthy())
        top = sorted(os.listdir(self.base))
        self.assertEqual(top, ["jobs"])

    def test_live_fetcher_waits_between_same_host_requests(self):
        waits = []

        class Live(FakeTransport):
            seeded = False
        f = fetch.GuardedFetcher(Live({GH.format("a"): [(200, gh_body([]))]}),
                                 min_gap_s=1.0, clock=lambda: 0.0, sleep=waits.append)
        f.get(GH.format("a"))
        f.get(GH.format("a"))
        self.assertEqual(waits, [1.0])


if __name__ == "__main__":
    unittest.main()
