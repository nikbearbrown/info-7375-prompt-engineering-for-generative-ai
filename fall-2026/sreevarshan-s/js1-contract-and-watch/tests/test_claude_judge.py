"""Claude judge tests. The claude subprocess is MOCKED: no real Claude call, no network."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from js1 import claude_judge as cj
from js1.rule_judge import judge as rule_judge

ROOT = Path(__file__).resolve().parent.parent
RESUME = json.loads((ROOT / "persona" / "priya-nair.resume.json").read_text(encoding="utf-8"))
PROFILE = json.loads((ROOT / "persona" / "priya-nair.profile.json").read_text(encoding="utf-8"))
# CONSTRUCTED postings, not real ones.
POSTINGS = {p["id"]: p for p in json.loads(
    (Path(__file__).parent / "fixtures" / "constructed_postings.json").read_text(encoding="utf-8"))["jobs"]}
POSTING = POSTINGS[8000002]

VALID = json.dumps({
    "posting_id": 8000002,
    "verdict": "relevant",
    "skills_cited": [{"skill": "Python", "resume_field": "skills.languages"},
                     {"skill": "SQL", "resume_field": "skills.languages"}],
    "explanation": "The title is Data Engineer and the description asks for Python and SQL.",
})


class FakeClaude:
    """Stands in for the claude CLI: returns canned replies and records every prompt."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.prompts = []

    def __call__(self, prompt):
        self.prompts.append(prompt)
        return 0, self.replies.pop(0), ""


class ClaudeJudgeTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.evidence = Path(self._tmp.name) / "evidence" / "claude"

    def tearDown(self):
        self._tmp.cleanup()

    def _judge(self, fake, posting=POSTING, prompt_name="baseline"):
        return cj.judge(posting, RESUME, PROFILE, prompt_name=prompt_name, runner=fake,
                        evidence_dir=self.evidence, stamp="2026-10-29T23-00-00Z")

    def test_valid_json_is_accepted(self):
        fake = FakeClaude(VALID)
        result = self._judge(fake)
        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["label"], "judgment")
        self.assertEqual(result["posting_id"], 8000002)
        self.assertEqual(result["verdict"], "relevant")
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(len(fake.prompts), 1)

    def test_wrong_posting_id_is_rejected(self):
        allowed = cj.citable_fields(cj.candidate_fields(RESUME, PROFILE))
        wrong = json.loads(VALID)
        wrong["posting_id"] = 8000003
        with self.assertRaises(cj.InvalidReply):
            cj.validate(json.dumps(wrong), 8000002, allowed)
        wrong["posting_id"] = "8000002"
        with self.assertRaises(cj.InvalidReply):
            cj.validate(json.dumps(wrong), 8000002, allowed)

    def test_non_json_retries_exactly_once_then_invalid(self):
        fake = FakeClaude("Sure! Here is my answer.", "```json\n" + VALID + "\n```")
        result = self._judge(fake)
        self.assertEqual(len(fake.prompts), 2)
        self.assertEqual(fake.prompts[0], fake.prompts[1], "retry must reuse the same input")
        self.assertEqual(result["status"], "invalid")
        self.assertEqual(result["posting_id"], 8000002)
        self.assertEqual(len(result["validation_errors"]), 2)
        self.assertNotIn("verdict", result)

    def test_retry_that_succeeds_is_valid(self):
        result = self._judge(FakeClaude("not json", VALID))
        self.assertEqual((result["status"], result["attempts"]), ("valid", 2))

    def test_invalid_posting_does_not_stop_the_others(self):
        other = json.loads(VALID)
        other["posting_id"] = 8000005
        fake = FakeClaude("bad", "bad", json.dumps(other))
        results = cj.judge_all([POSTING, POSTINGS[8000005]], RESUME, PROFILE, runner=fake,
                               evidence_dir=self.evidence, stamp="2026-10-29T23-00-00Z")
        self.assertEqual([r["status"] for r in results], ["invalid", "valid"])

    def test_prompt_has_no_email_phone_or_rule_verdict(self):
        fake = FakeClaude(VALID)
        self._judge(fake)
        prompt = fake.prompts[0]
        for value in [RESUME["personal"]["email"], RESUME["personal"]["phone"], PROFILE["candidate"]["email"],
                      RESUME["personal"]["linkedin"], RESUME["personal"]["github"], "@", "555"]:
            self.assertNotIn(value, prompt)
        record = rule_judge(POSTING, RESUME, PROFILE)
        for marker in ['"record"', "failed_checks", '"checks"', "min_years_required", record["explanation"]]:
            self.assertNotIn(marker, prompt)
        data = json.loads(prompt.split("\nINPUT:\n", 1)[1])
        self.assertEqual(set(data), {"posting", "candidate"})
        self.assertEqual(set(data["posting"]), {"id", "title", "location", "description"})

    def test_prompt_files_differ_only_by_the_one_added_instruction(self):
        base = (ROOT / "prompts" / "baseline.txt").read_text(encoding="utf-8").splitlines()
        revised = (ROOT / "prompts" / "revised.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(revised), len(base) + 1)
        added = [line for line in revised if line not in base]
        self.assertEqual(added, ["Check every mandatory eligibility condition before giving the verdict."])
        revised.remove(added[0])
        self.assertEqual(revised, base)

    def test_validator_rejects_extra_keys_bad_verdict_and_familiar_citations(self):
        allowed = cj.citable_fields(cj.candidate_fields(RESUME, PROFILE))
        for change in [
            {"confidence": 0.9},
            {"verdict": "maybe"},
            {"skills_cited": [{"skill": "Ray", "resume_field": "skills.familiar_with_not_shipped"}]},
            {"skills_cited": [{"skill": "Python", "resume_field": "skills.made_up"}]},
            {"explanation": "Looks good to me."},
        ]:
            reply = dict(json.loads(VALID), **change)
            with self.subTest(change=change), self.assertRaises(cj.InvalidReply):
                cj.validate(json.dumps(reply), 8000002, allowed)

    def test_every_raw_reply_and_the_result_are_saved(self):
        self._judge(FakeClaude("not json", VALID))
        names = sorted(p.name for p in self.evidence.iterdir())
        self.assertEqual(names, ["2026-10-29T23-00-00Z-baseline-8000002-attempt1.txt",
                                 "2026-10-29T23-00-00Z-baseline-8000002-attempt2.txt",
                                 "2026-10-29T23-00-00Z-baseline-8000002-result.json"])
        self.assertEqual((self.evidence / names[0]).read_text(encoding="utf-8"), "not json")

    def test_revised_prompt_is_selected_by_name(self):
        fake = FakeClaude(VALID)
        result = self._judge(fake, prompt_name="revised")
        self.assertIn("Check every mandatory eligibility condition", fake.prompts[0])
        self.assertEqual(result["prompt"], "revised")

    def test_cli_call_disables_tools_and_runs_in_an_empty_temp_dir(self):
        seen = {}

        def fake_run(cmd, **kwargs):
            seen["cmd"], seen["cwd"] = cmd, kwargs["cwd"]
            seen["cwd_empty"] = os.listdir(kwargs["cwd"]) == []
            return subprocess.CompletedProcess(cmd, 0, stdout=VALID, stderr="")

        with mock.patch.object(cj.subprocess, "run", fake_run):
            code, out, _ = cj.run_claude("prompt text")
        self.assertEqual((code, out), (0, VALID))
        self.assertEqual(seen["cmd"][:2], ["claude", "-p"])
        self.assertEqual(seen["cmd"][seen["cmd"].index("--tools") + 1], "")
        self.assertIn("--strict-mcp-config", seen["cmd"])
        self.assertTrue(seen["cwd_empty"])
        self.assertNotEqual(Path(seen["cwd"]).resolve(), ROOT)
        self.assertFalse(Path(seen["cwd"]).exists(), "temp dir is removed after the call")

    def test_failed_call_records_stdout_and_stderr(self):
        def not_logged_in(prompt):
            return 1, "Not logged in · Please run /login\n", "some stderr text\n"

        result = cj.judge(POSTING, RESUME, PROFILE, runner=not_logged_in, evidence_dir=self.evidence, stamp="s")
        self.assertEqual(result["status"], "invalid")
        self.assertEqual(len(result["validation_errors"]), 2)
        for err in result["validation_errors"]:
            self.assertEqual(err["exit_code"], 1)
            self.assertIn("Not logged in", err["stdout"])
            self.assertIn("some stderr text", err["stderr"])
        saved = json.loads((self.evidence / "s-baseline-8000002-result.json").read_text(encoding="utf-8"))
        self.assertIn("Not logged in", saved["validation_errors"][0]["stdout"])

    def test_invalid_reply_also_records_its_output(self):
        result = self._judge(FakeClaude("not json", "still not json"))
        self.assertEqual([e["stdout"] for e in result["validation_errors"]], ["not json", "still not json"])

    def test_model_is_pinned_in_the_command_and_recorded_in_every_result(self):
        self.assertEqual(cj.CLAUDE_CMD[cj.CLAUDE_CMD.index("--model") + 1], "claude-sonnet-4-6")
        valid = self._judge(FakeClaude(VALID))
        invalid = cj.judge(POSTING, RESUME, PROFILE, runner=FakeClaude("x", "y"), evidence_dir=self.evidence,
                           stamp="t")
        self.assertEqual(valid["model"], "claude-sonnet-4-6")
        self.assertEqual(invalid["model"], "claude-sonnet-4-6")
        saved = json.loads((self.evidence / "t-baseline-8000002-result.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["model"], "claude-sonnet-4-6")

    def test_subprocess_failure_counts_as_a_failed_attempt(self):
        def broken(prompt):
            raise subprocess.TimeoutExpired("claude", 180)

        result = cj.judge(POSTING, RESUME, PROFILE, runner=broken, evidence_dir=self.evidence, stamp="s")
        self.assertEqual(result["status"], "invalid")
        self.assertEqual(len(result["validation_errors"]), 2)


if __name__ == "__main__":
    unittest.main()
