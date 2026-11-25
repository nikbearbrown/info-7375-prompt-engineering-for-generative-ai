"""GATE.md section 6: the wrong versions the tests must catch, W1-W19.

Written before jsagent/policy.py, net.py, providers.py, loop.py and scripts/verify_run.py existed.
scripts/sabotage_check.py plants each wrong version and shows its test going red.
"""
import json
import os
import re
import tempfile
import unittest
import urllib.request
from pathlib import Path

from tests.js2_helpers import (BIG, HOSTS, ROOT, LoopSandbox, gh_body, gh_detail_url, gh_job, gh_url, http, lever_body,
                               lever_url, load_verifier, ok, timeout)

GATE = (ROOT / "GATE.md").read_text()


class FileSandbox(unittest.TestCase):
    def setUp(self):
        from jsagent import policy
        self.policy = policy
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name).resolve()
        self.proj = base / "proj"
        self.outside = base / "outside"
        for d in [self.proj / "config", self.proj / "out", self.outside]:
            d.mkdir(parents=True)
        self.files = policy.FilePolicy(self.proj / "out", root=self.proj)

    def tearDown(self):
        self._tmp.cleanup()


class TestFileWrongVersions(FileSandbox):
    def test_W1_prefix_trick_out_evil(self):
        with self.assertRaises(self.policy.PolicyViolation):
            self.files.check_write(self.proj / "out-evil" / "x.json")

    def test_W2_symlink_escape(self):
        os.symlink(self.outside, self.proj / "out" / "link")
        with self.assertRaises(self.policy.PolicyViolation):
            self.files.check_write(self.proj / "out" / "link" / "x.json")
        with self.assertRaises(self.policy.PolicyViolation):
            self.files.check_write(self.proj / "out" / ".." / "config" / "x.json")

    def test_W11_write_config_denied(self):
        with self.assertRaises(self.policy.PolicyViolation):
            self.files.check_write(self.proj / "config" / "allowlist.json")
        self.files.check_read(self.proj / "config" / "allowlist.json")  # reading the same file is allowed

    def test_W12_overwrite_needs_approval(self):
        raw = self.proj / "out" / "runs" / "r1" / "raw" / "x.json"
        self.policy.write_new(self.files, raw, b"first")
        with self.assertRaises(self.policy.NeedsApproval):
            self.policy.write_new(self.files, raw, b"second")
        self.assertEqual(raw.read_bytes(), b"first")
        approved = self.policy.FilePolicy(self.proj / "out", root=self.proj, approvals=[raw])
        approved.check_write(raw, "overwrite")  # one named approval allows exactly this path

    def test_W16_out_root_in_protected_folder(self):
        for bad in [self.proj / "config", self.proj / "config" / "sub", self.proj / "tests", self.proj / "jsagent",
                    self.proj / "evidence", self.proj]:
            with self.subTest(out=str(bad)), self.assertRaises(self.policy.PolicyViolation):
                self.policy.FilePolicy(bad, root=self.proj)
        self.policy.FilePolicy(self.proj / "evidence" / "seeded" / "x", root=self.proj)  # a subfolder of evidence/ is fine

    def test_W16_loop_refuses_bad_out_root_before_any_fetch(self):
        from tests.js2_helpers import FakeFetcher
        from jsagent import loop
        boards = self.proj / "boards.json"
        boards.write_text(json.dumps({"boards": [{"provider": "greenhouse", "board": "alpha"}]}))
        fetcher = FakeFetcher({gh_url("alpha"): [ok(gh_body([gh_job(1)]))]})
        import io
        res = loop.run(boards_path=boards, out_root=self.proj / "config", fetcher=fetcher, root=self.proj,
                       budgets=BIG, sleep=lambda s: None, no_claude=True, stream=io.StringIO(), baselines={})
        self.assertEqual(res["code"], 3)
        self.assertEqual(fetcher.calls, [])
        self.assertEqual(sorted(p.name for p in (self.proj / "config").iterdir()), [])


class TestNetworkWrongVersions(unittest.TestCase):
    def setUp(self):
        from jsagent import policy
        self.policy = policy

    def test_W3_lookalike_host(self):
        for url in ["https://boards-api.greenhouse.io.evil.com/v1/boards/samsara/jobs",
                    "https://evil-boards-api.greenhouse.io/v1/boards/samsara/jobs",
                    "https://api.lever.co.evil.example/v0/postings/palantir?mode=json"]:
            with self.subTest(url=url), self.assertRaises(self.policy.PolicyViolation):
                self.policy.check_url(url, HOSTS)

    def test_W4_port_refused(self):
        with self.assertRaises(self.policy.PolicyViolation):
            self.policy.check_url("https://boards-api.greenhouse.io:8443/v1/boards/samsara/jobs", HOSTS)

    def test_W4_userinfo_refused(self):
        for url in ["https://user:pw@boards-api.greenhouse.io/v1/boards/samsara/jobs",
                    "https://user@api.lever.co/v0/postings/palantir?mode=json"]:
            with self.subTest(url=url), self.assertRaises(self.policy.PolicyViolation):
                self.policy.check_url(url, HOSTS)

    def test_W5_redirect_hops_count(self):
        from jsagent import net
        counted = []
        handler = net.PolicyRedirectHandler(HOSTS, 3, counted.append)
        req = urllib.request.Request(gh_url("samsara"))
        for i in range(3):
            handler.redirect_request(req, None, 302, "Found", {}, gh_url("samsara") + f"?hop={i}")
        self.assertEqual(len(counted), 3)  # every hop is charged to the request budget
        with self.assertRaises(net.RedirectLimit):
            handler.redirect_request(req, None, 302, "Found", {}, gh_url("samsara") + "?hop=4")


class TestLoopWrongVersions(unittest.TestCase):
    def setUp(self):
        self.sb = LoopSandbox()

    def tearDown(self):
        self.sb.close()

    def test_W6_failed_board_count_null(self):
        res, _ = self.sb.run([("greenhouse", "alpha")], {gh_url("alpha"): [http(404)]})
        board = res["report"]["boards"][0]
        self.assertEqual(board["status"], "failed")
        self.assertIsNone(board["count"])
        saved = json.loads((Path(res["run_dir"]) / "report.json").read_text())
        self.assertIsNone(saved["boards"][0]["count"])
        self.assertIn("unknown, not zero", res["console"])
        self.assertNotIn("no new jobs", res["console"].lower())

    def test_W7_failed_board_incomplete(self):
        entries = [("greenhouse", "alpha"), ("greenhouse", "beta"), ("lever", "gamma"), ("greenhouse", "delta")]
        script = {gh_url("alpha"): [ok(gh_body([gh_job(1)]))], gh_url("beta"): [ok(gh_body([gh_job(2)]))],
                  lever_url("gamma"): [ok(lever_body([]))], gh_url("delta"): [http(404)]}
        res, _ = self.sb.run(entries, script)
        self.assertEqual(res["status"], "incomplete")
        self.assertEqual(res["code"], 1)

    def test_W8_retries_consume_budget(self):
        res, fetcher = self.sb.run([("greenhouse", "alpha")], {gh_url("alpha"): [timeout()]})
        self.assertEqual(len(fetcher.calls), 3)  # 1 attempt + 2 retries
        self.assertEqual(res["report"]["requests_used"], 3)
        tight = dict(BIG, max_requests=2)
        res, fetcher = self.sb.run([("greenhouse", "alpha")], {gh_url("alpha"): [timeout()]}, budgets=tight)
        self.assertEqual(len(fetcher.calls), 2)
        self.assertEqual(res["status"], "budget-exhausted")

    def test_W9_no_retry_on_404(self):
        res, fetcher = self.sb.run([("greenhouse", "alpha")], {gh_url("alpha"): [http(404)]})
        self.assertEqual(len(fetcher.calls), 1)
        self.assertEqual(res["report"]["boards"][0]["attempts"], 1)

    def test_W10_trailing_slash_is_repeat(self):
        from jsagent import loop
        log = loop.ActionLog()
        self.assertTrue(log.allow("GET", gh_url("alpha")))
        self.assertFalse(log.allow("GET", gh_url("alpha") + "/"))
        self.assertFalse(log.allow("GET", "https://BOARDS-API.greenhouse.io/v1/boards/alpha/jobs"))
        self.assertTrue(log.allow("GET", gh_url("alpha"), retry=True))  # a recorded retry is the one allowed re-send

    def test_W13_failed_board_state_unchanged(self):
        first, _ = self.sb.run([("greenhouse", "alpha")], {gh_url("alpha"): [ok(gh_body([gh_job(1)]))]})
        before = self.sb.state()["boards"]["greenhouse:alpha"]
        self.sb.run([("greenhouse", "alpha")], {gh_url("alpha"): [http(404)]})
        self.assertEqual(self.sb.state()["boards"]["greenhouse:alpha"], before)

    def test_W14_unjudged_stay_new(self):
        alpha = [("greenhouse", "alpha")]
        self.sb.run(alpha, {gh_url("alpha"): [ok(gh_body([gh_job(1)]))]})  # baseline
        jobs = [gh_job(1), gh_job(2, "Data Engineer", "Remote - US"), gh_job(3, "Data Engineer", "Remote - US")]
        detail = lambda i: ok(json.dumps(gh_job(i, "Data Engineer", "Remote - US", "4+ years of experience. Python and SQL.")).encode())
        script = {gh_url("alpha"): [ok(gh_body(jobs))], gh_detail_url("alpha", 2): [detail(2)], gh_detail_url("alpha", 3): [detail(3)]}
        res, _ = self.sb.run(alpha, script, budgets=dict(BIG, max_requests=2))
        self.assertEqual(res["status"], "budget-exhausted")
        seen = set(self.sb.state()["boards"]["greenhouse:alpha"]["seen"])
        self.assertIn("2", seen)
        self.assertNotIn("3", seen)
        res, _ = self.sb.run(alpha, script)
        self.assertEqual(res["report"]["boards"][0]["new_ids"], ["3"])

    def test_W15_verifier_ignores_report_counts(self):
        verifier = load_verifier()
        alpha = [("greenhouse", "alpha")]
        self.sb.run(alpha, {gh_url("alpha"): [ok(gh_body([gh_job(1)]))]})
        res, _ = self.sb.run(alpha, {gh_url("alpha"): [ok(gh_body([gh_job(1), gh_job(2)]))]})
        good, _ = verifier.verify(Path(res["run_dir"]), ROOT)
        self.assertTrue(good)
        report_path = Path(res["run_dir"]) / "report.json"
        report = json.loads(report_path.read_text())
        report["boards"][0]["count"] = 99  # a report that lies about the count
        report_path.write_text(json.dumps(report))
        good, lines = verifier.verify(Path(res["run_dir"]), ROOT)
        self.assertFalse(good)

    def test_W19_empty_board_fails_verification(self):
        verifier = load_verifier()
        res, _ = self.sb.run([("lever", "kraken")], {lever_url("kraken"): [ok(lever_body([]))]})
        self.assertEqual(res["status"], "finished")  # the loop's own answer: finished
        good, lines = verifier.verify(Path(res["run_dir"]), ROOT)
        self.assertFalse(good)  # the independent check: empty, needs review
        self.assertTrue(any("empty" in line for line in lines))


class TestConfigMatchesGate(unittest.TestCase):
    def test_W17_allowlist_matches_gate(self):
        network = GATE.split("### Network", 1)[1].split("Compare hosts", 1)[0]
        gate_hosts = set(re.findall(r"^- `([^`]+)`", network, re.M))
        config = set(json.loads((ROOT / "config" / "allowlist.json").read_text())["hosts"])
        self.assertEqual(gate_hosts, HOSTS)
        self.assertEqual(config, gate_hosts)

    def test_W18_budgets_match_gate(self):
        def num(pattern):
            return int(re.search(pattern, GATE).group(1))
        gate = {"max_boards": num(r"Maximum boards per run: (\d+)"),
                "max_requests": num(r"Maximum HTTP requests per run: (\d+)"),
                "max_seconds": num(r"Maximum wall-clock time: (\d+) seconds"),
                "request_timeout_s": num(r"Per-request timeout: (\d+) seconds"),
                "max_redirect_hops": num(r"Maximum redirect hops per request: (\d+)"),
                "max_loop_steps": num(r"Maximum loop steps per run: (\d+)")}
        config = json.loads((ROOT / "config" / "budgets.json").read_text())
        self.assertEqual({k: config[k] for k in gate}, gate)


if __name__ == "__main__":
    unittest.main()
