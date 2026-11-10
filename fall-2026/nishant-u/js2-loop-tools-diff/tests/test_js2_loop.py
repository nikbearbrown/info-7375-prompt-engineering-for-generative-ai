"""The loop against GATE.md: exits, budgets, error policy, repeat rule, records. Fakes only, no network."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tests import helpers, js2_helpers as h


class LoopTest(helpers.ContractTest):
    modules = ("agent2.loop", "agent2.policy", "agent2.providers")

    def setUp(self):
        super().setUp()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / "out"
        self.clock = h.FakeClock()

    def run_loop(self, boards, responses, budgets=None, advance=0.0, loop_class=None):
        self.client = h.FakeClient(responses, clock=self.clock, advance=advance)
        cls = loop_class or self.loop.Loop
        return cls(boards, policy=self.policy.Policy(self.out), client=self.client,
                   clock=self.clock, sleep=self.clock.sleep, budgets=budgets).run()

    def profile(self, name):
        return self.loop.PROFILES[name]

    def entry(self, report, system, board):
        return next(b for b in report["boards"] if (b["system"], b["board"]) == (system, board))

    def run_dir(self, report):
        return self.out / "runs" / report["run"]


class Profiles(LoopTest):
    def test_profiles_are_the_gate_boards(self):
        full = [(b["system"], b["board"], b["url"]) for b in self.profile("full")]
        self.assertEqual(full, [("greenhouse", "faire", h.URLS["faire"]),
                                ("greenhouse", "instacart", h.URLS["instacart"]),
                                ("ashby", "poshmark", h.URLS["ashby_poshmark"]),
                                ("greenhouse", "poshmark", h.URLS["gh_poshmark"]),
                                ("greenhouse", "no-such-board-js2-test", h.URLS["bad"])])
        self.assertEqual(self.profile("demo"), self.profile("full")[:4])

    def test_default_budgets(self):
        self.assertEqual(self.loop.DEFAULT_BUDGETS, {"boards": 5, "requests": 10, "seconds": 60})


class Exits(LoopTest):
    def test_finished_when_every_board_parsed(self):
        report = self.run_loop(self.profile("demo"), h.ok_responses())
        self.assertEqual(report["exit"], "finished")
        self.assertEqual(report["used"]["requests"], 4)

    def test_incomplete_with_a_404_board(self):
        report = self.run_loop(self.profile("full"), h.ok_responses())
        self.assertEqual(report["exit"], "incomplete")
        bad = self.entry(report, "greenhouse", "no-such-board-js2-test")
        self.assertEqual((bad["status"], bad["reason"], bad["http_status"]), ("failed", "not-found", 404))

    def test_budget_exhausted_by_requests(self):
        report = self.run_loop(self.profile("demo"), h.ok_responses(), budgets={"requests": 3})
        self.assertEqual(report["exit"], "budget-exhausted")
        self.assertEqual(len(self.client.calls), 3)
        self.assertEqual(report["not_attempted"], ["greenhouse:poshmark"])

    def test_budget_exhausted_by_boards(self):
        six = self.profile("full") + [h.board("greenhouse", "stitchfix")]
        responses = dict(h.ok_responses(), **{six[-1]["url"]: [(200, h.gh_body([]))]})
        report = self.run_loop(six, responses, budgets={"requests": 20})
        self.assertEqual(report["exit"], "budget-exhausted")
        self.assertEqual(report["not_attempted"], ["greenhouse:stitchfix"])
        self.assertNotIn(six[-1]["url"], self.client.calls)

    def test_budget_exhausted_by_seconds_on_a_fake_clock(self):
        report = self.run_loop(self.profile("demo"), h.ok_responses(), advance=25.0)
        # requests start at t=0, 25 and 50; at t=75 the 60-second budget is spent
        self.assertEqual(report["exit"], "budget-exhausted")
        self.assertEqual(len(self.client.calls), 3)
        self.assertEqual(report["not_attempted"], ["greenhouse:poshmark"])
        self.assertGreaterEqual(report["used"]["seconds"], 60)

    def test_error_on_bad_config_leaves_state_untouched(self):
        state = self.out / "state" / "seen_ids.json"
        state.parent.mkdir(parents=True)
        state.write_bytes(b'{"seen_ids": ["greenhouse:faire:1"]}\n')
        for boards, budgets in [(self.profile("demo"), {"requests": 0}),
                                (self.profile("demo"), {"seconds": "60"}),
                                (self.profile("demo"), {"boards": True}),
                                ([h.board("lever", "gopuff")], None),
                                ([], None)]:
            with self.subTest(boards=[b["system"] for b in boards], budgets=budgets):
                report = self.run_loop(boards, h.ok_responses(), budgets=budgets)
                self.assertEqual(report["exit"], "error")
                self.assertEqual(self.client.calls, [])
                self.assertEqual(state.read_bytes(), b'{"seen_ids": ["greenhouse:faire:1"]}\n')

    def test_unexpected_exception_is_error_and_state_untouched(self):
        def broken_judge(postings):
            raise RuntimeError("judge exploded")
        self.run_loop(self.profile("demo"), h.ok_responses())  # baseline writes state
        state = self.out / "state" / "seen_ids.json"
        before = state.read_bytes()
        responses = h.ok_responses()
        responses[h.URLS["faire"]] = [(200, h.gh_body([h.gh_job(1), h.gh_job(2), h.gh_job(99)]))]
        client = h.FakeClient(responses)
        report = self.loop.Loop(self.profile("demo"), policy=self.policy.Policy(self.out), client=client,
                                clock=self.clock, sleep=self.clock.sleep, judge=broken_judge).run()
        self.assertEqual(report["exit"], "error")
        self.assertIn("judge exploded", report["error"])
        self.assertEqual(state.read_bytes(), before)


class ErrorPolicy(LoopTest):
    def one(self, items, system="greenhouse", name="faire"):
        b = h.board(system, name)
        return self.run_loop([b], {b["url"]: items}), b

    def test_404_and_410_no_retry(self):
        for code in (404, 410):
            with self.subTest(code=code):
                self.clock.sleeps.clear()
                report, b = self.one([(code, b"gone")])
                self.assertEqual(self.client.calls, [b["url"]])
                self.assertEqual(self.clock.sleeps, [])
                self.assertEqual(self.entry(report, "greenhouse", "faire")["reason"], "not-found")
                self.assertEqual(report["exit"], "incomplete")

    def test_5xx_retried_once_after_2s_then_parsed(self):
        report, b = self.one([(503, b"busy"), (200, h.gh_body([h.gh_job(1)]))])
        self.assertEqual(self.client.calls, [b["url"], b["url"]])
        self.assertEqual(self.clock.sleeps, [2])
        self.assertEqual(report["used"]["requests"], 2, "the retry counts against the request budget")
        self.assertEqual(report["exit"], "finished")

    def test_5xx_twice_fails_after_exactly_one_retry(self):
        report, b = self.one([(500, b"err")])
        self.assertEqual(len(self.client.calls), 2)
        self.assertEqual(self.clock.sleeps, [2])
        e = self.entry(report, "greenhouse", "faire")
        self.assertEqual((e["status"], e["reason"]), ("failed", "server-error"))

    def test_timeout_twice_fails_after_exactly_one_retry(self):
        report, b = self.one([self.providers.Transient("timeout")])
        self.assertEqual(len(self.client.calls), 2)
        self.assertEqual(self.clock.sleeps, [2])
        self.assertEqual(self.entry(report, "greenhouse", "faire")["reason"], "timeout")
        self.assertEqual(report["used"]["requests"], 2)

    def test_connection_error_then_success(self):
        report, b = self.one([self.providers.Transient("connection-error"), (200, h.gh_body([]))])
        self.assertEqual(len(self.client.calls), 2)
        self.assertEqual(self.entry(report, "greenhouse", "faire")["status"], "parsed")

    def test_invalid_json_or_wrong_shape_no_retry(self):
        for body in (b"<html>oops</html>", b'{"jobs": "x"}', b"{}"):
            with self.subTest(body=body):
                self.clock.sleeps.clear()
                report, b = self.one([(200, body)])
                self.assertEqual(len(self.client.calls), 1)
                self.assertEqual(self.clock.sleeps, [])
                self.assertEqual(self.entry(report, "greenhouse", "faire")["reason"], "bad-response")

    def test_failed_board_never_reported_as_zero_new(self):
        report = self.run_loop(self.profile("full"), h.ok_responses())
        bad = self.entry(report, "greenhouse", "no-such-board-js2-test")
        self.assertIsNone(bad["new_ids"])
        self.assertIsNone(bad["postings"])
        md = (self.run_dir(report) / "report.md").read_text(encoding="utf-8")
        line = next(l for l in md.splitlines() if "no-such-board-js2-test" in l and "failed" in l)
        self.assertNotIn("0 new", line)

    def test_retry_denied_by_request_budget(self):
        b = h.board("greenhouse", "faire")
        report = self.run_loop([b], {b["url"]: [(500, b"err")]}, budgets={"requests": 1})
        self.assertEqual(len(self.client.calls), 1)
        self.assertEqual(report["exit"], "budget-exhausted")
        self.assertIsNone(self.entry(report, "greenhouse", "faire")["new_ids"])

    def test_policy_refused_host_is_never_requested(self):
        lever = {"system": "greenhouse", "board": "x", "company": "x", "url": "https://api.lever.co/v0/postings/x"}
        report = self.run_loop([lever, h.board("greenhouse", "faire")], h.ok_responses())
        self.assertNotIn(lever["url"], self.client.calls)
        self.assertEqual(self.entry(report, "greenhouse", "x")["reason"], "refused")
        self.assertEqual(report["exit"], "incomplete")


class RepeatRule(LoopTest):
    def test_identical_request_refused_and_traced(self):
        b = h.board("greenhouse", "faire")
        report = self.run_loop([b, dict(b)], {b["url"]: [(200, h.gh_body([]))]})
        self.assertEqual(self.client.calls, [b["url"]])
        refusals = [t for t in report["trace"] if t["decision"] == "refused: repeat"]
        self.assertEqual(len(refusals), 1)
        self.assertEqual(report["exit"], "incomplete")

    def test_error_policy_retry_is_allowed_and_counted(self):
        b = h.board("greenhouse", "faire")
        report = self.run_loop([b], {b["url"]: [(502, b""), (200, h.gh_body([]))]})
        actions = [t["action"] for t in report["trace"] if t["action"] in ("fetch", "retry")]
        self.assertEqual(actions, ["fetch", "retry"])
        self.assertEqual(report["trace"][-1]["requests_used"], 2)


class Records(LoopTest):
    def test_raw_responses_saved_verbatim_with_sha256(self):
        report = self.run_loop(self.profile("full"), h.ok_responses())
        raw = self.run_dir(report) / "raw"
        metas = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(raw.glob("*.meta.json"))]
        self.assertEqual(len(metas), 5)
        for meta in metas:
            body = (raw / meta["file"]).read_bytes()
            self.assertEqual(meta["sha256"], hashlib.sha256(body).hexdigest())
            self.assertEqual(meta["bytes"], len(body))
        bad = next(m for m in metas if m["board"] == "no-such-board-js2-test")
        self.assertEqual((raw / bad["file"]).read_bytes(), h.NOT_FOUND)
        self.assertEqual(bad["http_status"], 404)

    def test_trace_jsonl_one_line_per_observation(self):
        report = self.run_loop(self.profile("full"), h.ok_responses())
        lines = (self.run_dir(report) / "trace.jsonl").read_text(encoding="utf-8").splitlines()
        trace = [json.loads(l) for l in lines]
        self.assertEqual(trace, report["trace"])
        keys = {"step", "action", "host", "path", "http_status", "bytes", "sha256", "decision",
                "requests_used", "boards_attempted", "seconds_used"}
        fetches = [t for t in trace if t["action"] == "fetch"]
        self.assertEqual(len(fetches), 5)
        for t in trace:
            self.assertLessEqual(keys, set(t))
        self.assertEqual([t["step"] for t in trace], list(range(1, len(trace) + 1)))

    def test_report_contents(self):
        report = self.run_loop(self.profile("full"), h.ok_responses())
        saved = json.loads((self.run_dir(report) / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["exit"], "incomplete")
        for key in ("exit", "boards", "used", "budgets", "trace", "new_ids"):
            self.assertIn(key, saved)
        self.assertTrue((self.run_dir(report) / "report.md").exists())

    def test_baseline_then_only_new_ids(self):
        first = self.run_loop(self.profile("demo"), h.ok_responses())
        self.assertTrue(all(b["baseline"] and b["new_ids"] == [] for b in first["boards"]))
        responses = h.ok_responses()
        relevant = helpers.posting(9000000008)
        responses[h.URLS["faire"]] = [(200, h.gh_body([h.gh_job(1), h.gh_job(2), relevant]))]
        second = self.run_loop(self.profile("demo"), responses)
        faire = self.entry(second, "greenhouse", "faire")
        self.assertEqual((faire["baseline"], faire["new_ids"]), (False, ["greenhouse:faire:9000000008"]))
        self.assertEqual(self.entry(second, "greenhouse", "instacart")["new_ids"], [])
        verdicts = second["rule_verdicts"]
        self.assertEqual([(v["posting_id"], v["verdict"]) for v in verdicts],
                         [("greenhouse:faire:9000000008", "relevant")])
        state = json.loads((self.out / "state" / "seen_ids.json").read_text(encoding="utf-8"))
        self.assertIn("greenhouse:faire:9000000008", state["seen_ids"])
        self.assertIn("ashby:poshmark:00000000-0000-0000-0000-000000000001", state["seen_ids"])

    def test_failed_board_ids_not_written_and_old_ids_kept(self):
        self.run_loop(self.profile("demo"), h.ok_responses())
        responses = h.ok_responses()
        responses[h.URLS["faire"]] = [(404, h.NOT_FOUND)]
        self.run_loop(self.profile("demo"), responses)
        state = json.loads((self.out / "state" / "seen_ids.json").read_text(encoding="utf-8"))
        self.assertIn("greenhouse:faire:1", state["seen_ids"], "a failed board must not drop its old ids")


if __name__ == "__main__":
    unittest.main()
