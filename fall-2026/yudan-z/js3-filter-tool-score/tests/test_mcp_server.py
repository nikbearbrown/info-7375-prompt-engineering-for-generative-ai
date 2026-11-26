"""Tests for mcp/server.py: the handshake, the read-only tools, and the refusals."""
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = os.path.join(ROOT, "mcp", "server.py")


def session(*msgs):
    inp = "".join(json.dumps(m) + "\n" for m in msgs)
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1",
               JS3_MCP_LOG_DIR=os.path.join(ROOT, "runs", "tmp", "mcp-test-logs"))
    out = subprocess.run([sys.executable, SERVER], input=inp, capture_output=True, text=True, encoding="utf-8",
                         env=env, timeout=60).stdout
    return [json.loads(line) for line in out.splitlines() if line.strip()]


INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}}}
INITED = {"jsonrpc": "2.0", "method": "notifications/initialized"}


def call(i, name, args):
    return {"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": name, "arguments": args}}


class McpServerTests(unittest.TestCase):
    def test_handshake_and_list(self):
        r = session(INIT, INITED, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(len(r), 2)  # the notification gets no reply
        self.assertEqual(r[0]["result"]["serverInfo"]["name"], "js3-postings")
        self.assertEqual({t["name"] for t in r[1]["result"]["tools"]}, {"search_postings", "score_posting"})

    def test_every_tool_declares_read_only_and_closed_world(self):
        r = session(INIT, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        for t in r[1]["result"]["tools"]:
            self.assertTrue(t["annotations"]["readOnlyHint"])
            self.assertFalse(t["annotations"]["openWorldHint"])

    def test_search_then_score(self):
        r = session(INIT, call(2, "search_postings", {"query": "deployment strategist new grad", "limit": 3}))
        found = json.loads(r[1]["result"]["content"][0]["text"])
        self.assertGreaterEqual(found["total_matches"], 1)
        key = found["postings"][0]["key"]
        r = session(INIT, call(3, "score_posting", {"key": key, "version": "v2"}))
        res = json.loads(r[1]["result"]["content"][0]["text"])
        self.assertIn(res["decision"], ("keep", "reject", "cannot tell"))
        self.assertTrue(all(c["label"] in ("supported", "contradicted", "insufficient") for c in res["claims"]))

    def test_path_outside_filter_folder_is_refused(self):
        r = session(INIT, call(2, "score_posting", {"key": "x", "version": "../../persona/resume"}))
        self.assertTrue(r[1]["result"]["isError"])

    def test_limit_is_bounded(self):
        r = session(INIT, call(2, "search_postings", {"query": "engineer", "limit": 5000}))
        self.assertTrue(r[1]["result"]["isError"])

    def test_unknown_tool_and_unknown_method(self):
        r = session(INIT, call(2, "write_file", {"path": "x"}), {"jsonrpc": "2.0", "id": 3, "method": "resources/list"})
        self.assertEqual(r[1]["error"]["code"], -32602)
        self.assertEqual(r[2]["error"]["code"], -32601)

    def test_source_has_no_network_process_or_delete_calls(self):
        with open(SERVER, encoding="utf-8") as fh:
            src = fh.read()
        for banned in ("urllib", "requests", "socket", "subprocess", "smtplib", "os.remove", "shutil", "http.client"):
            self.assertNotIn(banned, src)


if __name__ == "__main__":
    unittest.main()
