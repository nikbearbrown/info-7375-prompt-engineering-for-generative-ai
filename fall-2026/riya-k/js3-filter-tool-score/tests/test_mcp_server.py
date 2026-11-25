"""The tool server speaks the message shapes it declares, and does only what it declares. Offline."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from js3 import mcp_server as S  # noqa: E402


def call(name="score_posting", args=None, mid=7):
    return S.handle({"jsonrpc": "2.0", "id": mid, "method": "tools/call", "params": {"name": name, "arguments": args}})


class Protocol(unittest.TestCase):
    def test_initialize_echoes_supported_version(self):
        r = S.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}})
        self.assertEqual(r["result"]["protocolVersion"], "2025-06-18")
        self.assertEqual(r["result"]["capabilities"], {"tools": {"listChanged": False}})

    def test_initialize_unknown_version_falls_back(self):
        r = S.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "1999-01-01"}})
        self.assertEqual(r["result"]["protocolVersion"], S.SUPPORTED_VERSIONS[0])

    def test_notification_gets_no_reply(self):
        self.assertIsNone(S.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_unknown_method_and_bad_request(self):
        self.assertEqual(S.handle({"jsonrpc": "2.0", "id": 2, "method": "server/discover"})["error"]["code"], -32601)
        self.assertEqual(S.handle({"id": 3, "method": "ping"})["error"]["code"], -32600)

    def test_exactly_one_read_only_tool(self):
        tools = S.handle({"jsonrpc": "2.0", "id": 4, "method": "tools/list"})["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        self.assertTrue(tools[0]["annotations"]["readOnlyHint"])
        self.assertFalse(tools[0]["annotations"]["openWorldHint"])


class ToolBehaviour(unittest.TestCase):
    def test_known_posting_matches_filter_run(self):
        r = call(args={"board": "greenhouse:databricks", "id": "8933544002"})["result"]
        rec = json.loads(r["content"][0]["text"])
        self.assertFalse(r["isError"])
        self.assertEqual((rec["decision"], rec["score"]), ("kept", 9))
        self.assertTrue(rec["claims"])

    def test_missing_posting_says_cannot_tell(self):
        r = call(args={"board": "ashby:notion", "id": "does-not-exist"})["result"]
        self.assertTrue(r["isError"])
        self.assertIn("cannot tell", r["content"][0]["text"])

    def test_board_with_no_data_is_not_reported_as_no_jobs(self):
        r = call(args={"board": "smartrecruiters:hubspot", "id": "1"})["result"]
        self.assertTrue(r["isError"])
        self.assertIn("no data", r["content"][0]["text"])

    def test_extra_arguments_and_unknown_tool_refused(self):
        self.assertTrue(call(args={"board": "ashby:notion", "id": "x", "send_email": True})["result"]["isError"])
        self.assertEqual(call(name="apply_to_job", args={})["error"]["code"], -32602)


class Boundaries(unittest.TestCase):
    def _run(self, transcript_path):
        env = dict(os.environ, PYTHONPATH=str(ROOT), JS3_MCP_TRANSCRIPT=transcript_path)
        msg = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping"}) + "\n"
        return subprocess.run([sys.executable, "-m", "js3.mcp_server"], input=msg, capture_output=True, text=True,
                              env=env, cwd=ROOT, timeout=30)

    def test_refuses_transcript_outside_its_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            outside = os.path.join(tmp, "x.jsonl")
            p = self._run(outside)
            self.assertIn("refusing", p.stderr)
            self.assertFalse(os.path.exists(outside))
            self.assertEqual(json.loads(p.stdout)["result"], {})  # still answers; just does not write

    def test_refuses_dotdot_escape(self):
        p = self._run("transcripts/../../escape.jsonl")
        self.assertIn("refusing", p.stderr)
        self.assertFalse((ROOT.parent / "escape.jsonl").exists())

    def test_server_source_has_no_network_or_send_calls(self):
        src = (ROOT / "js3" / "mcp_server.py").read_text()
        for bad in ["urllib", "socket", "http.client", "smtplib", "requests", "subprocess"]:
            self.assertNotIn(f"import {bad}", src)


if __name__ == "__main__":
    unittest.main()
