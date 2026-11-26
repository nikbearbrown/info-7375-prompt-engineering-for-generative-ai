"""FILTER.md Rule 8 and the section 9 experience cases. Every sentence here is
CONSTRUCTED unless its comment says it is quoted from a saved JS2 posting."""
import unittest

from helpers import evaluate, exp


class ReadingOneRequirement(unittest.TestCase):
    def test_2_plus_years_is_a_minimum_of_two_not_zero_to_two(self):
        e = exp("2+ years of experience in data engineering.")
        self.assertEqual(e["status"], "within_cutoff")
        self.assertEqual(e["decisive_min"], 2)

    def test_2_to_8_years_uses_the_lower_bound(self):
        for s in ("2–8 years of engineering experience.", "2-8 years of engineering experience.",
                  "2 to 8 years of engineering experience."):
            with self.subTest(s=s):
                e = exp(s)
                self.assertEqual(e["status"], "within_cutoff")
                self.assertEqual(e["decisive_min"], 2)

    def test_status_by_minimum(self):
        self.assertEqual(exp("0-1 years of experience in software engineering")["status"], "compatible")
        self.assertEqual(exp("1+ years of experience")["status"], "within_cutoff")
        self.assertEqual(exp("3+ years of experience")["status"], "above_cutoff")
        self.assertEqual(exp("Have 4-6 years of professional software engineering experience")["status"], "above_cutoff")
        self.assertEqual(exp("Three or more years of experience with SQL")["status"], "above_cutoff")

    def test_no_professional_experience_required_is_compatible(self):
        self.assertEqual(exp("No professional experience is required.")["status"], "compatible")


class MultipleRequirements(unittest.TestCase):
    def test_and_requirements_use_the_largest_minimum(self):
        # Quoted from a saved OpenAI Data Engineer posting.
        e = exp("Have 3+ years of experience as a data engineer and 8+ years of any software engineering experience.")
        self.assertEqual(e["status"], "above_cutoff")
        self.assertEqual(e["decisive_min"], 8)
        self.assertEqual(len(e["units"]), 2)

    def test_nested_including_is_and(self):
        e = exp("8+ years of industry experience building production software, including 3+ years leading projects.")
        self.assertEqual(e["decisive_min"], 8)

    def test_clear_or_with_all_alternatives_above_two_rejects(self):
        e = exp("3+ years as a Software Engineer OR 3+ years as a Solutions Architect.")
        self.assertEqual(e["status"], "above_cutoff")
        self.assertEqual([u["kind"] for u in e["units"]], ["OR"])

    def test_clear_or_with_one_compatible_alternative_does_not_reject(self):
        e = exp("4+ years in data engineering OR 0–1 years of software engineering experience.")  # CONSTRUCTED (FILTER.md Rule 8)
        self.assertEqual(e["status"], "compatible")

    def test_or_on_separate_lines_is_linked(self):
        e = exp("Have 4+ years in data infrastructure engineering OR", "Have 0-1 years in infrastructure engineering")
        self.assertEqual([u["kind"] for u in e["units"]], ["OR"])
        self.assertEqual(e["status"], "compatible")

    def test_or_with_a_degree_alternative_is_unknown(self):
        # Quoted from a saved OpenAI Physical Design Engineer posting.
        e = exp("BS w/ 4+ or MS with 2+ years or PhD with 0-1 year(s) of relevant industry experience in physical design")
        self.assertEqual(e["status"], "unknown")
        self.assertIn("degree", e["reason"])

    def test_or_with_both_or_and_and_between_counts_is_unknown(self):
        e = exp("5+ years in data and analytics or 1+ years in machine learning.")
        self.assertEqual(e["status"], "unknown")
        self.assertIn("both 'or' and 'and'", e["reason"])

    def test_compatible_or_plus_separate_3_plus_requirement_still_rejects(self):
        e = exp("4+ years in data engineering OR 0–1 years of software engineering experience.",
                "3+ years of experience with SQL.")
        self.assertEqual(e["status"], "above_cutoff")
        self.assertEqual(e["decisive_min"], 3)


class PreferredAndUnrelated(unittest.TestCase):
    def test_preferred_requirement_is_not_mandatory(self):
        e = exp("Have 8+ years of software engineering experience, ideally with 2+ years at a Staff level.")
        self.assertEqual(e["decisive_min"], 8)
        self.assertEqual([p["text"] for p in e["preferred"]], ["2+ years"])

    def test_preferred_alone_never_rejects(self):
        e = exp("[Preferred] 5+ years customer-facing experience in a pre-sales role")
        self.assertEqual(e["status"], "unknown")
        self.assertEqual(len(e["preferred"]), 1)

    def test_preferred_heading_makes_its_items_preferred(self):
        e = exp("5+ years of Python experience.", headings="<h3>Preferred Qualifications</h3>")
        self.assertEqual(e["status"], "unknown")
        self.assertEqual(len(e["preferred"]), 1)

    def test_unrelated_year_counts_are_not_qualifications(self):
        for s in ("After 30 years of painfully slow progress, the agentic era has arrived.",  # quoted (Databricks)
                  "We will grow this into several roles over the next 1-2 years.",  # quoted (Databricks)
                  "The team has shipped every quarter for the past 5 years.",
                  "The company was founded 10 years ago.",
                  "We have 45 years of history."):
            with self.subTest(s=s):
                e = exp(s)
                self.assertEqual(e["units"], [])
                self.assertEqual(len(e["ignored"]), 1)

    def test_a_hyphenated_n_year_degree_is_not_a_count(self):
        self.assertEqual(exp("A 4-year degree in computer science.")["units"], [])

    def test_months_only_is_unknown(self):
        e = exp("6+ months of internship experience.")
        self.assertEqual(e["status"], "unknown")
        self.assertIn("months", e["reason"])

    def test_anthropic_experience_boilerplate_is_not_a_minimum(self):
        # Quoted from the saved Anthropic postings (all 677 contain it).
        e = exp("Minimum years of experience: Years of experience required will correlate with the "
                "internal job level requirements for the position.")
        self.assertEqual(e["status"], "unknown")
        self.assertEqual(e["units"], [])


class ConstructedDegreeDependentOr(unittest.TestCase):
    """FILTER.md section 9: Degree-dependent OR requirement (CONSTRUCTED)."""

    def test_is_unknown_and_goes_to_review_not_confirmed(self):
        body = ("<p>You will build data pipelines and machine learning models in Python and SQL on AWS.</p>"
                "<p>BS with 4+ years OR MS with 2+ years OR PhD with 0–1 years.</p>")
        r = evaluate(title="Machine Learning Engineer", body=body)
        self.assertEqual(r["experience_status"], "unknown")
        self.assertGreaterEqual(r["score"], 65)
        self.assertEqual(r["decision"], "review")


if __name__ == "__main__":
    unittest.main()
