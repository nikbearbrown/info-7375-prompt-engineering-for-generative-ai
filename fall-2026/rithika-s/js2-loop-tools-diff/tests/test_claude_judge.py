"""Claude judge tests. The CLI is always replaced by a FAKE runner."""

import json
import unittest
from unittest import mock

import fixtures
from agent import claude_judge as cj

RESUME, TARGET = fixtures.load_example_inputs()
PID = fixtures.RELEVANT["id"]
GOOD = {"posting_id": PID, "verdict": "relevant",
        "resume_fields": ["skills.languages"],
        "posting_fields": ["posting.content"],
        "reason": "FAKE: Python and SQL appear in the posting."}


def as_json(**changes):
    return json.dumps(dict(GOOD, **changes))


class ValidatorTests(unittest.TestCase):

    def test_accepts_exact_shape(self):
        self.assertEqual(cj.validate(json.dumps(GOOD), PID), GOOD)

    def test_rejects_non_json(self):
        for raw in ("relevant", "", "{posting_id: 9001}"):
            with self.subTest(raw=raw):
                with self.assertRaises(cj.ClaudeOutputInvalid):
                    cj.validate(raw, PID)

    def test_rejects_extra_prose(self):
        for raw in ("Here is my verdict: " + json.dumps(GOOD),
                    json.dumps(GOOD) + "\nHope this helps!",
                    "```json\n" + json.dumps(GOOD) + "\n```"):
            with self.subTest(raw=raw[:30]):
                with self.assertRaises(cj.ClaudeOutputInvalid):
                    cj.validate(raw, PID)

    def test_rejects_unknown_verdict(self):
        for verdict in ("maybe", "Relevant", "", None):
            with self.subTest(verdict=verdict):
                with self.assertRaisesRegex(cj.ClaudeOutputInvalid, "verdict"):
                    cj.validate(as_json(verdict=verdict), PID)

    def test_rejects_mismatched_posting_id(self):
        for pid in (PID + 1, str(PID), True):
            with self.subTest(pid=pid):
                with self.assertRaisesRegex(cj.ClaudeOutputInvalid,
                                            "posting_id"):
                    cj.validate(as_json(posting_id=pid), PID)

    def test_rejects_empty_field_lists(self):
        for key in ("resume_fields", "posting_fields"):
            with self.subTest(key=key):
                with self.assertRaisesRegex(cj.ClaudeOutputInvalid, key):
                    cj.validate(as_json(**{key: []}), PID)

    def test_rejects_extra_or_missing_keys_and_contact_fields(self):
        extra = dict(GOOD, confidence=0.9)
        missing = {k: v for k, v in GOOD.items() if k != "reason"}
        for raw in (json.dumps(extra), json.dumps(missing),
                    as_json(resume_fields=["personal.email"])):
            with self.subTest(raw=raw[:40]):
                with self.assertRaises(cj.ClaudeOutputInvalid):
                    cj.validate(raw, PID)


class JudgeTests(unittest.TestCase):

    def test_prompt_contract_has_schema_and_no_contact_fields(self):
        prompt = cj.build_prompt(fixtures.RELEVANT, RESUME, TARGET)
        self.assertIn(f"posting_id must be {PID}", prompt)
        self.assertIn("JSON only", prompt)
        self.assertIn("skills.languages: Python, SQL", prompt)
        for key in ("email", "phone", "linkedin", "github"):
            self.assertNotIn(RESUME["personal"][key], prompt)

    def test_valid_fake_output_is_judged(self):
        result = cj.judge(fixtures.RELEVANT, RESUME, TARGET,
                          runner=lambda prompt: json.dumps(GOOD))
        self.assertEqual(result, {"status": "judged", "verdict": GOOD})

    def test_invalid_fake_output_is_rejected_not_fabricated(self):
        result = cj.judge(fixtures.RELEVANT, RESUME, TARGET,
                          runner=lambda prompt: "Strong ML fit.")
        self.assertEqual(result["status"], "rejected")
        self.assertNotIn("verdict", result)

    def test_unavailable_cli_is_not_run(self):
        result = cj.judge(fixtures.RELEVANT, RESUME, TARGET,
                          runner=lambda prompt: None)
        self.assertEqual(result, {"status": "not run"})
        with mock.patch("subprocess.run", side_effect=FileNotFoundError):
            self.assertIsNone(cj.run_claude_cli("prompt"))


if __name__ == "__main__":
    unittest.main()
