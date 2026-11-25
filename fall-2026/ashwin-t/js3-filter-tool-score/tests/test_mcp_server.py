"""The tool server's protocol behavior and its exposure limits (offline, stub tool)."""
import ast
import io
import json
import shutil
import sys
import unittest
from pathlib import Path

from jobfilter import mcp_server
from jobfilter.mcp_server import FOLDER, Server, Tool, Transcript

SCHEMA = {"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"],
          "additionalProperties": False}
TMP = FOLDER / "tests" / "tmp" / "mcp"


def stub(args):
    if args["key"] == "boom":
        raise RuntimeError("tool failed")
    if args["key"] == "missing":
        return {"_is_error": True, "error": "unknown posting key"}
    return {"key": args["key"], "score": 3}


def make(transcript=None):
    return Server([Tool("score_posting", "stub", SCHEMA, stub)], transcript)


def rpc(server, method, params=None, mid=1):
    msg = {"jsonrpc": "2.0", "id": mid, "method": method}
    if params is not None:
        msg["params"] = params
    return json.loads(server.handle_line(json.dumps(msg)))


class Handshake(unittest.TestCase):
    def test_initialize_echoes_a_supported_version(self):
        r = rpc(make(), "initialize", {"protocolVersion": "2025-06-18", "capabilities": {}})["result"]
        self.assertEqual(r["protocolVersion"], "2025-06-18")
        self.assertEqual(r["capabilities"], {"tools": {"listChanged": False}})

    def test_initialize_unknown_version_gets_servers_latest(self):
        r = rpc(make(), "initialize", {"protocolVersion": "1999-01-01"})["result"]
        self.assertEqual(r["protocolVersion"], mcp_server.SUPPORTED_VERSIONS[0])

    def test_notification_gets_no_reply(self):
        s = make()
        self.assertIsNone(s.handle_line('{"jsonrpc":"2.0","method":"notifications/initialized"}'))
        self.assertTrue(s.initialized)

    def test_tools_list_declares_exactly_one_read_only_tool(self):
        tools = rpc(make(), "tools/list", {})["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        self.assertEqual(tools[0]["annotations"]["readOnlyHint"], True)
        self.assertEqual(tools[0]["annotations"]["openWorldHint"], False)


class Calls(unittest.TestCase):
    def test_call_returns_text_content(self):
        r = rpc(make(), "tools/call", {"name": "score_posting", "arguments": {"key": "a/b/1"}})["result"]
        self.assertFalse(r["isError"])
        self.assertEqual(json.loads(r["content"][0]["text"]), {"key": "a/b/1", "score": 3})

    def test_unknown_tool_is_a_protocol_error(self):
        r = rpc(make(), "tools/call", {"name": "apply_to_job", "arguments": {}})
        self.assertEqual(r["error"]["code"], mcp_server.INVALID_PARAMS)

    def test_extra_or_wrong_type_arguments_are_refused(self):
        s = make()
        self.assertIn("error", rpc(s, "tools/call", {"name": "score_posting", "arguments": {"key": "x", "path": "/etc"}}))
        self.assertIn("error", rpc(s, "tools/call", {"name": "score_posting", "arguments": {"key": 7}}))
        self.assertIn("error", rpc(s, "tools/call", {"name": "score_posting", "arguments": {}}))

    def test_tool_failure_is_a_tool_result_not_a_crash(self):
        s = make()
        r = rpc(s, "tools/call", {"name": "score_posting", "arguments": {"key": "boom"}})["result"]
        self.assertTrue(r["isError"])
        r = rpc(s, "tools/call", {"name": "score_posting", "arguments": {"key": "missing"}})["result"]
        self.assertTrue(r["isError"])

    def test_unknown_method_and_garbage(self):
        s = make()
        self.assertEqual(rpc(s, "resources/list", {})["error"]["code"], mcp_server.METHOD_NOT_FOUND)
        self.assertEqual(json.loads(s.handle_line("{not json"))["error"]["code"], mcp_server.PARSE_ERROR)
        self.assertEqual(json.loads(s.handle_line('{"id":3,"method":"ping"}'))["error"]["code"],
                         mcp_server.INVALID_REQUEST)

    def test_stdio_loop_writes_only_json_rpc_lines(self):
        out = io.StringIO()
        make().serve(io.StringIO('{"jsonrpc":"2.0","id":1,"method":"ping"}\n\n'
                                 '{"jsonrpc":"2.0","method":"notifications/initialized"}\n'), out)
        self.assertEqual([json.loads(l) for l in out.getvalue().splitlines()],
                         [{"jsonrpc": "2.0", "id": 1, "result": {}}])


class Exposure(unittest.TestCase):
    def setUp(self):
        shutil.rmtree(TMP, ignore_errors=True)

    def test_transcript_records_both_directions_verbatim(self):
        path = TMP / "t.jsonl"
        s = make(Transcript(path))
        line = '{"jsonrpc":"2.0","id":9,"method":"ping"}'
        reply = s.handle_line(line)
        recs = [json.loads(l) for l in path.read_text().splitlines()]
        self.assertEqual([(r["dir"], r["line"]) for r in recs],
                         [("client->server", line), ("server->client", reply)])

    def test_transcript_outside_the_folder_is_refused(self):
        with self.assertRaises(ValueError):
            Transcript(Path("/tmp/js3-escape.jsonl"))
        with self.assertRaises(ValueError):
            Transcript(FOLDER / ".." / "escape.jsonl")

    def test_server_modules_import_no_network_or_process_code(self):
        banned = {"socket", "urllib", "http", "subprocess", "shutil", "smtplib", "ftplib", "requests"}
        for name in ("mcp_server.py", "serve_tool.py"):
            path = FOLDER / "jobfilter" / name
            if not path.exists():
                continue
            tree = ast.parse(path.read_text())
            imported = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported |= {a.name.split(".")[0] for a in node.names}
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
            self.assertFalse(imported & banned, f"{name} imports {imported & banned}")


if __name__ == "__main__":
    unittest.main()
