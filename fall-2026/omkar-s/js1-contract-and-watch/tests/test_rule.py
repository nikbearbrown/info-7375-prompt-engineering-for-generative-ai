"""The written rule (CONTRACT.md "The rule"). Written by Claude Code, 2026-10-25."""
import copy
import json
import os
import unittest

from jsagent import rule, persona

HERE = os.path.dirname(__file__)
RESUME = persona.load(os.path.join(HERE, "..", "persona", "aarav-patel.example.json"))


def post(title="Software Engineer", loc="Boston, MA", content=""):
    return {"id": 1, "title": title, "location": {"name": loc}, "content": content}


class ClauseA(unittest.TestCase):
    def test_title_must_contain_software_engineer(self):
        self.assertTrue(rule.judge(post("Software Engineer II - Recommendations"), RESUME)["clauses"]["A"]["pass"])
        self.assertTrue(rule.judge(post("Senior Software Engineer - Growth"), RESUME)["clauses"]["A"]["pass"])
        self.assertFalse(rule.judge(post("Staff Engineer, Applied AI"), RESUME)["clauses"]["A"]["pass"])
        self.assertFalse(rule.judge(post("Analytics Engineer"), RESUME)["clauses"]["A"]["pass"])

    def test_no_seniority_gate(self):
        r = rule.judge(post("Principal Software Engineer", content="Python and Kafka"), RESUME)
        self.assertEqual(r["verdict"], "relevant")


US_OFFICE = [{"name": "Boston", "location": "Boston, Massachusetts, United States"}]
DE_OFFICE = [{"name": "Munich", "location": "M\u00fcnchen, Bavaria, Germany"}]
UK_OFFICE = [{"name": "London", "location": "London, England, United Kingdom"}]


class ClauseB(unittest.TestCase):
    """Contract v2 (2026-10-26): any US location."""

    def test_locations(self):
        cases = [("Boston, MA", [], True), ("Boston, MA; Denver, CO", US_OFFICE, True),
                 ("Denver, CO", US_OFFICE, True), ("San Francisco, CA", US_OFFICE, True),
                 ("Remote - US", [], True), ("Remote, United States", [], True),
                 ("Remote - UK", UK_OFFICE, False), ("London, UK", UK_OFFICE, False),
                 ("Singapore", [], False), ("", [], False)]
        for loc, offices, want in cases:
            with self.subTest(loc=loc):
                self.assertEqual(rule.location_ok(loc, offices)[0], want)

    def test_state_code_that_is_also_a_country_needs_a_us_office(self):
        self.assertFalse(rule.location_ok("Munich, DE", DE_OFFICE)[0])   # Germany, not Delaware
        self.assertTrue(rule.location_ok("Wilmington, DE", US_OFFICE)[0])
        self.assertFalse(rule.location_ok("Denver, CO", [])[0])          # no office data: not provable


class ClauseC(unittest.TestCase):
    def c(self, content):
        return rule.judge(post(content=content), RESUME)["clauses"]["C"]

    def test_two_skills_pass_one_fails(self):
        self.assertTrue(self.c("Python and Redis")["pass"])
        self.assertFalse(self.c("Python only")["pass"])

    def test_whole_word_only(self):
        self.assertEqual(self.c("JavaScript, MySQL, PostgreSQLx")["found"], [])
        self.assertEqual(sorted(self.c("Java; SQL; PostgreSQL.")["found"]), ["Java", "PostgreSQL", "SQL"])

    def test_familiar_with_not_shipped_never_counts(self):
        r = self.c("Rust, Terraform and Python")
        self.assertEqual(r["found"], ["Python"])
        self.assertFalse(r["pass"])

    def test_double_escaped_html_is_cleaned(self):
        self.assertEqual(rule.clean_content("&lt;p&gt;Node.js &amp;amp; Kafka&lt;/p&gt;"), "Node.js & Kafka")
        self.assertTrue(self.c("&lt;li&gt;Node.js&lt;/li&gt;&lt;li&gt;Kafka&lt;/li&gt;")["pass"])

    def test_skill_counted_once(self):
        r = self.c("Python Python Python")
        self.assertFalse(r["pass"])


class Justification(unittest.TestCase):
    def test_each_clause_line_names_resume_and_posting_fields(self):
        r = rule.judge(post("Software Engineer", "Boston, MA", "Python, Kafka"), RESUME)
        a, b, c, v = r["justification"]
        for line in (a, b, c):
            self.assertIn("posting.", line)
            self.assertIn("resume.", line)
        self.assertIn('posting.title="Software Engineer"', a)
        self.assertIn('posting.location.name="Boston, MA"', b)
        self.assertIn("resume.skills.languages[Python]", c)
        self.assertIn("resume.skills.backend_automation[Kafka]", c)
        self.assertTrue(v.startswith("verdict: relevant"))

    def test_verdict_is_and_of_clauses(self):
        for t, loc, content, want in [
            ("Software Engineer", "Boston, MA", "Python, Kafka", "relevant"),
            ("Account Executive", "Boston, MA", "Python, Kafka", "not_relevant"),
            ("Software Engineer", "London, UK", "Python, Kafka", "not_relevant"),
            ("Software Engineer", "Singapore", "Python, Kafka", "not_relevant"),
            ("Software Engineer", "Boston, MA", "Python", "not_relevant"),
        ]:
            self.assertEqual(rule.judge(post(t, loc, content), RESUME)["verdict"], want)


if __name__ == "__main__":
    unittest.main()
