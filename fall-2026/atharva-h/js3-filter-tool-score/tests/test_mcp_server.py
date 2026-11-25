"""The MCP server: the protocol (initialize, tools/list, tools/call, errors, notifications), and the claim that
a request never writes, sends, or fetches anything."""
import builtins
import json
import os
import socket
import subprocess
import sys
import unittest
import urllib.request
from unittest import mock

from helpers import ROOT

import mcp_server as M

POSTINGS = [{"key": "greenhouse/acme/1", "title": "Data Analyst", "text": "SQL and Tableau.",
             "locations": ["New York, NY"], "location": "New York, NY", "country": None, "url": "https://x.invalid/1",
             "corpus": "v1.0"},
            {"key": "lever/acme/a-2", "title": "Senior Data Analyst", "text": "SQL.", "locations": ["Remote"],
             "location": "Remote", "country": None, "url": "https://x.invalid/2", "corpus": "v1.0"}]


def call(server, method, params=None, mid=1):
    msg = {"jsonrpc": "2.0", "id": mid, "method": method}
    if params is not None:
        msg["params"] = params
    return json.loads(server.handle_line(json.dumps(msg)))


class Protocol(unittest.TestCase):
    def setUp(self):
        self.log = []
        self.server = M.Server(POSTINGS, lambda d, m: self.log.append((d, m)))

    def test_initialize_echoes_a_supported_version_else_offers_the_newest(self):
        r = call(self.server, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {}})["result"]
        self.assertEqual(r["protocolVersion"], "2025-06-18")
        self.assertEqual(r["capabilities"], {"tools": {"listChanged": False}})
        r = call(self.server, "initialize", {"protocolVersion": "1999-01-01"})["result"]
        self.assertEqual(r["protocolVersion"], M.PROTOCOL_VERSIONS[0])

    def test_notifications_get_no_reply(self):
        self.assertIsNone(self.server.handle_line('{"jsonrpc":"2.0","method":"notifications/initialized"}'))
        self.assertTrue(self.server.initialized)

    def test_tools_list_declares_one_read_only_tool(self):
        [tool] = call(self.server, "tools/list")["result"]["tools"]
        self.assertEqual(tool["name"], "score_posting")
        self.assertEqual(tool["annotations"]["readOnlyHint"], True)
        self.assertEqual(tool["annotations"]["openWorldHint"], False)
        self.assertEqual(tool["inputSchema"]["required"], ["key"])

    def test_tools_call_returns_the_filter_verdict_with_its_evidence(self):
        r = call(self.server, "tools/call", {"name": "score_posting", "arguments": {"key": "greenhouse/acme/1"}})
        out = r["result"]["structuredContent"]
        self.assertFalse(r["result"]["isError"])
        self.assertEqual((out["verdict"], out["score"], out["skills"]), ("keep", 6, {"SQL": "SQL", "Tableau": "Tableau"}))
        self.assertEqual(json.loads(r["result"]["content"][0]["text"]), out)
        r = call(self.server, "tools/call", {"name": "score_posting", "arguments": {"key": "lever/acme/a-2"}})
        self.assertEqual(r["result"]["structuredContent"]["rejected_by"], {"R1": "Senior"})

    def test_bad_arguments_are_tool_errors_not_protocol_errors(self):
        for args in ({}, {"key": "../../etc/passwd"}, {"key": "greenhouse/acme/999"},
                     {"key": "greenhouse/acme/1", "extra": 1}, {"key": 5}):
            with self.subTest(args=args):
                r = call(self.server, "tools/call", {"name": "score_posting", "arguments": args})
                self.assertTrue(r["result"]["isError"])

    def test_protocol_errors(self):
        self.assertEqual(call(self.server, "tools/call", {"name": "send_email"})["error"]["code"], -32602)
        self.assertEqual(call(self.server, "resources/list")["error"]["code"], -32601)
        self.assertEqual(json.loads(self.server.handle_line("{not json"))["error"]["code"], -32700)
        self.assertEqual(json.loads(self.server.handle_line('{"id": 4}'))["error"]["code"], -32600)

    def test_every_message_is_logged_in_both_directions(self):
        call(self.server, "ping")
        self.assertEqual([d for d, _ in self.log], ["in", "out"])

    def test_a_request_never_writes_fetches_or_connects(self):
        boom = mock.Mock(side_effect=AssertionError("side effect during a request"))
        with mock.patch.object(builtins, "open", boom), mock.patch.object(urllib.request, "urlopen", boom), \
                mock.patch.object(socket, "socket", boom), mock.patch.object(os, "remove", boom):
            call(self.server, "initialize", {"protocolVersion": "2025-06-18"})
            call(self.server, "tools/list")
            call(self.server, "tools/call", {"name": "score_posting", "arguments": {"key": "greenhouse/acme/1"}})
        boom.assert_not_called()


class OverStdio(unittest.TestCase):
    def test_real_process_answers_one_line_per_request_and_nothing_else_on_stdout(self):
        lines = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
                 {"jsonrpc": "2.0", "method": "notifications/initialized"},
                 {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                 {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                  "params": {"name": "score_posting", "arguments": {"key": "greenhouse/fanduel/8055746"}}}]
        proc = subprocess.run([sys.executable, os.path.join(ROOT, "mcp_server.py"), "--log", "none"],
                              input="".join(json.dumps(m) + "\n" for m in lines), capture_output=True, text=True,
                              timeout=60)
        replies = [json.loads(line) for line in proc.stdout.splitlines()]
        self.assertEqual([r["id"] for r in replies], [1, 2, 3])
        self.assertEqual(replies[2]["result"]["structuredContent"]["verdict"], "keep")


if __name__ == "__main__":
    unittest.main()
