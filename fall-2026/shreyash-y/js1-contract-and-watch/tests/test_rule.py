"""One test per interpretation in INTERPRETATIONS.md. All postings are CONSTRUCTED."""
import unittest

from jsagent import rule, posting
from tests import helpers


def judge(**kw):
    return rule.judge(posting.normalize(helpers.make_job(900, **kw), "testboard"),
                      helpers.load_persona())


class Title(unittest.TestCase):
    def test_phrase_inside_longer_title(self):
        self.assertNotIn(1, judge(title="Senior Software Engineer, Backend")["failed_conditions"])

    def test_case_insensitive(self):
        self.assertNotIn(1, judge(title="machine learning engineer")["failed_conditions"])

    def test_boundary(self):
        self.assertIn(1, judge(title="MAI Engineer")["failed_conditions"])
        self.assertNotIn(1, judge(title="AI/ML Engineer")["failed_conditions"])

    def test_data_scientist_fails(self):
        self.assertIn(1, judge(title="Data Scientist II")["failed_conditions"])


class Department(unittest.TestCase):
    def test_exact_name_only(self):
        self.assertIn(2, judge(department="Data")["failed_conditions"])
        self.assertNotIn(2, judge(department="data science")["failed_conditions"])

    def test_missing_department_fails_as_missing(self):
        rec = judge(department=None)
        self.assertIn(2, rec["failed_conditions"])
        self.assertIn("missing", rec["justification"])


class Location(unittest.TestCase):
    def test_boston(self):
        self.assertNotIn(3, judge()["failed_conditions"])

    def test_new_york_fails(self):
        self.assertIn(3, judge(location="New York, New York, United States",
                               offices=("New York, NY",))["failed_conditions"])

    def test_remote_with_state_office_passes(self):
        self.assertNotIn(3, judge(location="Remote", offices=("Remote (Florida)",))["failed_conditions"])

    def test_remote_without_any_us_mention_fails(self):
        self.assertIn(3, judge(location="Remote", offices=("Remote",),
                               content="<p>Python and Docker.</p>")["failed_conditions"])

    def test_remote_needs_remote_ok(self):
        resume = dict(helpers.load_persona(), remote_ok=False)
        rec = rule.judge(posting.normalize(helpers.make_job(
            900, location="Remote", offices=("Remote (Texas)",)), "testboard"), resume)
        self.assertIn(3, rec["failed_conditions"])


class Skills(unittest.TestCase):
    def test_two_needed(self):
        self.assertIn(4, judge(content="<p>Python only.</p>")["failed_conditions"])
        self.assertNotIn(4, judge(content="<p>Python and SQL.</p>")["failed_conditions"])

    def test_whole_terms(self):
        rec = judge(content="<p>JavaScript and PostgreSQL and Python.</p>")
        self.assertIn(4, rec["failed_conditions"])

    def test_known_weakness_react_verb(self):
        # INTERPRETATIONS.md keeps this weakness as written: "react" the verb counts.
        self.assertNotIn(4, judge(content="<p>Python. Able to react quickly.</p>")["failed_conditions"])


class Experience(unittest.TestCase):
    def test_largest_requirement_wins(self):
        rec = judge(content="<p>Python, SQL. 5+ years of software experience. "
                            "2+ years of experience with LLMs.</p>")
        self.assertIn(5, rec["failed_conditions"])
        self.assertIn("5", rec["justification"])

    def test_three_passes(self):
        self.assertNotIn(5, judge(content="<p>Python, SQL. 3+ years of experience.</p>")["failed_conditions"])

    def test_range_takes_lower(self):
        self.assertNotIn(5, judge(content="<p>Python, SQL. 2-4 years of experience.</p>")["failed_conditions"])

    def test_number_word(self):
        self.assertIn(5, judge(content="<p>Python, SQL. Five years of experience.</p>")["failed_conditions"])

    def test_none_stated_passes_and_says_so(self):
        rec = judge(content="<p>Python and SQL.</p>")
        self.assertNotIn(5, rec["failed_conditions"])
        self.assertIn("no experience requirement stated", rec["justification"])

    def test_years_not_about_experience_ignored(self):
        rec = judge(content="<p>Python, SQL. Founded 12 years ago. 2 years of experience.</p>")
        self.assertNotIn(5, rec["failed_conditions"])


class Exclusions(unittest.TestCase):
    def test_title_words(self):
        for t in ("Staff Software Engineer", "Software Engineer Lead", "Principal ML Engineer",
                  "Director, Software Engineering", "Software Engineering Manager"):
            self.assertIn(6, judge(title=t)["failed_conditions"], t)

    def test_leader_is_not_lead(self):
        self.assertNotIn(6, judge(title="Software Engineer, Team Leader")["failed_conditions"])

    def test_unpaid_contract_relocation(self):
        self.assertIn(6, judge(content="<p>Python, SQL. This is an unpaid internship.</p>")["failed_conditions"])
        self.assertIn(6, judge(title="Software Engineer (Contract)")["failed_conditions"])
        self.assertIn(6, judge(location="Remote", offices=("Remote (Texas)",),
                               content="<p>Python, SQL. You must relocate to Austin.</p>")["failed_conditions"])
        self.assertNotIn(6, judge(content="<p>Python, SQL. Relocation assistance offered.</p>")["failed_conditions"])


class Decision(unittest.TestCase):
    def test_relevant_only_when_all_pass(self):
        rec = judge()
        self.assertEqual(rec["verdict"], "Relevant")
        self.assertEqual(rec["failed_conditions"], [])

    def test_conditions_listed_in_record(self):
        rec = judge(title="Staff Data Scientist", department="Data")
        self.assertEqual(rec["verdict"], "Not Relevant")
        self.assertEqual(rec["failed_conditions"], [1, 2, 6])

    def test_label_is_record(self):
        self.assertEqual(judge()["judge"], "rule (record)")


if __name__ == "__main__":
    unittest.main()
