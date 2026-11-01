"""Boundary cases for the four checks (CONTRACT.md, The rule). Constructed postings."""
import unittest

from jobwatch import rule
from tests.helpers import RESUME, make_posting

SKILLS_OK = "<p>Python, Redis &amp; Kubernetes.</p>"


def verdict(title, content=SKILLS_OK, **kw):
    return rule.classify(make_posting(1, title, content, **kw), RESUME)


class TitleAndSeniority(unittest.TestCase):
    def test_target_titles_pass(self):
        for title in ("Software Engineer", "Backend Engineer, Billing", "Back-End Developer", "Software Engineer I"):
            self.assertTrue(verdict(title)["checks"]["title"], title)

    def test_sales_engineer_fails_title(self):
        self.assertFalse(verdict("Sales Engineer")["checks"]["title"])

    def test_engineer_ii_is_deliberately_allowed(self):
        self.assertEqual(verdict("Software Engineer II - Recommendations")["verdict"], rule.RELEVANT)

    def test_excluded_seniority_overrides_title(self):
        for title in ("Senior Software Engineer", "Sr. Software Engineer", "Staff Software Engineer",
                      "Software Engineer III", "Lead Software Engineer", "Software Engineer Intern"):
            r = verdict(title)
            self.assertTrue(r["checks"]["title"], title)
            self.assertFalse(r["checks"]["seniority"], title)
            self.assertEqual(r["verdict"], rule.NOT_RELEVANT, title)

    def test_seniority_words_are_whole_words(self):
        # "leadership" is not "lead"; "Engineer II" is not "Engineer III"
        self.assertTrue(verdict("Software Engineer, Leadership Tools")["checks"]["seniority"])
        self.assertTrue(verdict("Software Engineer II")["checks"]["seniority"])


class Location(unittest.TestCase):
    def test_boston_in_offices_is_enough(self):
        self.assertTrue(verdict("Software Engineer", location="Hybrid", offices=("London", "Boston"))["checks"]["location"])

    def test_us_remote_patterns_pass(self):
        for loc in ("Remote - US", "Remote, US", "United States - Remote", "US Remote"):
            self.assertTrue(verdict("Software Engineer", location=loc, offices=())["checks"]["location"], loc)

    def test_other_remote_and_distributed_fail(self):
        for loc in ("Distributed", "Remote - Canada", "Remote - Europe", "Remote - Massachusetts", "Remote - USA"):
            self.assertFalse(verdict("Software Engineer", location=loc, offices=())["checks"]["location"], loc)

    def test_boston_only_in_description_fails(self):
        r = verdict("Software Engineer", "<p>Python and Redis. Our Boston office is lovely.</p>",
                    location="London, UK", offices=("London",))
        self.assertFalse(r["checks"]["location"])

    def test_missing_structured_location_fails(self):
        self.assertFalse(verdict("Software Engineer", location=None, offices=())["checks"]["location"])


class Skills(unittest.TestCase):
    def test_threshold_is_two_distinct_skills(self):
        self.assertFalse(verdict("Software Engineer", "<p>Python, python, PYTHON.</p>")["checks"]["skills"])
        self.assertTrue(verdict("Software Engineer", "<p>Python and Docker.</p>")["checks"]["skills"])

    def test_postgres_is_not_postgresql(self):
        r = verdict("Software Engineer", "<p>Python with Postgres.</p>")
        self.assertEqual([m["skill"] for m in r["details"]["skills"]["matched"]], ["Python"])

    def test_distributed_systems_is_a_phrase_across_whitespace_and_tags(self):
        r = verdict("Software Engineer", "<p>Python. Distributed\n<b>systems</b> at scale.</p>")
        self.assertIn("Distributed Systems", [m["skill"] for m in r["details"]["skills"]["matched"]])
        r = verdict("Software Engineer", "<p>Python. Distributed teams, systems thinking.</p>")
        self.assertNotIn("Distributed Systems", [m["skill"] for m in r["details"]["skills"]["matched"]])

    def test_escaped_html_is_decoded_before_matching(self):
        r = verdict("Software Engineer", "&lt;li&gt;Python&lt;/li&gt;&lt;li&gt;Redis&lt;/li&gt;")
        self.assertTrue(r["checks"]["skills"])

    def test_every_check_is_reported_even_when_several_fail(self):
        r = verdict("Senior Sales Engineer", "<p>Nothing here.</p>", location="Tokyo", offices=())
        self.assertEqual(r["checks"], {"title": False, "seniority": False, "location": False, "skills": False})
        self.assertEqual(len([l for l in r["justification"] if "FAIL" in l or "failed" in l]), 4)


if __name__ == "__main__":
    unittest.main()
