"""A closed posting must not read as reaching Alex (found by the re-grade of 2026-11-25: the v1.1 report
printed "closed ...: not shortlisted" above "Agent's answer: reaches Alex"). Written before the fix
in js3/shortlist.py."""
import unittest

from js3 import shortlist

CFG = {"version": "vtest"}


def item(is_open):
    return {"key": "board:1", "title": "Software Engineer", "url": "https://example.com/1",
            "open_in_latest_run": is_open, "last_seen": "20261110T000000Z", "answer": "reaches Alex",
            "abstain_because": [], "made_up_quotes": [], "claims": []}


def answer_line(is_open):
    md = shortlist.markdown(CFG, [item(is_open)])
    return next(line for line in md.splitlines() if line.startswith("**Agent's answer"))


class ClosedPostingAnswer(unittest.TestCase):
    def test_a_closed_posting_says_on_its_answer_line_that_it_is_not_shortlisted(self):
        self.assertIn("not shortlisted", answer_line(False))

    def test_an_open_posting_answer_line_is_unchanged(self):
        self.assertEqual(answer_line(True), "**Agent's answer: reaches Alex**")


if __name__ == "__main__":
    unittest.main()
