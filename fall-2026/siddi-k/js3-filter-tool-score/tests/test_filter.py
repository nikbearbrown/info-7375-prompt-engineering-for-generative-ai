"""FILTER.md D, wrong versions 1-5: each test fails if its wrong version is put into the filter (tests/mutants.py)."""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixtures import ROOT, cfg, posting  # noqa: E402
from js3 import filter as flt  # noqa: E402
from js3.location import posting_place  # noqa: E402


class WV1Substring(unittest.TestCase):
    def test_wv1_no_substring_hits(self):
        p = posting(title="HTML Email Engineer",
                    text="<p>Maintain our email templates for Taiwan. Write HTML and CSS.</p>")
        parts = flt.score_parts(cfg(), p["title"], ["maintain our email templates for taiwan.", "write html and css."])
        self.assertIsNone(parts["role_word"], "'ml' must not match inside 'HTML'")
        self.assertEqual(parts["topics"], [], "'ai' must not match inside maintain/email/taiwan")
        self.assertEqual(parts["score"], 0)


class WV2Boilerplate(unittest.TestCase):
    def test_wv2_blurb_and_cut_section_do_not_count(self):
        text = ("<p>Stripe is a financial infrastructure platform for businesses, built with python and kafka.</p>"
                "<p>You will write sql.</p><h3>In-office expectations</h3><p>We use spark, airflow and dbt.</p>")
        r = flt.evaluate(cfg(), posting(title="Data Engineer", text=text))
        skills = {s["skill"] for s in r["parts"]["skills"]}
        self.assertEqual(skills, {"sql"}, "the dropped blurb sentence and the cut section must add no skills")
        self.assertEqual(r["verdict"], "keep")      # 3 (role) + 1 (sql) = 4


class WV3GatesBeforeScore(unittest.TestCase):
    RICH = "<p>python, sql, spark, airflow, kafka, dbt and machine learning.</p>"

    def test_wv3_senior_title_rejected_despite_score(self):
        r = flt.evaluate(cfg(), posting(title="Sr. Machine Learning Engineer", text=self.RICH))
        self.assertEqual(r["verdict"], "reject")
        self.assertIn("G2_seniority", r["reasons"])

    def test_wv3_toronto_rejected_despite_score(self):
        r = flt.evaluate(cfg(), posting(title="Machine Learning Engineer", text=self.RICH, location="Toronto, ON"))
        self.assertEqual(r["verdict"], "reject")
        self.assertIn("G4_location", r["reasons"])

    def test_wv3_years_over_cap_rejected(self):
        text = "<p>5+ years of experience with python, sql, spark and airflow.</p>"
        r = flt.evaluate(cfg(), posting(title="Data Engineer", text=text))
        self.assertEqual(r["verdict"], "reject")
        self.assertEqual(r["gates"]["G3_years"]["years_required"], 5)


class WV4MissingIsCannotTell(unittest.TestCase):
    def test_wv4_no_text_is_cannot_tell(self):
        r = flt.evaluate(cfg(), posting(title="Data Engineer", text=None))
        self.assertEqual(r["verdict"], "cannot_tell")
        self.assertEqual(r["reasons"], ["text_missing"])

    def test_wv4_bare_remote_is_cannot_tell_when_it_would_be_kept(self):
        r = flt.evaluate(cfg(), posting(title="Data Engineer", location="Remote"))
        self.assertEqual(r["verdict"], "cannot_tell")
        self.assertEqual(r["reasons"], ["location_unknown"])

    def test_wv4_no_text_but_clearly_abroad_is_reject(self):
        r = flt.evaluate(cfg(), posting(title="Data Engineer", text=None, location="London, United Kingdom"))
        self.assertEqual(r["verdict"], "reject")


class WV5Repetition(unittest.TestCase):
    def test_wv5_repeats_count_once_and_cap_holds(self):
        many = " ".join(["python"] * 9)
        self.assertEqual(flt.score_parts(cfg(), "Engineer", [many])["R2"], 1)
        six = "python sql scala spark airflow kafka"
        self.assertEqual(flt.score_parts(cfg(), "Engineer", [six])["R2"], 4)

    def test_wv5_ranking_prefers_distinct_skills_over_repetition(self):
        c = cfg()
        a = flt.evaluate(c, posting(title="Data Engineer", pid="a", text="<p>" + "python " * 9 + "</p>"))
        b = flt.evaluate(c, posting(title="Data Engineer", pid="b", text="<p>python, sql, kafka</p>"))
        self.assertEqual([r["id"] for r in flt.shortlist(c, [a, b])], ["b", "a"])


class Location(unittest.TestCase):
    def place(self, name, country=None, other=None):
        return posting_place({"name": name, "country": country, "other": other or []})["place"]

    def test_location_rule_cases(self):
        self.assertEqual(self.place("San Francisco, CA"), "us")
        self.assertEqual(self.place("US-Remote"), "us")
        self.assertEqual(self.place("Remote - US"), "us")
        self.assertEqual(self.place("Remote, North America"), "us")
        self.assertEqual(self.place("Remote - Australia"), "not_us")
        self.assertEqual(self.place("Toronto, ON"), "not_us")
        self.assertEqual(self.place("Remote"), "unknown")
        self.assertEqual(self.place(""), "unknown")
        self.assertEqual(self.place("Dublin", country="United States"), "us", "a country field decides")
        self.assertEqual(self.place("Seattle, Washington", country="Canada"), "not_us", "a country field decides")
        self.assertEqual(self.place("London", other=[{"name": "New York, NY", "country": None}]), "us")


class FilterFileAgreesWithFilterMd(unittest.TestCase):
    def test_every_listed_word_and_number_appears_in_filter_md(self):
        doc = (ROOT / "FILTER.md").read_text(encoding="utf-8").lower()
        c = cfg()
        for w in c["title_exclusions"] + c["role_words"] + c["topic_words"] + list(c["skills"]):
            self.assertRegex(doc, r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])", w)
        self.assertIn("+3", doc)
        self.assertIn("score of 4 or more", doc)
        self.assertIn("at most 4", doc)


if __name__ == "__main__":
    unittest.main()
