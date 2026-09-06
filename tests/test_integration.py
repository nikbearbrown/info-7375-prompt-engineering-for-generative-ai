"""Offline contract tests; never contact Claude or consume API credits."""
import importlib.util
import io
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from coursekit.claude import payload, send

ROOT = Path(__file__).resolve().parents[1]


def lesson(slug):
    spec = importlib.util.spec_from_file_location(slug, ROOT / "lessons" / slug / "code/main.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TransportTests(unittest.TestCase):
    def test_request_shape(self):
        body = payload("hello", "claude-test-fixture")
        self.assertEqual(body["messages"][0]["role"], "user")
        self.assertIn("system", body)
        self.assertEqual(body["max_tokens"], 256)

    def test_requires_claude(self):
        with self.assertRaises(ValueError):
            payload("hello", "other-model")

    def test_budget(self):
        for value in [0, -1, 4097, True]:
            with self.assertRaises(ValueError):
                payload("hello", "claude-test-fixture", value)

    def test_offline_denied_before_key_access(self):
        with self.assertRaises(ValueError):
            send({"model":"claude-test-fixture"})

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_key(self):
        with self.assertRaises(ValueError):
            send({"model":"claude-test-fixture"}, live=True)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY":"fixture-not-a-secret"})
    def test_mock_transport_headers_and_timeout(self):
        def opener(req, timeout):
            self.assertEqual(req.full_url, "https://api.anthropic.com/v1/messages")
            self.assertEqual(req.get_header("Anthropic-version"), "2023-06-01")
            self.assertEqual(timeout, 30)
            self.assertEqual(json.loads(req.data)["model"], "claude-test-fixture")
            return io.BytesIO(b'{"content":[],"stop_reason":"end_turn"}')
        self.assertEqual(send(payload("hello", "claude-test-fixture"), live=True, opener=opener)["content"], [])

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY":"fixture-not-a-secret"})
    def test_http_error_is_sanitized(self):
        def opener(req, timeout):
            raise HTTPError(req.full_url, 429, "secret-body", {}, None)
        with self.assertRaisesRegex(RuntimeError, "Claude HTTP 429") as caught:
            send(payload("hello", "claude-test-fixture"), live=True, opener=opener)
        self.assertNotIn("secret-body", str(caught.exception))

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY":"fixture-not-a-secret"})
    def test_malformed_response(self):
        with self.assertRaises(ValueError):
            send(payload("hello", "claude-test-fixture"), live=True,
                 opener=lambda *a, **kw: io.BytesIO(b'{"content":4}'))


class ToolLoopTests(unittest.TestCase):
    def setUp(self):
        self.module = lesson("11-tool-use-and-verification")

    def test_multiple_results_and_history(self):
        content = [{"type":"tool_use","id":"a","name":"add","input":{"a":2,"b":3}},
                   {"type":"tool_use","id":"b","name":"unknown","input":{}}]
        calls = []
        def fake(body):
            calls.append(json.loads(json.dumps(body)))
            if len(calls) == 1:
                return {"stop_reason":"tool_use","content":content}
            return {"stop_reason":"end_turn","content":[{"type":"text","text":"5"}]}
        self.assertEqual(self.module.loop(fake, {"messages":[]})["status"], "finished")
        self.assertEqual(calls[1]["messages"][0]["content"], content)
        returned = calls[1]["messages"][1]
        self.assertEqual(returned["role"], "user")
        self.assertEqual([r["tool_use_id"] for r in returned["content"]], ["a","b"])
        self.assertTrue(returned["content"][1]["is_error"])

    def test_budget_stops_repeated_actions(self):
        response = {"stop_reason":"tool_use","content":[{"type":"tool_use","id":"x","name":"add","input":{"a":1,"b":2}}]}
        result = self.module.loop(lambda _: response, {"messages":[]}, 2)
        self.assertEqual(result["status"], "budget-exhausted")
        self.assertEqual(len(result["trace"]), 2)

    def test_duplicate_ids_rejected(self):
        block = {"type":"tool_use","id":"x","name":"add","input":{"a":1,"b":2}}
        with self.assertRaises(ValueError):
            self.module.results([block, block])

    def test_overflow_rejected(self):
        with self.assertRaises(ValueError):
            self.module.dispatch("add", {"a":1e308,"b":1e308})


class McpTests(unittest.TestCase):
    def test_full_fixture_lifecycle(self):
        server = lesson("08-mcp-from-scratch").Server()
        self.assertIn("result", server.handle({"jsonrpc":"2.0","id":1,"method":"initialize"}))
        server.handle({"jsonrpc":"2.0","method":"notifications/initialized"})
        response = server.handle({"jsonrpc":"2.0","id":2,"method":"tools/call",
                                  "params":{"name":"lookup","arguments":{"key":"office"}}})
        self.assertFalse(response["result"]["isError"])
        self.assertEqual(response["result"]["content"][0]["text"], "505A Dana Hall")


if __name__ == "__main__":
    unittest.main()
