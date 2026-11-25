"""The filter against FILTER.md: each v1.0 reject rule, the score, the threshold, the missing-field rule, the
two wrong versions (which the real filter must not behave like), and the three v1.2 changes."""
import os
import re
import unittest

from helpers import ROOT

import filter as F

FILTER = open(os.path.join(ROOT, "FILTER.md"), encoding="utf-8").read()


def v10(p):
    return F.evaluate(p, "1.0")


def posting(title="Data Analyst", text="Use SQL and Tableau.", locations=("New York, NY",), country=None):
    return {"key": "t/t/1", "title": title, "text": text, "locations": list(locations),
            "location": locations[0] if locations else None, "country": country}


class RejectRules(unittest.TestCase):
    def test_r1_seniority_anywhere_in_the_title_whole_word(self):
        for title in ("Senior Data Analyst", "Data Analyst, Senior", "Sr. Data Analyst", "Lead BI Analyst",
                      "Data Analyst - Staff"):
            with self.subTest(title=title):
                self.assertEqual(v10(posting(title))["rejected_by"].get("R1", "").lower()[:2],
                                 re.search(r"senior|sr|lead|staff", title, re.I).group(0).lower()[:2])
        self.assertNotIn("R1", v10(posting("Leadership Data Analyst"))["rejected_by"])

    def test_r2_uses_the_lowest_stated_years(self):
        cases = {"3+ years of experience with SQL": True, "3-5 years of relevant experience": True,
                 "at least 4 years of experience": True, "1-3 years of experience": False,
                 "2+ years of experience": False, "3+ years of SQL experience; 1+ years of Tableau experience": False,
                 "Founded 20 years ago, we have 25 years of experience": False, "Five years of experience": False}
        for text, rejects in cases.items():
            with self.subTest(text=text):
                self.assertEqual("R2" in v10(posting(text=text))["rejected_by"], rejects)

    def test_r3_rejects_only_when_every_location_is_outside_the_us(self):
        self.assertIn("R3", v10(posting(locations=("London, UK", "Dublin, Ireland")))["rejected_by"])
        for locs in (("London, UK", "New York, NY"), ("Remote",), ("LOCATION",), (), ("Remote - US",),
                     ("Remote - Americas",)):
            with self.subTest(locations=locs):
                self.assertNotIn("R3", v10(posting(locations=locs))["rejected_by"])
        self.assertNotIn("R3", v10(posting(locations=("Somewhere",), country="US"))["rejected_by"])

    def test_r3_the_israel_il_false_match_is_fixed(self):
        self.assertIn("R3", v10(posting(locations=("Israel - Kiryat Ono IL",)))["rejected_by"])

    def test_r4_only_a_stated_refusal_rejects_silence_does_not(self):
        self.assertIn("R4", v10(posting(text="SQL. We are unable to sponsor visas."))["rejected_by"])
        self.assertNotIn("R4", v10(posting(text="SQL and Tableau."))["rejected_by"])
        self.assertNotIn("R4", v10(posting(text="We sponsor visas."))["rejected_by"])

    def test_a_missing_description_never_rejects(self):
        v = v10(posting(text=None))
        self.assertEqual(v["rejected_by"], {})
        self.assertEqual((v["score"], v["verdict"]), (4, "keep"))


class Score(unittest.TestCase):
    def test_role_phrase_alone_reaches_the_threshold(self):
        self.assertEqual(v10(posting(text="Nothing relevant."))["verdict"], "keep")

    def test_bare_analyst_needs_three_skill_words(self):
        self.assertEqual(v10(posting("Financial Analyst", "SQL, Excel."))["verdict"], "reject")
        v = v10(posting("Financial Analyst", "SQL, Excel, and Tableau dashboards."))
        self.assertEqual((v["score"], v["verdict"]), (5, "keep"))

    def test_no_analyst_in_the_title_scores_zero_whatever_the_skills(self):
        v = v10(posting("Software Engineer", "SQL Python Excel Tableau dashboards reporting Power BI"))
        self.assertEqual((v["score"], v["skills"]), (0, {}))

    def test_each_skill_counts_once(self):
        v = v10(posting(text="SQL SQL SQL. Dashboard, dashboards."))
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
        self.assertEqual(v10(p)["skills"], {})
        self.assertEqual(v10(p)["verdict"], "reject")

    def test_wrong_2_title_only_keeps_a_posting_r2_rejects(self):
        p = posting("Data Analyst", "Requires 5+ years of experience in analytics.")
        self.assertEqual(F.wrong_title_only(p), "keep")
        v = v10(p)
        self.assertEqual((v["verdict"], set(v["rejected_by"])), ("reject", {"R2"}))


class Version12(unittest.TestCase):
    """FILTER.md v1.2: F1, F4, F5. Each must change exactly what it says, and v1.0 must still behave as before."""

    def test_current_version_is_1_2_and_v1_0_is_still_callable(self):
        self.assertEqual(F.VERSION, "1.2")
        self.assertEqual(F.evaluate(posting())["version"], "1.2")
        self.assertEqual(v10(posting())["version"], "1.0")
        with self.assertRaises(ValueError):
            F.evaluate(posting(), "9.9")

    def test_f1_does_not_provide_sponsorship_rejects_in_1_2_only(self):
        p = posting(text="SQL. Veeva does not provide sponsorship for employment visa status.")
        self.assertEqual(F.evaluate(p)["rejected_by"], {"R4": "does not provide sponsorship"})
        self.assertEqual(v10(p)["rejected_by"], {})

    def test_f4_r2_reads_the_highest_requirement(self):
        p = posting(text="6+ years experience in FP&A. 2+ years of direct experience with SQL.")
        self.assertIn("R2", F.evaluate(p)["rejected_by"])
        self.assertNotIn("R2", v10(p)["rejected_by"])
        self.assertNotIn("R2", F.evaluate(posting(text="1-3 years of experience. 2+ years of experience."))["rejected_by"])

    def test_f5_reporting_to_is_not_the_skill_but_reporting_work_still_is(self):
        p = posting("Financial Analyst", "Tableau, Excel. Reporting to the Senior Manager. Reporting directly to the CFO.")
        self.assertNotIn("reporting", F.evaluate(p)["skills"])
        self.assertIn("reporting", v10(p)["skills"])
        self.assertIn("reporting", F.evaluate(posting(text="Build weekly reporting in SQL."))["skills"])

    def test_threshold_weights_r1_r3_unchanged(self):
        for p in (posting("Senior Data Analyst"), posting(locations=("London, UK",)), posting(text="Nothing.")):
            self.assertEqual(F.evaluate(p)["verdict"], v10(p)["verdict"])


if __name__ == "__main__":
    unittest.main()
