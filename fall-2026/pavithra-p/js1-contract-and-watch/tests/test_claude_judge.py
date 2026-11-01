"""CONTRACT.md Out (Claude's fixed format and validator) and Refuses 4 (Claude's opinion is not a fact).

No test calls the real Claude: a fake runner returns CONSTRUCTED replies.
"""
import json
import subprocess
import unittest

from agent import claude_judge, config, resume

PERSONA = resume.load(config.RESUME)
GOOD = {"verdict": "Relevant", "posting_fields": ["title", "description"],
        "resume_fields": ["skills.languages"], "reason": "Software Engineer II; description names Python and Kubernetes."}
JOB = {"id": 42, "title": "Software Engineer II", "location": {"name": "Remote, US"},
       "content": "&lt;p&gt;Python and Kubernetes&lt;/p&gt;"}


def fake_runner(reply_text, returncode=0):
    calls = []

    def run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        envelope = {"result": reply_text, "is_error": False, "session_id": "constructed",
                    "modelUsage": {claude_judge.MODEL: {}}}
        return subprocess.CompletedProcess(cmd, returncode, json.dumps(envelope), "boom" if returncode else "")
    run.calls = calls
    return run


class ValidatorTests(unittest.TestCase):
    def test_validator_accepts_exact_format(self):
        self.assertEqual(claude_judge.validate(json.dumps(GOOD)), GOOD)

    def test_validator_rejects_everything_else(self):
        bad = {
            "text before": "Here you go: " + json.dumps(GOOD),
            "code fence": "```json\n" + json.dumps(GOOD) + "\n```",
            "not JSON": "{verdict: Relevant}",
            "missing key": json.dumps({k: v for k, v in GOOD.items() if k != "reason"}),
            "extra key": json.dumps({**GOOD, "confidence": 0.9}),
            "other verdict": json.dumps({**GOOD, "verdict": "Maybe"}),
            "unknown posting field": json.dumps({**GOOD, "posting_fields": ["salary"]}),
            "empty résumé fields": json.dumps({**GOOD, "resume_fields": []}),
            "multi-line reason": json.dumps({**GOOD, "reason": "line one\nline two"}),
            "too long reason": json.dumps({**GOOD, "reason": "x" * 301}),
            "empty reply": "",
        }
        for name, text in bad.items():
            with self.assertRaises(claude_judge.InvalidReply, msg=name):
                claude_judge.validate(text)


class JudgeTests(unittest.TestCase):
    def setUp(self):
        self.prompt = config.ROOT / "experiment" / "prompts" / "baseline.md"

    def test_claude_opinion_labelled_ai_judgment(self):
        record = claude_judge.judge(JOB, PERSONA, self.prompt, run=fake_runner(json.dumps(GOOD)))
        self.assertEqual(record["kind"], "judgment (Claude, prompt contract)")
        self.assertTrue(record["valid"])
        self.assertEqual(record["parsed"]["verdict"], "Relevant")

    def test_invalid_reply_is_saved_and_never_repaired(self):
        record = claude_judge.judge(JOB, PERSONA, self.prompt, run=fake_runner("```json\n" + json.dumps(GOOD) + "\n```"))
        self.assertFalse(record["valid"])
        self.assertIsNone(record["parsed"], "an invalid reply is not fixed or guessed")
        self.assertIn("```json", record["reply"], "the reply is kept exactly as it came back")

    def test_each_call_is_fresh_with_no_tools_and_no_project_folder(self):
        run = fake_runner(json.dumps(GOOD))
        claude_judge.judge(JOB, PERSONA, self.prompt, run=run)
        claude_judge.judge(JOB, PERSONA, self.prompt, run=run)
        self.assertEqual(len(run.calls), 2)
        for cmd, kwargs in run.calls:
            self.assertEqual(cmd[:2], ["claude", "-p"])
            self.assertEqual(cmd[cmd.index("--tools") + 1], "", "no tools")
            self.assertIn("--no-session-persistence", cmd)
            self.assertNotIn("--continue", cmd)
            self.assertNotIn("--resume", cmd)
            self.assertFalse(str(kwargs["cwd"]).startswith(str(config.ROOT)), "never run inside the repo")

    def test_prompt_contains_posting_and_resume_but_no_contact_details(self):
        prompt = claude_judge.build_prompt(self.prompt.read_text(), JOB, PERSONA)
        self.assertIn("Software Engineer II", prompt)
        self.assertIn("Kubernetes", prompt)
        self.assertNotIn(PERSONA["personal"]["email"], prompt)
        self.assertNotIn(PERSONA["personal"]["phone"], prompt)

    def test_cli_failure_is_recorded_as_invalid(self):
        record = claude_judge.judge(JOB, PERSONA, self.prompt, run=fake_runner("", returncode=1))
        self.assertFalse(record["valid"])
        self.assertEqual(record["cli_error"], "boom")


if __name__ == "__main__":
    unittest.main()
