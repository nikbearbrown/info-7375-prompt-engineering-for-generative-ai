"""FILTER.md is the filter; filter-v1.json is how the code reads it. These tests fail if the two
drift apart: every word list in the JSON must be the one quoted in FILTER.md, and the numbers must
be the ones FILTER.md states. Written by Claude Code on 2026-11-25 before js3/filtering.py."""
import json
import pathlib
import re
import unittest

HERE = pathlib.Path(__file__).resolve().parent.parent
DOC = (HERE / "FILTER.md").read_text()
CFG = json.loads((HERE / "filter-v1.json").read_text())
PERSONA = json.loads((HERE / "persona" / "alex_morgan.json").read_text())


def section(title):
    start = DOC.index(title)
    nxt = DOC.find("\n### ", start + 1)
    return DOC[start:nxt if nxt > 0 else None]


def backticked(text):
    return re.findall(r"`([^`]+)`", text)


class FilterDocAgreesWithConfig(unittest.TestCase):
    def test_version(self):
        self.assertIn("**Version: v1, 2026-11-25.**", DOC)
        self.assertEqual(CFG["version"], "v1")

    def test_rule1_phrases(self):
        self.assertEqual(backticked(section("### Rule 1")), CFG["rule1_title_phrases"])

    def test_rule2_departments_and_the_palantir_alias(self):
        self.assertEqual(backticked(section("### Rule 2")), CFG["rule2_departments"])
        self.assertIn('Palantir\'s "Dev" should count as engineering', section("### Rule 2"))
        self.assertEqual(CFG["rule2_department_aliases"], {"palantir": {"Dev": "Engineering"}})

    def test_rule4_skills_and_minimum(self):
        text = section("### Rule 4")
        self.assertIn("at least TWO", text)
        self.assertEqual(CFG["rule4_min_skills"], 2)
        listed = re.search(r"the ten skills:\*\s*(.+?)\.\n", text).group(1)
        self.assertEqual([s.strip() for s in listed.split(",")], PERSONA["skills"])

    def test_rule5_years(self):
        self.assertIn("3 years or less", section("### Rule 5"))
        self.assertEqual(CFG["rule5_max_years"], 3)
        self.assertEqual(PERSONA["experience_years"], 3)

    def test_rule6_title_words(self):
        self.assertEqual(backticked(section("### Rule 6")), CFG["rule6_title_words"])
        self.assertIn("Paid internships are out", section("### Rule 6"))
        self.assertIn("exclude part-time and temporary jobs too", section("### Rule 6"))

    def test_closest_call(self):
        self.assertIn("fails exactly one rule", section("### Final decision"))
        self.assertEqual(CFG["closest_call_fails"], 1)


if __name__ == "__main__":
    unittest.main()
