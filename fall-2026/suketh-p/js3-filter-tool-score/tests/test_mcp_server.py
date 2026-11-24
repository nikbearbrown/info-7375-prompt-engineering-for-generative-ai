"""The tool server's lifecycle, requests and results (Chapter 8's transition table, for this server).

Written by Claude Code right after jobwatch/mcp_server.py, not before it. Every message here is
CONSTRUCTED; the real sessions are in transcripts/."""

import json
import unittest

from jobwatch import corpus, mcp_server, screen

INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}}}
INITIALIZED = {"jsonrpc": "2.0", "method": "notifications/initialized"}
LIST = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}

_ITEMS, _ = corpus.load(mcp_server.CORPUS_RUN)
SAVED = next(i for i in _ITEMS if i.board == "greenhouse/anthropic")


def call(arguments, id_=3, name="score_posting"):
    return {"jsonrpc": "2.0", "id": id_, "method": "tools/call", "params": {"name": name, "arguments": arguments}}


def state(server):
    return (server.initialized, server.ready)


def ready_server():
    server = mcp_server.Server()
    server.handle(INIT)
    server.handle(INITIALIZED)
    return server


class LifecycleTableTest(unittest.TestCase):
    def test_rows(self):
        server = mcp_server.Server()
        rows = [
            # before, message, expected code or None for a result / "none" for no response, after
            ((False, False), {}, -32600, (False, False)),
            ((False, False), LIST, -32000, (False, False)),
            ((False, False), INITIALIZED, "none", (False, False)),
            ((False, False), INIT, None, (True, False)),
            ((True, False), LIST, -32000, (True, False)),      # initialize, no notification yet: still refused
            ((True, False), INITIALIZED, "none", (True, True)),
            ((True, True), LIST, None, (True, True)),
        ]
        for n, (before, message, expected, after) in enumerate(rows, start=1):
            with self.subTest(row=n):
                self.assertEqual(state(server), before)
                response = server.handle(message)
                if expected == "none":
                    self.assertIsNone(response)
                elif expected is None:
                    self.assertIn("result", response)
                else:
                    self.assertEqual(response["error"]["code"], expected)
                self.assertEqual(state(server), after)

    def test_ping_is_answered_in_any_state(self):
        server = mcp_server.Server()
        self.assertEqual(server.handle({"jsonrpc": "2.0", "id": "p", "method": "ping"}), {"jsonrpc": "2.0", "id": "p", "result": {}})

    def test_a_notification_never_gets_a_response_even_when_ready(self):
        server = ready_server()
        self.assertIsNone(server.handle({"jsonrpc": "2.0", "method": "tools/call", "params": {}}))
        self.assertIsNone(server.handle({"jsonrpc": "2.0", "method": "notifications/cancelled"}))


class InitializeTest(unittest.TestCase):
    def test_a_supported_version_is_echoed_and_an_unsupported_one_gets_the_latest(self):
        for requested, answered in (("2025-11-25", "2025-11-25"), ("2025-06-18", "2025-06-18"),
                                    ("unsupported-fixture", "2025-11-25")):
            with self.subTest(requested=requested):
                message = json.loads(json.dumps(INIT))
                message["params"]["protocolVersion"] = requested
                result = mcp_server.Server().handle(message)["result"]
                self.assertEqual(result["protocolVersion"], answered)
                self.assertEqual(result["capabilities"], {"tools": {"listChanged": False}})

    def test_initialize_without_its_required_fields_is_refused_and_changes_nothing(self):
        for params in (None, {}, {"protocolVersion": "2025-11-25", "capabilities": {}}, []):
            with self.subTest(params=params):
                server = mcp_server.Server()
                response = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": params})
                self.assertEqual(response["error"]["code"], -32602)
                self.assertEqual(state(server), (False, False))


class MessageShapeTest(unittest.TestCase):
    def test_parse_error_batch_and_bad_ids(self):
        server = ready_server()
        self.assertEqual(json.loads(mcp_server.handle_line(server, "{"))["error"]["code"], -32700)
        self.assertEqual(json.loads(mcp_server.handle_line(server, "[]"))["error"]["code"], -32600)
        for bad_id in (True, None, 1.5, [1]):
            with self.subTest(id=bad_id):
                response = server.handle({"jsonrpc": "2.0", "id": bad_id, "method": "tools/list"})
                self.assertEqual((response["id"], response["error"]["code"]), (None, -32600))

    def test_unknown_method_once_ready(self):
        self.assertEqual(ready_server().handle({"jsonrpc": "2.0", "id": 9, "method": "bad"})["error"]["code"], -32601)

    def test_every_response_carries_the_id_of_its_request(self):
        server = ready_server()
        for id_ in (7, "seven", 0):
            self.assertEqual(server.handle(dict(LIST, id=id_))["id"], id_)


class ToolTest(unittest.TestCase):
    def test_the_listing_declares_one_read_only_tool_and_its_schema(self):
        tools = ready_server().handle(LIST)["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        schema = tools[0]["inputSchema"]
        self.assertEqual(schema["required"], ["board", "posting_key"])
        self.assertFalse(schema["additionalProperties"])
        self.assertTrue(tools[0]["annotations"]["readOnlyHint"])

    def test_the_call_enforces_what_the_schema_declares(self):
        server = ready_server()
        good = {"board": SAVED.board, "posting_key": SAVED.key}
        bad_arguments = [[], {}, {"board": SAVED.board}, dict(good, extra=1), dict(good, board="greenhouse/stripe"),
                         dict(good, posting_key=""), dict(good, posting_key=5), dict(good, posting_key="x" * 301)]
        for arguments in bad_arguments:
            with self.subTest(arguments=arguments):
                self.assertEqual(server.handle(call(arguments))["error"]["code"], -32602)
        self.assertEqual(server.handle(call(good, name="lookup"))["error"]["code"], -32602)

    def test_a_missing_posting_is_a_tool_error_not_a_protocol_error(self):
        response = ready_server().handle(call({"board": "ashby/linear", "posting_key": "does-not-exist"}))
        self.assertNotIn("error", response)
        self.assertTrue(response["result"]["isError"])
        self.assertIn("No posting", response["result"]["content"][0]["text"])

    def test_the_value_matches_the_declared_source(self):
        # The evidence ledger: the tool's answer equals FILTER.md v0.1 recomputed on the saved posting.
        response = ready_server().handle(call({"board": SAVED.board, "posting_key": SAVED.key}))
        result = response["result"]
        self.assertFalse(result["isError"])
        expected = screen.score(SAVED)
        self.assertEqual(result["structuredContent"], expected)
        self.assertEqual(json.loads(result["content"][0]["text"]), expected)


if __name__ == "__main__":
    unittest.main()
