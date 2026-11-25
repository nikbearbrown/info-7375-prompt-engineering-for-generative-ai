"""Tests for the claim labeler (earlybird/claims.py). Written BEFORE claims.py.
Each claim is labelled supported / contradicted / insufficient against the posting's own text, with a quote.
All postings here are CONSTRUCTED. Run: python -m unittest discover -s tests"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from earlybird import claims  # noqa: E402
from earlybird.resume import load_resume  # noqa: E402
from cases import posting  # noqa: E402

RESUME = load_resume(ROOT / "data/resume/rohan-desai.example.json")


def label(p, name):
    got = {c["claim"]: c for c in claims.label_claims(p, RESUME)}
    return got[name]


class EarlyCareer(unittest.TestCase):
    def test_supported_when_all_years_below_three(self):
        c = label(posting("Software Engineer", desc="You have 1+ years of experience."), "early_career")
        self.assertEqual(c["label"], "supported")
        self.assertIn("1+ years", c["quote"])

    def test_contradicted_by_a_digit(self):
        self.assertEqual(label(posting("Software Engineer", desc="5+ years of experience"), "early_career")["label"],
                         "contradicted")

    def test_contradicted_by_a_spelled_number(self):  # the digit-only regex of v1 would miss this
        c = label(posting("Software Engineer", desc="At least five years of experience."), "early_career")
        self.assertEqual(c["label"], "contradicted")

    def test_en_dash_range_uses_the_minimum(self):  # found on real Stripe/Commure text; filter and labeler must agree
        for text in ("Minimum requirements 2–12+ years of industry experience", "1–4 years of experience",
                     "2-12+ years of experience"):
            c = label(posting("Software Engineer", desc=text), "early_career")
            self.assertEqual(c["label"], "supported", text)

    def test_range_whose_minimum_is_three_is_contradicted(self):
        c = label(posting("Software Engineer", desc="3–5 years of experience"), "early_career")
        self.assertEqual(c["label"], "contradicted")

    def test_insufficient_when_no_years_stated(self):  # relevant title is NOT evidence of level
        self.assertEqual(label(posting("Software Engineer"), "early_career")["label"], "insufficient")


class Sponsorship(unittest.TestCase):
    def test_absence_is_insufficient_not_supported(self):
        self.assertEqual(label(posting("Software Engineer"), "sponsorship")["label"], "insufficient")

    def test_supported_only_by_an_offer(self):
        c = label(posting("Software Engineer", desc="Visa sponsorship is available for this role."), "sponsorship")
        self.assertEqual(c["label"], "supported")

    def test_contradicted_by_a_refusal(self):
        c = label(posting("Software Engineer", desc="We are unable to sponsor visas."), "sponsorship")
        self.assertEqual(c["label"], "contradicted")

    def test_executive_sponsorship_is_a_false_friend(self):
        c = label(posting("Solutions Architect", desc="Gain executive sponsorship for deployments."), "sponsorship")
        self.assertEqual(c["label"], "insufficient")


class Clearance(unittest.TestCase):
    def test_supported_only_when_the_text_says_none_needed(self):
        c = label(posting("Software Engineer", desc="No security clearance is required."), "no_clearance")
        self.assertEqual(c["label"], "supported")

    def test_silence_is_insufficient(self):
        self.assertEqual(label(posting("Software Engineer"), "no_clearance")["label"], "insufficient")

    def test_contradicted_by_a_requirement(self):
        c = label(posting("Software Engineer", desc="Active TS/SCI security clearance required."), "no_clearance")
        self.assertEqual(c["label"], "contradicted")


class Location(unittest.TestCase):
    def test_supported_quotes_the_location(self):
        c = label(posting("Software Engineer", location="Seattle, WA, United States"), "us_location")
        self.assertEqual(c["label"], "supported")
        self.assertIn("Seattle", c["quote"])

    def test_missing_location_is_insufficient(self):
        self.assertEqual(label(posting("Software Engineer", location=None, country=None), "us_location")["label"],
                         "insufficient")


class StackFit(unittest.TestCase):
    """v2 of stack_fit (Vrajesh's hand labels on claim-check items 5, 18, 24): supported only for technologies in the
    persona's documented shipped project (ledgerline: Go, Postgres, GraphQL, Terraform, DigitalOcean). Technologies in
    'or' or slash lists still count (Vrajesh's decision after items 22-24 conflicted)."""

    def test_supported_quotes_a_shipped_technology(self):
        c = label(posting("Software Engineer", desc="Our stack: Go, PostgreSQL and Terraform."), "stack_fit")
        self.assertEqual(c["label"], "supported")
        self.assertIn("Terraform", c["quote"])

    def test_listed_skill_that_was_not_shipped_is_insufficient(self):  # claim-check item 5 pattern
        c = label(posting("Software Engineer", desc="Any language (e.g., Python, Java, Kotlin, etc.) is fine."),
                  "stack_fit")
        self.assertEqual(c["label"], "insufficient")

    def test_python_alone_is_insufficient(self):
        self.assertEqual(label(posting("Software Engineer", desc="You write Python daily."), "stack_fit")["label"],
                         "insufficient")

    def test_or_list_still_counts(self):  # Vrajesh, 2026-11-25: option lists count (claim-check items 22, 23)
        c = label(posting("Software Engineer", desc="You are proficient in GoLang, or Java with depth."), "stack_fit")
        self.assertEqual(c["label"], "supported")

    def test_slash_list_still_counts(self):  # items 22 vs 24 conflict; Vrajesh chose "they count"
        c = label(posting("Software Engineer", desc="Process that data using C++/Java/Python/Go."), "stack_fit")
        self.assertEqual(c["label"], "supported")

    def test_golang_any_capitalisation(self):  # claim-check item 23 wrote "GoLang"
        c = label(posting("Software Engineer", desc="You are proficient in GoLang and build services."), "stack_fit")
        self.assertEqual(c["label"], "supported")

    def test_go_to_market_is_a_false_friend(self):
        c = label(posting("Software Engineer", desc="Own the go-to-market plan. Go to market fast."), "stack_fit")
        self.assertEqual(c["label"], "insufficient")

    def test_no_skills_named_is_insufficient(self):
        self.assertEqual(label(posting("Software Engineer"), "stack_fit")["label"], "insufficient")


class AiFocus(unittest.TestCase):
    def test_only_asked_for_ai_titles(self):
        names = {c["claim"] for c in claims.label_claims(posting("Backend Engineer"), RESUME)}
        self.assertNotIn("ai_focus", names)

    def test_ai_title_without_ai_text_is_insufficient(self):  # relevance (title words) is not entailment
        c = label(posting("AI Engineer", desc="Build and ship web services with the team."), "ai_focus")
        self.assertEqual(c["label"], "insufficient")

    def test_ai_title_with_llm_text_is_supported(self):
        c = label(posting("AI Engineer", desc="You will build LLM-powered agents."), "ai_focus")
        self.assertEqual(c["label"], "supported")


class EveryClaimHasEvidenceOrAReason(unittest.TestCase):
    def test_supported_and_contradicted_always_quote(self):
        for p in (posting("Software Engineer", desc="1+ years. Python. No security clearance is required."),
                  posting("Software Engineer", desc="6 years. We cannot sponsor. TS/SCI security clearance.")):
            for c in claims.label_claims(p, RESUME):
                if c["label"] != "insufficient":
                    self.assertTrue(c["quote"], c)
                self.assertIn(c["label"], {"supported", "contradicted", "insufficient"})


if __name__ == "__main__":
    unittest.main()
