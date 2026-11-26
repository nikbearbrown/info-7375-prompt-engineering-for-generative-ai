"""The MCP server (js3/mcp_server.py): what it declares, what it does, and what a client is not
entitled to. Written by Claude Code on 2026-11-25 AFTER the server code (not test-first; FRICTIONAL.md
says so). The no-network and write-location checks run the server in a separate process."""
import io
import json
import pathlib
import subprocess
import sys
import unittest

from js3 import claims, corpus, filtering, mcp_server

HERE = pathlib.Path(__file__).resolve().parent.parent
KEPT = "klaviyo:7792539003"


def talk(server, *messages):
    out = io.StringIO()
    server.serve(io.StringIO("".join((m if isinstance(m, str) else json.dumps(m)) + "\n" for m in messages)), out)
    return [json.loads(line) for line in out.getvalue().splitlines()]


def req(mid, method, params=None):
    m = {"jsonrpc": "2.0", "id": mid, "method": method}
    if params is not None:
        m["params"] = params
    return m


class Protocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = mcp_server.Server(log_dir=None)

    def test_initialize_echoes_a_supported_version(self):
        (r,) = talk(self.s, req(1, "initialize", {"protocolVersion": "2025-03-26", "capabilities": {}}))
        self.assertEqual(r["result"]["protocolVersion"], "2025-03-26")
        self.assertEqual(r["result"]["capabilities"], {"tools": {"listChanged": False}})

    def test_initialize_offers_its_latest_for_an_unknown_version(self):
        """Claude Code 2.1.331 asked for 2025-11-25 on 2026-11-25 (transcripts/server/)."""
        (r,) = talk(self.s, req(0, "initialize", {"protocolVersion": "2025-11-25"}))
        self.assertEqual(r["result"]["protocolVersion"], "2025-06-18")

    def test_a_notification_gets_no_reply(self):
        self.assertEqual(talk(self.s, {"jsonrpc": "2.0", "method": "notifications/initialized"}), [])

    def test_unknown_method_parse_error_and_batch(self):
        r1, r2, r3 = talk(self.s, req(5, "server/discover"), "{not json", [req(6, "ping")])
        self.assertEqual(r1["error"]["code"], -32601)
        self.assertEqual((r2["id"], r2["error"]["code"]), (None, -32700))
        self.assertEqual(r3["error"]["code"], -32600)

    def test_ping(self):
        (r,) = talk(self.s, req(9, "ping"))
        self.assertEqual(r["result"], {})


class Declared(unittest.TestCase):
    def test_exactly_one_read_only_tool(self):
        (r,) = talk(mcp_server.Server(None), req(2, "tools/list", {}))
        tools = r["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        a = tools[0]["annotations"]
        self.assertEqual((a["readOnlyHint"], a["destructiveHint"], a["openWorldHint"]), (True, False, False))
        self.assertEqual(tools[0]["inputSchema"]["required"], ["posting_key"])
        self.assertFalse(tools[0]["inputSchema"]["additionalProperties"])


class Actual(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = mcp_server.Server(log_dir=None)
        cls.posting = {p["key"]: p for p in corpus.load()}[KEPT]

    def call(self, args, name="score_posting"):
        (r,) = talk(self.s, req(3, "tools/call", {"name": name, "arguments": args}))
        return r

    def test_score_a_kept_posting(self):
        res = self.call({"posting_key": KEPT})["result"]
        self.assertFalse(res["isError"])
        out = res["structuredContent"]
        self.assertEqual(json.loads(res["content"][0]["text"]), out)
        self.assertEqual(out["verdict"], "Relevant")
        self.assertEqual(out["justification"]["answer"], "I cannot tell")
        rec = {"rules": [{"n": r["rule"], "evidence": r["quotes"]} for r in out["rules"]]}
        self.assertEqual(filtering.verify_quotes(rec, self.posting), [], "every quote is in the posting")
        self.assertEqual(claims.verify(out["justification"], self.posting), [])

    def test_unknown_posting_is_a_tool_error_not_a_fetch(self):
        res = self.call({"posting_key": "greenhouse:99999"})["result"]
        self.assertTrue(res["isError"])
        self.assertIn("does not fetch", res["content"][0]["text"])

    def test_a_path_is_not_a_key(self):
        for bad in ("../../etc/passwd", "/etc/passwd", "klaviyo:1;rm -rf /", ""):
            self.assertTrue(self.call({"posting_key": bad})["result"]["isError"], bad)

    def test_extra_or_missing_arguments(self):
        self.assertTrue(self.call({"posting_key": KEPT, "url": "https://example.com"})["result"]["isError"])
        self.assertTrue(self.call({})["result"]["isError"])

    def test_unknown_tool(self):
        self.assertEqual(self.call({"url": "https://example.com"}, name="fetch_url")["error"]["code"], -32602)

    def test_contact_details_are_never_returned(self):
        text = self.call({"posting_key": KEPT})["result"]["content"][0]["text"]
        self.assertNotIn("alex.morgan@example.com", text)
        self.assertNotIn("555-0142", text)


class Boundaries(unittest.TestCase):
    def test_no_network_module_is_loaded(self):
        # Python starts with -I -S, so nothing from the environment (a sitecustomize, a .pth file,
        # PYTHONPATH) loads first, and only what importing the server adds is counted. Before this
        # change the test failed on any Python whose start-up imports socket, although the server
        # imports none of these (evidence/network-module-test-*).
        mods = ("socket", "ssl", "http.client", "urllib.request", "subprocess")
        code = (f"import sys; sys.path.insert(0, {str(HERE)!r}); mods = {mods!r}; "
                "before = {m for m in mods if m in sys.modules}; "
                "from js3 import mcp_server; mcp_server.Server(None); "
                "print(sorted(m for m in mods if m in sys.modules and m not in before))")
        out = subprocess.run([sys.executable, "-I", "-S", "-c", code], capture_output=True, text=True, cwd=HERE,
                             check=True)
        self.assertEqual(out.stdout.strip(), "[]")

    def test_the_transcript_folder_must_be_inside_transcripts(self):
        with self.assertRaises(SystemExit):
            mcp_server.Server(log_dir=HERE.parent)

    def test_a_full_session_over_real_stdio(self):
        msgs = [req(1, "initialize", {"protocolVersion": "2025-06-18"}),
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                req(2, "tools/list", {}), req(3, "tools/call", {"name": "score_posting", "arguments": {"posting_key": KEPT}})]
        out = subprocess.run([sys.executable, "-m", "js3", "serve", "--no-log"], input="".join(json.dumps(m) + "\n" for m in msgs),
                             capture_output=True, text=True, cwd=HERE, timeout=60)
        replies = [json.loads(l) for l in out.stdout.splitlines()]
        self.assertEqual([r["id"] for r in replies], [1, 2, 3])
        self.assertEqual(out.stderr, "")


if __name__ == "__main__":
    unittest.main()
