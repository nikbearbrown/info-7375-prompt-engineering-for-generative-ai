"""The Claude judge's validator and plumbing, offline: a fake runner stands in
for `claude -p`, so no test here is a real Claude reply."""

import json
import os
import unittest

from agent import claude_judge as cj
from tests.fixtures import resume, variant

HERE = os.path.dirname(__file__)
BASELINE = os.path.join(HERE, "..", "prompts", "baseline.md")

GOOD = {"posting_id": 42, "verdict": "relevant",
        "resume_fields": ["skills.languages", "experience.title"],
        "posting_fields": ["title", "content"],
        "reason": "AI title, US location, Python and AWS."}


def reply(**changes):
    obj = dict(GOOD, **changes)
    return json.dumps({k: v for k, v in obj.items() if v is not ...})


class TestValidator(unittest.TestCase):
    def setUp(self):
        self.resume = resume()

    def check(self, text):
        return cj.validate(text, 42, self.resume)

    def test_exact_format_passes(self):
        parsed, errors = self.check(reply())
        self.assertEqual(errors, [])
        self.assertEqual(parsed["verdict"], "relevant")

    def test_rejections(self):
        cases = {
            "code fence": "```json\n" + reply() + "\n```",
            "text after": reply() + "\nHope this helps!",
            "extra key": reply(confidence=0.9),
            "missing key": reply(reason=...),
            "wrong id": reply(posting_id=43),
            "id as string": reply(posting_id="42"),
            "id as bool": json.dumps(dict(GOOD, posting_id=True)),
            "third verdict": reply(verdict="maybe"),
            "empty resume_fields": reply(resume_fields=[]),
            "empty posting_fields": reply(posting_fields=[]),
            "invented resume field": reply(resume_fields=["skills.rust"]),
            "unknown posting field": reply(posting_fields=["salary"]),
            "blank reason": reply(reason="  "),
            "a list": "[" + reply() + "]",
        }
        for name, text in cases.items():
            with self.subTest(name):
                parsed, errors = self.check(text)
                self.assertIsNone(parsed)
                self.assertNotEqual(errors, [])

    def test_path_exists(self):
        r = self.resume
        self.assertTrue(cj.path_exists(r, "skills.languages"))
        self.assertTrue(cj.path_exists(r, "experience[0].title"))
        self.assertTrue(cj.path_exists(r, "work_authorization.needs_sponsorship"))
        self.assertFalse(cj.path_exists(r, "skills.rust"))
        self.assertFalse(cj.path_exists(r, ""))


class TestJudge(unittest.TestCase):
    def setUp(self):
        self.resume = resume()
        self.posting = variant(id=42)
        self.prompts = []

    def fake(self, text, is_error=False):
        def runner(prompt, model):
            self.prompts.append(prompt)
            return {"result": text, "is_error": is_error,
                    "modelUsage": {model: {}}, "session_id": "fake"}
        return runner

    def test_prompt_has_posting_but_no_contact_details(self):
        cj.judge(self.posting, self.resume, BASELINE, runner=self.fake(reply()))
        p = self.prompts[0]
        self.assertIn("posting_id: 42", p)
        self.assertIn("Python on AWS", p)
        for secret in ["priya.nair@example.com", "555-0163", "Priya Nair"]:
            self.assertNotIn(secret, p)

    def test_valid_reply_is_labeled_judgment(self):
        rec = cj.judge(self.posting, self.resume, BASELINE,
                       runner=self.fake(reply()))
        self.assertEqual((rec["kind"], rec["verdict"]),
                         ("judgment", "relevant"))
        self.assertEqual(rec["raw_reply"], reply())

    def test_invalid_reply_becomes_INVALID_not_a_verdict(self):
        rec = cj.judge(self.posting, self.resume, BASELINE,
                       runner=self.fake("Yes, relevant!"))
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertIsNone(rec["parsed"])
        self.assertEqual(rec["raw_reply"], "Yes, relevant!")

    def test_cli_error_is_INVALID(self):
        rec = cj.judge(self.posting, self.resume, BASELINE,
                       runner=self.fake(reply(), is_error=True))
        self.assertEqual(rec["verdict"], "INVALID")


if __name__ == "__main__":
    unittest.main()
