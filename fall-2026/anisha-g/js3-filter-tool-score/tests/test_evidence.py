"""Written from FILTER.md v1.0 section 2 BEFORE any evidence code existed (2026-11-25)."""
import unittest
from tests.helpers import cfg, P
from js3 import evidence as E

S, C, I = "SUPPORTED", "CONTRADICTED", "INSUFFICIENT"

class SkillClaims(unittest.TestCase):
    def test_requirement_sentence_supports(self):
        r = E.label_skill("About you: Proficiency in SQL. You will build reports.", "SQL")
        self.assertEqual(r["label"], S); self.assertIn("Proficiency in SQL", r["quote"])
    def test_duty_sentence_supports(self):
        self.assertEqual(E.label_skill("You will build dashboards in Tableau for the sales team.", "Tableau")["label"], S)
    def test_absent_is_insufficient(self):
        r = E.label_skill("Proficiency in SQL.", "Tableau"); self.assertEqual(r["label"], I); self.assertTrue(r["cannot_tell"])
    def test_nice_to_have_is_insufficient(self):
        for t in ["Experience with Tableau is a plus.", "Tableau experience preferred.", "Bonus: Tableau.",
                  "Nice to have: Tableau dashboards."]:
            r = E.label_skill(t, "Tableau"); self.assertEqual(r["label"], I, t); self.assertTrue(r["cannot_tell"], t)
    def test_nice_to_have_section_is_insufficient(self):
        t = "Requirements:\nProficiency in SQL\nNice to have:\nTableau dashboards\nLooker"
        self.assertEqual(E.label_skill(t, "SQL")["label"], S)
        self.assertEqual(E.label_skill(t, "Tableau")["label"], I)
        self.assertEqual(E.label_skill(t, "Looker")["label"], I)
    def test_required_mention_wins_over_a_plus_mention(self):
        t = "Strong SQL skills required. Advanced SQL tuning is a plus."
        self.assertEqual(E.label_skill(t, "SQL")["label"], S)
    def test_whole_word(self):
        self.assertEqual(E.label_skill("We run NoSQL databases.", "SQL")["label"], I)

class YearsClaims(unittest.TestCase):
    def test_within_limit_supported(self):
        r = E.label_years("We want 1-3 years of experience in analytics.", 3)
        self.assertEqual(r["label"], S); self.assertIn("1-3 years", r["quote"]); self.assertFalse(r["cannot_tell"])
    def test_over_limit_contradicted(self):
        r = E.label_years("You have 5+ years of experience.", 3)
        self.assertEqual(r["label"], C); self.assertIn("5+ years", r["quote"]); self.assertFalse(r["cannot_tell"])
    def test_unstated_is_insufficient_and_cannot_tell(self):
        r = E.label_years("You love data.", 3); self.assertEqual(r["label"], I); self.assertTrue(r["cannot_tell"])

class Justify(unittest.TestCase):
    def test_every_claim_is_labelled_with_a_quote_or_cannot_tell(self):
        p = P(text="Requirements: Proficiency in SQL. You will use Python daily. 1-2 years of experience.")
        j = E.justify(p, cfg())
        self.assertTrue(j["claims"])
        for c in j["claims"]:
            self.assertIn(c["label"], (S, C, I))
            if c["label"] in (S, C): self.assertTrue(c["quote"])
            else: self.assertTrue(c["cannot_tell"])
        self.assertTrue(j["shortlist"])
    def test_relevance_is_not_entailment(self):
        # the filter keeps it (title + 2 skill words), but one skill is only "a plus": only 1 skill is SUPPORTED
        p = P(text="Proficiency in SQL. Experience with Tableau is a plus.")
        from tests.helpers import filt
        self.assertEqual(filt().evaluate(p, cfg())["status"], "kept")
        j = E.justify(p, cfg())
        self.assertFalse(j["shortlist"]); self.assertIn("guess", j["why_not"].lower())
    def test_contradicted_years_never_shortlisted(self):
        j = E.justify(P(text="Proficiency in SQL and Python. 3-5 years of experience."), cfg())
        self.assertFalse(j["shortlist"])
    def test_unstated_years_shortlisted_but_years_claim_cannot_tell(self):
        j = E.justify(P(text="Proficiency in SQL and Python."), cfg())
        self.assertTrue(j["shortlist"])
        yc = [c for c in j["claims"] if c["kind"] == "years"][0]
        self.assertEqual(yc["label"], I); self.assertTrue(yc["cannot_tell"])
        self.assertIn("cannot tell", yc["say"].lower())
    def test_missing_text_cannot_tell_everything(self):
        j = E.justify(P(text=""), cfg())
        self.assertFalse(j["shortlist"]); self.assertTrue(j["cannot_tell"])

if __name__ == "__main__": unittest.main()
