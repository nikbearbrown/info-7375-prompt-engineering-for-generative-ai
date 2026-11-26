"""Expected sources (FILTER.md section 3): empty and failed sources are 'I cannot tell', never '0 matches'. Catches WV7."""
import gzip
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

from js3 import collect, run_filter
from js3.js2 import policy, transport

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def summary(statuses):
    return {"sources": [dict(source=s, company=s.split(":")[1], status=st, postings=n, reason=r) for s, st, n, r in statuses]}


class Coverage(unittest.TestCase):
    def test_empty_source_is_cannot_tell_and_incomplete(self):
        line = run_filter.coverage_line(summary([("greenhouse:a", "ok", 5, ""), ("greenhouse:webflow", "empty", 0, "HTTP 200 with 0 postings")]))
        self.assertIn("covered 1 of 2 sources", line)
        self.assertIn("INCOMPLETE", line)
        self.assertIn("I cannot tell whether webflow", line)

    def test_all_ok_is_complete(self):
        line = run_filter.coverage_line(summary([("greenhouse:a", "ok", 5, "")]))
        self.assertNotIn("INCOMPLETE", line)


class CollectWithFakeTransport(unittest.TestCase):
    """collect() on a temp copy of the folder, with a fake GET: no network."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        for d in ("config", "persona"):
            shutil.copytree(os.path.join(BASE, d), os.path.join(self.tmp, d))
        with open(os.path.join(self.tmp, "config", "test-sources.json"), "w") as f:
            json.dump({"sources": [{"ats": "greenhouse", "slug": "full", "company": "Full"},
                                   {"ats": "greenhouse", "slug": "empty", "company": "Empty"},
                                   {"ats": "greenhouse", "slug": "gone", "company": "Gone"}]}, f)
        self.patch = mock.patch.object(collect, "BASE", self.tmp)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        shutil.rmtree(self.tmp)

    @staticmethod
    def fake_get(url, timeout, max_bytes):
        if "/full/" in url:
            body = json.dumps({"jobs": [{"id": 1, "title": "Software Engineer", "location": {"name": "Boston, MA"},
                                         "content": "x", "absolute_url": "u"}]}).encode()
            return transport.Response(200, body)
        if "/empty/" in url:
            return transport.Response(200, b'{"jobs": []}')
        return transport.Response(404, b"not found")

    def test_statuses_and_files(self):
        s = collect.collect("config/test-sources.json", "config/budgets.json", label="t", get=self.fake_get)
        st = {x["source"]: x["status"] for x in s["sources"]}
        self.assertEqual(st, {"greenhouse:full": "ok", "greenhouse:empty": "empty", "greenhouse:gone": "error"})
        self.assertFalse(s["complete"])
        with gzip.open(os.path.join(self.tmp, "data", "corpus", s["run"] + ".jsonl.gz"), "rt") as f:
            rows = [json.loads(l) for l in f]
        self.assertEqual([r["source"] for r in rows], ["greenhouse:full"])

    def test_policy_still_refuses_other_hosts(self):
        d = policy.check_request("GET", "https://www.linkedin.com/jobs")
        self.assertEqual(d["decision"], policy.DENY)
        self.assertEqual(policy.check_request("POST", "https://boards-api.greenhouse.io/v1/boards/x/jobs")["decision"], policy.DENY)

    def test_rerun_with_same_name_refused(self):
        import datetime as dt
        now = dt.datetime(2026, 11, 17, 0, 0, 0, tzinfo=dt.timezone.utc)
        collect.collect("config/test-sources.json", "config/budgets.json", label="t", get=self.fake_get, now=now)
        with self.assertRaises(SystemExit):
            collect.collect("config/test-sources.json", "config/budgets.json", label="t", get=self.fake_get, now=now)


if __name__ == "__main__":
    unittest.main()
