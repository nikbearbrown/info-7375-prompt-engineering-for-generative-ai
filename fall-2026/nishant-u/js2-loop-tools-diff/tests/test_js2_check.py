"""The outcome check reads only the saved raw responses, never the agent's report.
Every raw response here is CONSTRUCTED (labeled "_constructed" or written by the test)."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tests import helpers, js2_helpers as h


def save_raw(run_dir, step, system, board, status, body, company=None):
    """Write one raw response and its sidecar the way GATE.md's run folder records them."""
    raw = Path(run_dir) / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    name = f"{step:02d}-{system}-{board}.body"
    (raw / name).write_bytes(body)
    meta = {"step": step, "system": system, "board": board, "company": company or board,
            "url": (h.GH if system == "greenhouse" else h.ASHBY).format(board), "http_status": status,
            "file": name, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()}
    (raw / f"{step:02d}-{system}-{board}.meta.json").write_text(json.dumps(meta), encoding="utf-8")


class OutcomeCheck(helpers.ContractTest):
    modules = ("agent2.check",)

    def setUp(self):
        super().setUp()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_dir = Path(self.tmp.name)

    def kinds(self, result):
        return sorted((f["kind"], f.get("board") or f.get("company")) for f in result["flags"])

    def test_zero_posting_board_is_flagged(self):
        save_raw(self.run_dir, 1, "greenhouse", "faire", 200, h.gh_body([h.gh_job(1)]))
        save_raw(self.run_dir, 2, "greenhouse", "instacart", 200, b'{"jobs":[],"meta":{"total":0}}')
        self.assertEqual(self.kinds(self.check.check_run(self.run_dir)),
                         [("zero-postings", "greenhouse:instacart")])

    def test_poshmark_zero_on_greenhouse_vs_22_on_ashby_is_flagged(self):
        save_raw(self.run_dir, 3, "ashby", "poshmark", 200, h.ashby_body([h.ashby_job(n) for n in range(1, 23)]))
        save_raw(self.run_dir, 4, "greenhouse", "poshmark", 200, b'{"jobs":[],"meta":{"total":0}}')
        result = self.check.check_run(self.run_dir)
        self.assertEqual(self.kinds(result), [("cross-system", "poshmark"), ("zero-postings", "greenhouse:poshmark")])
        cross = next(f for f in result["flags"] if f["kind"] == "cross-system")
        self.assertEqual(cross["counts"], {"ashby": 22, "greenhouse": 0})

    def test_healthy_boards_raise_no_flag(self):
        save_raw(self.run_dir, 1, "greenhouse", "faire", 200, h.gh_body([h.gh_job(1)]))
        save_raw(self.run_dir, 2, "ashby", "poshmark", 200, h.ashby_body([h.ashby_job(1)]))
        self.assertEqual(self.check.check_run(self.run_dir)["flags"], [])

    def test_ignores_the_agents_report(self):
        save_raw(self.run_dir, 1, "greenhouse", "poshmark", 200, b'{"jobs":[],"meta":{"total":0}}')
        (self.run_dir / "report.json").write_text(json.dumps({"exit": "finished", "flags": []}), encoding="utf-8")
        (self.run_dir / "trace.jsonl").write_text("not json at all\n", encoding="utf-8")
        self.assertEqual(self.kinds(self.check.check_run(self.run_dir)), [("zero-postings", "greenhouse:poshmark")])

    def test_tampered_body_is_flagged(self):
        save_raw(self.run_dir, 1, "greenhouse", "faire", 200, h.gh_body([h.gh_job(1)]))
        (self.run_dir / "raw" / "01-greenhouse-faire.body").write_bytes(h.gh_body([h.gh_job(1), h.gh_job(2)]))
        self.assertIn(("sha256-mismatch", "greenhouse:faire"), self.kinds(self.check.check_run(self.run_dir)))

    def test_failed_response_is_not_counted_as_zero(self):
        save_raw(self.run_dir, 5, "greenhouse", "no-such-board-js2-test", 404, h.NOT_FOUND)
        result = self.check.check_run(self.run_dir)
        self.assertEqual(result["flags"], [])
        board = result["boards"][0]
        self.assertIsNone(board["postings"])


class FinishedWrongAnswer(helpers.ContractTest):
    """The demo profile, on CONSTRUCTED responses: the loop ends `finished`, the check disagrees."""
    modules = ("agent2.loop", "agent2.policy", "agent2.check")

    def test_demo_finishes_and_the_check_flags_poshmark(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            clock = h.FakeClock()
            report = self.loop.Loop(self.loop.PROFILES["demo"], policy=self.policy.Policy(out),
                                    client=h.FakeClient(h.ok_responses()), clock=clock, sleep=clock.sleep).run()
            self.assertEqual(report["exit"], "finished")
            gh_posh = next(b for b in report["boards"] if (b["system"], b["board"]) == ("greenhouse", "poshmark"))
            self.assertEqual((gh_posh["status"], gh_posh["postings"]), ("parsed", 0))
            result = self.check.check_run(out / "runs" / report["run"])
            self.assertIn("cross-system", [f["kind"] for f in result["flags"]])


if __name__ == "__main__":
    unittest.main()
