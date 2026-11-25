"""Regression test for a bug I found by re-reading the shortlist labels against the posting text (2026-11-25, Stripe
'Processing Cost Analyst'): a short bullet such as 'Experience with Oracle Suite' was mistaken for a section heading,
which ended the 'Preferred qualifications' section, so skills listed under it were labelled SUPPORTED.
Written BEFORE the fix (logs/06 shows it failing)."""
import unittest
from js3 import evidence as E

TEXT = ("Minimum qualifications\nAbility to solve problems using Excel\nPreferred qualifications\n"
        "Experience in the technology or payments industry\nExperience with Oracle Suite\n"
        "Experience with data-querying and analysis tools, including SQL\n"
        "Experience with data-analysis tools, such as Power BI, Tableau, KNIME, Python, or Alteryx")

class PreferredSectionNotEndedByABullet(unittest.TestCase):
    def test_skills_under_preferred_are_insufficient(self):
        for s in ["SQL", "Python", "Tableau", "Power BI"]:
            self.assertEqual(E.label_skill(TEXT, s)["label"], "INSUFFICIENT", s)
    def test_minimum_section_still_supported(self):
        self.assertEqual(E.label_skill(TEXT, "Excel")["label"], "SUPPORTED")
    def test_real_headings_still_detected(self):
        t = "Preferred qualifications\nTableau\nResponsibilities\nYou will use Tableau daily."
        self.assertEqual(E.label_skill(t, "Tableau")["label"], "SUPPORTED")
        t2 = "What you'll bring\nSQL\nNice to have\nLooker"
        self.assertEqual(E.label_skill(t2, "SQL")["label"], "SUPPORTED"); self.assertEqual(E.label_skill(t2, "Looker")["label"], "INSUFFICIENT")

if __name__ == "__main__": unittest.main()
