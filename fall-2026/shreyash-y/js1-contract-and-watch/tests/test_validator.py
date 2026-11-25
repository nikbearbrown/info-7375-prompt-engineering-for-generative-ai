"""The Claude step's fixed output format: anything else is rejected."""
import json
import unittest

from jsagent import validator

GOOD = {
    "posting_id": 8119736,
    "verdict": "Not Relevant",
    "failed_conditions": [3, 5, 6],
    "resume_fields": ["location", "experience_years", "exclusions"],
    "posting_fields": ["location", "content", "title"],
    "justification": "posting.title has Staff (resume.exclusions); posting.location is New York, "
                     "not resume.location Boston; posting.content asks 7+ years, over resume.experience_years 3.",
}


def check(obj=None, text=None, pid=8119736):
    return validator.validate(text if text is not None else json.dumps(obj), pid)


class Validator(unittest.TestCase):
    def test_good_passes(self):
        parsed, errors = check(GOOD)
        self.assertEqual(errors, [])
        self.assertEqual(parsed["verdict"], "Not Relevant")

    def test_surrounding_whitespace_ok(self):
        self.assertEqual(check(text="\n  " + json.dumps(GOOD) + "\n")[1], [])

    def test_code_fence_rejected(self):
        self.assertTrue(check(text="```json\n" + json.dumps(GOOD) + "\n```")[1])

    def test_prose_rejected(self):
        self.assertTrue(check(text="This job is a good match.")[1])
        self.assertTrue(check(text="Here is my verdict: " + json.dumps(GOOD))[1])

    def test_extra_or_missing_keys_rejected(self):
        self.assertTrue(check(dict(GOOD, confidence=0.9))[1])
        self.assertTrue(check({k: v for k, v in GOOD.items() if k != "posting_fields"})[1])

    def test_wrong_posting_id_rejected(self):
        self.assertTrue(check(dict(GOOD, posting_id=1))[1])
        self.assertTrue(check(dict(GOOD, posting_id="8119736"))[1])

    def test_verdict_vocabulary(self):
        self.assertTrue(check(dict(GOOD, verdict="not relevant"))[1])
        self.assertTrue(check(dict(GOOD, verdict="Maybe"))[1])

    def test_verdict_consistent_with_failed_conditions(self):
        self.assertTrue(check(dict(GOOD, verdict="Relevant"))[1])
        self.assertTrue(check(dict(GOOD, failed_conditions=[]))[1])
        self.assertTrue(check(dict(GOOD, failed_conditions=[7]))[1])
        self.assertTrue(check(dict(GOOD, failed_conditions=[3, 3]))[1])

    def test_fields_must_be_real_and_cited(self):
        self.assertTrue(check(dict(GOOD, resume_fields=[]))[1])
        self.assertTrue(check(dict(GOOD, resume_fields=["salary"]))[1])
        self.assertTrue(check(dict(GOOD, posting_fields=["required_skills"]))[1])

    def test_generic_justification_rejected(self):
        self.assertTrue(check(dict(GOOD, justification="This job is a good match."))[1])

    def test_field_name_inside_another_word_does_not_count(self):
        # Found 2026-10-31 by a TA-style review: "id" matched inside "considered".
        generic = dict(GOOD, verdict="Relevant", failed_conditions=[], resume_fields=["skills"],
                       posting_fields=["id"],
                       justification="This job is a good match and should be considered for the skills.")
        self.assertTrue(check(generic)[1])

    def test_id_alone_is_not_a_posting_citation(self):
        self.assertTrue(check(dict(GOOD, posting_fields=["id"],
                                   justification="Posting id 8119736 fails resume.location and exclusions."))[1])

    def test_singular_and_spaced_forms_count(self):
        ok = dict(GOOD, resume_fields=["experience_years"], posting_fields=["departments"],
                  justification="The department is Data, and the ad asks 7 years against 3 experience years.")
        self.assertEqual(check(ok)[1], [])


if __name__ == "__main__":
    unittest.main()
