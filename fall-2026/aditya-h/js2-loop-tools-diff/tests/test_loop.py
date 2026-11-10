"""Loop tests from GATE.md (exits, budgets, repeat rule, error policy, wrong versions), written before
jobwatch2/loop.py existed. All boards here are constructed fixtures; shapes copied from real responses
probed on 2026-11-09. No network access.
"""
import json
import pathlib
import re
import shutil
import tempfile
import unittest

from jobwatch2 import ats, loop
from jobwatch2.loop import BUDGETS

HERE = pathlib.Path(__file__).resolve().parents[1]


def gh(*jobs):
    return json.dumps({"jobs": [{"id": i, "title": t, "location": {"name": loc}, "offices": [{"name": off}],
                                 "first_published": "2026-11-08T10:00:00-05:00",
                                 "absolute_url": f"https://x/{i}"} for i, t, loc, off in jobs],
                       "meta": {"total": len(jobs)}}).encode()


def ashby(*jobs):
    return json.dumps({"apiVersion": "1", "jobs": [
        {"id": i, "title": t, "location": loc, "secondaryLocations": [], "isListed": True,
         "address": {"postalAddress": {"addressCountry": c}}, "publishedAt": "2026-11-08T10:00:00+00:00",
         "jobUrl": f"https://x/{i}"} for i, t, loc, c in jobs]}).encode()


def lever(*jobs):
    return json.dumps([{"id": i, "text": t, "country": c, "categories": {"location": loc, "allLocations": [loc]},
                        "createdAt": 1794152400000, "hostedUrl": f"https://x/{i}"} for i, t, loc, c in jobs]).encode()


class FakeNet:
    """Fake fetcher: url -> list of responses (status, body) or exceptions, consumed in order."""

    def __init__(self, table):
        self.table = {k: list(v) for k, v in table.items()}
        self.calls = []

    def __call__(self, url, timeout):
        self.calls.append(url)
        for key, seq in self.table.items():
            if key in url:
                item = seq.pop(0) if len(seq) > 1 else seq[0]
                if isinstance(item, Exception):
                    raise item
                return item
        return 404, b'{"status":404}'


class Clock:
    def __init__(self):
        self.t = 0.0

    def now(self):
        return self.t

    def sleep(self, s):
        self.t += s


BOARDS = [{"ats": "greenhouse", "slug": "stripe"}, {"ats": "ashby", "slug": "openai"},
          {"ats": "lever", "slug": "palantir"}]
OK = {
    "boards/stripe/jobs": [(200, gh((1, "Product Manager, Billing", "NYC", "US"), (2, "Data Scientist", "US", "US")))],
    "job-board/openai": [(200, ashby(("a1", "Product Manager, API", "San Francisco", "United States")))],
    "postings/palantir": [(200, lever(("l1", "Software Engineer", "London", "GB")))],
}


class LoopCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        (self.root / "runs").mkdir()
        shutil.copytree(HERE / "personas", self.root / "personas")
        self.clock = Clock()

    def tearDown(self):
        self.tmp.cleanup()

    def run_loop(self, boards, table, **kw):
        net = FakeNet(table)
        res = loop.run(self.root, boards, fetcher=net, now=self.clock.now, sleep=self.clock.sleep, **kw)
        return res, net

    def board(self, res, key):
        return next(b for b in res["boards"] if b["key"] == key)


class Exits(LoopCase):
    def test_all_ok_is_finished_and_first_run_is_baseline(self):
        res, _ = self.run_loop(BOARDS, OK)
        self.assertEqual(res["exit"], "finished")
        for b in res["boards"]:
            self.assertEqual(b["status"], "ok")
            self.assertTrue(b["baseline"])
            self.assertEqual(b["new"], 0)

    def test_second_run_reports_new_per_board(self):
        self.run_loop(BOARDS, OK)
        table = dict(OK)
        table["boards/stripe/jobs"] = [(200, gh((1, "Product Manager, Billing", "NYC", "US"), (2, "Data Scientist", "US", "US"),
                                               (3, "Senior Product Manager, Risk", "Seattle", "US")))]
        res, _ = self.run_loop(BOARDS, table)
        self.assertEqual(res["exit"], "finished")
        self.assertEqual(self.board(res, "greenhouse/stripe")["new"], 1)
        self.assertEqual(self.board(res, "greenhouse/stripe")["relevant"], 1)
        self.assertEqual(self.board(res, "ashby/openai")["new"], 0)

    def test_policy_violation_is_error_and_stops(self):
        boards = [{"ats": "greenhouse", "slug": "Stripe/../x"}] + BOARDS
        res, net = self.run_loop(boards, OK)
        self.assertEqual(res["exit"], "error")
        self.assertEqual(net.calls, [])
        self.assertTrue(all(b["status"] == "not-attempted" for b in res["boards"][1:]))

    def test_corrupt_state_is_error(self):
        self.run_loop(BOARDS, OK)
        (self.root / "runs" / "state" / "greenhouse__stripe.json").write_text("{oops")
        res, _ = self.run_loop(BOARDS, OK)
        self.assertEqual(res["exit"], "error")

    def test_unknown_ats_is_error(self):
        res, net = self.run_loop([{"ats": "workday", "slug": "x"}], OK)
        self.assertEqual(res["exit"], "error")
        self.assertEqual(net.calls, [])

    def test_duplicate_board_fetched_once(self):
        res, net = self.run_loop(BOARDS + [{"ats": "greenhouse", "slug": "stripe"}], OK)
        self.assertEqual(sum("boards/stripe" in c for c in net.calls), 1)
        self.assertEqual(res["boards"][-1]["status"], "skipped-duplicate")
        self.assertEqual(res["exit"], "incomplete")


class WrongVersion1_StoppedIsNotSucceeded(LoopCase):
    def test_one_404_board_makes_run_incomplete(self):
        res, _ = self.run_loop(BOARDS + [{"ats": "greenhouse", "slug": "stripe-js2-bad"}], OK)
        self.assertEqual(res["exit"], "incomplete")
        bad = self.board(res, "greenhouse/stripe-js2-bad")
        self.assertEqual(bad["status"], "failed")
        self.assertEqual(bad["http_status"], 404)

    def test_request_budget_exhausted_lists_unattempted(self):
        five = BOARDS + [{"ats": "greenhouse", "slug": "anthropic"}, {"ats": "ashby", "slug": "notion"}]
        res, net = self.run_loop(five, OK, budgets={**BUDGETS, "requests": 2})
        self.assertEqual(res["exit"], "budget-exhausted")
        self.assertEqual(len(net.calls), 2)
        self.assertEqual(res["budget_hit"], "requests")
        self.assertEqual([b["status"] for b in res["boards"]][2:], ["not-attempted"] * 3)

    def test_seconds_budget(self):
        slow = {k: v for k, v in OK.items()}
        net_clock = self.clock

        class SlowNet(FakeNet):
            def __call__(self, url, timeout):
                net_clock.t += 70
                return super().__call__(url, timeout)

        net = SlowNet(slow)
        res = loop.run(self.root, BOARDS, fetcher=net, now=self.clock.now, sleep=self.clock.sleep)
        self.assertEqual(res["exit"], "budget-exhausted")
        self.assertEqual(res["budget_hit"], "seconds")
        self.assertEqual(len(net.calls), 2)

    def test_board_budget(self):
        many = [{"ats": "greenhouse", "slug": f"b{i}"} for i in range(12)]
        table = {f"boards/b{i}/jobs": [(200, gh((i, "X", "US", "US")))] for i in range(12)}
        res, net = self.run_loop(many, table)
        self.assertEqual(res["exit"], "budget-exhausted")
        self.assertEqual(res["budget_hit"], "boards")
        self.assertEqual(len(net.calls), 10)


class WrongVersion2_NoInventedValues(LoopCase):
    def test_failed_board_counts_are_null_and_state_untouched(self):
        self.run_loop(BOARDS, OK)
        state = self.root / "runs" / "state" / "ashby__openai.json"
        before = state.read_bytes()
        table = dict(OK)
        table["job-board/openai"] = [(503, b"down"), (503, b"down")]
        res, _ = self.run_loop(BOARDS, table)
        b = self.board(res, "ashby/openai")
        self.assertEqual(b["status"], "failed")
        for k in ("fetched", "new", "relevant"):
            self.assertIsNone(b[k], k)
        self.assertEqual(state.read_bytes(), before)
        self.assertIn("ashby/openai", pathlib.Path(res["report_path"]).read_text())

    def test_suspect_empty_is_failed_not_zero(self):
        self.run_loop(BOARDS, OK)
        table = dict(OK)
        table["postings/palantir"] = [(200, b"[]")]
        res, _ = self.run_loop(BOARDS, table)
        b = self.board(res, "lever/palantir")
        self.assertEqual(b["status"], "failed")
        self.assertIn("suspect-empty", b["reason"])
        self.assertIsNone(b["new"])

    def test_bad_shape_is_failed(self):
        table = dict(OK)
        table["job-board/openai"] = [(200, b'{"jobs": "nope"}')]
        res, _ = self.run_loop(BOARDS, table)
        self.assertEqual(self.board(res, "ashby/openai")["status"], "failed")
        self.assertEqual(res["exit"], "incomplete")


class WrongVersion3_RetryOnlyTransientOnce(LoopCase):
    def count(self, net, part):
        return sum(part in c for c in net.calls)

    def test_404_requested_exactly_once(self):
        res, net = self.run_loop([{"ats": "greenhouse", "slug": "stripe-js2-bad"}], OK)
        self.assertEqual(self.count(net, "stripe-js2-bad"), 1)

    def test_bad_json_not_retried(self):
        table = dict(OK)
        table["postings/palantir"] = [(200, b"<html>")]
        res, net = self.run_loop(BOARDS, table)
        self.assertEqual(self.count(net, "postings/palantir"), 1)

    def test_timeout_retried_exactly_once_then_fails(self):
        table = dict(OK)
        table["boards/stripe/jobs"] = [TimeoutError("t"), TimeoutError("t"), TimeoutError("t")]
        res, net = self.run_loop(BOARDS, table)
        self.assertEqual(self.count(net, "boards/stripe"), 2)
        self.assertEqual(self.board(res, "greenhouse/stripe")["attempts"], 2)
        self.assertEqual(self.board(res, "greenhouse/stripe")["status"], "failed")

    def test_timeout_then_success_is_ok(self):
        table = dict(OK)
        table["boards/stripe/jobs"] = [TimeoutError("t"), OK["boards/stripe/jobs"][0]]
        res, net = self.run_loop(BOARDS, table)
        self.assertEqual(self.board(res, "greenhouse/stripe")["status"], "ok")
        self.assertEqual(res["exit"], "finished")
        self.assertEqual(res["budget_used"]["requests"], 4)

    def test_request_counter_matches_trace(self):
        table = dict(OK)
        table["boards/stripe/jobs"] = [TimeoutError("t"), OK["boards/stripe/jobs"][0]]
        res, net = self.run_loop(BOARDS, table)
        trace = [json.loads(l) for l in pathlib.Path(res["trace_path"]).read_text().splitlines()]
        sent = [t for t in trace if t["step"] == "request" and t["decision"] == "allow"]
        self.assertEqual(len(sent), res["budget_used"]["requests"])
        self.assertEqual(len(sent), len(net.calls))


class TraceAndRecords(LoopCase):
    def test_every_board_observed_and_raw_saved(self):
        res, _ = self.run_loop(BOARDS + [{"ats": "greenhouse", "slug": "stripe-js2-bad"}], OK)
        trace = [json.loads(l) for l in pathlib.Path(res["trace_path"]).read_text().splitlines()]
        observed = {t["board"] for t in trace if t["step"] == "observation"}
        self.assertEqual(observed, {b["key"] for b in res["boards"]})
        for b in res["boards"]:
            self.assertTrue((pathlib.Path(res["run_dir"]) / b["raw_path"]).exists(), b["key"])

    def test_ids_namespaced_per_board(self):
        res, _ = self.run_loop(BOARDS, OK)
        st = json.loads((self.root / "runs" / "state" / "ashby__openai.json").read_text())
        self.assertEqual(st["seen_ids"], ["ashby/openai:a1"])

    def test_reset_needs_approval(self):
        self.run_loop(BOARDS, OK)
        with self.assertRaises(loop.PolicyError):
            loop.reset_board(self.root, "greenhouse/stripe", approvals=())
        loop.reset_board(self.root, "greenhouse/stripe", approvals=("greenhouse/stripe",))
        self.assertFalse((self.root / "runs" / "state" / "greenhouse__stripe.json").exists())


class BudgetsMatchGate(unittest.TestCase):
    def test_code_budgets_equal_latest_gate_entry(self):
        text = (HERE / "GATE.md").read_text()
        section = text.split("### Budget changes", 1)[1]
        last = re.findall(r"boards (\d+), requests (\d+), seconds (\d+)", section)[-1]
        self.assertEqual((BUDGETS["boards"], BUDGETS["requests"], BUDGETS["seconds"]), tuple(map(int, last)))


class Normalization(unittest.TestCase):
    def test_three_ats_normalize_and_judge(self):
        g = ats.parse("greenhouse", gh((1, "Product Manager, X", "N/A", "US")))
        a = ats.parse("ashby", ashby(("a", "Product Manager, Y", "Toronto", "Canada")))
        l = ats.parse("lever", lever(("l", "Product Analyst", "New York, NY", "US")))
        self.assertEqual((g[0]["title"], g[0]["us_office"]), ("Product Manager, X", True))
        self.assertEqual((a[0]["us_office"], a[0]["location_name"]), (False, "Toronto"))
        self.assertTrue(l[0]["us_office"])

    def test_shape_errors(self):
        for name, raw in (("greenhouse", b"[]"), ("ashby", b'{"x":1}'), ("lever", b'{"jobs":[]}')):
            with self.subTest(name=name), self.assertRaises(ats.ShapeError):
                ats.parse(name, raw)


if __name__ == "__main__":
    unittest.main()
