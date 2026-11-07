"""CONTRACT.md In: every board answer the contract calls broken stops the run."""

import json
import unittest

from job_agent import board
from job_agent.errors import BrokenInput

from .helpers import board_bytes, job


class BoardTest(unittest.TestCase):
    def test_a_good_answer_gives_its_jobs(self):
        jobs = board.parse(200, board_bytes([job("a-1"), job("a-2")]))
        self.assertEqual([j["id"] for j in jobs], ["a-1", "a-2"])

    def test_broken_answers(self):
        cases = {
            "HTTP 503": (503, board_bytes([job("a-1")])),
            "not JSON": (200, b"<html>maintenance</html>"),
            "not UTF-8": (200, b"\xff\xfe\x00"),
            "a JSON list, not an object": (200, b"[]"),
            "no jobs list": (200, json.dumps({"apiVersion": "1"}).encode()),
            "jobs is not a list": (200, json.dumps({"jobs": {"a": 1}}).encode()),
            "empty jobs list": (200, board_bytes([])),
            "a job that is not an object": (200, json.dumps({"jobs": ["a-1"]}).encode()),
            "a job without an id": (200, board_bytes([{"title": "Software Engineer"}])),
            "a job with a blank id": (200, board_bytes([job("  ")])),
            "a job whose id is a number": (200, board_bytes([dict(job("x"), id=7)])),
            "a job without a title": (200, board_bytes([{"id": "a-1"}])),
        }
        for name, (status, body) in cases.items():
            with self.subTest(name), self.assertRaises(BrokenInput):
                board.parse(status, body)


if __name__ == "__main__":
    unittest.main()
