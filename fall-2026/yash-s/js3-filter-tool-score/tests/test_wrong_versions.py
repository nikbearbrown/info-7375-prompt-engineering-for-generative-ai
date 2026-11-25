"""FILTER.md section 9: tests that must catch my four wrong versions.
All postings here are CONSTRUCTED."""
import unittest

from helpers import J, P, evaluate, exp, rules


class WV1SubstringMatching(unittest.TestCase):
    def test_ai_is_not_found_inside_email(self):
        self.assertFalse(J.has("AI", "Send us an email"))

    def test_research_engineer_with_email_in_title_is_not_a_target_role(self):
        role, _ = J.title_role("Research Engineer, Email Delivery", rules())
        self.assertNotEqual(role, "target")

    def test_sql_is_not_found_inside_postgresql(self):
        self.assertEqual(J.skills("Experience with PostgreSQL and MySQL.", rules()), [])

    def test_lead_does_not_match_leader_so_leader_is_listed(self):
        self.assertFalse(J.has("Lead", "AI Transformation Leader"))
        self.assertEqual(J.seniority_in_title("AI Transformation Leader", rules()), "Leader")


class WV2CountingBoilerplate(unittest.TestCase):
    COMPANY = "We build the world's best data and AI infrastructure platform."  # CONSTRUCTED sentence

    def body(self):
        return f"<p>{self.COMPANY}</p><p>Write Python.</p>"

    def entry(self, label, reviewed_on):
        return {"board": "Databricks", "sentence": self.COMPANY, "label": label, "reviewed_on": reviewed_on}

    def test_approved_boilerplate_sentence_earns_no_points(self):
        r = evaluate(body=self.body(), rules=rules([self.entry("company boilerplate", "2026-11-18")]))
        self.assertEqual(r["topics"], {})
        self.assertEqual(r["boilerplate_sentences_removed"], 1)

    def test_frequent_sentence_i_have_not_approved_still_counts(self):
        for label, date in (("", ""), ("job-specific", "2026-11-18"), ("company boilerplate", "")):
            with self.subTest(label=label, date=date):
                r = evaluate(body=self.body(), rules=rules([self.entry(label, date)]))
                self.assertIn("AI systems", r["topics"])
                self.assertEqual(r["boilerplate_sentences_removed"], 0)

    def test_approval_applies_only_to_its_own_board(self):
        r = evaluate(body=self.body(), board="OpenAI", rules=rules([self.entry("company boilerplate", "2026-11-18")]))
        self.assertIn("AI systems", r["topics"])

    def test_databricks_and_unity_catalog_are_never_skills(self):
        self.assertEqual(J.skills("Hands-on with Databricks and Unity Catalog.", rules()), [])
        self.assertNotIn("Databricks", rules()["skills"])
        self.assertNotIn("Unity Catalog", rules()["skills"])

    def test_standalone_ai_and_artificial_intelligence_earn_no_topic_points(self):
        r = evaluate(body="<p>We are an AI company advancing artificial intelligence.</p>")
        self.assertEqual(r["topics"], {})
        self.assertEqual(r["points"]["topics"], 0)


class WV3USLocation(unittest.TestCase):
    def test_known_us_cities_without_a_country_are_us(self):
        for loc in ("San Francisco", "Seattle", "Mountain View", "New York City", "San Francisco · Seattle"):
            with self.subTest(loc=loc):
                self.assertEqual(J.location(loc, rules())["status"], "us")

    def test_us_city_posting_is_not_rejected_for_location(self):
        r = evaluate(location="Seattle")
        self.assertEqual(r["location_status"], "us")
        self.assertNotIn("every location part is outside the US", r["hard_exclusions"])

    def test_us_remote_forms_are_us_and_ontario_remote_is_unknown(self):
        self.assertEqual(J.location("US - Remote", rules())["status"], "us")
        self.assertEqual(J.location("Remote-Friendly, United States", rules())["status"], "us")
        self.assertEqual(J.location("Ontario - Remote", rules())["status"], "unknown")

    def test_unknown_remote_locations_are_not_us(self):
        for loc in ("Remote", "Remote-Friendly (Travel Required)", "USCA", ""):
            with self.subTest(loc=loc):
                r = evaluate(location=loc)
                self.assertEqual(r["location_status"], "unknown")
                self.assertEqual(r["points"]["location"], 0)
                self.assertNotEqual(r["decision"], "confirmed")


class WV4MissingExperience(unittest.TestCase):
    def test_missing_experience_is_unknown_and_never_confirmed(self):
        body = "<p>You will build data pipelines and machine learning models in Python and SQL on AWS.</p>"
        r = evaluate(body=body)
        self.assertEqual(r["experience_status"], "unknown")
        self.assertEqual(r["points"]["experience"], 0)
        self.assertEqual(r["decision"], "review")
        self.assertTrue(any(x.startswith("experience unknown") for x in r["review_reasons"]))


if __name__ == "__main__":
    unittest.main()
