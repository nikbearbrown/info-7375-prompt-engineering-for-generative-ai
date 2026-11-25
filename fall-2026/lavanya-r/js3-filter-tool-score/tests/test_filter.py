"""Tests for the JS3 filter (FILTER.md v1.0), written before agent/filter.py.

Every posting here is CONSTRUCTED for the test (not from a board), except
where a test names a real posting key from the frozen corpus.
"""

import json
import pathlib
import re
import unittest

HERE = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((HERE / "config" / "filter.json").read_text())

LONG = " This paragraph is filler so the text is long enough to judge." * 5


def posting(title="Software Engineer", locations=("San Francisco, CA",),
            text="We build LLM agents for evaluation in Python and SQL." + LONG):
    return {"key": "test/x/1", "title": title, "locations": list(locations),
            "text": text}


def run(p, cfg=None):
    from agent import filter as f
    return f.evaluate(p, cfg or CFG)


class TestConfigMatchesFilterMd(unittest.TestCase):
    """config/filter.json must say what FILTER.md section 1 says."""

    def setUp(self):
        self.md = (HERE / "FILTER.md").read_text()

    def row(self, label):
        line = next(l for l in self.md.splitlines() if l.startswith(f"| {label}"))
        return line.split("|")[2]

    def test_word_lists(self):
        for label, key in [("R1", "seniority_words"), ("R2", "not_my_role_words"),
                           ("S1", "role_words"), ("S2", "topic_words")]:
            cell = self.row(label)
            for w in CFG[key]:
                self.assertIn(w, cell, f"{key}: {w!r} not in FILTER.md {label}")

    def test_numbers(self):
        self.assertIn("**Threshold:** 5 points", self.md)
        self.assertEqual(CFG["threshold"], 5)
        self.assertEqual(CFG["role_points"], 3)
        self.assertEqual((CFG["topic_max"], CFG["skill_max"]), (3, 3))
        self.assertIn("**3 or more**", self.row("R5"))
        self.assertEqual(CFG["max_years_asked"], 2)
        self.assertIn("under 200 characters", self.md)
        self.assertEqual(CFG["min_text_chars"], 200)


class TestHardRejects(unittest.TestCase):
    def test_r1_seniority_in_title(self):
        r = run(posting(title="Senior Software Engineer"))
        self.assertEqual(r["verdict"], "reject")
        self.assertIn("R1", r["rejected_by"])

    def test_r1_head_of(self):
        r = run(posting(title="Head of Early Career Recruiting"))
        self.assertIn("R1", r["rejected_by"])

    def test_r2_not_my_role(self):
        r = run(posting(title="Recruiter, Applied AI"))
        self.assertIn("R2", r["rejected_by"])

    def test_r3_outside_us(self):
        r = run(posting(locations=["London, United Kingdom"]))
        self.assertIn("R3", r["rejected_by"])

    def test_r3_us_forms(self):
        for loc in ["San Francisco", "Foster City, CA", "Remote - Washington D.C.",
                    "Austin, Texas", "Remote-Friendly, United States"]:
            r = run(posting(locations=[loc]))
            self.assertNotIn("R3", r["rejected_by"], loc)

    def test_r3_any_part_counts(self):
        r = run(posting(locations=["London, UK", "Seattle, WA"]))
        self.assertNotIn("R3", r["rejected_by"])

    def test_r4_cant_sponsor(self):
        r = run(posting(text="LLM agents in Python and SQL. We are unable to "
                             "sponsor visas for this role." + LONG))
        self.assertIn("R4", r["rejected_by"])

    def test_r4_silence_is_not_reject(self):
        r = run(posting())
        self.assertNotIn("R4", r["rejected_by"])

    def test_r5_years(self):
        for text, rejected in [("You have 3+ years of experience.", True),
                               ("2-4 years of experience in Python.", False),
                               ("At least 5 years building systems.", True),
                               ("1+ years with SQL; 5+ years preferred.", False),
                               ("We were founded 25 years ago.", False)]:
            r = run(posting(text="LLM agents, Python, SQL. " + text + LONG))
            self.assertEqual("R5" in r["rejected_by"], rejected, text)

    def test_every_failed_rule_is_listed(self):
        r = run(posting(title="Staff Recruiter", locations=["Tokyo, Japan"]))
        self.assertEqual(r["rejected_by"], ["R1", "R2", "R3"])

    def test_real_sales_platform_posting_rejected_by_r5_only(self):
        from agent.corpus import load
        posts = {p["key"]: p for p in load(HERE / "runs/2026-11-24T220432Z-live")}
        p = posts["ashby/openai/1f7c6071-ad3a-4903-9b05-4684f5c1a7c8"]
        self.assertEqual(run(p)["rejected_by"], ["R5"])


class TestScore(unittest.TestCase):
    def test_parts_and_threshold(self):
        r = run(posting())  # Software Engineer; LLM, agents, evaluation; Python, SQL
        self.assertEqual(r["score_parts"], {"S1": 3, "S2": 3, "S3": 2})
        self.assertEqual(r["score"], 8)
        self.assertEqual(r["verdict"], "keep")

    def test_title_alone_is_not_enough(self):
        r = run(posting(text="We build great things together." + LONG))
        self.assertEqual(r["score"], 3)
        self.assertEqual(r["verdict"], "reject")
        self.assertEqual(r["rejected_by"], ["below_threshold"])

    def test_exactly_threshold_keeps(self):
        r = run(posting(text="We use Python and SQL daily." + LONG))
        self.assertEqual(r["score"], 5)
        self.assertEqual(r["verdict"], "keep")

    def test_matches_are_recorded(self):
        r = run(posting())
        self.assertEqual(r["matched"]["S1"], ["Software Engineer"])
        self.assertEqual(sorted(r["matched"]["S3"]), ["Python", "SQL"])


class TestCannotTell(unittest.TestCase):
    def test_short_text(self):
        r = run(posting(text="Python LLM"))
        self.assertEqual(r["verdict"], "cannot_tell")

    def test_no_location(self):
        self.assertEqual(run(posting(locations=[]))["verdict"], "cannot_tell")

    def test_bare_remote(self):
        self.assertEqual(run(posting(locations=["Remote"]))["verdict"],
                         "cannot_tell")

    def test_title_reject_still_rejects_without_text(self):
        r = run(posting(title="Staff Engineer", text=""))
        self.assertEqual(r["verdict"], "reject")


class TestWrongVersions(unittest.TestCase):
    """FILTER.md section 4: each wrong version must be caught."""

    def test_w1_whole_words_only(self):
        # 'ML' inside 'HTML', 'AI' inside 'Aide', 'Intern' inside 'Internal'
        for title in ["HTML Email Developer", "Executive Aide",
                      "Internal Tools Engineer"]:
            self.assertEqual(run(posting(title=title))["score_parts"]["S1"], 0,
                             title)
        r = run(posting(title="Software Engineer", text=(
            "Leadership of the seniority-based team. Sr.ly not." + LONG)))
        self.assertNotIn("R1", r["rejected_by"])

    def test_w2_seniority_in_text_does_not_reject(self):
        r = run(posting(text="LLM agents, Python, SQL. You will work with "
                             "senior engineers and a staff mentor." + LONG))
        self.assertNotIn("R1", r["rejected_by"])

    def test_w3_cannot_tell_is_not_reject(self):
        self.assertNotEqual(run(posting(text=""))["verdict"], "reject")

    def test_w4_repetition_does_not_add_points(self):
        once = run(posting(text="LLM. Python." + LONG))
        many = run(posting(text="LLM. " * 40 + "Python." + LONG))
        self.assertEqual(once["score"], many["score"])

    def test_w6_sales_is_not_a_reject_word(self):
        r = run(posting(title="Full Stack Software Engineer, Sales Platform"))
        self.assertEqual(r["rejected_by"], [])
        self.assertEqual(r["verdict"], "keep")


if __name__ == "__main__":
    unittest.main()
