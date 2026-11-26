"""FILTER.md §4 'when something is missing', on fake responses. Offline."""
import json
import os
import shutil
import tempfile
import unittest

import js3.collect as C
from js3.fetch import FetchResult

GH_OK = {"jobs": [{"id": 1, "title": "ML Engineer", "content": "&lt;p&gt;Python&lt;/p&gt;",
                   "location": {"name": "SF"}, "departments": [{"name": "AI"}]},
                  {"id": None, "title": "no id"}]}
ASHBY = {"jobs": [{"id": "a", "title": "Data Engineer", "descriptionPlain": "SQL " * 100, "isListed": True},
                  {"id": "b", "title": "Hidden", "isListed": False}]}


class TestCollect(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(dir=os.path.join(C.HERE, "out"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_with(self, responses):
        cfg = {"allowed_hosts": ["boards-api.greenhouse.io", "api.ashbyhq.com"], "request_timeout_seconds": 1,
               "boards": [{"system": "greenhouse", "board": "g1"}, {"system": "greenhouse", "board": "g2"},
                          {"system": "ashby", "board": "a1"}]}
        it = iter(responses)
        return C.collect(cfg, self.tmp, fetch=lambda url, t: next(it))

    def test_failed_and_empty_boards_are_not_seen(self):
        snap, rep = self.run_with([
            FetchResult(200, json.dumps(GH_OK).encode(), None),
            FetchResult(200, b'{"jobs": []}', None),
            FetchResult(404, b"", None),
        ])
        self.assertFalse(rep["complete"])
        self.assertEqual(rep["not_seen"], ["greenhouse:g2", "ashby:a1"])
        self.assertEqual(rep["boards"][1]["status"], "suspicious: 0 jobs")
        self.assertEqual(rep["boards"][0]["dropped"], 1)
        posts = C.load_postings(snap)
        self.assertEqual([p["uid"] for p in posts], ["greenhouse:g1:1"])
        self.assertEqual(posts[0]["text"], "Python")  # double-escaped HTML undone

    def test_unlisted_ashby_jobs_are_skipped(self):
        snap, rep = self.run_with([
            FetchResult(200, json.dumps(GH_OK).encode(), None),
            FetchResult(200, json.dumps(GH_OK).encode(), None),
            FetchResult(200, json.dumps(ASHBY).encode(), None),
        ])
        self.assertTrue(rep["complete"])
        self.assertEqual(rep["boards"][2]["unlisted_skipped"], 1)
        self.assertEqual(rep["boards"][2]["postings"], 1)


if __name__ == "__main__":
    unittest.main()
