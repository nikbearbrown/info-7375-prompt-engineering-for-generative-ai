"""Review packet step 2: written BEFORE the R3 patch, from Yudan's predictions (2026-11-09).
Defect: R3 read only two-letter state codes, so 364 real Databricks postings such as
'San Francisco, California' failed R3 (review/01-reproduce-before.txt)."""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from agent import rule  # noqa: E402

RESUME = json.load(open(os.path.join(ROOT, "persona", "resume.json"), encoding="utf-8"))


def r3(loc):
    p = {"id": 1, "title": "Data Analyst", "location": {"name": loc}, "content": "SQL and Python"}
    return {r["check"]: r for r in rule.judge(p, RESUME)["reasons"]}["R3"]["result"]


class R3FullStateNames(unittest.TestCase):
    # Yudan's predictions: US
    def test_city_and_full_state(self):
        self.assertEqual(r3("San Francisco, California"), "pass")
        self.assertEqual(r3("New York City, New York"), "pass")

    def test_washington_dc(self):
        self.assertEqual(r3("Washington, D.C."), "pass")

    def test_remote_with_a_state(self):
        self.assertEqual(r3("Remote - California"), "pass")

    def test_state_name_alone(self):
        self.assertEqual(r3("California; New York"), "pass")

    # added 2026-11-09 after reviewing the first patch (Yudan's decision: revise). Six real Databricks
    # postings say 'Atlanta, Georgia' or 'Remote - Georgia' (review/06-reproduce-after.txt)
    def test_georgia_the_us_state(self):
        self.assertEqual(r3("Atlanta, Georgia"), "pass")
        self.assertEqual(r3("Remote - Georgia"), "pass")

    # Yudan's predictions: not US
    def test_georgia_the_country(self):
        self.assertEqual(r3("Tbilisi, Georgia"), "fail")

    def test_other_countries(self):
        for loc in ("Toronto, Canada", "London, United Kingdom", "Bengaluru, India"):
            self.assertEqual(r3(loc), "fail", loc)

    # unchanged from JS1 (regression)
    def test_js1_behaviour_kept(self):
        self.assertEqual(r3("San Francisco, CA"), "pass")
        self.assertEqual(r3("Toronto, ON, CA"), "fail")
        self.assertEqual(r3("Remote"), "fail")

    def test_state_name_inside_another_word_does_not_count(self):
        self.assertEqual(r3("Indianapolis Avenue, London, United Kingdom"), "fail")


if __name__ == "__main__":
    unittest.main()
