"""JS3 Step 5: the MCP-style tool server, written from scratch (JSON-RPC 2.0 over stdio, newline-delimited).

Checks the three methods (initialize, tools/list, tools/call), the error paths, and that what the tool DECLARES (read-only,
no network, no writes, same answer for the same input) is what it actually DOES. Uses a tiny in-memory snapshot.
Written before jsagent/mcp_server.py existed.
"""
import json
import socket
import unittest
from unittest import mock

from jsagent import mcp_server

POSTINGS = [{"board": "acme", "id": "1", "title": "Data Engineer", "location": {"name": "Boston, MA"},
             "content": "3+ years of experience. You have strong Python and SQL.", "absolute_url": "https://x/1"}]
OUTCOMES = {"acme": "observed", "gone": "not observed", "empty": "0 postings, needs review"}


def server():
    return mcp_server.Server(postings=POSTINGS, outcomes=OUTCOMES)


def init(s):
    r = s.handle({"jsonrpc": "2.0", "id": 0, "method": "initialize",
                  "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}})
    s.handle({"jsonrpc": "2.0", "method": "notifications/initialized"})
    return r


def call(s, args, name="score_posting", rid=5):
    return s.handle({"jsonrpc": "2.0", "id": rid, "method": "tools/call", "params": {"name": name, "arguments": args}})


class Protocol(unittest.TestCase):
    def test_initialize(self):
        r = init(server())
        self.assertEqual(r["id"], 0)
        self.assertEqual(r["result"]["protocolVersion"], "2025-06-18")
        self.assertIn("tools", r["result"]["capabilities"])
        self.assertEqual(r["result"]["serverInfo"]["name"], "js3-score-posting")

    def test_unsupported_version_gets_servers_version(self):
        s = server()
        r = s.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "1999-01-01"}})
        self.assertEqual(r["result"]["protocolVersion"], mcp_server.PROTOCOL_VERSIONS[0])

    def test_notification_gets_no_response(self):
        self.assertIsNone(server().handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_tools_list(self):
        s = server()
        init(s)
        tools = s.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        schema = tools[0]["inputSchema"]
        self.assertEqual(schema["required"], ["board", "posting_id"])
        self.assertFalse(schema["additionalProperties"])
        self.assertTrue(tools[0]["annotations"]["readOnlyHint"])
        self.assertFalse(tools[0]["annotations"]["openWorldHint"])

    def test_call_returns_bucket_score_and_evidence(self):
        s = server()
        init(s)
        r = call(s, {"board": "acme", "posting_id": "1"})["result"]
        self.assertFalse(r["isError"])
        out = r["structuredContent"]
        self.assertEqual((out["bucket"], out["score"]), ("kept", 42))
        self.assertEqual(json.loads(r["content"][0]["text"]), out)
        self.assertTrue(all(c["label"] in ("supported", "contradicted", "insufficient") for c in out["claims"]))

    def test_tools_before_initialize_refused(self):
        r = server().handle({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
        self.assertEqual(r["error"]["code"], -32002)

    def test_errors(self):
        s = server()
        init(s)
        self.assertEqual(s.handle({"jsonrpc": "2.0", "id": 4, "method": "resources/list"})["error"]["code"], -32601)
        self.assertEqual(call(s, {"board": "acme", "posting_id": "1"}, name="delete_posting")["error"]["code"], -32602)
        for bad in ({"board": "acme"}, {"board": "acme", "posting_id": 1}, {"board": "acme", "posting_id": "1", "x": 1},
                    {"board": "../etc", "posting_id": "1"}):
            self.assertEqual(call(s, bad)["error"]["code"], -32602, bad)
        self.assertEqual(s.handle_line("{not json")["error"]["code"], -32700)
        self.assertEqual(s.handle_line("[]")["error"]["code"], -32600)  # no batches in 2025-06-18

    def test_not_observed_and_missing_are_said_not_guessed(self):
        s = server()
        init(s)
        for args, phrase in (({"board": "gone", "posting_id": "1"}, "not observed"),
                             ({"board": "empty", "posting_id": "1"}, "0 postings"),
                             ({"board": "acme", "posting_id": "999"}, "not in the snapshot"),
                             ({"board": "nobody", "posting_id": "1"}, "not one of the snapshot's boards")):
            r = call(s, args)["result"]
            self.assertTrue(r["isError"], args)
            self.assertIn(phrase, r["content"][0]["text"])
            self.assertNotIn("no relevant", r["content"][0]["text"].lower())


class DeclaredVsActual(unittest.TestCase):
    def test_no_network_during_a_call(self):
        s = server()
        init(s)
        with mock.patch.object(socket, "socket", side_effect=AssertionError("network used")), \
                mock.patch.object(socket, "create_connection", side_effect=AssertionError("network used")):
            self.assertFalse(call(s, {"board": "acme", "posting_id": "1"})["result"]["isError"])

    def test_no_file_writes_during_a_call(self):
        s = server()
        init(s)
        real_open = open

        def guarded(path, mode="r", *a, **k):
            if any(c in mode for c in "wax+"):
                raise AssertionError(f"write to {path}")
            return real_open(path, mode, *a, **k)

        with mock.patch("builtins.open", guarded):
            self.assertFalse(call(s, {"board": "acme", "posting_id": "1"})["result"]["isError"])

    def test_description_declares_the_version_it_runs(self):
        # Found by Claude Code as a real client (evidence/mcp/claude_client): the description said v1.2, the output v1.3.
        s = server()
        init(s)
        desc = s.handle({"jsonrpc": "2.0", "id": 9, "method": "tools/list"})["result"]["tools"][0]["description"]
        out = call(s, {"board": "acme", "posting_id": "1"})["result"]["structuredContent"]
        self.assertIn(out["filter_version"], desc)
        self.assertEqual(desc.count("FILTER.md v"), 1)

    def test_same_input_same_answer(self):
        s = server()
        init(s)
        a = call(s, {"board": "acme", "posting_id": "1"}, rid=1)["result"]
        b = call(s, {"board": "acme", "posting_id": "1"}, rid=2)["result"]
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
