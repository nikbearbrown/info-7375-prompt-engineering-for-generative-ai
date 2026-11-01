"""The validator for Claude's replies. Replies here are CONSTRUCTED strings, not Claude output."""

import json
import unittest
from pathlib import Path

from jsagent.claude_judge import build_prompt, validate
from tests import fixtures as F

GOOD = {
    "posting_id": "101",
    "verdict": "RELEVANT",
    "evidence": [
        {"skill": "Java", "resume_field": "skills.languages[2]", "posting_quote": "experience with Java or Python"},
        {"skill": "AWS", "resume_field": "skills.database_cloud[3]", "posting_quote": "deployed services on AWS"},
    ],
    "reason": "US new-grad software engineer role citing Java and AWS.",
}


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.resume = F.persona()

    def check(self, reply):
        return validate(reply, F.RELEVANT, self.resume)[1]

    def test_good_reply_accepted(self):
        self.assertEqual(self.check(json.dumps(GOOD)), [])

    def test_not_relevant_with_no_evidence_accepted(self):
        self.assertEqual(self.check(json.dumps(dict(GOOD, verdict="NOT RELEVANT", evidence=[]))), [])

    def test_rejections(self):
        cases = {
            "code fence": "```json\n" + json.dumps(GOOD) + "\n```",
            "prose before": "Here is my answer: " + json.dumps(GOOD),
            "not json": "{verdict: RELEVANT}",
            "extra key": json.dumps(dict(GOOD, confidence=0.9)),
            "missing key": json.dumps({k: v for k, v in GOOD.items() if k != "reason"}),
            "wrong posting": json.dumps(dict(GOOD, posting_id="102")),
            "lower-case verdict": json.dumps(dict(GOOD, verdict="Relevant")),
            "relevant, one skill": json.dumps(dict(GOOD, evidence=GOOD["evidence"][:1])),
            "relevant, generic": json.dumps(dict(GOOD, evidence=[])),
            "invented quote": json.dumps(dict(GOOD, evidence=[GOOD["evidence"][0],
                                         {"skill": "Docker", "resume_field": "skills.devops_cicd[0]", "posting_quote": "Docker required"}])),
            "skill not on résumé": json.dumps(dict(GOOD, evidence=[GOOD["evidence"][0],
                                              {"skill": "Scala", "resume_field": "skills.languages[9]", "posting_quote": "Java or Python"}])),
            "evidence not objects": json.dumps(dict(GOOD, evidence=["Java", "AWS"])),
            "empty reason": json.dumps(dict(GOOD, reason="")),
        }
        for name, reply in cases.items():
            with self.subTest(name):
                self.assertTrue(self.check(reply), name)

    def test_prompt_carries_no_personal_fields(self):
        prompt = build_prompt(Path("prompts/baseline.txt").read_text(), F.RELEVANT, self.resume)
        for private in ("Rohan", "555", "example.com", "linkedin"):
            self.assertNotIn(private, prompt)
        self.assertIn('"posting_id": "101"', prompt)


if __name__ == "__main__":
    unittest.main()
