"""Tests for the tool server, written before jsagent3/mcp_server.py existed.

What the server must declare and do (FILTER.md + brief): initialize, tools/list, tools/call; one read-only
capability, score_posting; nothing that sends or changes data outside this folder.
"""
import json
import unittest

from jsagent3.mcp_server import Server

POSTINGS = {
    "t:1": {"id": "t:1", "board": "t", "title": "Software Engineer, New Grad", "location": "Seattle, WA",
            "body": "Requirements\n- Java and SQL\n- 0-2 years", "url": "https://example.test/1"},
}


def init(s):
    r = s.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                  "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                             "clientInfo": {"name": "test", "version": "0"}}})
    s.handle({"jsonrpc": "2.0", "method": "notifications/initialized"})
    return r


def call(s, args, name="score_posting", i=3):
    return s.handle({"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": name, "arguments": args}})


class Handshake(unittest.TestCase):
    def test_initialize_declares_tools_only(self):
        r = init(Server(POSTINGS))["result"]
        self.assertEqual(r["protocolVersion"], "2025-06-18")
        self.assertIn("tools", r["capabilities"])
        self.assertNotIn("resources", r["capabilities"])
        self.assertNotIn("prompts", r["capabilities"])

    def test_notification_gets_no_reply(self):
        s = Server(POSTINGS)
        self.assertIsNone(s.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_call_before_initialize_refused(self):
        r = call(Server(POSTINGS), {"posting_id": "t:1"})
        self.assertIn("error", r)


class ToolList(unittest.TestCase):
    def test_exactly_one_read_only_tool(self):
        s = Server(POSTINGS)
        init(s)
        tools = s.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        self.assertTrue(tools[0]["annotations"]["readOnlyHint"])
        self.assertFalse(tools[0]["annotations"]["openWorldHint"])
        self.assertEqual(tools[0]["inputSchema"]["type"], "object")


class ToolCall(unittest.TestCase):
    def setUp(self):
        self.s = Server(POSTINGS)
        init(self.s)

    def payload(self, r):
        self.assertFalse(r["result"].get("isError"), r)
        return json.loads(r["result"]["content"][0]["text"])

    def test_score_by_id(self):
        out = self.payload(call(self.s, {"posting_id": "t:1"}))
        self.assertTrue(out["decision"]["keep"])
        self.assertIn("claims", out)
        self.assertEqual(out["filter_version"], "v1")

    def test_score_pasted_text(self):
        out = self.payload(call(self.s, {"title": "Account Executive", "body": "Java SQL", "location": "NYC"}))
        self.assertFalse(out["decision"]["keep"])

    def test_unknown_id_is_tool_error_not_crash(self):
        r = call(self.s, {"posting_id": "../../etc/passwd"})
        self.assertTrue(r["result"]["isError"])

    def test_unknown_tool(self):
        r = call(self.s, {}, name="apply_to_job")
        self.assertIn("error", r)
        self.assertEqual(r["error"]["code"], -32602)

    def test_unknown_method(self):
        r = self.s.handle({"jsonrpc": "2.0", "id": 9, "method": "resources/list"})
        self.assertEqual(r["error"]["code"], -32601)

    def test_bad_arguments(self):
        r = call(self.s, {"posting_id": 5})
        self.assertTrue(r["result"]["isError"])


class Wire(unittest.TestCase):
    def test_parse_error_line(self):
        s = Server(POSTINGS)
        r = s.handle_line("{not json")
        self.assertEqual(json.loads(r)["error"]["code"], -32700)


if __name__ == "__main__":
    unittest.main()
