"""Tests for the filter in FILTER.md v1.0, written and committed before src/filter.py existed.

Every posting here is CONSTRUCTED for the test; none is a real posting.

    python3 -m unittest discover -s tests -v
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import filter as flt  # noqa: E402

with open(os.path.join(ROOT, "persona", "aarav-patel.resume.json"), encoding="utf-8") as f:
    SKILLS = flt.resume_skills(json.load(f))

GOOD_TEXT = ("You will build backend services in Python and Java on AWS. "
             "Requirements: 1+ years of experience building web services.")


def posting(title="Software Engineer, Payments", location="New York, NY", country=None,
            text=GOOD_TEXT, pid="c1"):
    return {"board": "constructed", "id": pid, "title": title, "location": location,
            "country": country, "text": text}


def verdict(**kw):
    """The tests below pin FILTER.md v1.0; class V1_1 tests the adopted changes."""
    return flt.judge(posting(**kw), SKILLS, flt.V1_0)


class Skills(unittest.TestCase):
    def test_resume_skills_exclude_unshipped(self):
        self.assertIn("Python", SKILLS)
        self.assertIn("Fluent Bit", SKILLS)
        self.assertNotIn("Rust", SKILLS)
        self.assertNotIn("Terraform", SKILLS)
        self.assertEqual(len(SKILLS), 15)


class R1_RoleWords(unittest.TestCase):
    def test_non_engineering_title_rejected(self):
        v = verdict(title="Account Executive, Enterprise")
        self.assertEqual((v["verdict"], v["rule"]), ("reject", "R1"))

    def test_each_role_word_passes_r1(self):
        for t in ["Software Engineer", "Software Developer", "Backend Engineer",
                  "Back-End Engineer", "Back End Engineer", "Full Stack Engineer",
                  "Full-Stack Engineer", "Fullstack Engineer", "Cloud Engineer",
                  "Platform Engineer, Data"]:
            with self.subTest(title=t):
                self.assertNotEqual(verdict(title=t)["rule"], "R1")

    def test_software_engineering_is_not_software_engineer(self):
        # whole-word: "Software Engineering" must not match the role word "software engineer"
        self.assertEqual(verdict(title="Software Engineering Intern Program")["rule"], "R1")


class R2_Seniority(unittest.TestCase):
    def test_each_seniority_word_rejects(self):
        for t in ["Senior Software Engineer", "Sr. Software Engineer", "Staff Software Engineer",
                  "Principal Software Engineer", "Lead Software Engineer",
                  "Software Engineer Manager", "Director, Software Engineer", "Head Software Engineer"]:
            with self.subTest(title=t):
                v = verdict(title=t)
                self.assertEqual((v["verdict"], v["rule"]), ("reject", "R2"))


class R3_NoDescription(unittest.TestCase):
    def test_empty_text_cannot_tell(self):
        for text in ["", "   ", None]:
            with self.subTest(text=text):
                v = verdict(text=text)
                self.assertEqual((v["verdict"], v["rule"]), ("cannot_tell", "R3"))


class R4_Location(unittest.TestCase):
    def test_us_locations_pass(self):
        for loc in ["San Francisco, CA", "New York, NY", "United States", "Remote - US",
                    "Remote, USA", "Seattle, Washington", "Toronto, ON • San Francisco, CA"]:
            with self.subTest(location=loc):
                self.assertEqual(verdict(location=loc)["verdict"], "keep")

    def test_non_us_locations_rejected(self):
        for loc in ["Sao Paulo - Brazil", "São Paulo, Brazil", "Berlin, Germany", "London",
                    "Toronto, ON", "Remote - Europe"]:
            with self.subTest(location=loc):
                v = verdict(location=loc)
                self.assertEqual((v["verdict"], v["rule"]), ("reject", "R4"))

    def test_missing_or_remote_only_cannot_tell(self):
        for loc in ["", None, "Remote", "Remote / Hybrid"]:
            with self.subTest(location=loc):
                v = verdict(location=loc)
                self.assertEqual((v["verdict"], v["rule"]), ("cannot_tell", "R4"))

    def test_structured_country_used_first(self):
        self.assertEqual(verdict(location="Remote", country="US")["verdict"], "keep")
        v = verdict(location="Remote", country="BR")
        self.assertEqual((v["verdict"], v["rule"]), ("reject", "R4"))


class R5_Years(unittest.TestCase):
    def yrs(self, sentence):
        return verdict(text="You will write Python and Java services on AWS. " + sentence)

    def test_under_four_passes(self):
        for s in ["Requirements: 1+ years of experience.", "0-2 years of experience preferred.",
                  "3+ years of professional experience.", "At least 3 years of industry experience."]:
            with self.subTest(s=s):
                self.assertEqual(self.yrs(s)["verdict"], "keep")

    def test_four_or_more_rejected(self):
        for s in ["4+ years of experience.", "5+ years of professional software experience.",
                  "7 or more years of experience building systems.", "10 yrs experience."]:
            with self.subTest(s=s):
                v = self.yrs(s)
                self.assertEqual((v["verdict"], v["rule"]), ("reject", "R5"))

    def test_range_across_line_or_no_number_cannot_tell(self):
        for s in ["3-5 years of experience.", "3 to 5 years of relevant experience.",
                  "Several years of experience with distributed systems."]:
            with self.subTest(s=s):
                v = self.yrs(s)
                self.assertEqual((v["verdict"], v["rule"]), ("cannot_tell", "R5"))

    def test_years_not_about_experience_ignored(self):
        v = self.yrs("We have grown for 12 years. Experience with APIs is a plus.")
        self.assertEqual(v["verdict"], "keep")

    def test_smallest_lower_bound_used(self):
        v = self.yrs("5+ years of experience, or 3+ years of experience with a Master's degree.")
        self.assertEqual(v["verdict"], "keep")

    def test_years_quote_is_from_the_text(self):
        v = self.yrs("5+ years of professional software experience.")
        self.assertTrue(any("5+ years" in e["quote"] for e in v["evidence"]))


class R6_Skills(unittest.TestCase):
    def test_two_skills_kept_one_rejected(self):
        self.assertEqual(verdict(text="We use Python and Kafka.")["verdict"], "keep")
        v = verdict(text="We use Python and Go.")
        self.assertEqual((v["verdict"], v["rule"]), ("reject", "R6"))

    def test_unshipped_skills_do_not_count(self):
        v = verdict(text="We use Rust, Terraform, and Python.")
        self.assertEqual((v["verdict"], v["rule"]), ("reject", "R6"))

    def test_skills_listed_with_quotes(self):
        v = verdict(text="We use Python and Kafka.")
        self.assertEqual(sorted(v["skills"]), ["Kafka", "Python"])
        for s in v["skills"]:
            self.assertTrue(any(e["check"] == "skill" and e["quote"] == s for e in v["evidence"]))


class Score(unittest.TestCase):
    def test_title_bonus_and_skill_points(self):
        self.assertEqual(verdict(title="Software Engineer", text="Python, Java, AWS.")["score"], 5)
        self.assertEqual(verdict(title="Backend Engineer", text="Python, Java, AWS.")["score"], 3)

    def test_no_score_unless_kept(self):
        self.assertIsNone(verdict(title="Account Executive")["score"])


class WrongVersion1_SubstringMatching(unittest.TestCase):
    """FILTER.md wrong version 1: part-word matches must not change any verdict."""

    def test_javascript_is_not_java(self):
        v = verdict(text="We use JavaScript and Python.")
        self.assertEqual((v["verdict"], v["rule"]), ("reject", "R6"))
        self.assertNotIn("Java", v["skills"])

    def test_postgresql_is_not_sql(self):
        v = verdict(text="We use PostgreSQL.")
        self.assertEqual(v["skills"], ["PostgreSQL"])

    def test_leadership_is_not_lead(self):
        self.assertEqual(verdict(title="Software Engineer, Leadership Tools")["verdict"], "keep")

    def test_russia_and_belarus_are_not_us(self):
        for loc in ["Moscow, Russia", "Minsk, Belarus", "Sydney, Australia"]:
            with self.subTest(location=loc):
                self.assertEqual(verdict(location=loc)["rule"], "R4")


class WrongVersion2_IgnoresLocation(unittest.TestCase):
    """FILTER.md wrong version 2: the same posting must flip when only the location changes."""

    def test_same_posting_flips_on_location(self):
        self.assertEqual(verdict(location="Austin, TX")["verdict"], "keep")
        self.assertEqual(verdict(location="Sao Paulo - Brazil")["verdict"], "reject")
        self.assertEqual(verdict(location="")["verdict"], "cannot_tell")


class Evidence(unittest.TestCase):
    def test_every_quote_occurs_in_the_posting(self):
        p = posting(text="Python and Kafka on AWS. 2+ years of experience.")
        v = flt.judge(p, SKILLS, flt.V1_0)
        whole = " ".join([p["title"], p["location"] or "", p["text"]])
        for e in v["evidence"]:
            self.assertIn(e["quote"], whole)

    def test_context_is_the_whole_sentence(self):
        t = "Experience with front-end (e.g. React/TypeScript) and Node.js services. Python is used too."
        ctx = {e["quote"]: e["context"] for e in flt.judge(posting(text=t), SKILLS, flt.V1_0)["evidence"]
               if e["check"] == "skill"}
        self.assertEqual(ctx["TypeScript"], "Experience with front-end (e.g. React/TypeScript) and Node.js services.")
        self.assertEqual(ctx["Python"], "Python is used too.")


class V1_1(unittest.TestCase):
    """FILTER.md v1.1: changes A, B, C (added after the audit, 2026-11-14)."""

    def v(self, **kw):
        return flt.judge(posting(**kw), SKILLS, flt.V1_1)

    def test_a_largest_years_bound(self):
        # the false friend from the audit: "including 3+ years" is a sub-requirement of 5+
        t = "Python and Java. Bring 5+ years of professional experience, including 3+ years of experience with Ruby."
        v = self.v(text=t)
        self.assertEqual((v["verdict"], v["rule"]), ("reject", "R5"))
        self.assertEqual(flt.judge(posting(text=t), SKILLS, flt.V1_0)["verdict"], "keep")

    def test_b_interns_rejected(self):
        for t in ["Software Engineer Intern (Summer 2027)", "PhD Intern, Software Engineer - Graphics",
                  "Software Engineer Internship"]:
            with self.subTest(title=t):
                self.assertEqual(self.v(title=t)["rule"], "R2")

    def test_b_internal_is_not_intern(self):
        self.assertEqual(self.v(title="Software Engineer, Internal Tools")["verdict"], "keep")

    def test_c_one_skill_kept_zero_rejected(self):
        self.assertEqual(self.v(text="We use Python and Go.")["verdict"], "keep")
        v = self.v(text="We use Go and Kotlin.")
        self.assertEqual((v["verdict"], v["rule"]), ("reject", "R6"))

    def test_default_is_v1_1(self):
        self.assertEqual(flt.judge(posting(), SKILLS)["filter_version"], "1.1")


if __name__ == "__main__":
    unittest.main()
