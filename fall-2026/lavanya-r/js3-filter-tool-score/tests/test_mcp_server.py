"""The MCP server, driven as a subprocess over stdio, the way a client sees it.
Offline: it reads only the frozen corpus in runs/."""

import ast
import json
import os
import pathlib
import subprocess
import sys
import unittest

JS3 = pathlib.Path(__file__).resolve().parent.parent
SERVER = JS3 / "mcp" / "server.py"


def converse(messages):
    """Send messages (dicts) to a fresh server, one per line; return the
    parsed replies in order."""
    stdin = "".join(json.dumps(m) + "\n" for m in messages)
    p = subprocess.run([sys.executable, "-B", str(SERVER)], input=stdin,
                       capture_output=True, text=True, timeout=60,
                       cwd=str(JS3))
    return [json.loads(l) for l in p.stdout.splitlines() if l.strip()]


INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                   "clientInfo": {"name": "test", "version": "0"}}}
INITED = {"jsonrpc": "2.0", "method": "notifications/initialized"}


def call(id_, name, arguments):
    return {"jsonrpc": "2.0", "id": id_, "method": "tools/call",
            "params": {"name": name, "arguments": arguments}}


class TestProtocol(unittest.TestCase):
    def test_initialize_shape(self):
        [r] = converse([INIT])
        res = r["result"]
        self.assertEqual(r["id"], 1)
        self.assertEqual(res["protocolVersion"], "2025-06-18")
        self.assertEqual(res["serverInfo"]["name"], "js3-postings")
        self.assertIn("tools", res["capabilities"])

    def test_unknown_protocol_version_gets_servers_own(self):
        init = json.loads(json.dumps(INIT))
        init["params"]["protocolVersion"] = "1999-01-01"
        [r] = converse([init])
        self.assertEqual(r["result"]["protocolVersion"], "2025-06-18")

    def test_notification_gets_no_reply(self):
        replies = converse([INIT, INITED,
                            {"jsonrpc": "2.0", "id": 2, "method": "ping"}])
        self.assertEqual([r["id"] for r in replies], [1, 2])

    def test_tools_list_schema(self):
        [_, r] = converse([INIT, {"jsonrpc": "2.0", "id": 2,
                                  "method": "tools/list"}])
        [tool] = r["result"]["tools"]
        self.assertEqual(tool["name"], "search_postings")
        schema = tool["inputSchema"]
        self.assertEqual(schema["required"], ["query"])
        self.assertFalse(schema["additionalProperties"])
        self.assertTrue(tool["annotations"]["readOnlyHint"])
        self.assertFalse(tool["annotations"]["openWorldHint"])

    def test_unknown_method(self):
        [_, r] = converse([INIT, {"jsonrpc": "2.0", "id": 2,
                                  "method": "resources/list"}])
        self.assertEqual(r["error"]["code"], -32601)

    def test_parse_error(self):
        p = subprocess.run([sys.executable, "-B", str(SERVER)],
                           input="{not json\n", capture_output=True,
                           text=True, timeout=30)
        self.assertEqual(json.loads(p.stdout)["error"]["code"], -32700)


class TestSearchTool(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.replies = converse([
            INIT, INITED,
            call(2, "search_postings", {"query": "MLflow",
                                        "board": "greenhouse/databricks",
                                        "limit": 5}),
            call(3, "search_postings", {"query": "MLflow", "limit": 99}),
            call(4, "search_postings", {}),
            call(5, "search_postings", {"query": "x", "path": "/etc"}),
            call(6, "no_such_tool", {}),
            call(7, "search_postings", {"query": "ml"}),
            call(8, "search_postings", {"query": "MLflow",
                                        "board": "nope/nope"}),
        ])
        cls.by_id = {r["id"]: r for r in cls.replies}

    def test_search_results(self):
        res = self.by_id[2]["result"]
        self.assertFalse(res["isError"])
        out = res["structuredContent"]
        self.assertGreater(out["count_total"], 0)
        self.assertLessEqual(len(out["results"]), 5)
        for hit in out["results"]:
            self.assertTrue(hit["key"].startswith("greenhouse/databricks/"))
            self.assertTrue(hit["matched_in"])
        self.assertEqual(json.loads(res["content"][0]["text"]), out)

    def test_bad_params_are_errors(self):
        for i in (3, 4, 5, 8):
            self.assertEqual(self.by_id[i]["error"]["code"], -32602, i)

    def test_unknown_tool_is_error_result(self):
        self.assertTrue(self.by_id[6]["result"]["isError"])

    def test_whole_word_not_substring(self):
        # "ml" must not match inside "HTML" or "MLflow"
        for hit in self.by_id[7]["result"]["structuredContent"]["results"]:
            self.assertNotIn("html", hit["title"].lower().split())


class TestSideEffects(unittest.TestCase):
    def snapshot(self):
        out = {}
        for root, dirs, files in os.walk(JS3):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
            for f in files:
                p = pathlib.Path(root, f)
                out[str(p)] = p.stat().st_mtime_ns
        return out

    def test_server_writes_no_files(self):
        before = self.snapshot()
        converse([INIT, INITED, call(2, "search_postings",
                                     {"query": "Python", "limit": 20})])
        self.assertEqual(self.snapshot(), before)

    def test_no_network_imports(self):
        tree = ast.parse(SERVER.read_text())
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module.split(".")[0])
        for banned in ("socket", "urllib", "http", "requests", "ssl"):
            self.assertNotIn(banned, names)

    def test_corpus_dir_is_inside_js3(self):
        src = SERVER.read_text()
        self.assertIn('JS3 / "runs" / "2026-11-24T220432Z-live"', src)


if __name__ == "__main__":
    unittest.main()
