"""Tests for agent/mcp_server.py, written before the server exists (Nov 24, 2026).

They start the server as a subprocess and talk to it over stdio, one JSON-RPC
message per line, the way an MCP client does.

    python3 -m unittest -v tests.test_mcp_server
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class Server:
    def __init__(self, log_path: str):
        env = dict(os.environ, JS3_MCP_LOG=log_path)
        self.p = subprocess.Popen([sys.executable, "-m", "agent.mcp_server"], cwd=ROOT, env=env, text=True,
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.next_id = 0

    def send(self, msg: dict):
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()

    def request(self, method: str, params=None) -> dict:
        self.next_id += 1
        msg = {"jsonrpc": "2.0", "id": self.next_id, "method": method}
        if params is not None:
            msg["params"] = params
        self.send(msg)
        reply = json.loads(self.p.stdout.readline())
        assert reply["id"] == self.next_id, reply
        return reply

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=5)
        self.p.stdout.close()
        self.p.stderr.close()


class McpServer(unittest.TestCase):
    def setUp(self):
        (ROOT / "out").mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / "out")   # the log must be inside out/
        self.log = os.path.join(self.tmp.name, "calls.jsonl")
        self.s = Server(self.log)
        r = self.s.request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                          "clientInfo": {"name": "unittest", "version": "0"}})
        self.init = r["result"]
        self.s.send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def tearDown(self):
        self.s.close()
        self.tmp.cleanup()

    def call(self, name, args):
        return self.s.request("tools/call", {"name": name, "arguments": args})

    def test_initialize(self):
        self.assertEqual(self.init["protocolVersion"], "2025-06-18")
        self.assertIn("tools", self.init["capabilities"])
        self.assertEqual(self.init["serverInfo"]["name"], "js3-job-filter")

    def test_tools_list_is_read_only(self):
        tools = self.s.request("tools/list")["result"]["tools"]
        names = {t["name"] for t in tools}
        self.assertEqual(names, {"search_postings", "get_posting", "judge_posting", "shortlist_entry"})
        for t in tools:
            self.assertEqual(t["inputSchema"]["type"], "object")
            self.assertTrue(t["annotations"]["readOnlyHint"], t["name"])
            self.assertFalse(t["annotations"]["openWorldHint"], t["name"])

    def test_search(self):
        r = self.call("search_postings", {"query": "Software Engineer I", "board": "affirm", "limit": 5})["result"]
        self.assertFalse(r["isError"])
        hits = r["structuredContent"]["results"]
        self.assertTrue(0 < len(hits) <= 5)
        self.assertTrue(all(h["board"] == "affirm" for h in hits))

    def test_get_posting(self):
        r = self.call("get_posting", {"uid": "affirm:8032173003"})["result"]
        self.assertIn("1.5+ years", r["structuredContent"]["text"])

    def test_judge_posting_uses_v1_2(self):
        r = self.call("judge_posting", {"uid": "affirm:7727320003"})["result"]["structuredContent"]
        self.assertEqual(r["version"], "v1.2")
        self.assertFalse(r["keep"])
        self.assertEqual(r["years"], 3)

    def test_shortlist_entry_quotes(self):
        r = self.call("shortlist_entry", {"uid": "robinhood:7263592"})["result"]["structuredContent"]
        entry = {c["id"]: c for c in r["claims"]}["entry"]
        self.assertEqual(entry["label"], "contradicted")

    def test_unknown_uid_is_a_tool_error_not_a_crash(self):
        r = self.call("get_posting", {"uid": "nope:1"})["result"]
        self.assertTrue(r["isError"])
        self.assertEqual(self.s.request("ping")["result"], {})   # still alive

    def test_bad_arguments(self):
        r = self.call("search_postings", {"limit": 5})["result"]          # query missing
        self.assertTrue(r["isError"])
        r = self.call("search_postings", {"query": "x", "limit": 10_000})["result"]
        self.assertTrue(r["isError"])

    def test_unknown_tool_and_method(self):
        self.assertEqual(self.call("apply_to_job", {"uid": "affirm:8032173003"})["error"]["code"], -32602)
        self.assertEqual(self.s.request("resources/list")["error"]["code"], -32601)

    def test_malformed_json_gets_parse_error(self):
        self.s.p.stdin.write("{not json\n")
        self.s.p.stdin.flush()
        self.assertEqual(json.loads(self.s.p.stdout.readline())["error"]["code"], -32700)

    def test_every_call_is_logged(self):
        self.call("get_posting", {"uid": "affirm:8032173003"})
        self.call("get_posting", {"uid": "nope:1"})
        rows = [json.loads(l) for l in open(self.log)]
        calls = [r for r in rows if r["method"] == "tools/call"]
        self.assertEqual([r["tool"] for r in calls], ["get_posting", "get_posting"])
        self.assertEqual([r["is_error"] for r in calls], [False, True])

    def test_log_must_stay_in_folder(self):
        s = subprocess.run([sys.executable, "-m", "agent.mcp_server"], cwd=ROOT, input="",
                           env=dict(os.environ, JS3_MCP_LOG="/etc/js3.log"), capture_output=True, text=True)
        self.assertNotEqual(s.returncode, 0)


if __name__ == "__main__":
    unittest.main()
