"""Reading each applicant-tracking system's response, and shaping postings for the JS1 rule."""

import json
import unittest

from agent.boards import BadShape, board_url, normalize, parse_postings
from agent.rule import judge
from tests.helpers import ashby_body, ashby_job, gh_body, gh_job, lever_body, lever_job, load_persona


class Urls(unittest.TestCase):
    def test_urls_match_gate_md(self):
        self.assertEqual(board_url("greenhouse", "anthropic"),
                         "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true")
        self.assertEqual(board_url("lever", "palantir"), "https://api.lever.co/v0/postings/palantir?mode=json")
        self.assertEqual(board_url("ashby", "linear"), "https://api.ashbyhq.com/posting-api/job-board/linear")

    def test_unknown_system(self):
        with self.assertRaises(ValueError):
            board_url("workday", "x")


class Shapes(unittest.TestCase):
    def test_each_system_shape(self):
        self.assertEqual(len(parse_postings("greenhouse", gh_body(gh_job(1), gh_job(2)))), 2)
        self.assertEqual(len(parse_postings("lever", lever_body(lever_job("a")))), 1)
        self.assertEqual(len(parse_postings("ashby", ashby_body(ashby_job("x")))), 1)

    def test_wrong_shapes_are_refused_not_guessed(self):
        for system, body in [("greenhouse", b"<html></html>"), ("greenhouse", b'{"status": 404}'),
                             ("lever", b'{"ok": false}'), ("ashby", lever_body(lever_job("a"))),
                             ("greenhouse", b'{"jobs": "none"}'), ("lever", b"[1, 2]"),
                             ("greenhouse", json.dumps({"jobs": [{"title": "no id"}]}).encode())]:
            with self.assertRaises(BadShape, msg="%s %r" % (system, body)):
                parse_postings(system, body)

    def test_empty_lists_parse_as_empty(self):
        """The loop, not the parser, decides that an empty board is suspect."""
        self.assertEqual(parse_postings("greenhouse", gh_body()), [])
        self.assertEqual(parse_postings("lever", lever_body()), [])
        self.assertEqual(parse_postings("ashby", ashby_body()), [])


class Normalize(unittest.TestCase):
    def test_ids_are_strings_for_every_system(self):
        self.assertEqual(normalize("greenhouse", gh_job(5), "Anthropic")["id"], "5")
        self.assertEqual(normalize("lever", lever_job("a-1"), "Palantir")["id"], "a-1")

    def test_lever_requirement_lists_reach_the_rule(self):
        """Lever puts requirements in `lists`, not in the description. The rule must see them."""
        job = lever_job("a", lists=[("Requirements", "<li>5+ years with Python and AWS</li>")])
        posting = normalize("lever", job, "Palantir")
        verdict = judge(posting, load_persona())
        r4 = next(c for c in verdict["checks"] if c["rule"] == "R4")
        self.assertFalse(r4["passed"])
        self.assertEqual(posting["title"], "Software Engineer")
        self.assertEqual(posting["location"]["name"], "Palo Alto, CA")

    def test_ashby_secondary_locations_are_kept(self):
        job = ashby_job("x", location="London", secondary=["New York, NY"])
        posting = normalize("ashby", job, "Linear")
        r3 = next(c for c in judge(posting, load_persona())["checks"] if c["rule"] == "R3")
        self.assertTrue(r3["passed"])

    def test_greenhouse_posting_is_unchanged_from_js1(self):
        job = gh_job(7, body="Python and AWS, 2+ years")
        posting = normalize("greenhouse", job, "Anthropic")
        self.assertEqual(posting["content"], job["content"])
        self.assertEqual(judge(posting, load_persona())["verdict"], "MATCH")


if __name__ == "__main__":
    unittest.main()
