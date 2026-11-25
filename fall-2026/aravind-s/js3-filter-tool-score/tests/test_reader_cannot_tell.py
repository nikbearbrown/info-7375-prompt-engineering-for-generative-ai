"""FILTER.md v1.0, Section 3 and wrong version W4 (2026-11-20): one posting with no title no longer makes its whole
board unverified. It is kept as "I cannot tell", never sent to Claude, and the rest of the board is read. Changed
from JS2, where the reader refused the board (OpenAI on 2026-11-20: 853 postings went unread because of one).
Every answer here is a CONSTRUCTED fixture.
"""

import importlib.util
import json
import unittest

from job_agent import providers
from job_agent.errors import Unverified

from .loop_helpers import FakeNet, REPO, Workspace, answer, ashby_job, url


class ReaderTest(unittest.TestCase):
    """FILTER.md Section 3 and W4: one posting with no title no longer hides the rest of its board."""

    def test_one_empty_title_keeps_the_rest_of_the_board(self):
        body = json.dumps({"jobs": [ashby_job("a-1"), ashby_job("a-2", title=""), ashby_job("a-3")]}).encode()
        postings = providers.read("ashby", 200, body)
        self.assertEqual([p["id"] for p in postings], ["a-1", "a-2", "a-3"])
        self.assertEqual(postings[1]["_cannot_tell"], "the posting has no title")
        self.assertNotIn("_cannot_tell", postings[0])

    def test_an_answer_with_no_titled_posting_or_no_id_is_still_unverified(self):
        with self.assertRaises(Unverified):
            providers.read("ashby", 200, json.dumps({"jobs": [ashby_job("a-1", title="")]}).encode())
        with self.assertRaises(Unverified):
            providers.read("ashby", 200, json.dumps({"jobs": [ashby_job("", title="x")]}).encode())

    def test_posting_dates_are_mapped(self):
        gh = {"jobs": [{"id": 7, "title": "Backend Engineer", "first_published": "2026-11-18T13:21:31-05:00",
                        "updated_at": "2026-11-19T10:00:00-05:00", "location": {"name": "San Mateo, CA"},
                        "metadata": [], "content": "x"}]}
        self.assertEqual(providers.read("greenhouse", 200, json.dumps(gh).encode())[0]["publishedAt"],
                         "2026-11-18T13:21:31-05:00")
        lv = [{"id": "l-1", "text": "Software Engineer", "createdAt": 1786469891368, "categories": {}}]
        self.assertEqual(providers.read("lever", 200, json.dumps(lv).encode())[0]["publishedAt"],
                         "2026-08-11T17:38:11+00:00")

    def test_the_independent_checker_agrees(self):
        spec = importlib.util.spec_from_file_location("check_run", REPO / "tools" / "check_run.py")
        check_run = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(check_run)
        body = json.dumps({"jobs": [ashby_job("a-1"), ashby_job("a-2", title="")]}).encode()
        self.assertEqual(check_run.readable("ashby", 200, body), (True, ["a-1", "a-2"]))
        none_titled = json.dumps({"jobs": [ashby_job("a-1", title="")]}).encode()
        self.assertFalse(check_run.readable("ashby", 200, none_titled)[0])


class LoopCannotTellTest(unittest.TestCase):
    def test_a_new_posting_with_no_title_is_read_and_never_sent_to_claude(self):
        ws = Workspace()
        self.addCleanup(ws.cleanup)
        openai = ("ashby", "openai")
        ws.boards(openai)
        ws.run(FakeNet({url(*openai): [answer(*openai, [ashby_job("a-1"), ashby_job("a-2")])]}))
        jobs = [ashby_job("a-1"), ashby_job("a-2"), ashby_job("a-3", title="")]
        summary = ws.run(FakeNet({url(*openai): [answer(*openai, jobs)]}))
        board = next(b for b in summary["boards"] if b["key"] == "ashby-openai")
        self.assertEqual(board["status"], "read")
        new = {p["id"]: p for p in board["new"]}
        self.assertTrue(new["a-3"]["rule_verdict"].startswith("I cannot tell"))
        self.assertNotIn("a-3", ws.judges.claude_calls)
        self.assertIn("a-3", ws.state("ashby", "openai")["seen_ids"])


if __name__ == "__main__":
    unittest.main()
