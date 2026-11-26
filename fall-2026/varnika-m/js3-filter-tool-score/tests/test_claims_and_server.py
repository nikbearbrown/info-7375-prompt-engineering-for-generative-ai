"""The evidence rules (FILTER.md section 2), the loader (section 3) and the tool server.

Constructed postings only, except where a test loads the saved 2026-11-10 data to check the hashes.
"""

import gzip
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from js3.claims import answer, label_claims
from js3.filter import evaluate
from js3.load import FOLDER, SOURCES, SourceChanged, load
from js3.mcp_server import TOOL, Server
from tests.test_filter import RESUME, posting


def claims_for(p):
    return {c["text"]: c for c in label_claims(p, evaluate(p, RESUME))}


class EvidenceRules(unittest.TestCase):
    def test_wf4_no_years_is_insufficient_and_the_answer_is_cannot_tell(self):
        p = posting(body="<li>Experience with Python and AWS</li>")
        claims = claims_for(p)
        self.assertEqual(evaluate(p, RESUME)["outcome"], "keep")  # the filter keeps it...
        self.assertEqual(claims["It asks for 3 years or fewer"]["label"], "insufficient")
        self.assertEqual(answer(list(claims.values()))["answer"], "I cannot tell")  # ...the evidence cannot say it fits

    def test_years_with_a_quote_are_supported(self):
        claim = claims_for(posting())["It asks for 3 years or fewer"]
        self.assertEqual(claim["label"], "supported")
        self.assertIn("2+ years", claim["quote"])

    def test_more_years_contradict(self):
        p = posting(body="<li>Python and AWS</li><li>Preferred: 5+ years</li>")
        claims = claims_for(p)
        self.assertEqual(claims["It asks for 3 years or fewer"]["label"], "contradicted")
        self.assertEqual(answer(list(claims.values()))["answer"], "does not fit")

    def test_relevance_is_not_entailment_a_listed_word_is_not_an_ask(self):
        p = posting(body="<li>2+ years building services</li><li>Experience with Python</li>"
                         "<li>Technologies we use: Kafka, Kubernetes</li>")
        claims = claims_for(p)
        self.assertEqual(claims["It asks for Python"]["label"], "supported")
        self.assertEqual(claims["It asks for Kafka"]["label"], "insufficient")

    def test_a_nice_to_have_skill_is_not_supported(self):
        claim = claims_for(posting(body="<li>2+ years with Python</li><li>AWS is a plus</li>"))["It asks for AWS"]
        self.assertEqual(claim["label"], "insufficient")

    def test_every_claim_label_is_one_of_three(self):
        for claim in claims_for(posting()).values():
            self.assertIn(claim["label"], ("supported", "contradicted", "insufficient"))


class Sources(unittest.TestCase):
    def test_the_saved_data_is_what_js2_recorded(self):
        postings, not_checked = load()
        self.assertEqual((len(postings), not_checked), (1014, []))

    def copy(self):
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, True)
        (folder / "data").mkdir()
        for _, _, relative, _ in SOURCES.values():
            shutil.copy(FOLDER / relative, folder / relative)
        return folder

    def test_a_missing_board_is_not_checked_not_empty(self):
        folder = self.copy()
        (folder / SOURCES["ashby"][2]).unlink()
        postings, not_checked = load(folder)
        self.assertEqual(not_checked, ["ashby/linear"])
        self.assertEqual(len(postings), 1014 - 33)

    def test_changed_bytes_stop_the_run(self):
        folder = self.copy()
        path = folder / SOURCES["ashby"][2]
        path.write_bytes(gzip.compress(gzip.decompress(path.read_bytes()) + b" "))
        with self.assertRaises(SourceChanged):
            load(folder)


class ToolServer(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir, True)
        self.server = Server(self.dir / "t.jsonl")

    def call(self, method, params=None, mid=1):
        message = {"jsonrpc": "2.0", "id": mid, "method": method}
        if params is not None:
            message["params"] = params
        return self.server.handle(message)

    def test_initialize_agrees_a_version_and_declares_tools_only(self):
        reply = self.call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}})
        self.assertEqual(reply["result"]["protocolVersion"], "2025-06-18")
        self.assertEqual(reply["result"]["capabilities"], {"tools": {"listChanged": False}})
        unknown = self.call("initialize", {"protocolVersion": "1999-01-01"})
        self.assertEqual(unknown["result"]["protocolVersion"], "2025-11-25")

    def test_one_read_only_tool(self):
        tools = self.call("tools/list")["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        self.assertTrue(tools[0]["annotations"]["readOnlyHint"])
        self.assertFalse(tools[0]["annotations"]["openWorldHint"])

    def test_a_tool_it_does_not_offer_is_an_error(self):
        reply = self.call("tools/call", {"name": "send_email", "arguments": {"to": "x"}})
        self.assertEqual(reply["error"]["code"], -32602)

    def test_extra_or_wrong_arguments_are_refused(self):
        for arguments in ({}, {"posting_id": 5}, {"posting_id": "x", "path": "/etc/passwd"}, {"posting_id": "x" * 201}):
            self.assertEqual(self.call("tools/call", {"name": "score_posting", "arguments": arguments})["error"]["code"],
                             -32602, arguments)

    def test_an_unknown_posting_is_a_tool_error_not_a_crash(self):
        result = self.call("tools/call", {"name": "score_posting", "arguments": {"posting_id": "nope"}})["result"]
        self.assertTrue(result["isError"])

    def test_a_real_posting_comes_back_with_claims_and_an_answer(self):
        key = load()[0][0]["key"]
        result = self.call("tools/call", {"name": "score_posting", "arguments": {"posting_id": key}})["result"]
        body = json.loads(result["content"][0]["text"])
        self.assertEqual(body["posting_id"], key)
        self.assertIn(body["answer"]["answer"], ("I cannot tell", "does not fit",
                                                 "fits by the evidence rules (the decision is mine)"))

    def test_notifications_get_no_reply_and_unknown_methods_an_error(self):
        self.assertIsNone(self.server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))
        self.assertEqual(self.call("resources/list")["error"]["code"], -32601)

    def test_the_transcript_keeps_both_directions(self):
        import io
        out = io.StringIO()
        self.server.serve(io.StringIO('{"jsonrpc":"2.0","id":1,"method":"ping"}\nnot json\n'), out)
        lines = [json.loads(l) for l in (self.dir / "t.jsonl").read_text().splitlines()]
        self.assertEqual([l["dir"] for l in lines], ["client->server", "server->client"] * 2)
        self.assertEqual(json.loads(out.getvalue().splitlines()[1])["error"]["code"], -32700)

    def test_the_server_writes_nothing_but_its_transcript(self):
        source = (FOLDER / "js3" / "mcp_server.py").read_text()
        self.assertEqual(source.count("open("), 1)  # only in log()
        for banned in ("urllib", "socket", "subprocess", "requests", "http.client", "os.remove", "unlink", "shutil"):
            self.assertNotIn(banned, source)
        self.assertEqual(TOOL["inputSchema"]["additionalProperties"], False)


if __name__ == "__main__":
    unittest.main()
