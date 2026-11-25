"""FILTER.md v2 (accepted changes 1, 2, 7, 8 of 2026-11-25). Written from FILTER.md before the v2 code.

Every posting here is CONSTRUCTED. v1 stays the library default so the v1 tests and the
v1 run remain reproducible; v2 is selected with version=2.
"""
import json
import tempfile
import unittest
from pathlib import Path

from tests.js3_helpers import ROOT, FILLER, ashby, body, flt, gh, skills, sl


def v2(posting):
    return flt().evaluate(posting, skills(), version=2)


def v1(posting):
    return flt().evaluate(posting, skills(), version=1)


class Change1LeadNoLongerExcluded(unittest.TestCase):
    def test_lead_no_longer_blocks(self):
        p = gh("Lead Data Scientist", content=body("SQL"))
        self.assertEqual(v2(p)["verdict"], "accept")
        self.assertEqual((v1(p)["verdict"], v1(p)["rule"]), ("reject", "F2"))

    def test_manager_still_blocks(self):
        v = v2(gh("Data Science Manager", content=body("SQL")))
        self.assertEqual((v["verdict"], v["rule"], v["field"]), ("reject", "F2", "title"))

    def test_other_exclusions_still_block(self):
        for title in ("Director, Analytics", "Head of Data", "Data Science Intern"):
            with self.subTest(title=title):
                self.assertEqual(v2(gh(title, content=body("SQL")))["rule"], "F2")


class Change2ResumePractices(unittest.TestCase):
    def test_each_practice_passes_f4_without_a_shipped_skill(self):
        for sentence, practice in (("We run experimentation and causal inference.", "experimentation"),
                                   ("You will own A/B testing for ranking.", "A/B testing"),
                                   ("Every launch is an A/B test.", "A/B test"),
                                   ("Several A/B tests run each week.", "A/B tests"),
                                   ("You will build LLM evaluation pipelines.", "LLM evaluation"),
                                   ("Quality is scored with LLM-as-judge metrics.", "LLM-as-judge")):
            with self.subTest(practice=practice):
                p = gh("Applied ML Scientist", content=body(sentence))
                v = v2(p)
                self.assertEqual(v["verdict"], "accept")
                self.assertIn(practice, v["practices_found"])
                self.assertEqual(v["skills_found"], [])
                self.assertEqual((v1(p)["verdict"], v1(p)["rule"]), ("reject", "F4"))

    def test_near_words_do_not_count(self):
        v = v2(gh("Applied ML Scientist", content=body("We experiment often and value evaluation and testing.")))
        self.assertEqual((v["verdict"], v["rule"]), ("reject", "F4"))

    def test_c2_still_names_shipped_skills_only(self):
        p = gh("Applied ML Scientist", content=body("We run experimentation in Python."))
        entries = sl().build_shortlist([p], skills(), version=2)
        self.assertEqual([c["text"] for c in entries[0]["claims"] if c["claim"] == "C2"], ["Uses Python"])

    def test_known_miss_managing_duties_are_not_read(self):
        # FILTER.md v2 accepts this known miss (audit row 15): managing duties in the text are not seen.
        p = gh("Staff Applied AI/ML Scientist",
               content=body("Use experimentation and causal inference. Mentor or manage Senior Applied Scientists."))
        self.assertEqual(v2(p)["verdict"], "accept")


class Change7USOfficeLocations(unittest.TestCase):
    def test_us_state_city_office_counts_as_us(self):
        for location in ("US California (Redwood City) - Office", "US Pennsylvania (Philadelphia) - Office",
                         "US New York (New York) - Office", "US District of Columbia (Washington) - Office"):
            with self.subTest(location=location):
                p = ashby(location=location, html_text=body("SQL"))
                self.assertEqual(v2(p)["verdict"], "accept")
                c1 = sl().label_c1(p, version=2)
                self.assertEqual((c1["label"], c1["quote"]), ("supported", location))

    def test_non_us_or_unknown_state_is_still_rejected(self):
        for location in ("IN Tamil Nadu (Chennai) - Office", "US Narnia (Cair Paravel) - Office",
                         "UK London (Soho) - Office", "US California (Redwood City) - Warehouse"):
            with self.subTest(location=location):
                v = v2(ashby(location=location, html_text=body("SQL")))
                self.assertEqual((v["verdict"], v["rule"]), ("reject", "F3"))

    def test_v1_still_rejects_the_office_form(self):
        p = ashby(location="US California (Redwood City) - Office", html_text=body("SQL"))
        self.assertEqual(v1(p)["rule"], "F3")


class Change8HybridNeedsScheduleWords(unittest.TestCase):
    TECH = "Choose an agent strategy (preload vs. tool-calling vs. hybrid) for each surface."

    def test_technical_hybrid_alone_does_not_contradict(self):
        p = gh(location="New York City, NY", content=body(self.TECH))
        self.assertEqual(sl().label_c4(p, version=2)["label"], "insufficient")
        self.assertEqual(sl().label_c4(p, version=1)["label"], "contradicted")

    def test_schedule_hybrid_after_a_technical_one_is_the_quote(self):
        schedule = "Hybrid employees go into the office 3 days per week."
        p = gh(location="New York City, NY", content=body(self.TECH + " " + schedule))
        c4 = sl().label_c4(p, version=2)
        self.assertEqual(c4["label"], "contradicted")
        self.assertIn("office 3 days per week", c4["quote"])
        self.assertNotIn("tool-calling", c4["quote"])

    def test_schedule_and_location_hybrid_still_contradict(self):
        p = gh(location="New York City, NY", content=body("We work a hybrid schedule, three days a week."))
        self.assertEqual(sl().label_c4(p, version=2)["label"], "contradicted")
        p = gh(location="Israel - Hybrid (3 days/week in office required)")
        self.assertEqual(sl().label_c4(p, version=2)["label"], "contradicted")

    def test_onsite_and_in_office_unchanged(self):
        for sentence in ("This role is onsite five days a week.", "This position is in-office only."):
            with self.subTest(sentence=sentence):
                p = gh(location="New York City, NY", content=body(sentence))
                self.assertEqual(sl().label_c4(p, version=2)["label"], "contradicted")


class Unchanged(unittest.TestCase):
    def test_default_version_is_v1(self):
        p = gh("Lead Data Scientist", content=body("SQL"))
        self.assertEqual(flt().evaluate(p, skills())["rule"], "F2")

    def test_f1_abstention_and_missing_fields_unchanged_in_v2(self):
        self.assertEqual(v2(gh("Software Engineer", content=body("SQL")))["rule"], "F1")
        self.assertEqual(v2(gh(content="<p>Short.</p>"))["verdict"], "abstain")
        v = v2(gh(content=body("SQL"), drop=("location",)))
        self.assertIn("missing: location.name", v["reason"])

    def test_unknown_version_is_refused(self):
        with self.assertRaises(ValueError):
            flt().evaluate(gh(content=body("SQL")), skills(), version=3)


class RunV2(unittest.TestCase):
    def test_run_records_the_filter_version(self):
        from agent3 import run
        with tempfile.TemporaryDirectory() as tmp:
            run.run(ROOT / "out", Path(tmp), ROOT / "data" / "resume.example.json", version=2)
            doc = json.loads((Path(tmp) / "results.json").read_text(encoding="utf-8"))
        self.assertEqual(doc["filter"], "FILTER.md v2")
        self.assertEqual(len(doc["results"]), 182)


if __name__ == "__main__":
    unittest.main()
