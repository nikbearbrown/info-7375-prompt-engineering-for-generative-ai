"""Tests for the from-scratch MCP server (earlybird/mcp_server.py). Written BEFORE the server.
The server speaks JSON-RPC 2.0 over stdio, one JSON object per line: initialize, tools/list, tools/call.
Run: python -m unittest discover -s tests"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class Server:
    """Starts the real server as a subprocess and talks to it over stdio."""

    def __init__(self, log=None, extra_env=None):
        env = dict(os.environ, PYTHONIOENCODING="utf-8", **(extra_env or {}))
        if log:
            env["EARLYBIRD_MCP_LOG"] = str(log)
        self.p = subprocess.Popen([sys.executable, "-m", "earlybird.mcp_server"], cwd=ROOT, env=env,
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.n = 0

    def send_raw(self, line):
        self.p.stdin.write(line.encode("utf-8") + b"\n")
        self.p.stdin.flush()

    def read(self):
        return json.loads(self.p.stdout.readline().decode("utf-8"))

    def request(self, method, params=None):
        self.n += 1
        msg = {"jsonrpc": "2.0", "id": self.n, "method": method}
        if params is not None:
            msg["params"] = params
        self.send_raw(json.dumps(msg))
        return self.read()

    def notify(self, method):
        self.send_raw(json.dumps({"jsonrpc": "2.0", "method": method}))

    def close(self):
        if not self.p.stdin.closed:
            self.p.stdin.close()
        self.p.wait(timeout=10)
        self.p.stdout.close()
        self.p.stderr.close()

    def handshake(self):
        r = self.request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                        "clientInfo": {"name": "test-client", "version": "0"}})
        self.notify("notifications/initialized")
        return r


def a_real_posting():
    sys.path.insert(0, str(ROOT))
    from earlybird import boards
    f = next((ROOT / "data/snapshot-2026-11-01").glob("greenhouse_stripe.json"))
    p = boards.parse("greenhouse", f.read_text(encoding="utf-8"))[0]
    return "greenhouse_stripe", p["id"]


class Handshake(unittest.TestCase):
    def setUp(self):
        self.s = Server()

    def tearDown(self):
        self.s.close()

    def test_initialize_declares_name_version_and_only_tools(self):
        r = self.s.handshake()
        self.assertEqual(r["jsonrpc"], "2.0")
        self.assertEqual(r["id"], 1)
        res = r["result"]
        self.assertEqual(res["protocolVersion"], "2025-06-18")
        self.assertEqual(res["serverInfo"]["name"], "earlybird-score")
        self.assertEqual(list(res["capabilities"]), ["tools"])  # no resources, prompts or logging claimed

    def test_unknown_protocol_version_gets_the_servers_own(self):
        r = self.s.request("initialize", {"protocolVersion": "1999-01-01", "capabilities": {},
                                          "clientInfo": {"name": "t", "version": "0"}})
        self.assertIn(r["result"]["protocolVersion"], {"2025-06-18", "2025-03-26", "2024-11-05"})

    def test_notification_gets_no_reply(self):
        self.s.handshake()
        r = self.s.request("ping")  # the next line read must be ping's reply, not a reply to the notification
        self.assertEqual(r["id"], 2)
        self.assertEqual(r["result"], {})


class ToolList(unittest.TestCase):
    def setUp(self):
        self.s = Server()
        self.s.handshake()

    def tearDown(self):
        self.s.close()

    def test_exactly_one_read_only_tool(self):
        tools = self.s.request("tools/list")["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        t = tools[0]
        self.assertTrue(t["annotations"]["readOnlyHint"])
        self.assertFalse(t["annotations"]["openWorldHint"])
        self.assertEqual(t["inputSchema"]["required"], ["posting_id"])
        self.assertEqual(t["inputSchema"]["additionalProperties"], False)

    def test_no_declared_tool_can_send_or_write(self):
        names = [t["name"] for t in self.s.request("tools/list")["result"]["tools"]]
        for name in names:
            for word in ("send", "email", "apply", "write", "delete", "post_", "message"):
                self.assertNotIn(word, name)


class CallTool(unittest.TestCase):
    def setUp(self):
        self.s = Server()
        self.s.handshake()

    def tearDown(self):
        self.s.close()

    def call(self, args, name="score_posting"):
        return self.s.request("tools/call", {"name": name, "arguments": args})

    def test_scores_a_real_posting_with_the_filter_and_the_claims(self):
        board, pid = a_real_posting()
        r = self.call({"posting_id": pid, "board": board})["result"]
        self.assertFalse(r["isError"])
        body = json.loads(r["content"][0]["text"])
        self.assertEqual(body["posting_id"], pid)
        self.assertIn(body["verdict"], {"relevant", "not_relevant", "cannot_tell"})
        self.assertIn("justification", body)
        self.assertIn("claims", body)
        self.assertEqual(body["filter_version"], "v2")

    def test_matches_the_filter_run_on_the_same_posting(self):
        rows = json.loads((ROOT / "results/filter-v2c-r1.json").read_text(encoding="utf-8"))
        for row in (next(x for x in rows if x["verdict"] == "relevant"),
                    next(x for x in rows if x["failed_check"] == "R5")):
            r = self.call({"posting_id": row["id"], "board": row["board"]})["result"]
            body = json.loads(r["content"][0]["text"])
            self.assertEqual((body["verdict"], body["failed_check"]), (row["verdict"], row["failed_check"]))

    def test_unknown_posting_is_a_tool_error_not_a_crash(self):
        r = self.call({"posting_id": "no-such-id"})["result"]
        self.assertTrue(r["isError"])
        self.assertIn("not found", r["content"][0]["text"])

    def test_path_traversal_is_refused(self):
        for bad in ("../../../etc/passwd", "..\\..\\x", "a/b", "id\x00x"):
            r = self.call({"posting_id": bad})["result"]
            self.assertTrue(r["isError"], bad)

    def test_board_must_be_one_of_the_snapshot_boards(self):
        r = self.call({"posting_id": "1", "board": "../secrets"})["result"]
        self.assertTrue(r["isError"])

    def test_missing_or_wrong_type_argument(self):
        self.assertTrue(self.call({})["result"]["isError"])
        self.assertTrue(self.call({"posting_id": 123})["result"]["isError"])

    def test_extra_arguments_are_refused(self):
        board, pid = a_real_posting()
        self.assertTrue(self.call({"posting_id": pid, "board": board, "cmd": "x"})["result"]["isError"])

    def test_unknown_tool_is_a_protocol_error(self):
        r = self.call({}, name="send_email")
        self.assertEqual(r["error"]["code"], -32602)


class Protocol(unittest.TestCase):
    def setUp(self):
        self.s = Server()

    def tearDown(self):
        self.s.close()

    def test_unknown_method(self):
        self.s.handshake()
        self.assertEqual(self.s.request("resources/list")["error"]["code"], -32601)

    def test_malformed_json_is_a_parse_error_and_the_server_survives(self):
        self.s.send_raw("{not json")
        self.assertEqual(self.s.read()["error"]["code"], -32700)
        self.assertEqual(self.s.request("ping")["result"], {})

    def test_stdout_carries_only_json_lines(self):
        self.s.handshake()
        self.s.request("tools/list")
        self.s.p.stdin.close()
        out = self.s.p.stdout.read().decode("utf-8")
        for line in out.splitlines():
            json.loads(line)


class Log(unittest.TestCase):
    def test_log_records_both_directions(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "log.jsonl"
            s = Server(log=log)
            s.handshake()
            s.request("tools/list")
            s.close()
            events = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()]
            self.assertEqual({e["dir"] for e in events}, {"client->server", "server->client"})
            self.assertGreaterEqual(len(events), 5)  # initialize, reply, initialized, tools/list, reply


class NetworkGuard(unittest.TestCase):
    """Found by evaluating my own server: the first guard patched connect() only, and connect_ex() got past it."""

    CODE = "\n".join([
        "import socket",
        "from earlybird import mcp_server as m",
        "srv = socket.socket(); srv.bind(('127.0.0.1', 0)); srv.listen(1); port = srv.getsockname()[1]",
        "m.disable_network()",
        "out = []",
        "for name, fn in (('connect', lambda s: s.connect(('127.0.0.1', port))),",
        "                 ('connect_ex', lambda s: s.connect_ex(('127.0.0.1', port)) == 0),",
        "                 ('create_connection', lambda s: socket.create_connection(('127.0.0.1', port)))):",
        "    try:",
        "        out.append(name + ':' + ('CONNECTED' if fn(socket.socket()) else 'refused'))",
        "    except OSError:",
        "        out.append(name + ':refused')",
        "print(' '.join(out))",
    ])

    def test_every_connect_path_is_refused(self):
        r = subprocess.run([sys.executable, "-c", self.CODE], cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertEqual(r.stdout.strip(), "connect:refused connect_ex:refused create_connection:refused", r.stderr)


class ResultVariant(unittest.TestCase):
    """The one change measured in REPORT-one-change.md: put each claim's statement in the tool result.
    Default (A) leaves it out, as the server did when Claude Code read it; EARLYBIRD_INCLUDE_STATEMENT=1 (B) adds it."""

    def claims_for(self, extra_env):
        board, pid = a_real_posting()
        s = Server(extra_env=extra_env)
        try:
            s.handshake()
            r = s.request("tools/call", {"name": "score_posting", "arguments": {"posting_id": pid, "board": board}})
            return json.loads(r["result"]["content"][0]["text"])["claims"]
        finally:
            s.close()

    def test_default_has_no_statement(self):
        for c in self.claims_for(None):
            self.assertNotIn("statement", c)

    def test_variant_b_adds_the_statement_and_changes_nothing_else(self):
        a, b = self.claims_for(None), self.claims_for({"EARLYBIRD_INCLUDE_STATEMENT": "1"})
        self.assertEqual(len(a), len(b))
        for ca, cb in zip(a, b):
            self.assertTrue(cb["statement"])
            self.assertEqual({k: v for k, v in cb.items() if k != "statement"}, ca)


if __name__ == "__main__":
    unittest.main()
