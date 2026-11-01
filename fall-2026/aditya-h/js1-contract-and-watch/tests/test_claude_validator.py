"""Tests for the Claude-judge validator, written from CONTRACT.md (Out: Claude output format)
before claude_judge.py existed. The replies below are constructed strings, not Claude output.
"""
import json
import pathlib
import unittest

from jobwatch import claude_judge

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAYA = json.loads((ROOT / "personas" / "maya-sehgal.resume.json").read_text())
POSTING = {"id": 7001, "title": "Product Manager, Global Payouts", "location": {"name": "New York"},
           "offices": [{"name": "US"}], "content": "We build payouts."}


def reply(**over):
    base = {"posting_id": 7001, "verdict": "relevant", "resume_fields": ["experience[1].title"],
            "posting_fields": ["title", "offices[0].name"], "reason": "PM payments background; US office."}
    base.update(over)
    return json.dumps(base)


class Validator(unittest.TestCase):
    def check(self, text):
        return claude_judge.validate(text, POSTING, MAYA)

    def test_well_formed_reply_is_valid(self):
        v = self.check(reply())
        self.assertEqual(v["status"], "valid", v.get("errors"))
        self.assertEqual(v["verdict"], "relevant")

    def test_not_json_rejected(self):
        self.assertEqual(self.check("Relevant — strong PM fit.")["status"], "invalid")

    def test_prose_around_json_rejected(self):
        self.assertEqual(self.check("Here you go:\n" + reply())["status"], "invalid")

    def test_code_fence_rejected(self):
        self.assertEqual(self.check("```json\n" + reply() + "\n```")["status"], "invalid")

    def test_missing_or_extra_keys_rejected(self):
        d = json.loads(reply())
        del d["reason"]
        self.assertEqual(self.check(json.dumps(d))["status"], "invalid")
        self.assertEqual(self.check(reply(confidence=0.9))["status"], "invalid")

    def test_verdict_outside_vocabulary_rejected(self):
        for v in ("Relevant", "maybe", "yes", True):
            with self.subTest(v=v):
                self.assertEqual(self.check(reply(verdict=v))["status"], "invalid")

    def test_wrong_posting_id_rejected(self):
        # Wrong version 1 at the Claude boundary: a verdict for another posting must not attach here.
        self.assertEqual(self.check(reply(posting_id=7002))["status"], "invalid")

    def test_empty_citations_rejected(self):
        # Wrong version 2: a justification that cites nothing.
        self.assertEqual(self.check(reply(resume_fields=[]))["status"], "invalid")
        self.assertEqual(self.check(reply(posting_fields=[]))["status"], "invalid")
        self.assertEqual(self.check(reply(reason="  "))["status"], "invalid")

    def test_invented_field_paths_rejected(self):
        self.assertEqual(self.check(reply(resume_fields=["experience[5].title"]))["status"], "invalid")
        self.assertEqual(self.check(reply(posting_fields=["salary"]))["status"], "invalid")
        self.assertEqual(self.check(reply(resume_fields=["years_of_experience"]))["status"], "invalid")

    def test_invalid_reply_keeps_raw_text_and_is_not_coerced(self):
        v = self.check("relevant")
        self.assertEqual(v["status"], "invalid")
        self.assertNotIn("verdict", v)
        self.assertEqual(v["raw"], "relevant")
        self.assertTrue(v["errors"])


class Judge(unittest.TestCase):
    def test_judge_labels_result_as_judgment_with_model_and_date(self):
        calls = []

        def fake_runner(prompt, model):
            calls.append(prompt)
            return reply(), "claude-sonnet-test"

        judge = claude_judge.make_judge(ROOT / "prompts" / "judge_v1.txt", model="sonnet", runner=fake_runner)
        out = judge(POSTING, MAYA)
        self.assertEqual(out["status"], "valid")
        self.assertEqual(out["kind"], "judgment")
        self.assertEqual(out["model"], "claude-sonnet-test")
        self.assertTrue(out["date"])
        self.assertIn("Product Manager, Global Payouts", calls[0])
        self.assertIn("7001", calls[0])

    def test_prompt_never_contains_contact_details(self):
        calls = []
        judge = claude_judge.make_judge(ROOT / "prompts" / "judge_v1.txt", model="sonnet",
                                        runner=lambda p, m: (calls.append(p) or reply(), "m"))
        judge(POSTING, MAYA)
        for secret in (MAYA["personal"]["email"], MAYA["personal"]["phone"]):
            self.assertNotIn(secret, calls[0])

    def test_runner_failure_is_invalid_not_a_verdict(self):
        def broken(prompt, model):
            raise claude_judge.ClaudeError("auth expired")

        out = claude_judge.make_judge(ROOT / "prompts" / "judge_v1.txt", runner=broken)(POSTING, MAYA)
        self.assertEqual(out["status"], "invalid")
        self.assertNotIn("verdict", out)


if __name__ == "__main__":
    unittest.main()
