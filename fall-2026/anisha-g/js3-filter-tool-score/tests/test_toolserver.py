"""Tool server contract (assignment Ch.8 + FILTER.md), written BEFORE the server existed (2026-11-25).
The server is started as a real subprocess and spoken to over stdio, one JSON-RPC message per line."""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "tests" / "fixtures" / "corpus_small.jsonl"

class Server:
    def __init__(self):
        self.tdir = tempfile.mkdtemp()
        self.p = subprocess.Popen([sys.executable, "-m", "toolserver.server", "--corpus", str(FIX), "--transcripts", self.tdir],
                                  cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    def send(self, obj, expect_reply=True):
        line = obj if isinstance(obj, str) else json.dumps(obj)
        self.p.stdin.write(line + "\n"); self.p.stdin.flush()
        return json.loads(self.p.stdout.readline()) if expect_reply else None
    def close(self):
        self.p.stdin.close(); self.p.wait(timeout=5); self.p.stdout.close(); self.p.stderr.close()

def init(s):
    return s.send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                   "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}}})

class Handshake(unittest.TestCase):
    def setUp(self): self.s = Server()
    def tearDown(self): self.s.close()
    def test_initialize(self):
        r = init(self.s)
        self.assertEqual(r["id"], 1); res = r["result"]
        self.assertIn("protocolVersion", res); self.assertIn("tools", res["capabilities"])
        self.assertEqual(res["serverInfo"]["name"], "js3-job-filter")
    def test_initialized_notification_gets_no_reply_then_ping(self):
        init(self.s); self.s.send({"jsonrpc": "2.0", "method": "notifications/initialized"}, expect_reply=False)
        r = self.s.send({"jsonrpc": "2.0", "id": 2, "method": "ping"}); self.assertEqual(r, {"jsonrpc": "2.0", "id": 2, "result": {}})
    def test_tools_list_declares_exactly_one_read_only_tool(self):
        init(self.s); r = self.s.send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = r["result"]["tools"]; self.assertEqual([t["name"] for t in tools], ["score_posting"])
        t = tools[0]; self.assertEqual(t["inputSchema"]["type"], "object")
        self.assertTrue(t["annotations"]["readOnlyHint"]); self.assertFalse(t["annotations"]["openWorldHint"])

class Calls(unittest.TestCase):
    def setUp(self): self.s = Server(); init(self.s)
    def tearDown(self): self.s.close()
    def call(self, args, name="score_posting", id_=3):
        return self.s.send({"jsonrpc": "2.0", "id": id_, "method": "tools/call", "params": {"name": name, "arguments": args}})
    def payload(self, r):
        self.assertFalse(r["result"].get("isError"), r); return json.loads(r["result"]["content"][0]["text"])
    def test_score_by_id_matches_the_filter(self):
        d = self.payload(self.call({"id": "fx:1"}))
        self.assertEqual(d["status"], "kept"); self.assertEqual(d["score"], 5); self.assertTrue(d["shortlist"])
        self.assertEqual(d["filter_version"], "1.0"); self.assertTrue(all("label" in c for c in d["claims"]))
    def test_senior_rejected_with_reasons(self):
        d = self.payload(self.call({"id": "fx:2"})); self.assertEqual(d["status"], "rejected"); self.assertIn("R2", d["failed"])
    def test_missing_text_is_cannot_tell(self):
        d = self.payload(self.call({"id": "fx:4"})); self.assertEqual(d["status"], "cannot_tell")
    def test_score_by_title_and_text(self):
        d = self.payload(self.call({"title": "BI Analyst", "text": "Proficiency in SQL and Tableau."}))
        self.assertEqual(d["status"], "kept")
    def test_unknown_id_is_an_error_not_an_invented_answer(self):
        r = self.call({"id": "fx:999"}); self.assertTrue(r["result"]["isError"])
        self.assertIn("not found", r["result"]["content"][0]["text"].lower())
    def test_bad_arguments(self):
        for a in [{}, {"id": 5}, {"title": "x"}, {"id": "fx:1", "extra": "y"}]:
            r = self.call(a); self.assertTrue("error" in r or r["result"].get("isError"), a)
    def test_unknown_tool(self):
        r = self.call({"id": "fx:1"}, name="apply_to_job"); self.assertIn("error", r); self.assertEqual(r["error"]["code"], -32602)
    def test_unknown_method(self):
        r = self.s.send({"jsonrpc": "2.0", "id": 9, "method": "resources/list"}); self.assertEqual(r["error"]["code"], -32601)
    def test_malformed_json(self):
        r = self.s.send("{not json"); self.assertEqual(r["error"]["code"], -32700); self.assertIsNone(r["id"])

class Transcript(unittest.TestCase):
    def test_both_directions_recorded(self):
        s = Server(); init(s); s.send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}); s.close()
        files = list(Path(s.tdir).glob("*.jsonl")); self.assertEqual(len(files), 1)
        rows = [json.loads(l) for l in files[0].read_text().splitlines()]
        self.assertEqual([r["dir"] for r in rows], ["in", "out", "in", "out"])
        self.assertEqual(rows[0]["msg"]["method"], "initialize"); self.assertIn("ts", rows[0])

class NoSideEffects(unittest.TestCase):
    def test_server_source_has_no_network_or_outside_writes(self):
        src = (ROOT / "toolserver" / "server.py").read_text()
        for banned in ["urllib", "requests", "http.client", "socket", "subprocess", "os.remove", "shutil", "smtplib"]:
            self.assertNotIn(banned, src, banned)

if __name__ == "__main__": unittest.main()
