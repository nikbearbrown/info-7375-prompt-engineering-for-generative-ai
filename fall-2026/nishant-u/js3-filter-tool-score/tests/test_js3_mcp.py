"""The JS3 MCP tool server (mcp_server/server.py): lifecycle, error layers, the one tool, read-only, transcript.

Uses the real saved v2 run under out3/filter-run-v2/ (committed data). Transcripts go to a temp folder.
"""
import ast
import builtins
import datetime
import io
import json
import pathlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from mcp_server import server as srv

ROOT = Path(__file__).resolve().parents[1]
ACCEPTED = "greenhouse:faire:8806617002"     # in the v2 shortlist
REJECTED = "greenhouse:instacart:8237393"    # rejected at F1 in v2


def req(ident, method, params=None):
    m = {"jsonrpc": "2.0", "id": ident, "method": method}
    if params is not None:
        m["params"] = params
    return m


INIT = req(1, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                             "clientInfo": {"name": "unit-test", "version": "0"}})
READY = {"jsonrpc": "2.0", "method": "notifications/initialized"}


def call(ident, args, name="score_posting"):
    return req(ident, "tools/call", {"name": name, "arguments": args})


def ready_server():
    s = srv.Server()
    s.handle(INIT)
    s.handle(READY)
    return s


class Lifecycle(unittest.TestCase):
    def test_handshake(self):
        s = srv.Server()
        r = s.handle(INIT)
        self.assertEqual(r["id"], 1)
        self.assertEqual(r["result"]["protocolVersion"], "2025-06-18")
        self.assertIn("tools", r["result"]["capabilities"])
        self.assertEqual(r["result"]["serverInfo"]["name"], "js3-score-posting")
        self.assertTrue(s.initialized)
        self.assertFalse(s.ready)
        self.assertIsNone(s.handle(READY), "a notification never gets a response")
        self.assertTrue(s.ready)

    def test_unsupported_version_gets_the_server_version(self):
        r = srv.Server().handle(req(1, "initialize", {"protocolVersion": "1999-01-01"}))
        self.assertEqual(r["result"]["protocolVersion"], "2025-11-25")

    def test_calling_before_initialize_is_refused(self):
        s = srv.Server()
        for m in (req(2, "tools/list"), call(3, {"posting_id": ACCEPTED})):
            with self.subTest(method=m["method"]):
                r = s.handle(m)
                self.assertEqual(r["error"]["code"], -32000)
                self.assertNotIn("result", r)

    def test_calling_after_initialize_but_before_the_notification_is_refused(self):
        s = srv.Server()
        s.handle(INIT)
        self.assertEqual(s.handle(req(2, "tools/list"))["error"]["code"], -32000)

    def test_initialized_notification_before_initialize_does_nothing(self):
        s = srv.Server()
        self.assertIsNone(s.handle(READY))
        self.assertFalse(s.ready)


class Discovery(unittest.TestCase):
    def test_tools_list_declares_one_read_only_tool(self):
        tools = ready_server().handle(req(2, "tools/list"))["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        schema = tools[0]["inputSchema"]
        self.assertEqual(schema["required"], ["posting_id"])
        self.assertFalse(schema["additionalProperties"])
        self.assertTrue(tools[0]["annotations"]["readOnlyHint"])


class Calls(unittest.TestCase):
    def test_good_call_on_an_accepted_posting(self):
        r = ready_server().handle(call(2, {"posting_id": ACCEPTED}))["result"]
        self.assertFalse(r["isError"])
        out = r["structuredContent"]
        self.assertEqual(json.loads(r["content"][0]["text"]), out)
        self.assertEqual((out["verdict"], out["filter"]), ("accept", "FILTER.md v2"))
        self.assertEqual({c["claim"] for c in out["claims"]}, {"C1", "C2", "C3", "C4"})
        self.assertTrue(all(c["quote"] for c in out["claims"]))

    def test_good_call_on_a_rejected_posting_has_no_claims(self):
        out = ready_server().handle(call(2, {"posting_id": REJECTED}))["result"]["structuredContent"]
        self.assertEqual((out["verdict"], out["claims"]), ("reject", None))
        self.assertTrue(out["reason"].startswith("F1"))

    def test_unknown_posting_id_is_a_tool_error_not_a_protocol_error(self):
        r = ready_server().handle(call(2, {"posting_id": "greenhouse:faire:999"}))
        self.assertNotIn("error", r)
        self.assertTrue(r["result"]["isError"])

    def test_bad_params_are_32602(self):
        s = ready_server()
        for name, m in (("no arguments", req(2, "tools/call", {"name": "score_posting"})),
                        ("extra argument", call(3, {"posting_id": ACCEPTED, "path": "x"})),
                        ("non-string id", call(4, {"posting_id": 8806617002})),
                        ("arguments a list", req(5, "tools/call", {"name": "score_posting", "arguments": [ACCEPTED]})),
                        ("unknown tool", call(6, {"posting_id": ACCEPTED}, name="delete_posting")),
                        ("params not an object", req(7, "tools/call", ["score_posting"]))):
            with self.subTest(case=name):
                self.assertEqual(s.handle(m)["error"]["code"], -32602)

    def test_unknown_method_is_32601(self):
        self.assertEqual(ready_server().handle(req(2, "resources/list"))["error"]["code"], -32601)

    def test_invalid_request_is_32600(self):
        s = ready_server()
        for m in ({"id": 2, "method": "tools/list"}, {"jsonrpc": "1.0", "id": 3, "method": "tools/list"},
                  {"jsonrpc": "2.0", "id": 4}, [req(5, "tools/list")], "tools/list"):
            with self.subTest(message=m):
                self.assertEqual(s.handle(m)["error"]["code"], -32600)


class ReadOnly(unittest.TestCase):
    def test_path_like_posting_id_is_refused_and_nothing_is_read(self):
        s = ready_server()
        opened = []

        def record(*args, **kwargs):
            opened.append(args[:1])
            raise AssertionError("the server opened a file during a call")
        with mock.patch.object(builtins, "open", record), mock.patch.object(pathlib.Path, "open", record), \
                mock.patch.object(pathlib.Path, "read_text", record), mock.patch.object(pathlib.Path, "read_bytes", record):
            for pid in ("../../x", "..\\..\\x", "greenhouse:faire:../../x", "/etc/passwd", "C:\\Windows\\win.ini",
                        "greenhouse:faire:8806617002/../../x"):
                with self.subTest(pid=pid):
                    r = s.handle(call(2, {"posting_id": pid}))["result"]
                    self.assertTrue(r["isError"])
                    self.assertIn("Refused", r["content"][0]["text"])
        self.assertEqual(opened, [])

    def test_server_imports_nothing_that_can_reach_the_network_or_run_programs(self):
        tree = ast.parse((ROOT / "mcp_server" / "server.py").read_text(encoding="utf-8"))
        imported = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        imported |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        self.assertEqual(imported, {"datetime", "json", "os", "re", "sys", "pathlib"})
        self.assertNotIn("os.system", (ROOT / "mcp_server" / "server.py").read_text(encoding="utf-8"))


class StdioAndTranscript(unittest.TestCase):
    def run_lines(self, lines, client="unit-test"):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        fixed = datetime.datetime(2026, 11, 25, 12, 0, tzinfo=datetime.timezone.utc)
        t = srv.Transcript(Path(tmp.name) / "transcripts", clock=lambda: fixed)
        stdin = io.BytesIO("".join(l + "\n" for l in lines).encode("utf-8"))
        stdout = io.StringIO()
        srv.serve(stdin, stdout, transcript=t)
        return [json.loads(l) for l in stdout.getvalue().splitlines()], Path(tmp.name)

    def test_malformed_json_is_32700_with_null_id(self):
        out, _ = self.run_lines(["{not json"])
        self.assertEqual(out, [{"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}])

    def test_full_sequence_over_stdio_and_both_directions_are_logged(self):
        lines = ["{oops", json.dumps(INIT), json.dumps(READY), json.dumps(req(2, "tools/list")),
                 json.dumps(call(3, {"posting_id": ACCEPTED}))]
        out, tmp = self.run_lines(lines)
        self.assertEqual([o["id"] for o in out], [None, 1, 2, 3], "no response to the notification")
        files = list(tmp.rglob("*"))
        self.assertEqual([f.name for f in files if f.is_file()], ["2026-11-25-unit-test.jsonl"])
        log = [json.loads(l) for l in (tmp / "transcripts" / "2026-11-25-unit-test.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([r["dir"] for r in log], ["in", "out", "in", "out", "in", "in", "out", "in", "out"])
        self.assertEqual(log[0]["raw"], "{oops", "the malformed line before initialize is kept")
        self.assertTrue(all(r["ts"].startswith("2026-11-25T12:00:00") for r in log))

    def test_client_name_cannot_steer_the_transcript_path(self):
        evil = req(1, "initialize", {"protocolVersion": "2025-06-18", "clientInfo": {"name": "../../../evil\\x"}})
        _, tmp = self.run_lines([json.dumps(evil)])
        written = [f for f in tmp.rglob("*") if f.is_file()]
        self.assertEqual(len(written), 1)
        self.assertEqual(written[0].parent, tmp / "transcripts")
        self.assertNotIn("..", written[0].name)


if __name__ == "__main__":
    unittest.main()
