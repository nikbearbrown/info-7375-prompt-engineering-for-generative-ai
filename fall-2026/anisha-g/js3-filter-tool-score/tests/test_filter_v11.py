"""Tests for filter v1.1, written after the audit's kept sample (group C) showed two false friends and BEFORE the v1.1
code existed. v1.0 behaviour must not change (tests/test_filter.py still runs on filter_v1.0.json)."""
import unittest
from tests.helpers import filt, P, ROOT
TWO = "You will write SQL and Python every day."
def c11(): return filt().load_filter(ROOT / "filters" / "filter_v1.1.json")
def c10(): return filt().load_filter(ROOT / "filters" / "filter_v1.0.json")

class TitleExclude(unittest.TestCase):          # false friend: 'Analytics' in 'Software Engineer, Data Warehouse Analytics'
    def test_engineer_title_rejected_in_v11(self):
        d = filt().evaluate(P(title="Software Engineer, Data Warehouse Analytics", text=TWO), c11())
        self.assertEqual(d["status"], "rejected"); self.assertIn("R1b", d["failed"])
    def test_still_kept_in_v10(self):
        self.assertEqual(filt().evaluate(P(title="Software Engineer, Data Warehouse Analytics", text=TWO), c10())["status"], "kept")
    def test_whole_word(self):
        self.assertEqual(filt().evaluate(P(title="Data Analyst, Engineering Org", text=TWO), c11())["status"], "kept")

class YearsEducation(unittest.TestCase):         # false friend: 'At least 2 years of university education'
    def test_education_years_ignored_in_v11(self):
        f = filt(); t = TWO + " At least 5 years of university education, or equivalent work experience."
        d = f.evaluate(P(text=t), c11()); self.assertIsNone(d["years_max"]); self.assertEqual(d["status"], "kept")
    def test_experience_years_still_count(self):
        d = filt().evaluate(P(text=TWO + " 5+ years of experience."), c11()); self.assertEqual(d["years_max"], 5)
    def test_v10_unchanged(self):
        d = filt().evaluate(P(text=TWO + " At least 5 years of university education."), c10()); self.assertEqual(d["years_max"], 5)

if __name__ == "__main__": unittest.main()
