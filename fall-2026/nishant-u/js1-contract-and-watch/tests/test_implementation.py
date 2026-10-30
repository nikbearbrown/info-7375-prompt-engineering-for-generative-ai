"""Behaviour specified for the implementation step rather than by CONTRACT.md.

Added with the implementation commit, not before it: raw responses saved verbatim
with a sha256, replay without network, the seeded label, and "Claude judge: not run".
"""
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests import helpers


class RunEvidence(helpers.ContractTest):
    modules = ("agent.run", "agent.watch", "agent.resume")

    def run_agent(self, tmp, *extra):
        return self.run.main([*extra,
                              "--state", str(Path(tmp) / "state" / "seen_ids.json"),
                              "--runs", str(Path(tmp) / "runs")])

    def test_raw_saved_verbatim_with_sha256(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = helpers.write_board(Path(tmp) / "board.json", helpers.postings())
            report = self.run_agent(tmp, "--replay", str(board))
            raw = Path(tmp) / "runs" / report["run"] / "raw.json"
            self.assertEqual(raw.read_bytes(), board.read_bytes())
            self.assertEqual(report["raw"]["sha256"], hashlib.sha256(board.read_bytes()).hexdigest())
            for name in ("report.json", "report.md", "meta.json"):
                self.assertTrue((raw.parent / name).exists(), name)

    def test_replay_makes_no_network_call_and_is_labeled(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = helpers.write_board(Path(tmp) / "board.json", helpers.postings())
            with mock.patch.object(self.watch, "fetch", side_effect=AssertionError("network used")):
                replay = self.run_agent(tmp, "--replay", str(board))
                seeded = self.run_agent(tmp, "--replay", str(board), "--seeded")
            self.assertEqual(replay["raw"]["mode"], "replay")
            self.assertEqual(seeded["raw"]["mode"], "seeded")
            self.assertEqual(seeded["new_ids"], [], "the same response twice has nothing new")
            self.assertNotEqual(replay["run"], seeded["run"], "each run gets its own directory")

    def test_refused_resume_stops_the_run_before_any_fetch(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(self.watch, "fetch", side_effect=AssertionError("network used")):
                with self.assertRaises(self.resume.RefusedResume):
                    self.run_agent(tmp, "--resume", str(helpers.FIXTURES / "resume_not_fictional.json"))
            self.assertFalse((Path(tmp) / "runs").exists())

    def test_every_rule_verdict_is_a_record_with_supported_citations(self):
        with tempfile.TemporaryDirectory() as tmp:
            jobs = helpers.postings()
            self.run_agent(tmp, "--replay", str(helpers.write_board(Path(tmp) / "b1.json", jobs[:1])))
            report = self.run_agent(tmp, "--replay", str(helpers.write_board(Path(tmp) / "b2.json", jobs)))
            self.assertEqual(len(report["rule_verdicts"]), len(jobs) - 1)
            self.assertTrue(all(v["label"] == "record" for v in report["rule_verdicts"]))
            self.assertEqual(report["unsupported_citations"], 0)
            self.assertEqual(report["claude"]["status"], "not requested")


class ClaudeNotRun(helpers.ContractTest):
    modules = ("agent.claude_judge",)

    def test_missing_cli_is_not_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            outcome = self.claude_judge.judge(helpers.posting(9000000008), helpers.resume(), tmp,
                                              which=lambda name: None)
        self.assertEqual(outcome["status"], "not run")

    def test_not_logged_in_is_not_run(self):
        reply = json.dumps({"type": "result", "is_error": True, "result": "Not logged in"})

        def runner(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 1, stdout=reply, stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            outcome = self.claude_judge.judge(helpers.posting(9000000008), helpers.resume(), tmp,
                                              runner=runner, which=lambda name: "claude")
            self.assertTrue((Path(tmp) / "9000000008.reply.json").exists(), "raw reply still saved")
        self.assertEqual(outcome["status"], "not run")
        self.assertIn("Not logged in", outcome["reason"])

    def test_prompt_carries_the_posting_and_resume(self):
        prompt = self.claude_judge.build_prompt("{{RESUME_JSON}}\n{{POSTING_JSON}}",
                                                helpers.resume(), helpers.posting(9000000007))
        self.assertIn("priya.nair@example.com", prompt)
        self.assertIn("MLflow", prompt)
        self.assertNotIn("&lt;", prompt, "content reaches Claude with HTML removed")


if __name__ == "__main__":
    unittest.main()
