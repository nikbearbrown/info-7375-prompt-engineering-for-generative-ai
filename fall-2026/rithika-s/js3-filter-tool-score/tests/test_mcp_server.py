"""mcp.server on a CONSTRUCTED corpus: protocol, tool, transcript, safety.

No network, no real client, no `claude`.
"""

import ast
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from mcp import server as srv
from tests.shortlist_fixtures import ROOT, make_root

SERVER_SOURCE = ROOT / "mcp" / "server.py"
FORBIDDEN_MODULES = ("socket", "urllib", "http", "subprocess")


def req(rid, method, params=None):
    msg = {"jsonrpc": "2.0", "id": rid, "method": method}
    if params is not None:
        msg["params"] = params
    return msg


def call(rid, args, name="score_posting"):
    return req(rid, "tools/call", {"name": name, "arguments": args})


class ServerTestBase(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_root(Path(self._tmp.name) / "project")
        self.config = self.root / "config" / "filter-v1.1.json"
        self.server = srv.Server(self.config, self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def init(self):
        reply = self.server.handle(req(1, "initialize",
                                       {"protocolVersion": "2025-06-18"}))
        self.assertIn("result", reply)
        self.assertIsNone(self.server.handle(
            {"jsonrpc": "2.0", "method": "notifications/initialized"}))


class ProtocolTests(ServerTestBase):

    def test_requests_before_initialize_are_errors(self):
        for method in ("ping", "tools/list", "tools/call", "nope"):
            with self.subTest(method=method):
                reply = self.server.handle(req(5, method))
                self.assertEqual(reply["error"]["code"],
                                 srv.NOT_INITIALIZED)
                self.assertEqual(reply["id"], 5)

    def test_initialize_echoes_supported_version_else_default(self):
        reply = self.server.handle(req(1, "initialize",
                                       {"protocolVersion": "2024-11-05"}))
        result = reply["result"]
        self.assertEqual(result["protocolVersion"], "2024-11-05")
        self.assertEqual(result["serverInfo"]["name"], "priya-filter")
        self.assertEqual(result["capabilities"], {"tools": {}})
        other = srv.Server(self.config, self.root)
        reply = other.handle(req(1, "initialize",
                                 {"protocolVersion": "1999-01-01"}))
        self.assertEqual(reply["result"]["protocolVersion"],
                         srv.DEFAULT_PROTOCOL_VERSION)

    def test_second_initialize_and_missing_version(self):
        reply = self.server.handle(req(1, "initialize", {}))
        self.assertEqual(reply["error"]["code"], srv.INVALID_PARAMS)
        self.init()
        reply = self.server.handle(req(2, "initialize",
                                       {"protocolVersion": "2025-06-18"}))
        self.assertEqual(reply["error"]["code"], srv.INVALID_REQUEST)

    def test_ping_unknown_method_and_notifications(self):
        self.init()
        self.assertEqual(self.server.handle(req(2, "ping"))["result"], {})
        reply = self.server.handle(req(3, "resources/list"))
        self.assertEqual(reply["error"]["code"], srv.METHOD_NOT_FOUND)
        self.assertIsNone(self.server.handle(
            {"jsonrpc": "2.0", "method": "notifications/cancelled"}))

    def test_malformed_messages(self):
        self.assertEqual(self.server.handle([req(1, "ping")])["error"]
                         ["code"], srv.INVALID_REQUEST)
        self.assertEqual(self.server.handle({"id": 1, "method": "ping"})
                         ["error"]["code"], srv.INVALID_REQUEST)
        self.assertEqual(self.server.handle(
            {"jsonrpc": "2.0", "id": True, "method": "ping"})["error"]
            ["code"], srv.INVALID_REQUEST)


class ToolTests(ServerTestBase):

    def setUp(self):
        super().setUp()
        self.init()

    def test_tools_list_has_exactly_one_strict_tool(self):
        tools = self.server.handle(req(2, "tools/list"))["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        schema = tools[0]["inputSchema"]
        self.assertEqual(schema["required"], ["board", "id"])
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(schema["properties"]["board"]["enum"],
                         ["constructed"])
        self.assertEqual(schema["properties"]["id"]["type"], "string")
        description = tools[0]["description"].lower()
        self.assertIn("read-only", description)
        self.assertIn("frozen corpus", description)

    def test_real_board_enum_is_the_three_corpus_boards(self):
        self.assertEqual(srv.corpus_boards(ROOT),
                         ["databricks", "openai", "scaleai"])

    def test_valid_call_returns_filter_result(self):
        reply = self.server.handle(call(3, {"board": "constructed",
                                            "id": "100000"}))
        result = reply["result"]
        self.assertIs(result["isError"], False)
        self.assertEqual(result["content"][0]["type"], "text")
        payload = json.loads(result["content"][0]["text"])
        for key in ("board", "id", "title", "url", "decision", "score",
                    "rules_fired", "matched_spans"):
            self.assertIn(key, payload)
        self.assertEqual(payload["decision"], "kept")
        self.assertEqual(payload["score"], 5)
        self.assertEqual(payload["rules_fired"], ["R1", "R2"])
        spans = {m["span"] for m in payload["matched_spans"]}
        self.assertEqual(spans, {"ML Engineer", "PyTorch", "Spark"})
        self.assertEqual(payload["config_version"], "1.1")

    def test_unknown_posting_is_tool_error(self):
        reply = self.server.handle(call(4, {"board": "constructed",
                                            "id": "999"}))
        self.assertIs(reply["result"]["isError"], True)
        self.assertNotIn("error", reply)

    def test_bad_arguments_are_invalid_params(self):
        cases = [
            {"board": "constructed", "id": "100000",
             "path": "../../etc/passwd"},
            {"board": "constructed"},
            {"board": "../out/raw", "id": "100000"},
            {"board": "constructed", "id": 100000},
            {"board": "constructed", "id": ""},
        ]
        for args in cases:
            with self.subTest(args=args):
                reply = self.server.handle(call(5, args))
                self.assertEqual(reply["error"]["code"], srv.INVALID_PARAMS)
        reply = self.server.handle(req(6, "tools/call", {
            "name": "score_posting", "arguments": "board=constructed"}))
        self.assertEqual(reply["error"]["code"], srv.INVALID_PARAMS)

    def test_unknown_tool_is_invalid_params(self):
        reply = self.server.handle(call(7, {"board": "constructed",
                                            "id": "100000"},
                                        name="delete_posting"))
        self.assertEqual(reply["error"]["code"], srv.INVALID_PARAMS)

    def test_corpus_hash_mismatch_is_tool_error(self):
        raw = next((self.root / "out" / "raw").glob("*.json"))
        raw.write_bytes(raw.read_bytes() + b" ")
        reply = self.server.handle(call(8, {"board": "constructed",
                                            "id": "100000"}))
        self.assertIs(reply["result"]["isError"], True)
        self.assertIn("corpus", reply["result"]["content"][0]["text"])


class StreamTests(ServerTestBase):

    def run_main(self, lines):
        stdin = io.StringIO("".join(json.dumps(m) + "\n" if not
                                    isinstance(m, str) else m + "\n"
                                    for m in lines))
        stdout, stderr = io.StringIO(), io.StringIO()
        transcripts = Path(self._tmp.name) / "transcripts"
        code = srv.main(["--config", str(self.config), "--root",
                         str(self.root), "--transcripts", str(transcripts)],
                        stdin=stdin, stdout=stdout, stderr=stderr)
        self.assertEqual(code, 0)
        files = list(transcripts.glob("server-*.jsonl"))
        self.assertEqual(len(files), 1)
        self.assertRegex(files[0].name, r"^server-\d{8}T\d{6}Z\.jsonl$")
        return stdout.getvalue(), stderr.getvalue(), files[0]

    def test_stdout_is_only_json_rpc_and_transcript_has_both_directions(
            self):
        out, err, path = self.run_main([
            req(1, "initialize", {"protocolVersion": "2025-06-18"}),
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            req(2, "tools/list"),
            call(3, {"board": "constructed", "id": "100001"}),
            "{not json",
        ])
        replies = [json.loads(line) for line in out.splitlines()]
        self.assertEqual(len(replies), 4)  # no reply to the notification
        self.assertTrue(all(r["jsonrpc"] == "2.0" for r in replies))
        self.assertEqual(replies[-1]["error"]["code"], srv.PARSE_ERROR)
        self.assertIn("priya-filter", err)
        entries = [json.loads(line) for line in
                   path.read_text("utf-8").splitlines()]
        self.assertEqual([e["direction"] for e in entries],
                         ["in", "out", "in", "in", "out", "in", "out",
                          "in", "out"])
        self.assertTrue(all(e["time_utc"].endswith("+00:00")
                            for e in entries))
        self.assertEqual(entries[-2]["raw"], "{not json")

    def test_server_writes_only_its_transcript(self):
        before = {p for p in self.root.rglob("*")}
        _, _, path = self.run_main([req(1, "ping")])
        after = {p for p in self.root.rglob("*")}
        self.assertEqual(after - before, set())
        self.assertFalse(path.is_relative_to(self.root))


class SafetyTests(unittest.TestCase):

    def test_source_has_no_network_or_process_calls(self):
        source = SERVER_SOURCE.read_text("utf-8")
        imported = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertFalse(imported & set(FORBIDDEN_MODULES), imported)
        # plain text scan of the whole file, comments and docstrings too
        for word in ("socket", "urllib", "http", "subprocess", "os.system",
                     "popen", "__import__", "importlib"):
            with self.subTest(word=word):
                self.assertNotIn(word, source.lower())

    def test_runtime_imports_exclude_network_and_process_modules(self):
        probe = ("import sys, mcp.server; print(','.join(sorted("
                 "m for m in sys.modules if m.split('.')[0] in "
                 f"{FORBIDDEN_MODULES!r})))")
        out = subprocess.run([sys.executable, "-c", probe], cwd=ROOT,
                             capture_output=True, text=True, check=True)
        self.assertEqual(out.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
