"""Tests for the collector's allow-list, the tool server, the claim checker and the audit math.

Written after the code (2026-11-14), unlike tests/test_filter.py. Offline: no network, no model.
"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import audit  # noqa: E402
import collect  # noqa: E402
import mcp_server  # noqa: E402
import shortlist  # noqa: E402


class Collector(unittest.TestCase):
    def test_allow_list(self):
        collect.check_url("https://api.lever.co/v0/postings/spotify?mode=json")
        for bad in ["http://api.lever.co/v0/postings/spotify", "https://example.com/jobs",
                    "https://boards-api.greenhouse.io.evil.com/v1/boards/x/jobs"]:
            with self.subTest(url=bad), self.assertRaises(collect.Refused):
                collect.check_url(bad)

    def test_every_board_url_is_on_the_list(self):
        for b in collect.BOARDS:
            collect.check_url(b["url"])

    def test_failed_board_is_not_collected_and_raw_is_byte_for_byte(self):
        body = b'{"jobs": [{"id": 1, "title": "X\\u00e9"}]}'

        def fetcher(url):
            if "airbnb" in url:
                raise collect.Refused("simulated")
            return 200, body
        with tempfile.TemporaryDirectory() as tmp:
            old = collect.ROOT
            collect.ROOT = tmp
            try:
                m = collect.collect("t1", fetcher=fetcher, gap_s=0)
                status = {b["board"]: b["status"] for b in m["boards"]}
                self.assertEqual(status["airbnb"], "not collected")
                self.assertEqual(status["figma"], "collected")
                with open(os.path.join(tmp, "runs", "t1", "raw", "figma.json"), "rb") as f:
                    self.assertEqual(f.read(), body)
                self.assertFalse(os.path.exists(os.path.join(tmp, "runs", "t1", "raw", "airbnb.json")))
            finally:
                collect.ROOT = old


class ToolServer(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.s = mcp_server.Server("live-20261114", os.path.join(self.tmp.name, "t.jsonl"))

    def tearDown(self):
        self.tmp.cleanup()

    def ask(self, msg):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.s.handle(msg)
        out = buf.getvalue().strip()
        return json.loads(out) if out else None

    def call(self, args, name="score_posting"):
        return self.ask({"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": name, "arguments": args}})

    def test_lists_exactly_one_read_only_tool(self):
        tools = self.ask({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        self.assertTrue(tools[0]["annotations"]["readOnlyHint"])
        self.assertFalse(tools[0]["annotations"]["openWorldHint"])

    def test_scores_a_saved_posting(self):
        r = self.call({"board": "figma", "posting_id": "5691911004"})["result"]
        self.assertFalse(r["isError"])
        self.assertEqual(json.loads(r["content"][0]["text"])["verdict"], "keep")

    def test_refuses_what_it_does_not_declare(self):
        for args in [{"board": "figma", "posting_id": "../../persona/aarav-patel.resume"},
                     {"board": "../persona", "posting_id": "x"},
                     {"board": "figma", "posting_id": "5691911004", "write_to": "/tmp/x"},
                     {"board": "figma", "posting_id": "0000000000"}]:
            with self.subTest(args=args):
                self.assertTrue(self.call(args)["result"]["isError"])
        self.assertEqual(self.call({}, name="read_file")["error"]["code"], -32602)
        self.assertEqual(self.ask({"jsonrpc": "2.0", "id": 3, "method": "resources/list"})["error"]["code"], -32601)

    def test_notifications_get_no_reply(self):
        self.assertIsNone(self.ask({"jsonrpc": "2.0", "method": "notifications/initialized"}))



class ToolServerWrites(unittest.TestCase):
    """Separate class on purpose: no setUp builds a server before the 'before' snapshot."""

    def test_a_real_session_writes_only_its_transcript(self):
        """Run the server as a process, send good and bad requests, and compare every file under
        this folder (content and write time) before and after: the only new or changed file may
        be the session transcript."""
        import hashlib
        import subprocess

        def snapshot():
            out = {}
            for d, dirs, files in os.walk(ROOT):
                dirs[:] = [x for x in dirs if x not in ("__pycache__", ".git")]
                for f in files:
                    path = os.path.join(d, f)
                    with open(path, "rb") as fh:  # content AND write time: a rewrite with equal bytes counts
                        out[os.path.relpath(path, ROOT)] = (hashlib.sha256(fh.read()).hexdigest(),
                                                            os.stat(path).st_mtime_ns)
            return out
        name = "unittest-write-check"
        transcript = os.path.join("transcripts", name + ".jsonl")
        if os.path.exists(os.path.join(ROOT, transcript)):
            os.remove(os.path.join(ROOT, transcript))
        before = snapshot()
        lines = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
                 {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "score_posting",
                  "arguments": {"board": "figma", "posting_id": "5691911004"}}},
                 {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "score_posting",
                  "arguments": {"board": "figma", "posting_id": "5691911004", "write_to": "runs/x.json"}}}]
        try:
            p = subprocess.run([sys.executable, os.path.join(ROOT, "src", "mcp_server.py"), "--transcript-name", name],
                               input="\n".join(json.dumps(x) for x in lines) + "\n", capture_output=True,
                               text=True, cwd=ROOT, timeout=60)
            self.assertEqual(len(p.stdout.strip().splitlines()), 3)
            after = snapshot()
            changed = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
            self.assertEqual(changed, {transcript})
        finally:
            if os.path.exists(os.path.join(ROOT, transcript)):
                os.remove(os.path.join(ROOT, transcript))


class ClaimChecker(unittest.TestCase):
    def test_labels(self):
        self.assertEqual(shortlist.skill_label("Design, build and maintain backend services (Java)", "Java")[0], "supported")
        self.assertEqual(shortlist.skill_label("Back-end technologies (e.g., Ruby, Python, Go)", "Python")[0], "insufficient")
        self.assertEqual(shortlist.skill_label("Proficiency in TypeScript, Python, or Ruby.", "Python")[0], "insufficient")
        self.assertEqual(shortlist.skill_label("Kubernetes experience is a plus.", "Kubernetes")[0], "insufficient")
        self.assertEqual(shortlist.skill_label("Python is not required for this role.", "Python")[0], "contradicted")


class AuditMath(unittest.TestCase):
    def test_clopper_pearson_known_values(self):
        for k, n, lo, hi in [(0, 30, 0.0, 0.1157), (2, 30, 0.0082, 0.2207), (5, 10, 0.1871, 0.8129)]:
            got = audit.clopper_pearson(k, n)
            self.assertAlmostEqual(got[0], lo, places=3)
            self.assertAlmostEqual(got[1], hi, places=3)


if __name__ == "__main__":
    unittest.main()
