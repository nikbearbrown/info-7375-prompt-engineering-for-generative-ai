"""Tests for candidate filter v1.3 (R4 counts the bottom of a range), written BEFORE the v1.3 code.
Reason: in H2 all 3 postings I marked y ('3-5 years', '5+'... ) were rejected by R4 counting the top of the range."""
import unittest
from tests.helpers import filt, P, ROOT
TWO = "You will write SQL and Python every day."
def c13(): return filt().load_filter(ROOT / "filters" / "filter_v1.3.json")
def c12(): return filt().load_filter(ROOT / "filters" / "filter_v1.2.json")
class RangeBottom(unittest.TestCase):
    def test_range_counts_bottom_in_v13(self):
        d = filt().evaluate(P(text=TWO + " 3-5 years of experience."), c13()); self.assertEqual(d["years_max"], 3); self.assertEqual(d["status"], "kept")
    def test_range_still_top_in_v12(self):
        d = filt().evaluate(P(text=TWO + " 3-5 years of experience."), c12()); self.assertEqual(d["years_max"], 5); self.assertEqual(d["status"], "rejected")
    def test_plus_and_single_unchanged(self):
        self.assertEqual(filt().evaluate(P(text=TWO + " 5+ years of experience."), c13())["status"], "rejected")
        self.assertEqual(filt().evaluate(P(text=TWO + " 4 years of experience."), c13())["status"], "rejected")
    def test_bottom_above_limit_still_rejected(self):
        self.assertEqual(filt().evaluate(P(text=TWO + " 4-6 years of experience."), c13())["status"], "rejected")
if __name__ == "__main__": unittest.main()
