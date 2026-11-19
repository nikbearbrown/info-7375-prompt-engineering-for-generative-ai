"""Tests for agent/filter.py's options: candidate FILTER v2 changes, not rules. Constructed postings only."""

import itertools
import unittest

from support import persona

from agent import filter as filter_v1
from agent import rule

ABSENT = object()
SKILLS2 = "Constructed: you will use Python and SQL."
S = {"seniority_words": filter_v1.SENIORITY_WORDS}
Y = {"max_years": 3}


def posting(title="Product Manager", location="New York", text=SKILLS2, posting_id="920001"):
    built = {"posting_id": posting_id, "ats": "greenhouse"}
    if title is not ABSENT:
        built["title"] = title
    if location is not ABSENT:
        built["location"] = {"name": location}
    if text is not ABSENT:
        built["content"] = text
    return built


def judge(p, options=None):
    return filter_v1.judge(p, persona(), options)


class TestDefaultsAreV1(unittest.TestCase):
    def test_no_options_or_the_defaults_reproduce_v1_exactly(self):
        titles = ["Product Manager", "Senior Product Manager", "Software Engineer", ABSENT, "  "]
        locations = ["New York", "London", "remote", ABSENT]
        texts = ["Java only.", "Python only.", SKILLS2, "Python, SQL, user research. 8+ years.", ABSENT, " "]
        resume = persona()
        for title, location, text in itertools.product(titles, locations, texts):
            p = posting(title, location, text)
            v1 = filter_v1.judge(p, resume)
            with self.subTest(title=title, location=location, text=text):
                for options in (None, {}, dict(filter_v1.DEFAULT_OPTIONS), {"seniority_words": []}):
                    self.assertEqual(filter_v1.judge(p, resume, options), v1)
                self.assertNotIn("C4", v1)
                if not v1["missing"]:
                    self.assertEqual(v1["verdict"], rule.judge(p, resume)[0])


class TestSkillsNeeded(unittest.TestCase):
    def test_one(self):
        record = judge(posting(text="Python only."), {"skills_needed": 1})
        self.assertEqual((record["C3"], record["score"], record["verdict"]), ("pass", 1, "relevant"))
        self.assertEqual(judge(posting(text="Java only."), {"skills_needed": 1})["C3"], "fail")
        self.assertEqual(judge(posting(text="Python only."))["verdict"], "not_relevant")  # v1

    def test_zero_passes_any_present_text(self):
        record = judge(posting(text="Java only."), {"skills_needed": 0})
        self.assertEqual((record["C3"], record["score"], record["verdict"]), ("pass", 0, "relevant"))

    def test_zero_keeps_a_missing_text_missing(self):
        for text in (ABSENT, None, "   ", "&lt;p&gt;&lt;/p&gt;"):
            with self.subTest(text=text):
                record = judge(posting(text=text), {"skills_needed": 0})
                self.assertEqual((record["C3"], record["score"], record["missing"], record["verdict"]),
                                 ("missing", None, ["text"], "cannot_tell"))

    def test_zero_can_turn_a_reject_into_cannot_tell(self):
        p = posting(location=ABSENT, text="Java only.")
        self.assertEqual(judge(p)["verdict"], "not_relevant")  # v1: C3 fails, so the missing location never decides
        self.assertEqual(judge(p, {"skills_needed": 0})["verdict"], "cannot_tell")

    def test_a_higher_threshold(self):
        self.assertEqual(judge(posting(), {"skills_needed": 3})["verdict"], "not_relevant")

    def test_closest_call_stays_v1_s_flag(self):
        p = posting(text="Python only.")  # gates pass, score 1: a v1 closest call
        self.assertTrue(judge(p)["closest_call"])
        record = judge(p, {"skills_needed": 1})
        self.assertEqual((record["verdict"], record["closest_call"]), ("relevant", True))


class TestSeniorityWords(unittest.TestCase):
    def test_each_word_fails_c4_as_a_whole_word(self):
        cases = {
            "Senior Product Manager": "Senior",
            "Staff Product Manager": "Staff",
            "Lead Product Manager, Payments": "Lead",
            "Group Product Manager": "Group",
            "Principal Product Manager": "Principal",
            "Director, Product Management": "Director",
            "Head of Product": "Head of",
            "SENIOR product manager": "SENIOR",
            "Product Manager (Staff)": "Staff",
            "Head \t of  Product": "Head of",  # F1 collapses the whitespace first
        }
        for title, word in cases.items():
            with self.subTest(title=title):
                record = judge(posting(title=title), S)
                self.assertEqual((record["C4"], record["C4_reason"]), ("fail", f'title has "{word}"'))
                self.assertEqual(record["verdict"], "not_relevant")

    def test_words_inside_other_words_do_not_count(self):
        for title in ("Product Manager, Leadership Tools", "Staffing Product Manager", "Product Manager, Principals",
                      "Directory Product Manager", "Product Manager, Groupware", "Product Manager, Ahead of Plan",
                      "Head Product Manager", "Seniority Product Manager"):
            with self.subTest(title=title):
                record = judge(posting(title=title), S)
                self.assertEqual((record["C4"], record["C4_reason"], record["verdict"]), ("pass", "", "relevant"))

    def test_c4_is_the_only_change(self):
        p = posting(title="Senior Product Manager", location="NYC")
        v1, s = judge(p), judge(p, S)
        self.assertEqual(v1["verdict"], "relevant")
        self.assertEqual((s["verdict"], s["C4"], s["years_matched"]), ("not_relevant", "fail", []))
        self.assertEqual({k: v for k, v in s.items() if k not in ("verdict", "C4", "C4_reason", "years_matched")},
                         {k: v for k, v in v1.items() if k != "verdict"})

    def test_every_word_found_is_named_and_the_text_is_never_read(self):
        record = judge(posting(title="Senior Staff Product Manager"), S)
        self.assertEqual(record["C4_reason"], 'title has "Senior"; title has "Staff"')
        record = judge(posting(text="Python and SQL with senior leadership and staff."), S)
        self.assertEqual(record["C4"], "pass")

    def test_missing_title(self):
        record = judge(posting(title=ABSENT), S)
        self.assertEqual((record["C1"], record["C4"], record["verdict"]), ("missing", "missing", "cannot_tell"))
        self.assertEqual(judge(posting(title=ABSENT))["verdict"], "cannot_tell")  # the same verdict as v1


class TestYearsPattern(unittest.TestCase):
    """The max_years pattern (agent/filter.py YEARS), with max_years 3. The minimum is the first number."""

    # (phrase in the text, the span the pattern matches)
    MATCHED_AND_FAILS = [
        ("5+ years of product experience", "5+ years"),
        ("5 years of experience", "5 years"),
        ("5-8 years of experience", "5-8 years"),
        ("5–8 years of experience", "5–8 years"),
        ("5 — 8 years of experience", "5 — 8 years"),
        ("5 to 8 years of experience", "5 to 8 years"),
        ("6–10+ years of experience", "6–10+ years"),
        ("5 + years", "5 + years"),
        ("4 YEARS in product", "4 YEARS"),
        ("at least 12 years", "12 years"),
        # Company history: the pattern does not read the sentence, so "10 years" matches and fails C4.
        # A known false positive, kept visible in the measurement rather than patched.
        ("Over the past 10 years we have grown to 500 people", "10 years"),
    ]
    MATCHED_AND_PASSES = [
        ("3+ years of experience", "3+ years"),   # 3 is not above 3
        ("3 years", "3 years"),
        ("2-5 years", "2-5 years"),               # a range is read by its low end (FILTER.md §5)
        ("2 to 4 years", "2 to 4 years"),
        ("1 year of SQL", "1 year"),
    ]
    NOT_MATCHED = [
        "five years of experience",               # a number in words
        "5 or more years",                        # not one of the listed forms
        "5yrs of experience",
        "5 yrs of experience",
        "a 5-year plan",                          # "5-year" is not "5 years"
        "100 years of history",                   # three digits: not a stated minimum
        "2.5 years",                              # a decimal
        "3.5 years",                              # a decimal above 3 the pattern misses: a known gap
        "years of experience: 5",
    ]

    def test_matched_and_fails(self):
        for phrase, span in self.MATCHED_AND_FAILS:
            with self.subTest(phrase=phrase):
                record = judge(posting(text=f"{SKILLS2} {phrase}."), Y)
                self.assertEqual(record["years_matched"], [span])
                self.assertEqual(record["C4"], "fail")
                self.assertEqual(record["C4_reason"], f'text states "{span}", a minimum above 3 years')
                self.assertEqual(record["verdict"], "not_relevant")

    def test_matched_and_passes(self):
        for phrase, span in self.MATCHED_AND_PASSES:
            with self.subTest(phrase=phrase):
                record = judge(posting(text=f"{SKILLS2} {phrase}."), Y)
                self.assertEqual((record["years_matched"], record["C4"], record["verdict"]), ([span], "pass", "relevant"))

    def test_not_matched(self):
        for phrase in self.NOT_MATCHED:
            with self.subTest(phrase=phrase):
                record = judge(posting(text=f"{SKILLS2} {phrase}."), Y)
                self.assertEqual((record["years_matched"], record["C4"], record["verdict"]), ([], "pass", "relevant"))

    def test_the_first_minimum_above_the_limit_is_the_reason(self):
        record = judge(posting(text=f"{SKILLS2} 2+ years in analytics, 7+ years overall, 9 years ideal."), Y)
        self.assertEqual(record["years_matched"], ["2+ years", "7+ years", "9 years"])
        self.assertEqual(record["C4_reason"], 'text states "7+ years", a minimum above 3 years')

    def test_the_limit_is_the_option(self):
        p = posting(text=f"{SKILLS2} 5+ years.")
        self.assertEqual(judge(p, {"max_years": 5})["C4"], "pass")
        self.assertEqual(judge(p, {"max_years": 4})["C4"], "fail")

    def test_missing_text(self):
        record = judge(posting(text=ABSENT), Y)
        self.assertEqual((record["C3"], record["C4"], record["years_matched"], record["verdict"]),
                         ("missing", "missing", [], "cannot_tell"))

    def test_the_title_is_never_read_for_years(self):
        self.assertEqual(judge(posting(title="Product Manager, 10 years program"), Y)["C4"], "pass")


class TestCombined(unittest.TestCase):
    def test_both_reasons(self):
        record = judge(posting(title="Staff Product Manager", text="Java only. 8+ years."), {"skills_needed": 0, **S, **Y})
        self.assertEqual((record["C3"], record["C4"]), ("pass", "fail"))
        self.assertEqual(record["C4_reason"], 'title has "Staff"; text states "8+ years", a minimum above 3 years')
        self.assertEqual(record["verdict"], "not_relevant")

    def test_a_failing_c4_beats_a_missing_field(self):
        record = judge(posting(location=ABSENT, title="Senior Product Manager"), S)
        self.assertEqual((record["C2"], record["C4"], record["verdict"]), ("missing", "fail", "not_relevant"))


class TestOptionValidation(unittest.TestCase):
    def test_bad_options(self):
        for options in ({"skills": 1}, {"skills_needed": -1}, {"skills_needed": "2"}, {"skills_needed": True},
                        {"seniority_words": "Senior"}, {"seniority_words": ["Senior", ""]}, {"max_years": -1},
                        {"max_years": 3.5}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                judge(posting(), options)


if __name__ == "__main__":
    unittest.main()
