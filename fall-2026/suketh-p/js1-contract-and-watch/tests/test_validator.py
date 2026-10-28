"""The Claude output contract from CONTRACT.md. Every response here is CONSTRUCTED
to exercise the validator; none of them is a response Claude gave."""

import json
import unittest

from jobwatch import judge
from jobwatch.errors import JudgeError
from tests.helpers import persona

POSTING = {
    "id": 101,
    "title": "Software Engineer, Inference",
    "location": {"name": "San Francisco, CA"},
    "content": "You write Python and PyTorch daily.",
}


def response(**changes):
    data = {
        "posting_id": "101",
        "verdict": "relevant",
        "justification": "Title, location and skills each match the named résumé fields.",
        "resume_evidence": [
            {"field": "resume.skills", "quote": "pytorch"},
            {"field": "resume.preferences.title_word", "quote": "engineer"},
        ],
        "posting_evidence": [
            {"field": "posting.title", "quote": "Software Engineer, Inference"},
            {"field": "posting.content", "quote": "Python and PyTorch"},
        ],
    }
    data.update(changes)
    return json.dumps(data)


def validate(text):
    return judge.validate_response(text, persona(), POSTING)


class OutputFormatTest(unittest.TestCase):
    def test_accepts_a_fully_supported_response(self):
        self.assertEqual(validate(response())["verdict"], "relevant")

    def test_rejects_format_violations(self):
        bad = {
            "markdown fence": "```json\n" + response() + "\n```",
            "commentary after": response() + "\nHope this helps!",
            "malformed json": response()[:-1],
            "not an object": json.dumps([json.loads(response())]),
            "missing key": json.dumps({k: v for k, v in json.loads(response()).items() if k != "justification"}),
            "extra key": response(confidence=0.9),
            "duplicate key": '{"verdict": "not_relevant", ' + response()[1:],
            "unsupported verdict": response(verdict="maybe"),
            "verdict wrong case": response(verdict="Relevant"),
            "numeric posting id": response(posting_id=101),
            "mismatched posting id": response(posting_id="202"),
            "empty justification": response(justification="   "),
            "evidence item missing quote": response(resume_evidence=[{"field": "resume.skills"}]),
            "evidence item extra key": response(resume_evidence=[{"field": "resume.skills", "quote": "sql", "why": "x"}]),
        }
        for case, text in bad.items():
            with self.subTest(case), self.assertRaises(JudgeError):
                validate(text)


class UnsupportedJustificationTest(unittest.TestCase):
    """CONTRACT.md wrong version 2: a plausible explanation that cites no fields,
    invents a quotation, or refers to a different posting must be rejected."""

    def test_rejects_a_justification_that_cites_no_fields(self):
        for changes in ({"resume_evidence": []}, {"posting_evidence": []},
                        {"resume_evidence": [], "posting_evidence": []}):
            with self.subTest(changes=changes), self.assertRaises(JudgeError):
                validate(response(**changes))

    def test_rejects_an_invented_quotation(self):
        with self.assertRaises(JudgeError):
            validate(response(posting_evidence=[{"field": "posting.content", "quote": "5+ years of Rust"}]))

    def test_rejects_a_quote_in_the_wrong_case(self):
        with self.assertRaises(JudgeError):
            validate(response(posting_evidence=[{"field": "posting.content", "quote": "python and pytorch"}]))

    def test_rejects_a_reference_to_a_different_posting(self):
        with self.assertRaises(JudgeError):
            validate(response(posting_evidence=[{"field": "posting.title", "quote": "Senior Data Engineer, Spark"}]))
        with self.assertRaises(JudgeError):
            validate(response(posting_id="202"))

    def test_rejects_paths_that_do_not_exist(self):
        for evidence in ({"resume_evidence": [{"field": "resume.preferences.locations", "quote": "boston"}]},
                         {"posting_evidence": [{"field": "posting.salary", "quote": "$1"}]},
                         {"posting_evidence": [{"field": "title", "quote": "Software Engineer"}]}):
            with self.subTest(evidence=evidence), self.assertRaises(JudgeError):
                validate(response(**evidence))

    def test_rejects_evidence_filed_under_the_wrong_side(self):
        with self.assertRaises(JudgeError):
            validate(response(resume_evidence=[{"field": "posting.title", "quote": "Software Engineer"}]))

    def test_rejects_a_path_that_is_not_text(self):
        with self.assertRaises(JudgeError):
            validate(response(resume_evidence=[{"field": "resume.fictional", "quote": "true"}]))

    def test_quote_may_come_from_one_array_item_but_not_span_two(self):
        validate(response(resume_evidence=[{"field": "resume.preferences.location_terms", "quote": "san francisco"}]))
        with self.assertRaises(JudgeError):
            validate(response(resume_evidence=[{"field": "resume.skills", "quote": "python sql"}]))

    def test_whitespace_runs_inside_a_quote_are_collapsed(self):
        validate(response(posting_evidence=[{"field": "posting.content", "quote": "Python  and\nPyTorch"}]))


if __name__ == "__main__":
    unittest.main()
