"""The tool server (Chapter 8): protocol shape, declared vs actual, and what a client is not entitled to."""
import io
import json
import os
import tempfile
import unittest

from js3 import mcp_server, store

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def session(*msgs, log=None):
    log = log or os.path.join(BASE, "transcripts", "test", "unit-test-session.jsonl")
    if os.path.exists(log):
        os.remove(log)
    inp = io.StringIO("".join((m if isinstance(m, str) else json.dumps(m)) + "\n" for m in msgs))
    out = io.StringIO()
    mcp_server.serve(inp, out, log_path=log)
    return [json.loads(l) for l in out.getvalue().splitlines()], log


INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}}
INITED = {"jsonrpc": "2.0", "method": "notifications/initialized"}


def call(mid, args, name="score_posting"):
    return {"jsonrpc": "2.0", "id": mid, "method": "tools/call", "params": {"name": name, "arguments": args}}


class Protocol(unittest.TestCase):
    def test_handshake_list_call(self):
        out, _ = session(INIT, INITED, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                         call(3, {"title": "Software Engineer", "location": "Boston, MA",
                                  "content": "Requirements: 2+ years of experience with Python and AWS. " * 8}))
        self.assertEqual([m["id"] for m in out], [1, 2, 3])  # the notification got no reply
        self.assertEqual(out[0]["result"]["protocolVersion"], "2025-06-18")
        tools = out[1]["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        self.assertTrue(tools[0]["annotations"]["readOnlyHint"])
        res = out[2]["result"]
        self.assertFalse(res["isError"])
        self.assertEqual(res["structuredContent"]["verdict"], "keep")
        self.assertIn("score", res["content"][0]["text"])

    def test_unknown_protocol_version_gets_the_newest_we_support(self):
        m = dict(INIT, params=dict(INIT["params"], protocolVersion="1999-01-01"))
        out, _ = session(m)
        self.assertEqual(out[0]["result"]["protocolVersion"], mcp_server.SUPPORTED_VERSIONS[0])

    def test_list_before_initialize_is_refused(self):
        out, _ = session({"jsonrpc": "2.0", "id": 9, "method": "tools/list"})
        self.assertEqual(out[0]["error"]["code"], -32002)

    def test_malformed_and_unknown(self):
        out, _ = session(INIT, "{not json", {"jsonrpc": "2.0", "id": 4, "method": "resources/list"}, {"id": 5})
        self.assertEqual(out[1]["error"]["code"], -32700)
        self.assertEqual(out[2]["error"]["code"], -32601)
        self.assertEqual(out[3]["error"]["code"], -32600)

    def test_transcript_has_both_directions_verbatim(self):
        out, log = session(INIT, INITED)
        with open(log, encoding="utf-8") as f:
            rows = [json.loads(l) for l in f]
        self.assertEqual([r["dir"] for r in rows], ["client->server", "server->client", "client->server"])
        self.assertEqual(json.loads(rows[0]["raw"]), INIT)


class NotEntitled(unittest.TestCase):
    """What a compatible client cannot get, however it asks."""

    def run1(self, args, name="score_posting"):
        out, _ = session(INIT, INITED, call(2, args, name))
        return out[-1]

    def test_no_file_path_from_a_request(self):
        r = self.run1({"posting_id": "../../../etc/passwd"})
        self.assertEqual(r["error"]["code"], -32602)

    def test_no_other_tools(self):
        for name in ("apply_to_job", "send_email", "fetch_url", "Bash"):
            self.assertEqual(self.run1({}, name)["error"]["code"], -32602, name)

    def test_no_extra_arguments(self):
        self.assertIn("unexpected", self.run1({"posting_id": "1", "url": "https://x"})["error"]["message"])

    def test_wrong_types_and_oversize(self):
        self.assertEqual(self.run1({"posting_id": 5})["error"]["code"], -32602)
        self.assertEqual(self.run1({"title": "x", "content": "a" * 50001})["error"]["code"], -32602)

    def test_declared_title_and_location_limits_are_enforced(self):  # found in the declared-vs-actual review
        self.assertIn("title longer", self.run1({"title": "t" * 301, "content": "c"})["error"]["message"])
        self.assertIn("location longer", self.run1({"title": "t", "location": "l" * 301, "content": "c"})["error"]["message"])

    def test_unknown_id_is_an_error_result_not_a_guess(self):
        r = self.run1({"posting_id": "999999999999"})
        self.assertTrue(r["result"]["isError"])
        self.assertIn("cannot tell", r["result"]["content"][0]["text"])

    def test_server_log_cannot_leave_the_folder(self):
        with self.assertRaises(store.WriteRefused):
            mcp_server.Server(log_path=os.path.join(tempfile.gettempdir(), "x.jsonl"))
        with self.assertRaises(store.WriteRefused):
            mcp_server.Server(log_path=os.path.join(BASE, "config", "x.jsonl"))

    def test_server_module_has_no_network_or_subprocess(self):
        with open(os.path.join(BASE, "js3", "mcp_server.py"), encoding="utf-8") as f:
            src = f.read()
        for bad in ("urllib", "socket", "subprocess", "http.client", "requests", "transport"):
            self.assertNotIn(f"import {bad}", src)
            self.assertNotIn(f"from .js2 import {bad}", src)


if __name__ == "__main__":
    unittest.main()
