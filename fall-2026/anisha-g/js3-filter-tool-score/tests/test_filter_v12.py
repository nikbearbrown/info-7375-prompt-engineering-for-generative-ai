"""Tests for filter v1.2 (R5: US-only location), written after measuring the audit and BEFORE the v1.2 code.
Missing or vague locations still pass (FILTER.md section 3: missing is not 'not relevant')."""
import unittest
from tests.helpers import filt, P, ROOT
TWO = "You will write SQL and Python every day."
def c12(): return filt().load_filter(ROOT / "filters" / "filter_v1.2.json")
def c11(): return filt().load_filter(ROOT / "filters" / "filter_v1.1.json")
def st(loc, cfg): return filt().evaluate(P(text=TWO, location=loc), cfg)

class USOnly(unittest.TestCase):
    def test_clearly_non_us_rejected(self):
        for loc in ["Toronto", "Toronto, CA", "Singapore", "IN-Bengaluru", "Mexico City", "London, United Kingdom", "Dublin, IE"]:
            d = st(loc, c12()); self.assertEqual(d["status"], "rejected", loc); self.assertIn("R5", d["failed"], loc)
    def test_us_kept(self):
        for loc in ["Boston, MA", "New York, New York, USA", "South San Francisco, CA", "US-Remote", "SF, NYC", "Seattle, WA"]:
            self.assertEqual(st(loc, c12())["status"], "kept", loc)
    def test_mixed_us_and_non_us_kept(self):
        for loc in ["SEA, SF, NY, Toronto", "New York, US, Canada, Remote", "US-Remote; CA-Toronto"]:
            self.assertEqual(st(loc, c12())["status"], "kept", loc)
    def test_missing_or_vague_kept(self):
        for loc in [None, "", "Remote", "N/A"]:
            self.assertEqual(st(loc, c12())["status"], "kept", repr(loc))
    def test_v11_ignores_location(self):
        self.assertEqual(st("Singapore", c11())["status"], "kept")

if __name__ == "__main__": unittest.main()
