"""The four-condition rule from CONTRACT.md. Every expected verdict below was worked out
by hand from the contract text, not computed by the code under test. Constructed postings."""

import unittest

from jobwatch import board, rule
from tests.helpers import board_bytes, job, persona

# (case, title, location, content markup, expected verdict, expected failed conditions)
CASES = [
    ("all four pass", "Software Engineer, Inference", "San Francisco, CA",
     "<p>Python and PyTorch</p>", "relevant", []),
    ("senior title", "Senior Software Engineer, Inference", "San Francisco, CA",
     "<p>Python and PyTorch</p>", "not_relevant", ["title_seniority"]),
    ("engineering is not engineer, manager is excluded", "Engineering Manager, Data", "Seattle, WA",
     "<p>Python, SQL</p>", "not_relevant", ["engineering_role", "title_seniority"]),
    ("focus phrase must be consecutive", "Machine Engineer, Learning Systems", "Boston, MA",
     "<p>Python, SQL</p>", "not_relevant", ["engineering_role"]),
    ("ai is a token, not a substring of email", "Engineer, Email Platform", "Boston, MA",
     "<p>Python, SQL</p>", "not_relevant", ["engineering_role"]),
    ("lead does not match leadership", "ML Engineer, Leadership Tools", "New York City, NY",
     "<p>Python, SQL</p>", "relevant", []),
    ("location outside the list", "Data Engineer", "London, UK",
     "<p>Python, SQL</p>", "not_relevant", ["location"]),
    ("empty location", "Data Engineer", "",
     "<p>Python, SQL</p>", "not_relevant", ["location"]),
    ("location words not consecutive", "Data Engineer", "New Jersey; York, PA",
     "<p>Python, SQL</p>", "not_relevant", ["location"]),
    ("python3 is not python", "AI Engineer", "Remote - United States",
     "<p>python3, Docker</p>", "not_relevant", ["skills"]),
    ("python alone, repeated, is one skill", "AI Engineer", "Remote - United States",
     "<p>Python. More Python. python!</p>", "not_relevant", ["skills"]),
    ("preferred qualifications count", "AI Engineer", "Remote - United States",
     "<h3>Preferred</h3><ul><li>Python</li><li>AWS</li></ul>", "relevant", []),
    ("all four fail", "Head of Recruiting", "Dublin, IE",
     "<p>Excel</p>", "not_relevant", ["engineering_role", "title_seniority", "location", "skills"]),
]


def posting_from(title, location, markup, job_id=7):
    return board.parse_board(board_bytes(job(job_id, title, location, markup)))[0]


def condition(record, name):
    return next(c for c in record["conditions"] if c["condition"] == name)


class RuleTableTest(unittest.TestCase):
    def test_hand_worked_cases(self):
        for case, title, location, markup, verdict, failed in CASES:
            with self.subTest(case):
                record = rule.rule_verdict(persona(), posting_from(title, location, markup))
                self.assertEqual(record["verdict"], verdict)
                self.assertEqual(record["failed_conditions"], failed)


class RuleRecordTest(unittest.TestCase):
    def test_record_shows_every_condition_with_fields_and_matches(self):
        record = rule.rule_verdict(persona(), posting_from(
            "Software Engineer, Inference", "San Francisco, CA", "<p>Python and PyTorch</p>", job_id=101))
        self.assertEqual(record["kind"], "record")
        self.assertEqual(record["posting_id"], 101)
        self.assertEqual([c["condition"] for c in record["conditions"]],
                         ["engineering_role", "title_seniority", "location", "skills"])
        self.assertTrue(all(c["passed"] for c in record["conditions"]))
        role = condition(record, "engineering_role")
        self.assertEqual(role["posting_field"], "posting.title")
        self.assertEqual(role["posting_value"], "Software Engineer, Inference")
        self.assertEqual(role["matched"], {
            "resume.preferences.title_word": ["engineer"],
            "resume.preferences.focus_terms": ["inference"],
        })
        self.assertEqual(condition(record, "location")["matched"],
                         {"resume.preferences.location_terms": ["san francisco"]})
        self.assertEqual(condition(record, "skills")["matched"], {"resume.skills": ["python", "pytorch"]})

    def test_negative_record_names_the_failed_condition_and_its_fields(self):
        record = rule.rule_verdict(persona(), posting_from(
            "Senior Software Engineer, Inference", "San Francisco, CA", "<p>Python and PyTorch</p>"))
        seniority = condition(record, "title_seniority")
        self.assertFalse(seniority["passed"])
        self.assertEqual(seniority["matched"], {"resume.preferences.excluded_title_words": ["senior"]})
        self.assertIn("title_seniority", record["justification"])
        self.assertIn("resume.preferences.excluded_title_words", record["justification"])
        self.assertIn("posting.title", record["justification"])


if __name__ == "__main__":
    unittest.main()
