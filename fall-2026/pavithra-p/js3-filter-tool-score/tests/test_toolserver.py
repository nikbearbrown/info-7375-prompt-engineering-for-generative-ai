"""The tool server (agent/toolserver.py): the protocol, the declared tool, and what it may touch.

It reads the real run saved on 2026-11-25; no request is made and no Claude call is made.
"""
import io
import json
import socket
import unittest
from unittest import mock

from agent import config, toolserver
from agent.policy import PolicyRefused

HELM = {"board": "ashby:ramp", "job_id": "d8925f84-562f-470c-a5bd-4f6c20009361"}


def call(server, method, params=None, mid=1):
    msg = {"jsonrpc": "2.0", "id": mid, "method": method}
    if params is not None:
        msg["params"] = params
    return server.handle(msg)


class Protocol(unittest.TestCase):
    def setUp(self):
        self.s = toolserver.Server()

    def test_initialize_echoes_a_supported_version(self):
        r = call(self.s, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {}})["result"]
        self.assertEqual(r["protocolVersion"], "2025-06-18")
        self.assertEqual(r["capabilities"], {"tools": {"listChanged": False}})

    def test_initialize_offers_its_latest_for_an_unknown_version(self):
        r = call(self.s, "initialize", {"protocolVersion": "1999-01-01"})["result"]
        self.assertEqual(r["protocolVersion"], toolserver.SUPPORTED_VERSIONS[0])

    def test_a_notification_gets_no_answer(self):
        self.assertIsNone(self.s.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))
        self.assertTrue(self.s.initialized)

    def test_tools_list_declares_one_read_only_tool(self):
        tools = call(self.s, "tools/list")["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        self.assertTrue(tools[0]["annotations"]["readOnlyHint"])
        self.assertFalse(tools[0]["annotations"]["openWorldHint"])
        self.assertIn("version 1.1", tools[0]["description"])  # read from the filter file it really uses

    def test_unknown_method_and_unknown_tool_are_errors(self):
        self.assertEqual(call(self.s, "resources/list")["error"]["code"], toolserver.METHOD_NOT_FOUND)
        self.assertEqual(call(self.s, "tools/call", {"name": "apply_to_job", "arguments": {}})["error"]["code"],
                         toolserver.INVALID_PARAMS)

    def test_params_that_are_not_an_object_are_refused_not_a_crash(self):
        out = io.StringIO()
        self.s.serve(io.StringIO('{"jsonrpc":"2.0","id":1,"method":"tools/call","params":[1,2]}\n'
                                 '{"jsonrpc":"2.0","id":2,"method":"ping"}\n'), out)
        replies = [json.loads(line) for line in out.getvalue().splitlines()]
        self.assertEqual(replies[0]["error"]["code"], toolserver.INVALID_PARAMS)
        self.assertEqual(replies[1]["result"], {})  # still serving after the bad request

    def test_an_unexpected_error_is_reported_and_the_session_goes_on(self):
        out = io.StringIO()
        with mock.patch.object(self.s, "handle", side_effect=[RuntimeError("boom"), {"jsonrpc": "2.0", "id": 2, "result": {}}]):
            self.s.serve(io.StringIO('{"jsonrpc":"2.0","id":1,"method":"ping"}\n{"jsonrpc":"2.0","id":2,"method":"ping"}\n'), out)
        replies = [json.loads(line) for line in out.getvalue().splitlines()]
        self.assertEqual((replies[0]["id"], replies[0]["error"]["code"]), (1, toolserver.INTERNAL_ERROR))
        self.assertEqual(replies[1]["result"], {})

    def test_declared_version_is_the_version_used(self):
        declared = call(self.s, "tools/list")["result"]["tools"][0]["description"]
        used = call(self.s, "tools/call", {"name": "score_posting", "arguments": HELM})["result"]["structuredContent"]
        self.assertIn(f"version {used['filter_version']}", declared)

    def test_parse_error_through_the_stdio_loop(self):
        out = io.StringIO()
        self.s.serve(io.StringIO("{not json\n"), out)
        self.assertEqual(json.loads(out.getvalue())["error"]["code"], toolserver.PARSE_ERROR)


class Tool(unittest.TestCase):
    def setUp(self):
        self.s = toolserver.Server()

    def test_scores_a_saved_posting_like_the_filter(self):
        r = call(self.s, "tools/call", {"name": "score_posting", "arguments": HELM})["result"]
        self.assertFalse(r["isError"])
        # v1.1: role 1 + Python, SQL; "HELM" no longer counts as the skill Helm (change D)
        self.assertEqual((r["structuredContent"]["verdict"], r["structuredContent"]["score"]), ("reject", 3))
        self.assertEqual(r["structuredContent"]["filter_version"], "1.1")

    def test_undeclared_argument_or_board_is_refused(self):
        for args in ({**HELM, "path": "/etc/passwd"}, {"board": "../../secrets", "job_id": "1"}, {"board": "ashby:ramp"}):
            self.assertEqual(call(self.s, "tools/call", {"name": "score_posting", "arguments": args})["error"]["code"],
                             toolserver.INVALID_PARAMS, args)

    def test_declared_boards_come_from_config_and_a_failed_board_says_cannot_tell(self):
        tool = call(self.s, "tools/list")["result"]["tools"][0]
        configured = [f"{b['system']}:{b['name']}" for b in config.load("boards")]
        self.assertEqual(tool["inputSchema"]["properties"]["board"]["enum"], configured)
        r = call(self.s, "tools/call", {"name": "score_posting", "arguments": {"board": "lever:no-such-board", "job_id": "1"}})
        self.assertTrue(r["result"]["isError"])
        self.assertIn("I cannot tell", r["result"]["content"][0]["text"])

    def test_unknown_job_is_a_tool_error_not_a_guess(self):
        r = call(self.s, "tools/call", {"name": "score_posting", "arguments": {"board": "ashby:ramp", "job_id": "nope"}})
        self.assertTrue(r["result"]["isError"])
        self.assertIn("nothing was guessed", r["result"]["content"][0]["text"])

    def test_makes_no_network_connection(self):
        with mock.patch.object(socket, "socket", side_effect=AssertionError("network used")):
            r = call(toolserver.Server(), "tools/call", {"name": "score_posting", "arguments": HELM})
        self.assertFalse(r["result"]["isError"])


class Writes(unittest.TestCase):
    def test_transcript_outside_its_folder_is_refused(self):
        with self.assertRaises(PolicyRefused):
            toolserver.Server(transcript=config.ROOT.parent / "outside.jsonl").log("in", "{}")

    def test_transcript_has_both_directions_and_nothing_else_is_written(self):
        path = config.ROOT / "transcripts" / "test-run.jsonl"
        before = {p: p.stat().st_mtime for p in config.ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        try:
            s = toolserver.Server(transcript=path)
            lines = [{"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                     {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "score_posting", "arguments": HELM}}]
            s.serve(io.StringIO("".join(json.dumps(m) + "\n" for m in lines)), io.StringIO())
            logged = [json.loads(line)["dir"] for line in path.read_text().splitlines()]
            self.assertEqual(logged, ["in", "out", "in", "out"])
            after = {p: p.stat().st_mtime for p in config.ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
            changed = {p for p in after if before.get(p) != after[p]}
            self.assertEqual(changed, {path})
        finally:
            path.unlink(missing_ok=True)
            if path.parent.exists() and not any(path.parent.iterdir()):
                path.parent.rmdir()


if __name__ == "__main__":
    unittest.main()
