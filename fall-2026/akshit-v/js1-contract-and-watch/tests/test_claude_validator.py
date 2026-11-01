"""The validator rejects anything that is not exactly the contracted JSON shape."""
import json
import unittest

from agent.claude_judge import resume_for_claude, validate
from tests.helpers import JACK

FIELDS = list(resume_for_claude(JACK))
GOOD = {"verdict": "relevant", "cited_resume_fields": ["skills"],
        "cited_posting_fields": ["title", "content"], "reason": "Python and Spark appear in the content."}


def check(obj_or_text):
    text = obj_or_text if isinstance(obj_or_text, str) else json.dumps(obj_or_text)
    return validate(text, FIELDS)


class Validator(unittest.TestCase):
    def test_accepts_contract_shape(self):
        parsed, why = check(GOOD)
        self.assertIsNone(why)
        self.assertEqual(parsed["verdict"], "relevant")

    def test_rejects(self):
        cases = {
            "code fence": "```json\n" + json.dumps(GOOD) + "\n```",
            "text before": "Here is my answer: " + json.dumps(GOOD),
            "extra key": {**GOOD, "confidence": 0.9},
            "missing key": {k: v for k, v in GOOD.items() if k != "reason"},
            "third verdict": {**GOOD, "verdict": "maybe"},
            "empty resume citations": {**GOOD, "cited_resume_fields": []},
            "empty posting citations": {**GOOD, "cited_posting_fields": []},
            "unknown resume field": {**GOOD, "cited_resume_fields": ["gpa"]},
            "identity field not given to Claude": {**GOOD, "cited_resume_fields": ["email"]},
            "unknown posting field": {**GOOD, "cited_posting_fields": ["salary"]},
            "blank reason": {**GOOD, "reason": "  "},
            "not an object": [GOOD],
        }
        for name, case in cases.items():
            parsed, why = check(case)
            self.assertIsNone(parsed, name)
            self.assertTrue(why, name)


if __name__ == "__main__":
    unittest.main()
