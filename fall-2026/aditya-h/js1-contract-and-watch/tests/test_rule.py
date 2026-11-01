"""Tests for the rule judge, written from CONTRACT.md before the implementation existed.

Posting titles, location names, and office names below are copied from the
public Stripe Greenhouse board as fetched on 2026-10-31. The posting ids and
the "Business Park, Dublin" location are constructed for testing.
"""
import json
import pathlib
import unittest

from jobwatch import fields, rule

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAYA = json.loads((ROOT / "personas" / "maya-sehgal.resume.json").read_text())


def posting(pid, title, location, offices, content=""):
    return {
        "id": pid,
        "title": title,
        "location": {"name": location},
        "offices": [{"name": o} for o in offices],
        "content": content,
    }


# (posting, expected verdict) — expected verdicts derived by hand from CONTRACT.md
CASES = [
    (posting(1, "Product Manager, Ecosystem Risk", "Toronto", ["Canada Locations"]), "not_relevant"),
    (posting(2, "Staff Product Manager, Connect", "N/A", ["US"]), "relevant"),
    (posting(3, "Product Marketing Manager", "San Francisco", ["US"]), "not_relevant"),
    (posting(4, "Engineering Manager, Accounting Products", "Seattle", ["US"]), "not_relevant"),
    (posting(5, "Staff Product Manager, Billing", "SF, NY, SEA, Remote-US", ["US"]), "relevant"),
    (posting(6, "Product Manager: New Grad Accelerator", "San Francisco, New York City, Seattle", ["US-SF-HQ"]), "relevant"),
    (posting(7, "Product Manager, Support Platform", "Business Park, Dublin", ["Ireland Locations"]), "not_relevant"),
    (posting(8, "Product Strategy & Operations APAC", "Singapore", ["Singapore Locations"]), "not_relevant"),
    (posting(9, "Startup Products Strategy & Operations, Product Strategy", "US-Remote", ["US"]), "relevant"),
    (posting(10, "Staff Product Manager, Mobile", "New York City, Toronto, Chicago, or Remote", ["US"]), "relevant"),
    (posting(11, "Software Engineer, Payments", "N/A", ["Brazil Locations"]), "not_relevant"),
]


class TitleCheck(unittest.TestCase):
    def test_phrases_match_case_and_whitespace_insensitive(self):
        p = posting(20, "Product Manager,  Startup  Products", "NYC", ["US"])
        self.assertEqual(rule.judge(p, MAYA)["verdict"], "relevant")

    def test_all_seniority_levels_accepted(self):
        for t in ("Senior Staff Product Manager, Risk", "Senior Product Manager, Enterprise",
                  "Product Manager: New Grad Accelerator"):
            with self.subTest(title=t):
                self.assertEqual(rule.judge(posting(21, t, "US", ["US"]), MAYA)["verdict"], "relevant")

    def test_product_analyst_and_owner_families(self):
        for t in ("Product Analyst, Billing", "Product Owner, Terminal", "Product Operations Lead"):
            with self.subTest(title=t):
                self.assertEqual(rule.judge(posting(22, t, "US", ["US"]), MAYA)["verdict"], "relevant")

    def test_abbreviation_pm_does_not_match(self):
        self.assertEqual(rule.judge(posting(23, "Senior PM, Payments", "US", ["US"]), MAYA)["verdict"], "not_relevant")

    def test_body_alone_never_makes_relevant(self):
        p = posting(24, "Android Engineer, Identity", "US-Remote", ["US"],
                    content="You will partner with the product manager and product analyst.")
        self.assertEqual(rule.judge(p, MAYA)["verdict"], "not_relevant")

    def test_missing_title_fails_with_reason(self):
        p = posting(25, "", "US", ["US"])
        j = rule.judge(p, MAYA)
        self.assertEqual(j["verdict"], "not_relevant")
        self.assertIn("title missing", j["reason"])


class LocationCheck(unittest.TestCase):
    def test_us_inside_word_does_not_match(self):
        p = posting(30, "Product Manager, Support Platform", "Business Park, Dublin", ["Ireland Locations"])
        self.assertEqual(rule.judge(p, MAYA)["verdict"], "not_relevant")

    def test_remote_without_country_is_not_us(self):
        p = posting(31, "Product Manager, X", "Remote", [])
        j = rule.judge(p, MAYA)
        self.assertEqual(j["verdict"], "not_relevant")
        self.assertIn("location not US / unknown", j["reason"])

    def test_na_location_uses_offices_only(self):
        self.assertEqual(rule.judge(posting(32, "Product Manager, X", "N/A", ["US"]), MAYA)["verdict"], "relevant")
        self.assertEqual(rule.judge(posting(33, "Product Manager, X", "N/A", ["Canada Locations"]), MAYA)["verdict"],
                         "not_relevant")

    def test_mixed_us_and_non_us_passes(self):
        self.assertEqual(rule.judge(posting(34, "Product Manager, X", "New York, Toronto", []), MAYA)["verdict"],
                         "relevant")

    def test_office_prefix_is_case_sensitive(self):
        self.assertEqual(rule.judge(posting(35, "Product Manager, X", "N/A", ["us-remote"]), MAYA)["verdict"],
                         "not_relevant")

    def test_both_checks_always_reported(self):
        j = rule.judge(posting(36, "Data Scientist", "Toronto", ["Canada Locations"]), MAYA)
        self.assertIn("title", j["checks"])
        self.assertIn("location", j["checks"])
        self.assertFalse(j["checks"]["title"]["pass"])
        self.assertFalse(j["checks"]["location"]["pass"])


class WrongVersion1_LabelsOnWrongPostings(unittest.TestCase):
    """CONTRACT wrong version 1: verdicts must travel with posting ids, not list positions."""

    def test_verdicts_stay_with_ids_when_order_reversed(self):
        expected = {p["id"]: v for p, v in CASES}
        postings = [p for p, _ in CASES]
        forward = {j["posting_id"]: j["verdict"] for j in rule.judge_all(postings, MAYA)}
        backward = {j["posting_id"]: j["verdict"] for j in rule.judge_all(list(reversed(postings)), MAYA)}
        self.assertEqual(forward, expected)
        self.assertEqual(backward, expected)

    def test_each_hand_labelled_case(self):
        for p, v in CASES:
            with self.subTest(title=p["title"]):
                self.assertEqual(rule.judge(p, MAYA)["verdict"], v)


class WrongVersion2_JustificationCitesNothing(unittest.TestCase):
    """CONTRACT wrong version 2: every justification must cite real résumé and posting fields."""

    def test_every_justification_cites_real_fields(self):
        for p, _ in CASES:
            with self.subTest(title=p["title"]):
                j = rule.judge(p, MAYA)
                self.assertTrue(j["resume_fields"], "no résumé field cited")
                self.assertTrue(j["posting_fields"], "no posting field cited")
                for path, value in j["resume_fields"].items():
                    self.assertEqual(fields.resolve(MAYA, path), value)
                for path, value in j["posting_fields"].items():
                    self.assertEqual(fields.resolve(p, path), value)
                self.assertTrue(j["reason"].strip())

    def test_skills_in_body_are_context_only(self):
        p = posting(40, "Data Scientist", "US", ["US"], content="Experience with SQL and Power BI.")
        j = rule.judge(p, MAYA)
        self.assertEqual(j["verdict"], "not_relevant")
        self.assertIn("SQL", j["skills_in_content"])


class WrongVersion3_SubstringFalsePositive(unittest.TestCase):
    """CONTRACT wrong version 3: phrase matching, not loose substrings."""

    def test_contract_listed_cases(self):
        cases = [
            (posting(50, "Product Marketing Manager", "US", ["US"]), "not_relevant"),
            (posting(51, "Engineering Manager, Accounting Products", "US", ["US"]), "not_relevant"),
            (posting(52, "Staff Product Manager, Billing", "US", ["US"]), "relevant"),
            (posting(53, "Product Manager: New Grad Accelerator", "SF", ["US-SF-HQ"]), "relevant"),
            (posting(54, "Product Manager, Support Platform", "Business Park, Dublin", ["Ireland Locations"]),
             "not_relevant"),
        ]
        for p, v in cases:
            with self.subTest(title=p["title"], loc=p["location"]["name"]):
                self.assertEqual(rule.judge(p, MAYA)["verdict"], v)


class FieldResolution(unittest.TestCase):
    def test_resolve_paths(self):
        self.assertEqual(fields.resolve(MAYA, "experience[0].title"), "AI Product Manager")
        self.assertEqual(fields.resolve(MAYA, "personal.location"), "Boston, MA")
        with self.assertRaises(KeyError):
            fields.resolve(MAYA, "experience[9].title")
        with self.assertRaises(KeyError):
            fields.resolve(MAYA, "personal.salary")


if __name__ == "__main__":
    unittest.main()
