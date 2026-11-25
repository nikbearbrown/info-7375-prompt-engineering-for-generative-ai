"""FILTER.md v1, rules F1-F4 and the abstention rule. Written from FILTER.md before agent3 existed.

Every posting here is CONSTRUCTED (tests/js3_helpers.py), not collected.
"""
import unittest

from tests.js3_helpers import ashby, body, gh, skills, verdict, FILLER


class ShippedSkills(unittest.TestCase):
    def test_ten_shipped_skills_and_not_the_familiar_ones(self):
        found = skills()
        self.assertEqual(len(found), 10)
        self.assertEqual(set(found), {"Python", "SQL", "Databricks", "Unity Catalog", "Power BI",
                                      "LangGraph", "MLflow", "Mem0", "Delta Lake", "AWS"})
        self.assertNotIn("Ray", found)
        self.assertNotIn("Kubeflow", found)


class Accepted(unittest.TestCase):
    def test_all_four_rules_hold_greenhouse(self):
        v = verdict(gh("Data Scientist", "New York City, NY", body("You will write Python daily.")))
        self.assertEqual(v["verdict"], "accept")
        self.assertFalse(v["abstain"])
        self.assertIsNone(v["rule"])
        self.assertEqual(v["skills_found"], ["Python"])

    def test_all_four_rules_hold_ashby_html(self):
        v = verdict(ashby("Machine Learning Engineer", "US California - Remote",
                          html_text=body("<li>Ship models with <b>MLflow</b>.</li>")))
        self.assertEqual(v["verdict"], "accept")
        self.assertEqual(v["skills_found"], ["MLflow"])

    def test_ashby_falls_back_to_plain_text_when_html_is_empty(self):
        v = verdict(ashby("Data Analyst", "US California - Remote", html_text="",
                          plain_text=FILLER + " Dashboards in Power BI."))
        self.assertEqual(v["verdict"], "accept")
        self.assertEqual(v["skills_found"], ["Power BI"])

    def test_seniority_is_not_judged(self):
        for title in ("Senior Data Scientist", "Staff Machine Learning Engineer"):
            with self.subTest(title=title):
                self.assertEqual(verdict(gh(title, content=body("SQL"))) ["verdict"], "accept")


class F1RoleWords(unittest.TestCase):
    def test_each_role_word_accepts(self):
        for title in ("Data Engineer", "Analytics Engineer", "Business Analyst", "Research Scientist",
                      "Machine Learning Engineer", "ML Platform Engineer", "Engineer, ML/AI", "DATA ANALYST"):
            with self.subTest(title=title):
                self.assertEqual(verdict(gh(title, content=body("SQL")))["verdict"], "accept")

    def test_no_role_word_rejects_on_title(self):
        v = verdict(gh("Software Engineer, Payments", content=body("SQL")))
        self.assertEqual((v["verdict"], v["rule"], v["field"]), ("reject", "F1", "title"))

    def test_role_word_inside_a_longer_word_does_not_count(self):
        for title in ("HTML Email Developer", "Metadata Platform Engineer", "Analysts Program Coordinator"):
            with self.subTest(title=title):
                v = verdict(gh(title, content=body("SQL")))
                self.assertEqual((v["verdict"], v["rule"]), ("reject", "F1"))


class F2Exclusions(unittest.TestCase):
    def test_each_exclusion_rejects(self):
        for title in ("Data Science Manager", "Director, Analytics", "Head of Data",
                      "Lead Data Scientist", "Data Science Intern"):
            with self.subTest(title=title):
                v = verdict(gh(title, content=body("SQL")))
                self.assertEqual((v["verdict"], v["rule"], v["field"]), ("reject", "F2", "title"))

    def test_exclusion_inside_a_longer_word_does_not_count(self):
        for title in ("Data Scientist, Internal Tools", "Analytics Engineer, Leadership Programs",
                      "Data Engineer, Headcount Planning"):
            with self.subTest(title=title):
                self.assertEqual(verdict(gh(title, content=body("SQL")))["verdict"], "accept")


class F3USLocation(unittest.TestCase):
    def test_us_locations_accept(self):
        for location in ("San Francisco, CA", "Kitchener-Waterloo, ON; Toronto, ON; New York City, NY",
                         "Remote - US", "United States - Remote", "United States - Remote ",
                         "US California - Remote"):
            with self.subTest(location=location):
                self.assertEqual(verdict(gh(location=location, content=body("SQL")))["verdict"], "accept")

    def test_non_us_locations_reject(self):
        for location in ("Toronto, ON", "London, UK", "Canada - Remote (ON, AB, BC, or NS Only)",
                         "Remote", "Remote - Canada", "Remote with us!", "Chennai, Tamil Nadu, India"):
            with self.subTest(location=location):
                v = verdict(gh(location=location, content=body("SQL")))
                self.assertEqual((v["verdict"], v["rule"], v["field"]), ("reject", "F3", "location.name"))

    def test_us_office_without_state_code_is_rejected_under_v1(self):
        # FILTER v1 read literally: no part ends in a state code and none says Remote.
        v = verdict(ashby(location="US California (Redwood City) - Office", html_text=body("SQL")))
        self.assertEqual((v["verdict"], v["rule"], v["field"]), ("reject", "F3", "location"))


class F4Skill(unittest.TestCase):
    def test_multi_word_skill_accepts(self):
        v = verdict(gh(content=body("Tables live in Delta Lake under Unity Catalog.")))
        self.assertEqual(v["verdict"], "accept")
        self.assertEqual(v["skills_found"], ["Unity Catalog", "Delta Lake"])

    def test_no_shipped_skill_rejects_on_text(self):
        v = verdict(gh(content=body("We use Spark, PostgreSQL, Pythonic idioms, Ray and Kubeflow.")))
        self.assertEqual((v["verdict"], v["rule"], v["field"]), ("reject", "F4", "content"))
        self.assertEqual(v["skills_found"], [])

    def test_skill_only_inside_html_markup_does_not_count(self):
        v = verdict(gh(content=body('<a href="https://aws.amazon.com/python">our cloud</a>')))
        self.assertEqual((v["verdict"], v["rule"]), ("reject", "F4"))

    def test_first_failing_rule_is_reported(self):
        v = verdict(gh("Product Manager", "London, UK", body("No skills here.")))
        self.assertEqual(v["rule"], "F1")
        v = verdict(gh("Data Manager", "London, UK", body("No skills here.")))
        self.assertEqual(v["rule"], "F2")
        v = verdict(gh("Data Scientist", "London, UK", body("No skills here.")))
        self.assertEqual(v["rule"], "F3")


class MissingFields(unittest.TestCase):
    def check(self, posting, rule, field):
        v = verdict(posting)
        self.assertEqual((v["verdict"], v["rule"], v["field"]), ("reject", rule, field))
        self.assertIn(f"missing: {field}", v["reason"])

    def test_missing_title(self):
        self.check(gh(content=body("SQL"), drop=("title",)), "F1", "title")
        self.check(gh(title="   ", content=body("SQL")), "F1", "title")

    def test_missing_location(self):
        self.check(gh(content=body("SQL"), drop=("location",)), "F3", "location.name")
        self.check(gh(location="", content=body("SQL")), "F3", "location.name")
        self.check(ashby(location=None, html_text=body("SQL")), "F3", "location")

    def test_missing_text(self):
        self.check(gh(drop=("content",)), "F4", "content")
        self.check(ashby(html_text="", plain_text=""), "F4", "descriptionHtml/descriptionPlain")


class Abstention(unittest.TestCase):
    def test_short_text_abstains(self):
        v = verdict(gh(content="<p>" + "x" * 299 + "</p> "))
        self.assertEqual(v["verdict"], "abstain")
        self.assertTrue(v["abstain"])
        self.assertIn("abstain: cannot tell", v["reason"])

    def test_three_hundred_characters_is_enough(self):
        v = verdict(gh(content="<p>" + "SQL " + "x" * 296 + "</p>"))
        self.assertEqual(v["text_chars"], 300)
        self.assertEqual(v["verdict"], "accept")

    def test_length_is_measured_after_removing_html(self):
        padded = "<div class='" + "y" * 400 + "'>SQL is used here.</div>"
        self.assertEqual(verdict(gh(content=padded))["verdict"], "abstain")

    def test_short_text_abstains_even_when_another_rule_would_reject(self):
        self.assertEqual(verdict(gh("Recruiter", "London, UK", "<p>Short.</p>"))["verdict"], "abstain")

    def test_unverified_empty_board_abstains(self):
        v = verdict(gh(content=body("SQL"), board_status="unverified-empty"))
        self.assertEqual(v["verdict"], "abstain")
        self.assertIn("unverified-empty", v["reason"])


if __name__ == "__main__":
    unittest.main()
