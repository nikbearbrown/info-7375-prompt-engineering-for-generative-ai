"""The v1.0 filter against FILTER.md: each reject rule, the score, the threshold, the missing-field rule, and
the two wrong versions, which the real filter must not behave like."""
import os
import re
import unittest

from helpers import ROOT

import filter as F

FILTER = open(os.path.join(ROOT, "FILTER.md"), encoding="utf-8").read()


def posting(title="Data Analyst", text="Use SQL and Tableau.", locations=("New York, NY",), country=None):
    return {"key": "t/t/1", "title": title, "text": text, "locations": list(locations),
            "location": locations[0] if locations else None, "country": country}


class RejectRules(unittest.TestCase):
    def test_r1_seniority_anywhere_in_the_title_whole_word(self):
        for title in ("Senior Data Analyst", "Data Analyst, Senior", "Sr. Data Analyst", "Lead BI Analyst",
                      "Data Analyst - Staff"):
            with self.subTest(title=title):
                self.assertEqual(F.evaluate(posting(title))["rejected_by"].get("R1", "").lower()[:2],
                                 re.search(r"senior|sr|lead|staff", title, re.I).group(0).lower()[:2])
        self.assertNotIn("R1", F.evaluate(posting("Leadership Data Analyst"))["rejected_by"])

    def test_r2_uses_the_lowest_stated_years(self):
        cases = {"3+ years of experience with SQL": True, "3-5 years of relevant experience": True,
                 "at least 4 years of experience": True, "1-3 years of experience": False,
                 "2+ years of experience": False, "3+ years of SQL experience; 1+ years of Tableau experience": False,
                 "Founded 20 years ago, we have 25 years of experience": False, "Five years of experience": False}
        for text, rejects in cases.items():
            with self.subTest(text=text):
                self.assertEqual("R2" in F.evaluate(posting(text=text))["rejected_by"], rejects)

    def test_r3_rejects_only_when_every_location_is_outside_the_us(self):
        self.assertIn("R3", F.evaluate(posting(locations=("London, UK", "Dublin, Ireland")))["rejected_by"])
        for locs in (("London, UK", "New York, NY"), ("Remote",), ("LOCATION",), (), ("Remote - US",),
                     ("Remote - Americas",)):
            with self.subTest(locations=locs):
                self.assertNotIn("R3", F.evaluate(posting(locations=locs))["rejected_by"])
        self.assertNotIn("R3", F.evaluate(posting(locations=("Somewhere",), country="US"))["rejected_by"])

    def test_r3_the_israel_il_false_match_is_fixed(self):
        self.assertIn("R3", F.evaluate(posting(locations=("Israel - Kiryat Ono IL",)))["rejected_by"])

    def test_r4_only_a_stated_refusal_rejects_silence_does_not(self):
        self.assertIn("R4", F.evaluate(posting(text="SQL. We are unable to sponsor visas."))["rejected_by"])
        self.assertNotIn("R4", F.evaluate(posting(text="SQL and Tableau."))["rejected_by"])
        self.assertNotIn("R4", F.evaluate(posting(text="We sponsor visas."))["rejected_by"])

    def test_a_missing_description_never_rejects(self):
        v = F.evaluate(posting(text=None))
        self.assertEqual(v["rejected_by"], {})
        self.assertEqual((v["score"], v["verdict"]), (4, "keep"))


class Score(unittest.TestCase):
    def test_role_phrase_alone_reaches_the_threshold(self):
        self.assertEqual(F.evaluate(posting(text="Nothing relevant."))["verdict"], "keep")

    def test_bare_analyst_needs_three_skill_words(self):
        self.assertEqual(F.evaluate(posting("Financial Analyst", "SQL, Excel."))["verdict"], "reject")
        v = F.evaluate(posting("Financial Analyst", "SQL, Excel, and Tableau dashboards."))
        self.assertEqual((v["score"], v["verdict"]), (5, "keep"))

    def test_no_analyst_in_the_title_scores_zero_whatever_the_skills(self):
        v = F.evaluate(posting("Software Engineer", "SQL Python Excel Tableau dashboards reporting Power BI"))
        self.assertEqual((v["score"], v["skills"]), (0, {}))

    def test_each_skill_counts_once(self):
        v = F.evaluate(posting(text="SQL SQL SQL. Dashboard, dashboards."))
        self.assertEqual(v["score"], 6)

    def test_threshold_and_points_match_filter_md(self):
        self.assertEqual(F.THRESHOLD, int(re.search(r"keep when the score is (\d+) or more", FILTER).group(1)))
        phrases = re.search(r"\*\*role phrase\*\*: (.+?) \|", FILTER).group(1)
        self.assertEqual(set(re.findall(r'"([^"]+)"', phrases)),
                         {"data analyst", "BI analyst", "business intelligence analyst", "business analyst",
                          "reporting analyst", "analytics analyst"})


class WrongVersions(unittest.TestCase):
    def test_wrong_1_substring_gives_points_the_real_filter_does_not(self):
        p = posting("Financial Analyst", "Excellent communication; mobile-first; ambitious; postgresql")
        self.assertGreaterEqual(F.wrong_substring(p), 4)  # excel, bi, sql inside other words
        self.assertEqual(F.evaluate(p)["skills"], {})
        self.assertEqual(F.evaluate(p)["verdict"], "reject")

    def test_wrong_2_title_only_keeps_a_posting_r2_rejects(self):
        p = posting("Data Analyst", "Requires 5+ years of experience in analytics.")
        self.assertEqual(F.wrong_title_only(p), "keep")
        v = F.evaluate(p)
        self.assertEqual((v["verdict"], set(v["rejected_by"])), ("reject", {"R2"}))


if __name__ == "__main__":
    unittest.main()
