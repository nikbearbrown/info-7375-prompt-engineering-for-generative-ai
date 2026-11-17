"""FILTER.md §4: the W6, W7 and W8 checks, in both directions (as tests/test_wrong_versions.py does for W1, W2).

Each check is a function that returns a list of failures. On agent/filter.py
it must return none; on its wrong version in tests/wrong_versions/ it must
return exactly the failure §4 predicts. A wrong version that raises makes
the test error, never pass.

Inputs: §4's constructed postings, with §4's words where §4 gives words. W7's
postings are given only board keys, ids, dates and a score of 3 in §4; their
titles, locations and text are filled in here, constructed, so both are
relevant with exactly three skills.
"""

import unittest

from support import load_table, persona, table_posting

from agent import filter as filter_v1
from wrong_versions import w6_role_words_anywhere as w6
from wrong_versions import w7_newest_first as w7
from wrong_versions import w8_missing_means_no as w8

# W6, word for word: title, location, body text (score 2).
W6_POSTING = {
    "posting_id": "c-w6", "ats": "greenhouse",
    "title": "Engineering Manager, Platform",
    "location": {"name": "New York"},
    "content": "You will partner closely with a Product Manager and the design team. You bring Python and SQL.",
}
# W7: A is greenhouse:stripe "900001", the later date; B is ashby:notion "c-1002", the earlier date; both score 3.
W7_TEXT = "Constructed: you bring Python, SQL and user research."
W7_A = ("greenhouse:stripe", {"posting_id": "900001", "ats": "greenhouse", "title": "Product Manager",
                              "location": {"name": "New York"}, "content": W7_TEXT,
                              "updated_at": "2026-11-07T10:00:00-05:00"})
W7_B = ("ashby:notion", {"posting_id": "c-1002", "ats": "ashby", "title": "Product Manager",
                         "location": {"name": "Remote"}, "content": W7_TEXT,
                         "publishedAt": "2026-10-20T09:00:00.000+00:00"})
# W8: title "Product Manager", no location field at all, body text naming Python and SQL (score 2).
W8_POSTING = {"posting_id": "c-w8", "ats": "greenhouse", "title": "Product Manager",
              "content": "Constructed: you bring Python and SQL."}


def check_w6(judge_fn):
    """Right: not_relevant, C1 fails, because the title names a different role."""
    record = judge_fn(W6_POSTING, persona())
    got = (record["verdict"], record["C1"])
    return [] if got == ("not_relevant", "fail") else [f"W6 posting: verdict, C1 = {got}; expected not_relevant, fail"]


def check_w7(judge_fn, rank_fn):
    """Right: B first, in either input order; the dates are never consulted."""
    expected = [("ashby:notion", "c-1002"), ("greenhouse:stripe", "900001")]
    failures = []
    for label, pair in (("A then B", (W7_A, W7_B)), ("B then A", (W7_B, W7_A))):
        records = [{"board_key": board, **judge_fn(p, persona())} for board, p in pair]
        got = [(r["board_key"], r["posting_id"]) for r in rank_fn(records)]
        if got != expected:
            failures.append(f"W7 [{label}]: ranked {got}; expected B first")
    return failures


def check_w8(judge_fn):
    """Right: cannot_tell, with location named as the missing field; never a reject."""
    record = judge_fn(W8_POSTING, persona())
    got = (record["verdict"], record["missing"])
    return [] if got == ("cannot_tell", ["location"]) else [f"W8 posting: verdict, missing = {got}; "
                                                            f"expected cannot_tell, ['location']"]


class Premises(unittest.TestCase):
    """The constructed postings are what §4 says they are."""

    def test_w6_posting(self):
        record = filter_v1.judge(W6_POSTING, persona())
        self.assertEqual((record["C2"], record["score"]), ("pass", 2))

    def test_w7_postings(self):
        for board, p in (W7_A, W7_B):
            record = filter_v1.judge(p, persona())
            with self.subTest(board=board):
                self.assertEqual((record["verdict"], record["score"]), ("relevant", 3))
        self.assertGreater(W7_A[1]["updated_at"], W7_B[1]["publishedAt"])  # A is the later date

    def test_w8_posting(self):
        self.assertNotIn("location", W8_POSTING)
        record = filter_v1.judge(W8_POSTING, persona())
        self.assertEqual((record["C1"], record["score"]), ("pass", 2))


class W6RoleWordsAnywhere(unittest.TestCase):
    def test_check_passes_on_the_filter(self):
        self.assertEqual(check_w6(filter_v1.judge), [])

    def test_check_fails_on_w6(self):
        self.assertEqual(check_w6(w6.judge), ["W6 posting: verdict, C1 = ('relevant', 'pass'); "
                                              "expected not_relevant, fail"])

    def test_w6_is_wrong_only_where_section_4_says(self):
        # No rule case names a target title in its text, so W6 agrees with the filter on every one.
        resume = persona()
        for row in load_table("rule_cases.json")["cases"]:
            with self.subTest(case=row["id"]):
                self.assertEqual(w6.judge(table_posting(row), resume), filter_v1.judge(table_posting(row), resume))


class W7NewestFirst(unittest.TestCase):
    def test_check_passes_on_the_filter(self):
        self.assertEqual(check_w7(filter_v1.judge, filter_v1.rank), [])

    def test_check_fails_on_w7(self):
        wrong = "[('greenhouse:stripe', '900001'), ('ashby:notion', 'c-1002')]; expected B first"
        self.assertEqual(check_w7(w7.judge, w7.rank), [f"W7 [A then B]: ranked {wrong}", f"W7 [B then A]: ranked {wrong}"])

    def test_w7_is_wrong_only_on_score_ties(self):
        # B (the earlier date) now scores 5, A still 3: no tie, so both put B first, by score.
        five = "Constructed: Python, SQL, A/B testing, roadmapping and user research."
        pairs = (W7_A, (W7_B[0], dict(W7_B[1], content=five)))
        records = [{"board_key": board, **w7.judge(p, persona())} for board, p in pairs]
        ids = lambda ranked: [r["posting_id"] for r in ranked]  # noqa: E731
        self.assertEqual(ids(w7.rank(records)), ["c-1002", "900001"])
        self.assertEqual(ids(w7.rank(records)), ids(filter_v1.rank(records)))


class W8MissingMeansNo(unittest.TestCase):
    def test_check_passes_on_the_filter(self):
        self.assertEqual(check_w8(filter_v1.judge), [])

    def test_check_fails_on_w8(self):
        self.assertEqual(check_w8(w8.judge), ["W8 posting: verdict, missing = ('not_relevant', []); "
                                              "expected cannot_tell, ['location']"])

    def test_w8_is_wrong_only_where_a_field_is_missing(self):
        resume = persona()
        for row in load_table("rule_cases.json")["cases"]:
            right, wrong = filter_v1.judge(table_posting(row), resume), w8.judge(table_posting(row), resume)
            with self.subTest(case=row["id"]):
                if right["missing"]:  # R11, no content
                    self.assertEqual((right["verdict"], wrong["verdict"]), ("cannot_tell", "not_relevant"))
                else:
                    self.assertEqual(wrong, right)


if __name__ == "__main__":
    unittest.main()
