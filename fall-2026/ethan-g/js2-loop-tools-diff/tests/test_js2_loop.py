"""JS2 loop behavior from GATE.md sections 1-4 and the run plan. Written before jsagent/loop.py existed. No network."""
import io
import json
import unittest
from pathlib import Path

from tests.js2_helpers import (BIG, ROOT, FakeFetcher, LoopSandbox, gh_body, gh_detail_url, gh_job, gh_url, http, lever_body,
                               lever_posting, lever_url, load_verifier, ok, timeout)

BASELINE_RAW = ROOT / "baseline" / "2026-10-31" / "samsara.json"
BASELINE_IDS = ROOT / "baseline" / "2026-10-31" / "seen_ids.json"


class TestLoop(unittest.TestCase):
    def setUp(self):
        self.sb = LoopSandbox()

    def tearDown(self):
        self.sb.close()

    def test_all_ok_is_finished_and_first_run_is_a_baseline(self):
        entries = [("greenhouse", "alpha"), ("lever", "beta")]
        script = {gh_url("alpha"): [ok(gh_body([gh_job(1), gh_job(2)]))],
                  lever_url("beta"): [ok(lever_body([lever_posting("b-1")]))]}
        res, _ = self.sb.run(entries, script)
        self.assertEqual((res["status"], res["code"]), ("finished", 0))
        for board in res["report"]["boards"]:
            self.assertTrue(board["baseline"])
            self.assertEqual(board["new_ids"], [])
        good, lines = load_verifier().verify(Path(res["run_dir"]), ROOT)
        self.assertTrue(good)
        self.assertIn("no history", lines[-1])

    def test_second_run_reports_new_and_judges_data_titles(self):
        alpha = [("greenhouse", "alpha")]
        self.sb.run(alpha, {gh_url("alpha"): [ok(gh_body([gh_job(1)]))]})
        jobs = [gh_job(1), gh_job(2, "Data Engineer", "Remote - US"), gh_job(3, "Recruiter")]
        detail = ok(json.dumps(gh_job(2, "Data Engineer", "Remote - US", "4+ years of experience with Python and Airflow.")).encode())
        res, fetcher = self.sb.run(alpha, {gh_url("alpha"): [ok(gh_body(jobs))], gh_detail_url("alpha", 2): [detail]})
        board = res["report"]["boards"][0]
        self.assertEqual(sorted(board["new_ids"]), ["2", "3"])
        self.assertEqual([j["id"] for j in board["new_judged"]], ["2"])
        self.assertEqual(board["new_judged"][0]["rule_verdict"], "relevant")
        self.assertEqual(board["new_other_ids"], ["3"])
        self.assertEqual(res["status"], "finished")
        self.assertTrue(load_verifier().verify(Path(res["run_dir"]), ROOT)[0])

    def test_lever_needs_no_detail_request(self):
        beta = [("lever", "beta")]
        self.sb.run(beta, {lever_url("beta"): [ok(lever_body([lever_posting("a")]))]})
        new = lever_posting("b", "Data Engineer", "Remote - US", "3+ years of experience with SQL and dbt.")
        res, fetcher = self.sb.run(beta, {lever_url("beta"): [ok(lever_body([lever_posting("a"), new]))]})
        self.assertEqual(fetcher.calls, [lever_url("beta")])
        self.assertEqual(res["report"]["boards"][0]["new_judged"][0]["id"], "b")

    def test_wrong_shape_fails_without_retry(self):
        cases = [(("lever", "beta"), lever_url("beta"), ok(b'{"jobs": []}')),
                 (("greenhouse", "alpha"), gh_url("alpha"), ok(b"[]")),
                 (("greenhouse", "alpha"), gh_url("alpha"), ok(b"")),
                 (("greenhouse", "alpha"), gh_url("alpha"), ok(b"<html>not json</html>"))]
        for entry, url, resp in cases:
            with self.subTest(entry=entry, body=resp.body):
                res, fetcher = self.sb.run([entry], {url: [resp]})
                self.assertEqual(len(fetcher.calls), 1)
                self.assertEqual(res["report"]["boards"][0]["status"], "failed")
                self.assertIsNone(res["report"]["boards"][0]["count"])

    def test_transient_then_success(self):
        res, fetcher = self.sb.run([("greenhouse", "alpha")], {gh_url("alpha"): [http(503), ok(gh_body([gh_job(1)]))]})
        self.assertEqual(len(fetcher.calls), 2)
        self.assertEqual(res["status"], "finished")

    def test_http_500_retried_once_429_with_long_wait_not_retried(self):
        res, fetcher = self.sb.run([("greenhouse", "alpha")], {gh_url("alpha"): [http(500)]})
        self.assertEqual(len(fetcher.calls), 2)
        res, fetcher = self.sb.run([("greenhouse", "alpha")], {gh_url("alpha"): [http(429, retry_after=60)]})
        self.assertEqual(len(fetcher.calls), 1)
        res, fetcher = self.sb.run([("greenhouse", "alpha")], {gh_url("alpha"): [http(429, retry_after=1), ok(gh_body([]))]})
        self.assertEqual(len(fetcher.calls), 2)

    def test_duplicate_boards_removed_before_loop(self):
        res, fetcher = self.sb.run([("greenhouse", "alpha"), ("greenhouse", "alpha")], {gh_url("alpha"): [ok(gh_body([gh_job(1)]))]})
        self.assertEqual(len(fetcher.calls), 1)
        self.assertEqual(res["report"]["duplicates_removed"], ["greenhouse:alpha"])

    def test_preflight_errors_before_any_fetch(self):
        for entries in [[], [("ashby", "kraken")], [("greenhouse", "Bad Name")], [("greenhouse", f"b{i}") for i in range(13)]]:
            with self.subTest(entries=entries):
                res, fetcher = self.sb.run(entries, {})
                self.assertEqual((res["status"], res["code"]), ("error", 3))
                self.assertEqual(fetcher.calls, [])

    def test_trace_has_a_line_per_request_with_required_fields(self):
        res, fetcher = self.sb.run([("greenhouse", "alpha")], {gh_url("alpha"): [timeout(), ok(gh_body([gh_job(1)]))]})
        lines = [json.loads(x) for x in (Path(res["run_dir"]) / "trace.jsonl").read_text().splitlines()]
        requests = [x for x in lines if x["action"] in ("list", "detail")]
        self.assertEqual(len(requests), len(fetcher.calls))
        for field in ["step", "time", "action", "url", "decision", "rule", "attempt", "http_status", "raw_path", "raw_sha256",
                      "budget_left", "outcome"]:
            self.assertIn(field, requests[0])
        self.assertEqual([x["attempt"] for x in requests], [1, 2])

    def test_raw_saved_even_when_unparseable(self):
        res, _ = self.sb.run([("greenhouse", "alpha")], {gh_url("alpha"): [ok(b"<html>oops</html>")]})
        raw = Path(res["run_dir"]) / res["report"]["boards"][0]["raw_paths"][0]
        self.assertEqual(raw.read_bytes(), b"<html>oops</html>")

    def test_reset_state_needs_approval(self):
        alpha = [("greenhouse", "alpha")]
        self.sb.run(alpha, {gh_url("alpha"): [ok(gh_body([gh_job(1)]))]})
        # Corrected after the first build run: the original assertion compared last_run, which the gate expects to change
        # (the run still updates boards it observed). What matters is that the refused reset did not happen.
        res, _ = self.sb.run(alpha, {gh_url("alpha"): [ok(gh_body([gh_job(1), gh_job(2)]))]}, reset_state=True)
        self.assertEqual(res["status"], "incomplete")
        self.assertTrue(res["report"]["approvals_refused"])
        board = res["report"]["boards"][0]
        self.assertEqual(board["history"], "state")  # compared with the old state: not reset
        self.assertEqual(board["new_ids"], ["2"])     # a reset would have baselined it and reported nothing
        self.assertEqual(self.sb.state()["boards"]["greenhouse:alpha"]["seen"], ["1", "2"])

    def test_samsara_first_run_compares_with_the_oct31_baseline(self):
        jobs = json.loads(BASELINE_RAW.read_bytes())["jobs"] + [gh_job(99999999, "Recruiter")]
        res, _ = self.sb.run([("greenhouse", "samsara")], {gh_url("samsara"): [ok(gh_body(jobs))]},
                             baselines={"greenhouse:samsara": BASELINE_IDS})
        board = res["report"]["boards"][0]
        self.assertFalse(board["baseline"])
        self.assertEqual(board["history"], "baseline 2026-10-31")
        self.assertEqual(board["new_ids"], ["99999999"])

    def test_seeded_empty_samsara_finishes_but_verifier_fails(self):
        from jsagent import net, policy
        files = policy.FilePolicy(self.sb.out, root=ROOT)
        fetcher = net.ReplayFetcher({gh_url("samsara"): ROOT / "tests" / "fixtures" / "seeded" / "empty-samsara.json"}, files,
                                    {"boards-api.greenhouse.io", "api.lever.co"})
        res, _ = self.sb.run([("greenhouse", "samsara")], {}, fetcher=fetcher, seeded="test: empty Samsara",
                             baselines={"greenhouse:samsara": BASELINE_IDS})
        self.assertEqual(res["status"], "finished")
        self.assertEqual(res["report"]["source"], "seeded")
        self.assertEqual(res["report"]["boards"][0]["new_ids"], [])
        good, lines = load_verifier().verify(Path(res["run_dir"]), ROOT)
        self.assertFalse(good)
        text = "\n".join(lines)
        self.assertIn("empty", text)
        self.assertIn("323", text)

    def test_replay_without_seeded_label_is_refused(self):
        from jsagent import loop
        with self.assertRaises(SystemExit):
            loop.main(["--boards", "config/boards_seeded.json", "--out", str(self.sb.out),
                       "--replay", "greenhouse:samsara=tests/fixtures/seeded/empty-samsara.json", "--no-claude"])

    def test_exit_precedence(self):
        from jsagent import loop
        failed = {"key": "a", "status": "failed", "reason": "HTTP 404", "new_unjudged": [], "detail_failures": []}
        okay = {"key": "b", "status": "ok", "reason": "observed", "new_unjudged": [], "detail_failures": []}
        self.assertEqual(loop.compute_exit([okay])[0], "finished")
        self.assertEqual(loop.compute_exit([okay, failed])[0], "incomplete")
        self.assertEqual(loop.compute_exit([okay, failed], budget_reason="requests")[0], "budget-exhausted")
        self.assertEqual(loop.compute_exit([okay, failed], budget_reason="requests", error_reason="policy")[0], "error")
        status, reasons = loop.compute_exit([okay, failed], budget_reason="requests")
        self.assertTrue(any("404" in r for r in reasons))  # every individual reason is kept


if __name__ == "__main__":
    unittest.main()
