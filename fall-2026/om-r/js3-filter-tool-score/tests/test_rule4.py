"""Candidate rule 4 (filter v1.1.0-candidate), written BEFORE js3/rule4.py
and js3/filter_v110.py existed. Design evidence: DEV split only
(logs/14_rule4_dev_evidence.txt). Fixtures are CONSTRUCTED sentences
modeled on dev patterns, not copied postings.

    JS3_RULE4_IMPL=js3.wrong_stub_rule4 python3 -m unittest -v tests.test_rule4

Interface fixed here:
    rule4.check(posting) -> {"fires": bool, "reasons": [str],
        "year_minimums": [{"n": int, "quote": str}],
        "seniority_title_word": str | None, "management_phrase": str | None,
        "eligibility_flags": [{"kind": "graduation" | "clearance", "quote": str}]}
    filter_v110.classify(posting) -> v1.0.0 result + rule-4 fields; a rule-4
        fire turns "relevant" into "rejected" with a "rule 4: ..." reason.
"""
import importlib
import os
import unittest

from tests.test_wrong_versions import posting

RULE4_IMPL = os.environ.get("JS3_RULE4_IMPL", "js3.rule4")
SKILLS = "Build LLM agents in Python. "   # passes rules 1-2 on its own


def check(title, content):
    return importlib.import_module(RULE4_IMPL).check(posting(1, title, content))


class YearMinimums(unittest.TestCase):
    def test_n_plus_years_at_or_above_3_fires(self):          # C13, C16, C18 pattern
        r = check("AI Engineer", SKILLS + "Minimum Requirements 4+ years of experience as an engineer.")
        self.assertTrue(r["fires"])
        self.assertEqual([y["n"] for y in r["year_minimums"]], [4])

    def test_at_least_n_years_fires(self):                    # C07, C09, C10 pattern
        self.assertTrue(check("Technical Solutions Engineer",
                              SKILLS + "At least 4 years of full-stack software development experience.")["fires"])

    def test_n_plus_years_without_the_word_experience_fires(self):   # C05 pattern
        self.assertTrue(check("Analytics Lead", SKILLS + "12+ years in analytics engineering or BI.")["fires"])

    def test_range_uses_its_lower_bound(self):                # C20 pattern
        self.assertTrue(check("Data Scientist", SKILLS + "BS with 4-8 years of data science.")["fires"])
        self.assertFalse(check("Data Scientist", SKILLS + "PhD with 1-3 years of research.")["fires"])
        self.assertTrue(check("Data Scientist", SKILLS + "3–5 years of experience.")["fires"])   # en dash

    def test_below_3_does_not_fire(self):
        for c in ["1+ years of experience.", "2+ years building production systems.", "0-2 years of experience."]:
            with self.subTest(c=c):
                self.assertFalse(check("Software Engineer", SKILLS + c)["fires"])

    def test_spelled_out_numbers(self):
        # Not evidenced in dev (dev postings use digits); the plain-English
        # equivalent of the digit pattern, decided before any held-out read.
        self.assertTrue(check("Engineer", SKILLS + "At least four years of backend experience.")["fires"])
        self.assertFalse(check("Engineer", SKILLS + "At least two years of backend experience.")["fires"])

    def test_no_years_minimum_does_not_fire(self):            # C03 pattern
        r = check("Backend Engineer (Python), AI Engineering",
                  SKILLS + "Relevant backend experience with Python. Work with Product Management and UX.")
        self.assertFalse(r["fires"], r)

    def test_years_mentioned_without_a_minimum_does_not_fire(self):
        self.assertFalse(check("Engineer", SKILLS + "Stripe has grown for over 10 years. Several years ago we began.")["fires"])


class SeniorityTitle(unittest.TestCase):
    def test_each_listed_title_word_fires(self):              # C02 Staff, C05 Director, C10 Manager
        for t in ["Staff Backend Engineer", "Principal ML Engineer", "Director, Analytics Engineering",
                  "Engineering Manager, AI Platform", "Head of Applied AI"]:
            with self.subTest(title=t):
                r = check(t, SKILLS)
                self.assertTrue(r["fires"])
                self.assertIsNotNone(r["seniority_title_word"])

    def test_title_words_are_whole_word(self):
        for t in ["Staffing Systems Engineer", "Engineering Management Tools Developer"]:
            with self.subTest(title=t):
                self.assertFalse(check(t, SKILLS)["fires"])

    def test_title_word_in_content_only_does_not_fire(self):  # C03: "Work with Product Management"
        self.assertFalse(check("ML Engineer", SKILLS + "Partner with your manager and Staff engineers.")["fires"])

    def test_senior_is_not_a_listed_word(self):               # C01: a known dev miss, by spec
        self.assertFalse(check("Senior Backend Engineer", SKILLS)["fires"])


class ManagementScope(unittest.TestCase):
    def test_management_phrases_fire(self):                   # C05 / C10 patterns
        for c in ["2+ years managing managers or senior leads.", "You'll lead a team of 8.",
                  "Experience managing ML teams.", "You will own the P&L for the region.",
                  "Strong people management skills.", "Manage 6 direct reports."]:
            with self.subTest(c=c):
                r = check("ML Engineer", SKILLS + c)
                self.assertTrue(r["fires"], c)
                self.assertIsNotNone(r["management_phrase"])

    def test_non_people_management_does_not_fire(self):       # C13, C16, C19, C05 false triggers
        for c in ["Ability to manage multiple projects at once.", "Managing dependencies and trade-offs.",
                  "Experience managing model costs.", "Weigh hedge cost and P&L volatility.",
                  "Multi-entity exposure management."]:
            with self.subTest(c=c):
                self.assertFalse(check("ML Engineer", SKILLS + c)["fires"], c)


class EligibilityIsFlaggedNeverRejected(unittest.TestCase):
    """EXPERIMENT.md section 3, decision B."""

    def test_graduation_requirement_flags_without_firing(self):
        r = check("Software Engineer, New Grad", SKILLS + "Must be graduating in December 2026 or Spring 2027.")
        self.assertFalse(r["fires"])
        self.assertEqual([f["kind"] for f in r["eligibility_flags"]], ["graduation"])

    def test_clearance_requirement_flags_without_firing(self):
        r = check("Software Engineer", SKILLS + "Security clearance or the ability to obtain a clearance.")
        self.assertFalse(r["fires"])
        self.assertIn("clearance", [f["kind"] for f in r["eligibility_flags"]])

    def test_flag_quotes_are_from_the_posting(self):
        from js3.filter import field_text
        p = posting(2, "Intern", SKILLS + "Graduating in 2028. Active security clearance required.")
        r = importlib.import_module(RULE4_IMPL).check(p)
        self.assertEqual(len(r["eligibility_flags"]), 2)
        for f in r["eligibility_flags"]:
            self.assertIn(f["quote"], field_text(p, "content"))


class FilterV110Integration(unittest.TestCase):
    def classify(self, p):
        from js3.filter_v110 import classify
        return classify(p)

    def test_rule4_turns_relevant_into_rejected_with_reason(self):
        r = self.classify(posting(3, "AI Engineer", SKILLS + "4+ years of experience."))
        self.assertEqual(r["bucket"], "rejected")
        self.assertTrue(any(x.startswith("rule 4") for x in r["reasons"]), r["reasons"])
        self.assertEqual(r["filter_version"], "1.1.0-candidate")

    def test_c03_style_posting_stays_relevant(self):
        r = self.classify(posting(4, "Backend Engineer (Python), AI Engineering", SKILLS + "Relevant backend experience."))
        self.assertEqual(r["bucket"], "relevant")

    def test_eligibility_flag_is_carried_but_bucket_unchanged(self):
        r = self.classify(posting(5, "Software Engineer, New Grad", SKILLS + "Graduating in 2028."))
        self.assertEqual(r["bucket"], "relevant")
        self.assertEqual([f["kind"] for f in r["eligibility_flags"]], ["graduation"])

    def test_rule3_still_wins(self):
        self.assertEqual(self.classify(posting(6, "Staff LLM Python Engineer", ""))["bucket"], "insufficient_data")

    def test_v100_module_is_untouched(self):
        from js3 import filter as v100
        self.assertEqual(v100.VERSION, "1.0.0")
        self.assertEqual(v100.classify(posting(7, "AI Engineer", SKILLS + "4+ years of experience."))["bucket"],
                         "relevant")


if __name__ == "__main__":
    unittest.main()
