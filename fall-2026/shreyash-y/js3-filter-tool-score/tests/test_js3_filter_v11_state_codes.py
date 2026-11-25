"""A gap in Claude Code's first v1.1 code for Shreyash's decision A4, found by measuring it (2026-11-25):
FILTER.md said 36 location results would go from "cannot tell" to "fail", but only 12 did. The other 24
REAL Oscar ads write the state as a two-letter code ("reside in: Dallas, TX."), and the residence reading
knew only full state names. Written by Claude Code before the fix."""
import json
import pathlib
import unittest

from js3 import corpus, filtering
from tests.test_js3_filter import GOOD_LINES, P, PERSONA, outcome

HERE = pathlib.Path(__file__).resolve().parent.parent
V11 = filtering.load_config(HERE / "filter-v1.1.json")
POSTS = {p["key"]: p for p in corpus.load()}


class StateCodes(unittest.TestCase):
    def test_a_two_letter_state_code_is_a_state(self):
        p = P(location="Dallas, Texas, United States", offices=["Dallas"], lines=GOOD_LINES + (
            "Work Location: This is a remote position, open to candidates who reside in: Dallas, TX.",))
        self.assertEqual(outcome(filtering.evaluate(p, PERSONA, V11), 3), "fail")

    def test_ma_means_massachusetts(self):
        p = P(location="Remote", offices=["Remote"], lines=GOOD_LINES + (
            "This is a remote position, open to candidates who reside in: Boston, MA.",))
        self.assertEqual(outcome(filtering.evaluate(p, PERSONA, V11), 3), "pass")

    def test_the_real_oscar_ads_with_codes(self):
        for key in ("oscar:8013107", "oscar:8013108", "oscar:7573019"):
            self.assertEqual(outcome(filtering.evaluate(POSTS[key], PERSONA, V11), 3), "fail", key)

    def test_words_that_look_like_codes_are_not_states(self):
        p = P(location="Remote", offices=["Remote"], lines=GOOD_LINES + (
            "This role is remote anywhere in the United States.", "Teams that live in OK shape ship faster."))
        self.assertEqual(outcome(filtering.evaluate(p, PERSONA, V11), 3), "pass")


if __name__ == "__main__":
    unittest.main()
