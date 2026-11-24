"""Tests for agent/filter.py, written before agent/filter.py exists (Nov 24, 2026).

Each test names the FILTER.md rule or wrong version (W1-W5) it checks.
Run from js3-filter-tool-score/:

    python3 -m unittest -v tests.test_filter
"""

from __future__ import annotations

import unittest

from agent import filter as F
from agent.postings import load_run

RUN = "evidence/run-20261123-185425Z"
SKILLS = ["Python", "Go", "React", "TypeScript", "SQL", "Java"]


def posting(title="Software Engineer", location="Remote US", text="", uid=None):
    return {"uid": uid or f"t:{title}:{location}", "board": "t", "title": title,
            "location": location, "text": text, "url": "https://example.test/job"}


def years(text):
    return [n for n, _quote in F.find_years(text)]


class DecimalYears(unittest.TestCase):
    """R2 + FILTER.md v1.1: "1.5+" is 1.5, never 5 (the Day 1 survey bug)."""

    def test_decimal_is_read_whole(self):
        self.assertEqual(years("1.5+ years of experience building backend systems"), [1.5])

    def test_integer_forms(self):
        self.assertEqual(years("5+ years of experience"), [5])
        self.assertEqual(years("2 years of professional experience"), [2])

    def test_ranges_take_the_low_end(self):
        self.assertEqual(years("2-4 years of industry experience"), [2])
        self.assertEqual(years("2–4 years of industry experience"), [2])   # en dash
        self.assertEqual(years("3 to 5 years of experience"), [3])

    def test_smallest_wins(self):
        text = "4+ years of experience, or 2+ years of experience with a Master's degree"
        self.assertEqual(F.min_years(text), 2)

    def test_needs_experience_nearby(self):
        # Company boilerplate: "years" with no "experience" within 60 characters.
        self.assertEqual(years("We have been building the future of finance for 10 years."), [])
        self.assertIsNone(F.min_years("Founded 12 years ago."))

    def test_real_posting_swe_ii_asks_1_5(self):
        # affirm:8032173003, Software Engineer II, Full Stack (Card Acquisition): "1.5+ years".
        p = next(p for p in load_run(RUN) if p["uid"] == "affirm:8032173003")
        self.assertEqual(F.min_years(p["text"]), 1.5)


class Gates(unittest.TestCase):
    def test_g1_seniority_word(self):
        for t in ["Senior Software Engineer", "Sr. Software Engineer", "Staff Software Engineer, Backend",
                  "Engineering Manager", "Lead Software Engineer"]:
            self.assertIn("G1", F.judge(posting(t), SKILLS)["gates"], t)

    def test_g1_whole_word_only(self):
        self.assertNotIn("G1", F.judge(posting("Software Engineer, Leadership Tools"), SKILLS)["gates"])

    def test_g2_intern_whole_word(self):
        self.assertIn("G2", F.judge(posting("Software Engineer Intern"), SKILLS)["gates"])
        self.assertIn("G2", F.judge(posting("Software Engineering Internship"), SKILLS)["gates"])
        self.assertNotIn("G2", F.judge(posting("Software Engineer, Internal Tools"), SKILLS)["gates"])

    def test_g3_all_parts_non_us(self):
        self.assertIn("G3", F.judge(posting(location="Remote Canada"), SKILLS)["gates"])
        self.assertIn("G3", F.judge(posting(location="Toronto, Canada; London, UK"), SKILLS)["gates"])
        self.assertNotIn("G3", F.judge(posting(location="Remote US"), SKILLS)["gates"])
        self.assertNotIn("G3", F.judge(posting(location="Palo Alto, CA (Open to US-based Remote)"), SKILLS)["gates"])

    def test_g3_empty_or_unknown_location_cannot_tell(self):
        for loc in ["", None, "Somewhere Else"]:
            d = F.judge(posting(location=loc), SKILLS)
            self.assertNotIn("G3", d["gates"], loc)
            self.assertIn("location", d["cannot_tell"], loc)

    def test_no_title_is_its_own_reject(self):
        d = F.judge(posting(title=""), SKILLS)
        self.assertFalse(d["keep"])
        self.assertEqual(d["gates"], ["no title"])


class W1EngineerSubstring(unittest.TestCase):
    """W1: 'Engineer' anywhere in the title is not a role match."""

    def test_other_engineer_jobs_get_no_role_points(self):
        for t in ["Sales Engineer", "Partner Engineer", "IT Engineer", "Offensive Security Engineer",
                  "Analyst, Early Career (Full Stack)"]:
            self.assertEqual(F.judge(posting(t), SKILLS)["rules"]["R1"], 0, t)

    def test_role_phrases_get_role_points(self):
        for t in ["Software Engineer, Backend", "Full Stack Engineer", "iOS Engineer", "Machine Learning Engineer"]:
            self.assertEqual(F.judge(posting(t), SKILLS)["rules"]["R1"], 0.5, t)


class W2TitleLevel(unittest.TestCase):
    """W2: a title level of I/II is not entry level when the body asks for more."""

    def test_swe_ii_with_5_years_is_rejected(self):
        d = F.judge(posting("Software Engineer II", text="5+ years of experience with Python"), SKILLS)
        self.assertFalse(d["keep"])
        self.assertEqual(d["rules"]["R2"], -0.4)

    def test_engineer_ii_is_not_an_entry_signal(self):
        self.assertEqual(F.judge(posting("Software Engineer II"), SKILLS)["rules"]["R3"], 0)

    def test_engineer_i_is_an_entry_signal(self):
        self.assertEqual(F.judge(posting("Software Engineer I, Fullstack (Search)"), SKILLS)["rules"]["R3"], 0.2)


class W3RankByHits(unittest.TestCase):
    """W3: more keyword/skill hits does not mean a better fit."""

    def test_short_entry_posting_outranks_long_many_skill_posting(self):
        short = posting("Software Engineer, New Grad", text="1+ years of experience with Python.", uid="short")
        long_ = posting("Software Engineer, Platform", uid="long", text=(
            "4+ years of experience. Python, Go, React, TypeScript, SQL, Java. " * 20))
        ranked = F.rank([F.judge(long_, SKILLS), F.judge(short, SKILLS)])
        self.assertEqual(ranked[0]["uid"], "short")

    def test_skill_bonus_is_flat(self):
        one = F.judge(posting(text="Python"), SKILLS)["rules"]["R4"]
        six = F.judge(posting(text="Python, Go, React, TypeScript, SQL, Java"), SKILLS)["rules"]["R4"]
        self.assertEqual(one, six)


class W4DedupeBeforeFilter(unittest.TestCase):
    """W4: duplicates are not removed before the filter."""

    def test_us_copy_survives_when_canada_copy_comes_first(self):
        title = "Software Engineer I, Fullstack (Search)"
        ps = [posting(title, "Remote Canada", uid="ca"), posting(title, "Remote US", uid="us")]
        kept = [d["uid"] for d in F.filter_postings(ps, SKILLS) if d["keep"]]
        self.assertEqual(kept, ["us"])


class W5AnyNonUsPart(unittest.TestCase):
    """W5: one non-US part does not reject a posting that also lists US places."""

    def test_mixed_locations_pass(self):
        d = F.judge(posting(location="Menlo Park, CA; New York, NY; Toronto"), SKILLS)
        self.assertNotIn("G3", d["gates"])


class Threshold(unittest.TestCase):
    def test_role_phrase_alone_is_kept(self):
        d = F.judge(posting("Software Engineer, Backend"), SKILLS)
        self.assertEqual(d["score"], 0.5)
        self.assertTrue(d["keep"])

    def test_known_hole_non_swe_with_entry_signal_and_low_years(self):
        # FILTER.md section 1: R2 (+0.30) + R3 (+0.20) = 0.50 keeps a non-SWE title.
        d = F.judge(posting("Analyst, Early Career", text="1+ years of experience"), SKILLS)
        self.assertEqual(d["score"], 0.5)
        self.assertTrue(d["keep"])

    def test_text_missing_is_marked(self):
        d = F.judge(posting(text=""), SKILLS)
        self.assertIn("text", d["cannot_tell"])

    def test_level_cannot_tell(self):
        d = F.judge(posting("Software Engineer, Backend", text="You will build Python services."), SKILLS)
        self.assertIn("level", d["cannot_tell"])


class RealRun(unittest.TestCase):
    def test_every_posting_gets_one_decision(self):
        ps = load_run(RUN)
        ds = F.filter_postings(ps, SKILLS)
        self.assertEqual(len(ds), 400)
        self.assertEqual(len({d["uid"] for d in ds}), 400)


if __name__ == "__main__":
    unittest.main()
