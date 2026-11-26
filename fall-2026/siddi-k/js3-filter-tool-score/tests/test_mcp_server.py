"""What js3.mcp_server declares versus what it does (brief Step 2.3). No network, no Claude."""
from __future__ import annotations

import builtins
import io
import json
import socket
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixtures import cfg, posting  # noqa: E402
from js3 import mcp_server, policy  # noqa: E402

INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}}


def call(args, name="score_posting", id_=9):
    return {"jsonrpc": "2.0", "id": id_, "method": "tools/call", "params": {"name": name, "arguments": args}}


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.s = mcp_server.Server(cfg(), "test-run", [posting(pid="42", title="Data Engineer")])
        self.s.handle(INIT)

    def test_declares_one_read_only_tool(self):
        tools = self.s.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        ann = tools[0]["annotations"]
        self.assertTrue(ann["readOnlyHint"] and not ann["destructiveHint"] and not ann["openWorldHint"])

    def test_call_is_actually_read_only_and_offline(self):
        """readOnlyHint / openWorldHint are only claims; here the call runs with writes and sockets blocked."""
        real_open, real_socket = builtins.open, socket.socket

        def guarded_open(file, mode="r", *a, **k):
            if any(ch in mode for ch in "wax+"):
                raise AssertionError(f"tool tried to write {file}")
            return real_open(file, mode, *a, **k)

        def no_socket(*a, **k):
            raise AssertionError("tool tried to open a network socket")

        builtins.open, socket.socket = guarded_open, no_socket
        try:
            r = self.s.handle(call({"board": "stripe", "posting_id": "42"}))
        finally:
            builtins.open, socket.socket = real_open, real_socket
        self.assertFalse(r["result"]["isError"])
        body = json.loads(r["result"]["content"][0]["text"])
        self.assertEqual(body["verdict"], "keep")
        self.assertIn("not a judgment", body["label"])

    def test_same_call_same_answer(self):
        a = self.s.handle(call({"board": "stripe", "posting_id": "42"}))
        b = self.s.handle(call({"board": "stripe", "posting_id": "42"}))
        self.assertEqual(a, b)

    def test_schema_is_enforced_not_just_declared(self):
        for bad in ({"board": "stripe"}, {"board": "stripe", "posting_id": "42", "path": "x"},
                    {"board": "linkedin", "posting_id": "42"}, {"board": "stripe", "posting_id": "../../.env"},
                    {"board": "stripe", "posting_id": 42}, []):
            r = self.s.handle(call(bad))
            self.assertTrue(r["result"]["isError"], bad)
        r = self.s.handle(call({"board": "stripe", "posting_id": "999"}))
        self.assertTrue(r["result"]["isError"])

    def test_protocol_errors(self):
        self.assertEqual(self.s.handle(call({}, name="delete_posting"))["error"]["code"], -32602)
        self.assertEqual(self.s.handle({"jsonrpc": "2.0", "id": 3, "method": "resources/list"})["error"]["code"], -32601)
        self.assertIsNone(self.s.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))
        self.assertEqual(json.loads(self.s.handle_line("{"))["error"]["code"], -32700)
        self.assertEqual(json.loads(self.s.handle_line("[]"))["error"]["code"], -32600)

    def test_refuses_tools_before_initialize(self):
        fresh = mcp_server.Server(cfg(), "test-run", [])
        self.assertEqual(fresh.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["error"]["code"], -32000)

    def test_unknown_protocol_version_gets_servers_version(self):
        fresh = mcp_server.Server(cfg(), "test-run", [])
        init = json.loads(json.dumps(INIT))
        init["params"]["protocolVersion"] = "2099-01-01"
        self.assertEqual(fresh.handle(init)["result"]["protocolVersion"], "2025-11-25")

    def test_transcript_can_only_be_written_inside_the_folder(self):
        with self.assertRaises(policy.Refused):
            mcp_server.Transcript(str(Path.home() / "js3-transcript.jsonl"))
        with self.assertRaises(policy.Refused):
            mcp_server.Transcript("js3/evil.jsonl")

    def test_stdio_loop_writes_only_replies(self):
        lines = [json.dumps(INIT), json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
                 json.dumps(call({"board": "stripe", "posting_id": "42"}))]
        out = io.BytesIO()
        s = mcp_server.Server(cfg(), "test-run", [posting(pid="42")])
        mcp_server.serve(s, mcp_server.Transcript(None), io.BytesIO(("\n".join(lines) + "\n").encode()), out)
        replies = [json.loads(x) for x in out.getvalue().decode().splitlines()]
        self.assertEqual([r["id"] for r in replies], [1, 9])


if __name__ == "__main__":
    unittest.main()
