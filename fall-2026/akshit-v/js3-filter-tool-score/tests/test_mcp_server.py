"""What agent3.mcp_server declares versus what it does, checked in-process on the real corpus."""
import json
import unittest

from agent3 import filter as flt, mcp_server as ms


def req(i, method, params=None):
    m = {"jsonrpc": "2.0", "id": i, "method": method}
    if params is not None:
        m["params"] = params
    return m


def call(i, args):
    return req(i, "tools/call", {"name": "score_posting", "arguments": args})


class Server(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = ms.Session(flt.V1_0, "unittest")
        cls.s.log = lambda *a: None          # tests write no transcript
        cls.kept = next(pid for pid, p in cls.s.postings.items() if flt.apply(p)["verdict"] == "keep")

    def setUp(self):
        self.s.initialized_by_client = False

    def init(self):
        r = self.s.handle(req(1, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {}}))
        self.assertEqual(r["result"]["protocolVersion"], "2025-06-18")
        self.assertIsNone(self.s.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_tools_refused_before_initialize_but_discover_falls_through(self):
        self.assertEqual(self.s.handle(call(0, {"posting_id": self.kept}))["error"]["code"], -32002)
        self.assertEqual(self.s.handle(req(0, "server/discover", {}))["error"]["code"], -32601)

    def test_unknown_protocol_version_gets_servers_latest(self):
        r = self.s.handle(req(1, "initialize", {"protocolVersion": "1999-01-01"}))
        self.assertEqual(r["result"]["protocolVersion"], ms.SUPPORTED_PROTOCOLS[0])

    def test_declared_schema_is_enforced(self):
        self.init()
        tool = self.s.handle(req(2, "tools/list"))["result"]["tools"][0]
        self.assertFalse(tool["inputSchema"]["additionalProperties"])
        self.assertTrue(tool["annotations"]["readOnlyHint"])
        for bad in ({"posting_id": self.kept, "extra": 1}, {"posting_id": "../../data/x.json"}, {"posting_id": 5}, {}):
            self.assertTrue(self.s.handle(call(3, bad))["result"]["isError"], bad)

    def test_score_matches_the_filter_and_is_idempotent(self):
        self.init()
        a = self.s.handle(call(4, {"posting_id": self.kept}))["result"]
        b = self.s.handle(call(5, {"posting_id": self.kept}))["result"]
        self.assertEqual(a, b)
        self.assertEqual(a["structuredContent"]["score"], flt.apply(self.s.postings[self.kept])["score"])
        self.assertEqual(json.loads(a["content"][0]["text"]), a["structuredContent"])

    def test_missing_board_is_cannot_tell_and_unknown_id_is_an_error_not_a_no(self):
        self.init()
        r = self.s.handle(call(6, {"posting_id": "greenhouse:no-such-board-js2:1"}))["result"]
        self.assertEqual(r["structuredContent"]["verdict"], "cannot_tell")
        r = self.s.handle(call(7, {"posting_id": "greenhouse:figma:999"}))["result"]
        self.assertTrue(r["isError"])
        self.assertNotIn("structuredContent", r)

    def test_protocol_errors(self):
        self.init()
        self.assertEqual(self.s.handle(req(8, "resources/list"))["error"]["code"], -32601)
        self.assertEqual(self.s.handle(req(9, "tools/call", {"name": "apply_to_job"}))["error"]["code"], -32602)
        self.assertEqual(self.s.handle({"id": 10})["error"]["code"], -32600)


if __name__ == "__main__":
    unittest.main()
