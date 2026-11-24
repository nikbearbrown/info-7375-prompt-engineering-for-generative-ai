"""Tests for agent/filter.py (FILTER.md v1: F1-F6 as rule.py runs them, F7, F8, closest calls).

Every posting here is constructed, in the shape agent/adapters.py returns.
No test reads the corpus.
"""

import itertools
import json
import random
import unittest

from support import load_table, persona, table_posting

from agent import adapters, rule
from agent import filter as filter_v1

ABSENT = object()
PASS_TITLE, FAIL_TITLE = "Product Manager, Payments", "Software Engineer"
PASS_LOCATION, FAIL_LOCATION = "New York", "London"
TEXT = {n: text for n, text in enumerate([
    "Constructed: you will write Java services.",
    "Constructed: you will use Python.",
    "Constructed: you will use Python and SQL.",
    "Constructed: you will use Python, SQL and user research.",
    "Constructed: Python, SQL, user research and roadmapping.",
    "Constructed: Python, SQL, A/B testing, roadmapping and user research.",
])}


def posting(title=PASS_TITLE, location=PASS_LOCATION, text=TEXT[2], ats="greenhouse", posting_id="910001"):
    """A constructed posting. ABSENT leaves the field out; location is location.name."""
    built = {"posting_id": posting_id, "ats": ats}
    if title is not ABSENT:
        built["title"] = title
    if location is not ABSENT:
        built["location"] = {"name": location}
    if text is not ABSENT:
        built["content"] = text
    return built


def judge(p, resume=None):
    return filter_v1.judge(p, resume or persona())


def statuses(record):
    return tuple(record[c] for c in ("C1", "C2", "C3"))


# Every way F7 calls a field missing: absent, null (or not text), empty after F1's cleanup.
MISSING_FORMS = {
    "title": [
        ("absent", lambda p: p.pop("title")),
        ("null", lambda p: p.update(title=None)),
        ("empty", lambda p: p.update(title="")),
        ("whitespace only", lambda p: p.update(title="  \n\t ")),
        ("not text", lambda p: p.update(title=42)),
    ],
    "location": [
        ("absent", lambda p: p.pop("location")),
        ("null", lambda p: p.update(location=None)),
        ("no name", lambda p: p.update(location={})),
        ("null name", lambda p: p.update(location={"name": None})),
        ("whitespace-only name", lambda p: p.update(location={"name": "   "})),
        ("not an object", lambda p: p.update(location="New York")),
    ],
    "text": [
        ("absent", lambda p: p.pop("content")),
        ("null", lambda p: p.update(content=None)),
        ("empty", lambda p: p.update(content="")),
        ("whitespace only", lambda p: p.update(content=" \n\t ")),
        ("only tags, escaped as Greenhouse sends them", lambda p: p.update(content="&lt;p&gt; &lt;br/&gt; &lt;/p&gt;")),
        ("Ashby, whitespace only", lambda p: p.update(ats="ashby", content="  \n  ")),
    ],
}


class TestF7MissingFields(unittest.TestCase):
    def test_each_field_missing_alone_is_cannot_tell(self):
        for field, forms in MISSING_FORMS.items():
            for how, mutate in forms:
                with self.subTest(field=field, how=how):
                    p = posting()
                    mutate(p)
                    record = judge(p)
                    self.assertEqual(record["verdict"], "cannot_tell")
                    self.assertEqual(record["missing"], [field])
                    expected = {"title": ("missing", "pass", "pass"), "location": ("pass", "missing", "pass"),
                                "text": ("pass", "pass", "missing")}[field]
                    self.assertEqual(statuses(record), expected)
                    self.assertEqual(record["score"], None if field == "text" else 2)
                    self.assertFalse(record["closest_call"])

    def test_missing_with_a_failing_present_field_is_not_relevant(self):
        cases = [
            # (title, location, text, statuses, missing, score)
            (ABSENT, FAIL_LOCATION, TEXT[2], ("missing", "fail", "pass"), ["title"], 2),
            (FAIL_TITLE, ABSENT, TEXT[3], ("fail", "missing", "pass"), ["location"], 3),
            (PASS_TITLE, ABSENT, TEXT[1], ("pass", "missing", "fail"), ["location"], 1),
            (FAIL_TITLE, PASS_LOCATION, ABSENT, ("fail", "pass", "missing"), ["text"], None),
            (PASS_TITLE, FAIL_LOCATION, None, ("pass", "fail", "missing"), ["text"], None),
            (None, "  ", TEXT[0], ("missing", "missing", "fail"), ["title", "location"], 0),
        ]
        for title, location, text, expected, missing, score in cases:
            with self.subTest(statuses=expected):
                record = judge(posting(title, location, text))
                self.assertEqual(record["verdict"], "not_relevant")
                self.assertEqual(statuses(record), expected)
                self.assertEqual(record["missing"], missing)  # still named, though the verdict is settled
                self.assertEqual(record["score"], score)
                self.assertFalse(record["closest_call"])

    def test_several_missing_with_the_rest_passing_is_cannot_tell(self):
        cases = [
            (PASS_TITLE, ABSENT, ABSENT, ["location", "text"]),
            (ABSENT, PASS_LOCATION, "   ", ["title", "text"]),
            (ABSENT, ABSENT, ABSENT, ["title", "location", "text"]),
        ]
        for title, location, text, missing in cases:
            with self.subTest(missing=missing):
                record = judge(posting(title, location, text))
                self.assertEqual(record["verdict"], "cannot_tell")
                self.assertEqual(record["missing"], missing)

    def test_ashby_postings_through_the_real_adapter(self):
        body = json.dumps({"jobs": [
            {"id": "c-ab-1", "title": "Product Manager", "location": "  ", "secondaryLocations": [{"location": ""}],
             "descriptionPlain": "Constructed: Python and SQL."},
            {"id": "c-ab-2", "title": "Product Manager", "location": "Remote", "descriptionPlain": " \n "},
            {"id": "c-ab-3", "title": "Product Manager", "location": "Dublin",
             "secondaryLocations": [{"location": "New York"}], "descriptionPlain": "Constructed: Python and SQL."},
        ]}).encode()
        no_location, blank_text, secondary = (judge(p) for p in adapters.ashby(body))
        self.assertEqual((no_location["verdict"], no_location["missing"]), ("cannot_tell", ["location"]))
        self.assertEqual((blank_text["verdict"], blank_text["missing"]), ("cannot_tell", ["text"]))
        self.assertEqual((secondary["verdict"], secondary["location"], secondary["location_match"]),
                         ("relevant", "Dublin; New York", ["New York"]))

    def test_score_is_blank_only_when_the_text_is_missing(self):
        self.assertEqual(judge(posting(text=TEXT[0]))["score"], 0)
        self.assertEqual(judge(posting(text=TEXT[0]))["C3"], "fail")
        self.assertIsNone(judge(posting(text=ABSENT))["score"])


class TestScore(unittest.TestCase):
    def test_distinct_skills_zero_to_five(self):
        for n, text in TEXT.items():
            with self.subTest(n=n):
                self.assertEqual(judge(posting(text=text))["score"], n)

    def test_each_skill_counts_once_and_matching_is_rule_py_s(self):
        cases = {
            "Python python PYTHON.": (1, ["Python"]),
            "Data in NoSQL, analysis in Python.": (2, ["Python", "SQL"]),  # pinned: SQL inside NoSQL
            "Own the roadmap with Python.": (1, ["Python"]),  # pinned: roadmap is not roadmapping
            "&lt;p&gt;user research&lt;/p&gt;&lt;p&gt;a/b TESTING&lt;/p&gt;": (2, ["A/B testing", "user research"]),
        }
        for text, (score, found) in cases.items():
            with self.subTest(text=text):
                record = judge(posting(text=text))
                self.assertEqual((record["score"], record["skills_found"]), (score, found))  # persona order


class TestRecord(unittest.TestCase):
    def test_record_fields(self):
        record = judge(posting(title="  Associate   Product Manager \n", location=" New\tYork, NY ",
                               text="Constructed BODY-MARKER: Python and SQL.", posting_id="910042"))
        self.assertEqual(set(record), {"posting_id", "title", "location", "verdict", "C1", "C2", "C3", "score",
                                       "title_match", "location_match", "skills_found", "missing", "closest_call"})
        self.assertEqual(record["posting_id"], "910042")
        self.assertEqual(record["title"], "Associate Product Manager")  # F1
        self.assertEqual(record["location"], "New York, NY")
        self.assertEqual(record["title_match"], ["Associate Product Manager", "Product Manager"])
        self.assertEqual(record["location_match"], ["New York"])
        self.assertNotIn("BODY-MARKER", repr(record))  # the record never holds the text

    def test_location_match_through_rule_py_s_exact_remote_clause(self):
        resume = dict(persona(), locations=["New York", "Remote - US"])
        record = judge(posting(location="REMOTE"), resume)  # "Remote - US" is not inside "REMOTE"
        self.assertEqual((record["C2"], record["location_match"]), ("pass", ["Remote - US"]))
        self.assertEqual(rule.judge(posting(location="REMOTE"), resume)[0], record["verdict"])

    def test_no_match_lists_for_failing_or_missing_fields(self):
        record = judge(posting(title=FAIL_TITLE, location=ABSENT, text=ABSENT))
        self.assertEqual((record["title_match"], record["location_match"], record["skills_found"]), ([], [], []))


class TestClosestCalls(unittest.TestCase):
    def test_closest_calls(self):
        cases = [
            # (title, location, text, closest call?)
            (PASS_TITLE, PASS_LOCATION, TEXT[1], True),    # both gates pass, one skill short
            (PASS_TITLE, PASS_LOCATION, TEXT[2], True),    # both gates pass, exactly on the threshold
            (PASS_TITLE, PASS_LOCATION, TEXT[3], False),
            (PASS_TITLE, PASS_LOCATION, TEXT[0], False),
            (FAIL_TITLE, PASS_LOCATION, TEXT[2], True),    # score 2+, exactly one gate fails
            (PASS_TITLE, FAIL_LOCATION, TEXT[5], True),
            (FAIL_TITLE, FAIL_LOCATION, TEXT[3], False),   # both gates fail
            (FAIL_TITLE, PASS_LOCATION, TEXT[1], False),   # one gate fails, score under 2
            # never with a missing condition
            (PASS_TITLE, PASS_LOCATION, ABSENT, False),
            (ABSENT, PASS_LOCATION, TEXT[2], False),
            (FAIL_TITLE, ABSENT, TEXT[3], False),          # exactly one gate fails, but the other is missing
            (ABSENT, FAIL_LOCATION, TEXT[2], False),
            (PASS_TITLE, ABSENT, TEXT[1], False),
        ]
        for title, location, text, expected in cases:
            record = judge(posting(title, location, text))
            with self.subTest(statuses=statuses(record), score=record["score"]):
                self.assertEqual(record["closest_call"], expected)

    def test_is_closest_call_directly(self):
        p, f, m = "pass", "fail", "missing"
        self.assertTrue(filter_v1.is_closest_call({"C1": p, "C2": p, "C3": f}, 1))
        self.assertTrue(filter_v1.is_closest_call({"C1": p, "C2": f, "C3": p}, 4))
        self.assertFalse(filter_v1.is_closest_call({"C1": m, "C2": f, "C3": p}, 4))
        self.assertFalse(filter_v1.is_closest_call({"C1": p, "C2": p, "C3": m}, None))


def ranked_record(board, posting_id, score, **extra):
    """A relevant (or not) record as filter_run builds it: judge's record plus its board key."""
    return {"board_key": board, **judge(posting(text=TEXT[score], posting_id=posting_id, **extra))}


def order(records):
    return [(r["board_key"], r["posting_id"]) for r in filter_v1.rank(records)]


class TestF8Ranking(unittest.TestCase):
    BOARDS = ["greenhouse:stripe", "greenhouse:robinhood", "greenhouse:duolingo", "ashby:notion"]

    def test_score_high_to_low(self):
        records = [ranked_record("ashby:notion", f"c-{n}", n) for n in (2, 5, 3, 4)]
        self.assertEqual(order(records), [("ashby:notion", f"c-{n}") for n in (5, 4, 3, 2)])

    def test_score_ties_by_board_key_alphabetical(self):
        records = [ranked_record(board, "910001", 3) for board in self.BOARDS]
        self.assertEqual([board for board, _ in order(records)],
                         ["ashby:notion", "greenhouse:duolingo", "greenhouse:robinhood", "greenhouse:stripe"])

    def test_then_by_id_compared_as_strings(self):
        records = [ranked_record("greenhouse:stripe", posting_id, 2) for posting_id in ("9", "90001", "10", "900001")]
        # As numbers this would be 9, 10, 90001, 900001.
        self.assertEqual([i for _, i in order(records)], ["10", "9", "900001", "90001"])

    def test_all_three_keys_together_in_any_input_order(self):
        records = [ranked_record("greenhouse:stripe", "2", 3), ranked_record("ashby:notion", "z", 2),
                   ranked_record("greenhouse:stripe", "10", 3), ranked_record("ashby:notion", "a", 4),
                   ranked_record("greenhouse:duolingo", "5", 3)]
        expected = [("ashby:notion", "a"), ("greenhouse:duolingo", "5"), ("greenhouse:stripe", "10"),
                    ("greenhouse:stripe", "2"), ("ashby:notion", "z")]
        for seed in range(5):
            shuffled = list(records)
            random.Random(seed).shuffle(shuffled)
            with self.subTest(seed=seed):
                self.assertEqual(order(shuffled), expected)

    def test_relevant_records_only(self):
        records = [ranked_record("ashby:notion", "rel", 3),
                   ranked_record("ashby:notion", "short", 1),
                   {"board_key": "ashby:notion", **judge(posting(location=ABSENT, posting_id="ct"))},
                   {"board_key": "ashby:notion", **judge(posting(title=FAIL_TITLE, text=TEXT[5], posting_id="no"))}]
        self.assertEqual(order(records), [("ashby:notion", "rel")])

    def test_dates_are_never_read(self):
        older = ranked_record("greenhouse:stripe", "2", 3, )
        newer = ranked_record("greenhouse:stripe", "1", 3)
        self.assertNotIn("updated_at", judge(dict(posting(), updated_at="2026-11-07T10:00:00-05:00")))
        older["updated_at"], newer["updated_at"] = "2026-01-01T00:00:00Z", "2026-12-31T00:00:00Z"
        self.assertEqual(order([older, newer]), order([newer, older]))
        self.assertEqual(order([older, newer]), [("greenhouse:stripe", "1"), ("greenhouse:stripe", "2")])


class TestRulePyCrossCheck(unittest.TestCase):
    """On a posting with no missing field, filter.judge's verdict is rule.py's."""

    ROWS = load_table("rule_cases.json")["cases"]

    def test_every_rule_case_with_no_missing_field_gives_rule_py_s_verdict(self):
        resume = persona()
        compared = 0
        for row in self.ROWS:
            p = table_posting(row)
            record = filter_v1.judge(p, resume)
            if record["missing"]:
                continue
            compared += 1
            with self.subTest(case=row["id"]):
                self.assertEqual(record["verdict"], rule.judge(p, resume)[0])
                self.assertEqual(record["verdict"], row["expect_verdict"])
                self.assertEqual(statuses(record), tuple("pass" if row[f"expect_{c}"] else "fail"
                                                         for c in ("C1", "C2", "C3")))
        self.assertEqual(compared, 13)

    def test_how_the_missing_field_cases_differ(self):
        resume = persona()
        differ = {}
        for row in self.ROWS:
            p = table_posting(row)
            record = filter_v1.judge(p, resume)
            if record["missing"]:
                differ[row["id"]] = (rule.judge(p, resume)[0], record["verdict"], record["missing"], statuses(record))
        # R11 has no content field: rule.py (missing means false) rejects it; F7 cannot tell.
        self.assertEqual(differ, {"R11": ("not_relevant", "cannot_tell", ["text"], ("pass", "pass", "missing"))})

    def test_constructed_sweep_agrees_with_rule_py_whenever_nothing_is_missing(self):
        resume = persona()
        titles = [PASS_TITLE, FAIL_TITLE, "Senior Product Manager", "APM", ABSENT, None, "   "]
        locations = [PASS_LOCATION, FAIL_LOCATION, "remote", "SF, SEA, NYC", "New-York", ABSENT, " "]
        texts = list(TEXT.values()) + ["&lt;p&gt;Python&lt;/p&gt;&lt;p&gt;SQL&lt;/p&gt;", ABSENT, None, "&lt;p&gt;&lt;/p&gt;"]
        compared = 0
        for title, location, text in itertools.product(titles, locations, texts):
            p = posting(title, location, text)
            record = filter_v1.judge(p, resume)
            with self.subTest(statuses=statuses(record), score=record["score"]):
                if not record["missing"]:
                    compared += 1
                    self.assertEqual(record["verdict"], rule.judge(p, resume)[0])
                elif "fail" in statuses(record):
                    self.assertEqual(record["verdict"], "not_relevant")
                else:
                    self.assertEqual(record["verdict"], "cannot_tell")
        self.assertEqual(compared, 4 * 5 * 7)  # present titles x present locations x present texts


if __name__ == "__main__":
    unittest.main()
