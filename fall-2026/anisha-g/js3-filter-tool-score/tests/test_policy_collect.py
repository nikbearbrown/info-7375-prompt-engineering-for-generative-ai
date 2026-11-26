"""Policy inherited from my JS2 GATE section 5, adapted for JS3; collector rules from FILTER.md section 3. Written before the code."""
import json, os, tempfile, unittest
from pathlib import Path
from js3.policy import Policy, Blocked
from js3 import collect

class Network(unittest.TestCase):
    def setUp(self): self.p = Policy(tempfile.mkdtemp())
    def test_allowed(self):
        self.p.check_request("GET", "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true")
        self.p.check_request("GET", "https://api.lever.co/v0/postings/palantir?mode=json")
    def test_blocked(self):
        for m, u in [("POST", "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"),
                     ("GET", "http://boards-api.greenhouse.io/v1/boards/stripe/jobs"),
                     ("GET", "https://evil.example/v1/boards/stripe/jobs"),
                     ("GET", "https://boards-api.greenhouse.io.evil.example/v1/boards/x/jobs"),
                     ("GET", "https://user@boards-api.greenhouse.io/v1/boards/x/jobs"),
                     ("GET", "https://boards-api.greenhouse.io/v1/boards/stripe/jobs/123/applications"),
                     ("GET", "https://api.lever.co/v0/postings/palantir/abc/apply")]:
            with self.assertRaises(Blocked, msg=u): self.p.check_request(m, u)

class Files(unittest.TestCase):
    def test_writes_only_inside_data_out_transcripts(self):
        d = tempfile.mkdtemp(); p = Policy(d)
        for sub in ("data", "out", "transcripts"):
            os.makedirs(Path(d) / sub); p.check_write(Path(d) / sub / "x.json")
        for bad in [Path(d) / "FILTER.md", Path(d) / "data" / ".." / "FILTER.md", Path("/tmp/x.json"), Path.home() / "x"]:
            with self.assertRaises(Blocked, msg=str(bad)): p.check_write(bad)

GH = {"jobs": [{"id": 11, "title": "Data Analyst", "location": {"name": "Boston, MA"}, "absolute_url": "https://x/11",
                "content": "&lt;p&gt;Proficiency in &lt;strong&gt;SQL&lt;/strong&gt; &amp;amp; Python.&lt;/p&gt;&lt;ul&gt;&lt;li&gt;1-3 years&lt;/li&gt;&lt;/ul&gt;"},
               {"id": 12, "title": "", "location": None, "absolute_url": "https://x/12", "content": ""}]}
LV = [{"id": "ab-1", "text": "Analyst", "categories": {"location": "NYC"}, "hostedUrl": "https://y/ab-1",
       "descriptionPlain": "We use SQL.", "lists": [{"text": "Requirements", "content": "<li>Python</li><li>2 years</li>"}],
       "additionalPlain": "Benefits."}]

class Parse(unittest.TestCase):
    def test_greenhouse_html_to_plain_text(self):
        ps = collect.parse_board("greenhouse", "stripe", json.dumps(GH).encode())
        self.assertEqual(ps[0]["id"], "greenhouse:stripe:11"); self.assertEqual(ps[0]["location"], "Boston, MA")
        self.assertIn("Proficiency in SQL & Python.", ps[0]["text"]); self.assertIn("1-3 years", ps[0]["text"])
        self.assertNotIn("<", ps[0]["text"]); self.assertNotIn("&lt;", ps[0]["text"])
        self.assertEqual(ps[1]["text"], ""); self.assertIsNone(ps[1]["location"])     # missing stays missing
    def test_lever_includes_lists(self):
        p = collect.parse_board("lever", "palantir", json.dumps(LV).encode())[0]
        self.assertEqual(p["id"], "lever:palantir:ab-1")
        for s in ["We use SQL.", "Requirements", "Python", "2 years"]: self.assertIn(s, p["text"])

class FailedBoard(unittest.TestCase):
    def test_failed_board_is_failed_not_zero(self):
        from js3.fetch import Response
        def fetch(url, timeout):
            if "nope" in url: return Response(404, b"not found")
            return Response(200, json.dumps(GH).encode())
        boards = [{"ats": "greenhouse", "slug": "stripe"}, {"ats": "greenhouse", "slug": "nope"}]
        postings, summary = collect.collect(boards, fetch)
        self.assertEqual(summary["greenhouse:nope"]["status"], "failed"); self.assertIsNone(summary["greenhouse:nope"]["n"])
        self.assertEqual(summary["greenhouse:stripe"]["status"], "ok"); self.assertEqual(summary["greenhouse:stripe"]["n"], 2)
        self.assertEqual(len(postings), 2)
    def test_more_than_five_boards_refused(self):
        from js3.fetch import Response
        boards = [{"ats": "greenhouse", "slug": f"b{i}"} for i in range(6)]
        _, summary = collect.collect(boards, lambda u, t: Response(200, b'{"jobs": []}'))
        self.assertEqual(summary["greenhouse:b5"]["status"], "not-reached")

if __name__ == "__main__": unittest.main()
