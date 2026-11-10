"""The Claude judge's validator must reject anything outside the fixed format.
These run offline: no Claude call is made."""
import json
import unittest

from agent.claude_judge import InvalidOutput, validate

GOOD = {"verdict": "relevant", "resume_fields": ["resume.skills.languages", "resume.experience"],
        "posting_fields": ["posting.title", "posting.content"], "reason": "New-grad title; asks for Go and Python."}


def dump(**changes):
    d = dict(GOOD, **changes)
    return json.dumps({k: v for k, v in d.items() if v is not ...})


class TestValidator(unittest.TestCase):
    def test_accepts_good_output(self):
        self.assertEqual(validate(json.dumps(GOOD))["verdict"], "relevant")

    def rejects(self, text):
        with self.assertRaises(InvalidOutput, msg=text):
            validate(text)

    def test_rejects_prose_and_fences(self):
        self.rejects("Sure! " + json.dumps(GOOD))
        self.rejects("```json\n" + json.dumps(GOOD) + "\n```")
        self.rejects("relevant")

    def test_rejects_wrong_or_extra_keys(self):
        self.rejects(dump(confidence=0.9))
        self.rejects(dump(reason=...))

    def test_rejects_other_verdicts(self):
        for v in ["Relevant", "maybe", "yes", True]:
            self.rejects(dump(verdict=v))

    def test_rejects_justification_that_cites_nothing(self):
        self.rejects(dump(resume_fields=[]))
        self.rejects(dump(posting_fields=[]))

    def test_rejects_invented_fields(self):
        self.rejects(dump(resume_fields=["resume.years_of_experience"]))
        self.rejects(dump(posting_fields=["posting.salary"]))
        self.rejects(dump(resume_fields=["resume.personal.email"]))

    def test_rejects_empty_or_long_reason(self):
        self.rejects(dump(reason=""))
        self.rejects(dump(reason="x" * 301))


if __name__ == "__main__":
    unittest.main()
