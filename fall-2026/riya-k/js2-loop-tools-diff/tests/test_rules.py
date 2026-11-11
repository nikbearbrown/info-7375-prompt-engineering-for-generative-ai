"""JS1 rule tests, copied unchanged from ../js1-contract-and-watch/tests/test_agent.py (class TestRule).
Postings here are CONSTRUCTED test inputs.  Run: python3 -m unittest discover -s tests -v
"""

import json
import unittest
from pathlib import Path

from jsagent import rules

ROOT = Path(__file__).resolve().parent.parent
RESUME = json.loads((ROOT / "persona" / "arya-sahni.json").read_text())

def posting(pid, title, content="", location="Boston, Massachusetts"):
    return {"id": pid, "title": title, "content": content, "location": {"name": location}}


GOOD = posting(1, "AI Engineer", "<p>We use Python and SQL with MLflow.</p>")
SENIOR = posting(2, "Senior AI Engineer", "<p>Python, SQL, MLflow.</p>")
SALES = posting(3, "Account Executive", "<p>Python, SQL.</p>")


class TestRule(unittest.TestCase):
    """Hand-computed cases: each expected verdict follows from CONTRACT.md 'The rule'."""

    def test_title_word_two_skills_us_is_relevant(self):
        v = rules.judge(GOOD, RESUME)
        self.assertEqual(v["verdict"], "relevant")
        self.assertIn("skills.languages: Python", v["justification"])

    def test_seniority_word_excludes(self):
        self.assertEqual(rules.judge(SENIOR, RESUME)["verdict"], "not_relevant")
        self.assertEqual(rules.judge(posting(4, "Sr. Data Engineer", "Python SQL"), RESUME)["verdict"], "not_relevant")

    def test_no_title_word_excludes(self):
        self.assertEqual(rules.judge(SALES, RESUME)["verdict"], "not_relevant")

    def test_one_skill_is_not_enough(self):
        self.assertEqual(rules.judge(posting(5, "Data Engineer", "Python only"), RESUME)["verdict"], "not_relevant")

    def test_databricks_is_not_a_free_skill(self):
        p = posting(6, "Data Engineer", "Databricks and Python")
        self.assertEqual(rules.judge(p, RESUME)["verdict"], "not_relevant")
        # Amendment 1: Unity Catalog is in Databricks' boilerplate, so it is not counted either.
        p = posting(8, "Data Engineer", "Python. Databricks offers ... Lakehouse, and Unity Catalog.")
        self.assertEqual(rules.judge(p, RESUME)["verdict"], "not_relevant")

    def test_location(self):
        self.assertTrue(rules.is_us_location("Remote - California"))
        self.assertTrue(rules.is_us_location("Northeast - United States"))
        self.assertTrue(rules.is_us_location("Remote"))
        self.assertFalse(rules.is_us_location("London, United Kingdom"))
        self.assertFalse(rules.is_us_location("Remote - Germany"))
        self.assertFalse(rules.is_us_location("Bengaluru, India"))
        # Amendment 2: state codes are capitals only, so "Montréal" is not Alabama.
        self.assertFalse(rules.is_us_location("Montréal, Canada"))
        self.assertTrue(rules.is_us_location("Austin, TX"))

    def test_out_fields_present(self):
        v = rules.judge({**GOOD, "absolute_url": "https://example.com/1"}, RESUME)
        self.assertEqual((v["location"], v["url"]), ("Boston, Massachusetts", "https://example.com/1"))

    def test_extra_substring_skill_match_is_caught(self):
        # Extra check: 'SQL' inside 'NoSQL' and 'AI' inside 'maintain' must not count.
        self.assertFalse(rules.find_word("SQL", "experience with NoSQL stores"))
        self.assertFalse(rules.find_word("AI", "maintain pipelines"))
        p = posting(7, "Data Engineer", "NoSQL and Python")
        self.assertEqual(rules.judge(p, RESUME)["verdict"], "not_relevant")


if __name__ == "__main__":
    unittest.main()
