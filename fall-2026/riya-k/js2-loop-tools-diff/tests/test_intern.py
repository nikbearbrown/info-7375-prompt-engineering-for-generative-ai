"""Intern exclusion (TA's JS1 feedback; rule amendment 3, decided by Riya 2026-11-09: whole-word Intern, Internship).
Written and committed BEFORE the patch to jsagent/rules.py. Before the patch the first three tests fail.
Run: python3 -m unittest tests.test_intern -v
"""

import json
import unittest
from pathlib import Path

from jsagent import ats, rules

ROOT = Path(__file__).resolve().parent.parent
RESUME = json.loads((ROOT / "persona" / "arya-sahni.json").read_text())
SKILLS = "<p>You will use Python and SQL every day, with MLflow for experiments.</p>"


def posting(title, location="San Francisco, California"):
    """CONSTRUCTED posting: passes every other part of the rule, so only the title decides."""
    return {"id": "t-" + title, "title": title, "content": SKILLS, "location": {"name": location}}


class TestInternExcluded(unittest.TestCase):
    def test_real_posting_6866538002_data_science_intern_is_not_relevant(self):
        job = json.loads((ROOT / "tests/fixtures/databricks-6866538002.json").read_text())["job"]
        p = ats.greenhouse_parse(json.dumps({"jobs": [job]}).encode())[0]
        v = rules.judge(p, RESUME)
        self.assertEqual(v["verdict"], "not_relevant")
        self.assertIn("intern", v["justification"].lower())  # the record must say WHY

    def test_internship_is_excluded(self):
        self.assertEqual(rules.judge(posting("Machine Learning Internship"), RESUME)["verdict"], "not_relevant")

    def test_intern_any_case_and_punctuation(self):
        for t in ["AI Engineer (Intern)", "ai engineer intern", "Data Engineer - INTERN, Summer 2027"]:
            self.assertEqual(rules.judge(posting(t), RESUME)["verdict"], "not_relevant", t)


class TestLookalikesNotExcluded(unittest.TestCase):
    """A substring fix ('intern' in title) would exclude these. They must stay relevant. They pass before the patch."""

    def test_internal_international_internals_stay_relevant(self):
        for t in ["Data Engineer, Internal Tools", "ML Engineer, International Expansion",
                  "Data Platform Engineer - Database Internals"]:
            self.assertEqual(rules.judge(posting(t), RESUME)["verdict"], "relevant", t)

    def test_control_same_posting_without_intern_is_relevant(self):
        self.assertEqual(rules.judge(posting("Data Scientist (2027 Start)"), RESUME)["verdict"], "relevant")


if __name__ == "__main__":
    unittest.main()
