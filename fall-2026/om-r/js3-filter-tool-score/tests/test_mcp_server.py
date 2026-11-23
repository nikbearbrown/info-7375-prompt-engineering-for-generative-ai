"""MCP-shaped tool server (Chapter 8), written BEFORE js3/mcp_server.py existed.

Wire format targeted: MCP 2025-06-18, stdio transport = newline-delimited
JSON-RPC 2.0, UTF-8, no embedded newlines, nothing but MCP messages on
stdout. Lifecycle: initialize -> notifications/initialized -> tools/list ->
tools/call. Errors (2025-06-18 split): unknown tool / invalid arguments ->
JSON-RPC -32602; execution failures -> result with isError: true.

Interface fixed here:
    Server(client_factory, log_dir, write_root) with handle_line(raw: str)
        -> response line (str, no trailing newline) or None for notifications.
        Every inbound raw line and every outbound line is appended verbatim
        to server.wire_log before it is processed / sent.
    python3 -m js3.mcp_server  - the same over real stdin/stdout.
No network here: Claude is the FakeClient from tests/test_shortlist.py.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from js3 import minischema
from tests.test_shortlist import FakeClient, claims_json

ROOT = Path(__file__).resolve().parent.parent
RELEVANT = {"board": "gitlab", "id": 8704363002}   # C03, filter v1.1.0 relevant
QUOTE = "Build and improve agentic flows and their reusable parts with LangChain and LangGraph, including the Flow Registry."


def mcp():
    import js3.mcp_server
    return js3.mcp_server


def a_rejected():
    from js3.shortlist import RUN_REPORT
    from js3.postings import load_run
    from js3 import filter_v110
    _, ps, _ = load_run(RUN_REPORT, ROOT)
    for p in sorted(ps, key=lambda p: (p["board"], str(p["id"]))):
        if filter_v110.classify(p)["bucket"] == "rejected":
            return {"board": p["board"], "id": p["id"]}


def req(i, method, params=None):
    m = {"jsonrpc": "2.0", "id": i, "method": method}
    if params is not None:
        m["params"] = params
    return json.dumps(m)


INIT = req(1, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                             "clientInfo": {"name": "test", "version": "0"}})
INITIALIZED = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.fake = FakeClient(claims_json(claims=[{"claim": "LangChain agent work matches key_skills.",
                                                    "quote": QUOTE, "contradicted_by": None}]))
        self.s = mcp().Server(client_factory=lambda: self.fake, log_dir=self.tmp, write_root=self.tmp)

    def send(self, line):
        out = self.s.handle_line(line)
        return None if out is None else json.loads(out)

    def ready(self):
        self.send(INIT)
        self.assertIsNone(self.send(INITIALIZED))

    def call(self, args, i=9, name="score_posting"):
        return self.send(req(i, "tools/call", {"name": name, "arguments": args}))


class Lifecycle(Base):
    def test_initialize_result_shape(self):
        r = self.send(INIT)
        self.assertEqual(r["id"], 1)
        self.assertEqual(r["result"]["protocolVersion"], "2025-06-18")
        self.assertIn("tools", r["result"]["capabilities"])
        self.assertEqual(r["result"]["serverInfo"]["name"], "js3-score")

    def test_unsupported_version_gets_servers_version(self):
        r = self.send(req(1, "initialize", {"protocolVersion": "1999-01-01", "capabilities": {},
                                            "clientInfo": {"name": "t", "version": "0"}}))
        self.assertEqual(r["result"]["protocolVersion"], "2025-06-18")

    def test_requests_before_initialize_are_refused_except_ping(self):
        self.assertIn("error", self.send(req(2, "tools/list")))
        self.assertEqual(self.send(req(3, "ping"))["result"], {})

    def test_notification_gets_no_response(self):
        self.send(INIT)
        self.assertIsNone(self.s.handle_line(INITIALIZED))


class ToolsList(Base):
    def test_exactly_one_tool_with_schemas(self):
        self.ready()
        tools = self.send(req(2, "tools/list"))["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        for k in ("description", "inputSchema", "outputSchema", "annotations"):
            self.assertIn(k, tools[0])
        self.assertEqual(tools[0]["inputSchema"]["type"], "object")


class ToolsCall(Base):
    def test_relevant_posting_is_judged_and_matches_output_schema(self):
        self.ready()
        r = self.call(RELEVANT)["result"]
        self.assertFalse(r["isError"])
        sc = r["structuredContent"]
        self.assertEqual(minischema.errors(sc, mcp().OUTPUT_SCHEMA), [])
        self.assertEqual(sc["filter"]["bucket"], "relevant")
        self.assertEqual(sc["judgment"]["verdict"], "relevant")
        self.assertEqual(sc["judgment"]["claims"][0]["label"], "supported")
        self.assertEqual(json.loads(r["content"][0]["text"]), sc)   # serialized JSON block (spec SHOULD)
        self.assertTrue(Path(sc["judgment"]["transcript"]).resolve().is_relative_to(self.tmp.resolve()))

    def test_rejected_posting_never_calls_claude(self):
        self.ready()
        sc = self.call(a_rejected())["result"]["structuredContent"]
        self.assertEqual(sc["filter"]["bucket"], "rejected")
        self.assertIsNone(sc["judgment"])
        self.fake.messages.with_raw_response.create.assert_not_called()

    def test_adhoc_title_and_content(self):
        self.ready()
        r = self.call({"title": "AI Engineer", "content": "Build LLM agents in Python. " + QUOTE})["result"]
        self.assertEqual(r["structuredContent"]["posting"]["source"], "adhoc")
        self.assertEqual(minischema.errors(r["structuredContent"], mcp().OUTPUT_SCHEMA), [])

    def test_unknown_tool_and_invalid_arguments_are_protocol_errors(self):
        self.ready()
        self.assertEqual(self.call(RELEVANT, name="nope")["error"]["code"], -32602)
        for bad in [{}, {"board": "gitlab"}, {**RELEVANT, "title": "x", "content": "y"},
                    {**RELEVANT, "extra": 1}, {"board": "monster", "id": 1}]:
            with self.subTest(bad=bad):
                self.assertEqual(self.call(bad)["error"]["code"], -32602)

    def test_unknown_posting_is_execution_error(self):
        self.ready()
        r = self.call({"board": "gitlab", "id": 1})["result"]
        self.assertTrue(r["isError"])

    def test_missing_key_is_execution_error_not_a_verdict(self):
        from js3.shortlist import MissingAPIKey
        def no_key():
            raise MissingAPIKey("ANTHROPIC_API_KEY is not set")
        s = mcp().Server(client_factory=no_key, log_dir=self.tmp, write_root=self.tmp)
        s.handle_line(INIT); s.handle_line(INITIALIZED)
        r = json.loads(s.handle_line(req(5, "tools/call", {"name": "score_posting", "arguments": RELEVANT})))
        self.assertTrue(r["result"]["isError"])
        self.assertNotIn("structuredContent", r["result"])


class InputSchemaModesAreExclusive(Base):
    """Found in the self-evaluation (2026-11-22), BEFORE this test existed:
    INPUT_SCHEMA's oneOf branches only listed required keys, so
    {board, id, title} and {board, id, content} validated and the extra key
    was silently ignored, contradicting the tool description ("Not both")."""

    def test_schema_rejects_board_id_plus_title_or_content(self):
        for bad in [{"board": "gitlab", "id": 8396674002, "title": "ignored"},
                    {"board": "gitlab", "id": 8396674002, "content": "ignored"}]:
            with self.subTest(bad=bad):
                self.assertNotEqual(minischema.errors(bad, mcp().INPUT_SCHEMA), [])

    def test_server_returns_invalid_arguments_for_them(self):
        self.ready()
        for bad in [{"board": "gitlab", "id": 8396674002, "title": "ignored"},
                    {"board": "gitlab", "id": 8396674002, "content": "ignored"}]:
            with self.subTest(bad=bad):
                self.assertEqual(self.call(bad)["error"]["code"], -32602)


class JsonRpc(Base):
    def test_parse_error_invalid_request_unknown_method(self):
        self.ready()
        r = self.send("{not json")
        self.assertEqual((r["error"]["code"], r["id"]), (-32700, None))
        self.assertEqual(self.send("[" + req(2, "ping") + "]")["error"]["code"], -32600)   # no batches
        self.assertEqual(self.send(json.dumps({"jsonrpc": "2.0", "id": None, "method": "ping"}))["error"]["code"], -32600)
        self.assertEqual(self.send(json.dumps({"jsonrpc": "1.0", "id": 4, "method": "ping"}))["error"]["code"], -32600)
        self.assertEqual(self.send(req(3, "resources/list"))["error"]["code"], -32601)


class WireLogAndWrites(Base):
    def test_every_line_logged_verbatim_both_directions(self):
        sent = [INIT, INITIALIZED, req(2, "tools/list"), "{not json"]
        got = [self.s.handle_line(l) for l in sent]
        log = [json.loads(l) for l in Path(self.s.wire_log).read_text().splitlines()]
        self.assertEqual([e["raw"] for e in log if e["dir"] == "client->server"], sent)
        self.assertEqual([e["raw"] for e in log if e["dir"] == "server->client"], [g for g in got if g is not None])
        for g in got:
            if g is not None:
                self.assertNotIn("\n", g)

    def test_writes_outside_write_root_are_refused(self):
        with self.assertRaises(PermissionError):
            self.s._append(Path(tempfile.mkdtemp()) / "x.jsonl", "x")


class OverRealStdio(unittest.TestCase):
    def test_subprocess_session(self):
        tmp = tempfile.mkdtemp()
        env = {**os.environ, "ANTHROPIC_API_KEY": "", "JS3_MCP_LOG_DIR": tmp}
        lines = [INIT, INITIALIZED, req(2, "tools/list"),
                 req(3, "tools/call", {"name": "score_posting", "arguments": a_rejected()})]
        p = subprocess.run([sys.executable, "-m", "js3.mcp_server"], input="\n".join(lines) + "\n",
                           capture_output=True, text=True, cwd=ROOT, env=env, timeout=60)
        out = [json.loads(l) for l in p.stdout.splitlines()]
        self.assertEqual([o["id"] for o in out], [1, 2, 3])        # stdout carries only MCP responses
        self.assertEqual(out[2]["result"]["structuredContent"]["filter"]["bucket"], "rejected")
        log = [json.loads(l) for f in Path(tmp).glob("server_*.jsonl") for l in f.read_text().splitlines()]
        self.assertEqual([e["raw"] for e in log if e["dir"] == "client->server"], lines)
        self.assertEqual([e["raw"] for e in log if e["dir"] == "server->client"], p.stdout.splitlines())


if __name__ == "__main__":
    unittest.main()
