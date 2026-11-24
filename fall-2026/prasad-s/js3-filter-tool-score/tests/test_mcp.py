"""Tests for tools/mcp_server.py and tools/mcp_client.py. Constructed corpus and vault, temporary folders only.

The corpus, vault and persona are tests/test_filter_run_v2.py's fixture: two
constructed boards, one posting in the final's set and one in JS3's held-out
set. The server runs in-process on byte streams for the protocol tests, and
as a real subprocess for the stdout and end-to-end tests. Nothing here reads
the real corpus or vault, registers anything with Claude Code, or uses the
network.
"""

import ast
import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import test_filter_run_v2 as v2t
from support import JS1 as PROJECT

from tools import filter_run, mcp_client, mcp_server

GH, AB = v2t.GH, v2t.AB
FINAL_ID, V2_ID = v2t.SEALED[0][1], v2t.SEALED[1][1]
NOW = datetime(2026, 11, 20, 10, 0, 0, tzinfo=timezone.utc)
TRANSCRIPT = "transcripts/mcp_server_2026-11-20T100000Z.jsonl"
UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$")
BOOT = (
    "import json, sys\n"
    "from pathlib import Path\n"
    f"sys.path.insert(0, {str(PROJECT)!r})\n"
    "from tools import mcp_server\n"
    "{patch}"
    "root, corpus = Path(sys.argv[1]), [tuple(entry) for entry in json.loads(sys.argv[2])]\n"
    "sys.exit(mcp_server.main([], root=root, corpus=corpus))\n"
)
NOISY = (  # a judge that prints: the prints must land on stderr, never on stdout
    "from agent import filter as _filter\n"
    "_real = _filter.judge\n"
    "def _noisy(*args, **kwargs):\n"
    "    print('STRAY-PRINT')\n"
    "    sys.stdout.write('STRAY-WRITE\\n')\n"
    "    return _real(*args, **kwargs)\n"
    "_filter.judge = _noisy\n"
)


def rpc(request_id, method, params=None):
    return json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method,
                       **({} if params is None else {"params": params})})


def notification(method):
    return json.dumps({"jsonrpc": "2.0", "method": method})


def call(request_id, arguments, name="score_posting"):
    return rpc(request_id, "tools/call", {"name": name, "arguments": arguments})


def init(request_id=1, version="2025-11-25"):
    return rpc(request_id, "initialize", {"protocolVersion": version, "capabilities": {},
                                          "clientInfo": {"name": "constructed-test-client", "version": "0"}})


def server_command(root, corpus, patch=""):
    return [sys.executable, "-c", BOOT.replace("{patch}", patch), str(root), json.dumps(corpus)]


def records(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()]


class Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.fx = v2t.Fixture(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def converse(self, *lines, raw=None, now=NOW):
        """Run the server in-process on these lines; (parsed responses, raw output lines)."""
        data = raw if raw is not None else "".join(line + "\n" for line in lines).encode("utf-8")
        stdout, stderr = io.BytesIO(), io.StringIO()
        code = mcp_server.main([], root=self.fx.root, corpus=self.fx.corpus, stdin=io.BytesIO(data), stdout=stdout,
                               stderr=stderr, now=now)
        self.assertEqual(code, 0, stderr.getvalue())
        out_lines = stdout.getvalue().decode("ascii").splitlines()
        return [json.loads(line) for line in out_lines], out_lines

    def tool_result(self, *arguments_list):
        """(isError, text) for each call, in one session."""
        responses, _ = self.converse(init(), *[call(n, a) for n, a in enumerate(arguments_list, start=2)])
        results = [r["result"] for r in responses[1:]]
        for result in results:
            self.assertEqual(len(result["content"]), 1)
            self.assertEqual(result["content"][0]["type"], "text")
        return [(r["isError"], r["content"][0]["text"]) for r in results]


# ---------------------------------------------------------------- lifecycle

class TestInitialize(Case):
    def test_the_requested_version_when_it_is_implemented(self):
        for version in ("2025-11-25", "2025-06-18", "2024-11-05"):
            with self.subTest(version=version):
                (response,), _ = self.converse(init(version=version))
                self.assertEqual(response["result"]["protocolVersion"], version)

    def test_otherwise_the_newest_implemented(self):
        for version in ("2025-03-26", "2026-07-28", "1999-01-01"):
            with self.subTest(version=version):
                (response,), _ = self.converse(init(version=version))
                self.assertEqual(response["result"]["protocolVersion"], "2025-11-25")

    def test_the_whole_answer(self):
        (response,), _ = self.converse(init(7))
        self.assertEqual(response, {"jsonrpc": "2.0", "id": 7, "result": {
            "protocolVersion": "2025-11-25", "capabilities": {"tools": {}},
            "serverInfo": {"name": "js3-filter-tool-score", "version": "1.0.0"}}})
        self.assertEqual(mcp_server.SUPPORTED_VERSIONS, ("2025-11-25", "2025-06-18", "2024-11-05"))

    def test_no_protocol_version_is_invalid_params(self):
        (response,), _ = self.converse(rpc(1, "initialize", {"capabilities": {}}))
        self.assertEqual(response["error"]["code"], -32602)


class TestNotificationsAndPing(Case):
    def test_notifications_get_no_reply(self):
        responses, _ = self.converse(init(), notification("notifications/initialized"),
                                     notification("notifications/unknown"), rpc(2, "ping"))
        self.assertEqual([r["id"] for r in responses], [1, 2])

    def test_ping_gets_an_empty_result(self):
        (response,), _ = self.converse(rpc("p-1", "ping"))
        self.assertEqual(response, {"jsonrpc": "2.0", "id": "p-1", "result": {}})

    def test_client_responses_and_blank_lines_get_no_reply(self):
        responses, _ = self.converse(json.dumps({"jsonrpc": "2.0", "id": 5, "result": {}}), "", "   ", rpc(2, "ping"))
        self.assertEqual([r["id"] for r in responses], [2])


# ---------------------------------------------------------------- tools/list

class TestToolsList(Case):
    def test_exactly_one_tool_with_this_schema(self):
        (_, response), _ = self.converse(init(), rpc(2, "tools/list"))
        (tool,) = response["result"]["tools"]
        self.assertEqual(set(response["result"]), {"tools"})
        self.assertEqual(set(tool), {"name", "description", "inputSchema"})
        self.assertEqual(tool["name"], "score_posting")
        self.assertIsInstance(tool["description"], str)
        self.assertIn("FILTER v2", tool["description"])
        self.assertEqual(tool["inputSchema"], {
            "type": "object",
            "properties": {
                "board_key": {"type": "string", "enum": [AB, GH], "description": "The posting's board, as ATS:name."},
                "posting_id": {"type": "string", "description": "The posting's id on that board, as a string."},
            },
            "required": ["board_key", "posting_id"],
            "additionalProperties": False,
        })

    def test_the_real_corpus_gives_the_four_board_keys(self):
        boards = sorted({board for board, _, _ in mcp_server.seal_draw.CORPUS})  # names only; no file is read
        self.assertEqual(mcp_server.tool_definition(boards)["inputSchema"]["properties"]["board_key"]["enum"],
                         ["ashby:notion", "greenhouse:duolingo", "greenhouse:robinhood", "greenhouse:stripe"])


# ---------------------------------------------------------------- tools/call

CLAIMS_6001 = [
    {"claim": "The title names a target role: Product Manager.", "field": "title"},
    {"claim": "The location is workable: New York.", "field": "location"},
    {"claim": "The title has no seniority word.", "field": "title"},
    {"claim": "The posting asks for no more than 3 years of experience.", "field": "text"},
    {"claim": "The role calls for Python.", "field": "text"},
    {"claim": "The role calls for SQL.", "field": "text"},
]


class TestScorePosting(Case):
    def test_a_good_call(self):
        ((is_error, text),) = self.tool_result({"board_key": GH, "posting_id": "6001"})
        self.assertFalse(is_error)
        self.assertEqual(json.loads(text), {
            "filter": "FILTER.md v2",
            "verdict": "relevant",
            "conditions": {
                "C1": {"status": "pass", "reason": "the title contains a target title: Product Manager"},
                "C2": {"status": "pass", "reason": "the location is workable: New York"},
                "C3": {"status": "pass", "reason": "the text is present (FILTER v2's C3 asks only that); "
                                                   "skills found: Python, SQL"},
                "C4": {"status": "pass", "reason": "no seniority word in the title, and no stated minimum above 3 "
                                                   "years in the text"},
            },
            "score": 2,
            "missing": [],
            "claims": CLAIMS_6001,
        })

    def test_rejected_and_undecided_postings_get_reasons_and_no_claims(self):
        senior, years, nowhere, engineer = (json.loads(text) for _, text in self.tool_result(
            {"board_key": GH, "posting_id": "6003"}, {"board_key": GH, "posting_id": "6004"},
            {"board_key": GH, "posting_id": "6006"}, {"board_key": GH, "posting_id": "6007"}))
        self.assertEqual((senior["verdict"], senior["conditions"]["C4"], senior["claims"]),
                         ("not_relevant", {"status": "fail", "reason": 'title has "Senior"'}, []))
        self.assertEqual(years["conditions"]["C4"]["reason"], 'text states "5+ years", a minimum above 3 years')
        self.assertEqual((nowhere["verdict"], nowhere["missing"], nowhere["conditions"]["C2"], nowhere["claims"]),
                         ("cannot_tell", ["location"], {"status": "missing", "reason": "the location is missing (F7)"},
                          []))
        self.assertEqual(engineer["conditions"]["C1"], {"status": "fail", "reason": "the title contains no target title"})

    def test_claims_are_the_justifications_tsv_sentences(self):
        code, _, err = v2t.run(self.fx.root, self.fx.corpus, "--filter", "v2", now=NOW)
        self.assertEqual(code, 0, err)
        rows = self.fx.rows("justifications.tsv", "filter_v2_2026-11-20T100000Z")
        shortlisted = list(dict.fromkeys((r["board_key"], r["id"]) for r in rows))
        answers = self.tool_result(*[{"board_key": b, "posting_id": i} for b, i in shortlisted])
        for (board, posting_id), (_, text) in zip(shortlisted, answers):
            with self.subTest(posting_id=posting_id):
                expected = [{"claim": r["claim"], "field": r["field"]} for r in rows
                            if (r["board_key"], r["id"]) == (board, posting_id)]
                self.assertEqual(json.loads(text)["claims"], expected)

    def test_every_verdict_is_filter_v2_s(self):
        code, _, err = v2t.run(self.fx.root, self.fx.corpus, "--filter", "v2", now=NOW)
        self.assertEqual(code, 0, err)
        expected = {(r["board_key"], r["id"]): r["verdict"]
                    for r in self.fx.rows("verdicts.tsv", "filter_v2_2026-11-20T100000Z")}
        answers = self.tool_result(*[{"board_key": b, "posting_id": i} for b, i in expected])
        self.assertEqual({key: json.loads(text)["verdict"] for key, (_, text) in zip(expected, answers)}, expected)

    def test_never_the_body_text(self):
        _, out_lines = self.converse(init(), *[call(n, {"board_key": GH, "posting_id": i})
                                               for n, i in enumerate(v2t.GH_JOBS, start=2)])
        for line in out_lines:
            for marker in ("BODY-MARKER", "You will run", "A body with no skill", "Python and SQL."):
                self.assertNotIn(marker, line)


class TestRefusals(Case):
    def assert_refused(self, arguments, needle, never=()):
        _, out_lines = self.converse(init(), call(2, arguments))
        response = json.loads(out_lines[1])
        self.assertNotIn("error", response)
        self.assertTrue(response["result"]["isError"])
        text = response["result"]["content"][0]["text"]
        self.assertIn(needle, text)
        for value in never:
            self.assertNotIn(value, out_lines[1])
        return text

    def test_sealed_postings_are_refused_without_an_id(self):
        for posting_id in (FINAL_ID, V2_ID):
            with self.subTest(posting_id=posting_id):
                text = self.assert_refused({"board_key": GH, "posting_id": posting_id}, "sealed set (SEAL.md",
                                           never=(posting_id,))
                self.assertNotIn("BODY", text)

    def test_sealed_postings_are_never_judged_or_even_looked_up(self):
        judged = []
        real = mcp_server.filter_v1.judge
        with mock.patch.object(mcp_server.filter_v1, "judge", lambda p, *a: judged.append(p["posting_id"]) or real(p, *a)), \
                mock.patch.object(mcp_server.filter_run, "read_checked_corpus", side_effect=AssertionError("loaded")):
            for posting_id in (FINAL_ID, V2_ID):
                self.assert_refused({"board_key": GH, "posting_id": posting_id}, "sealed set")
        self.assertEqual(judged, [])

    def test_unknown_id_or_board_key(self):
        self.assert_refused({"board_key": GH, "posting_id": "9999999"}, "no posting with this board key and id",
                            never=("9999999",))
        self.assert_refused({"board_key": AB, "posting_id": FINAL_ID}, "no posting with this board key and id",
                            never=(FINAL_ID,))  # a sealed id under another board is another posting, and not there
        self.assert_refused({"board_key": "lever:constructed-zzz", "posting_id": "6001"}, "unknown board key",
                            never=("lever:constructed-zzz", "6001"))

    def test_bad_arguments(self):
        cases = [
            ({"board_key": GH}, "both required"),
            ({}, "both required"),
            ({"board_key": GH, "posting_id": 6001}, "must both be strings"),
            ({"board_key": [GH], "posting_id": "6001"}, "must both be strings"),
            ({"board_key": GH, "posting_id": "6001", FINAL_ID: "extra"}, "only board_key and posting_id"),
        ]
        for arguments, needle in cases:
            with self.subTest(arguments=arguments):
                self.assert_refused(arguments, needle, never=(FINAL_ID, "6001"))
        _, out_lines = self.converse(init(), rpc(2, "tools/call", {"name": "score_posting"}))  # no arguments at all
        self.assertTrue(json.loads(out_lines[1])["result"]["isError"])

    def test_a_corpus_that_fails_its_hash_check_is_refused_and_the_server_goes_on(self):
        path = self.fx.root / "corpus/gh.json"
        path.write_bytes(path.read_bytes() + b" ")
        responses, _ = self.converse(init(), call(2, {"board_key": GH, "posting_id": "6001"}), rpc(3, "ping"))
        self.assertTrue(responses[1]["result"]["isError"])
        self.assertIn("cannot use the frozen corpus", responses[1]["result"]["content"][0]["text"])
        self.assertIn("corpus/gh.json: SHA-256 does not match", responses[1]["result"]["content"][0]["text"])
        self.assertEqual(responses[2]["result"], {})


# ---------------------------------------------------------------- protocol errors

class TestProtocolErrors(Case):
    def assert_error(self, line, code, request_id):
        responses, out_lines = self.converse(line, rpc("after", "ping"))
        self.assertEqual(responses[0]["error"]["code"], code)
        self.assertEqual(responses[0]["id"], request_id)
        self.assertEqual(responses[1], {"jsonrpc": "2.0", "id": "after", "result": {}})  # it keeps running
        return out_lines[0]

    def test_unknown_method(self):
        self.assert_error(rpc(4, "tools/delete"), -32601, 4)
        self.assert_error(rpc(5, "resources/list"), -32601, 5)

    def test_malformed_json(self):
        self.assert_error('{"jsonrpc": "2.0", "id": 1, "method": ', -32700, None)
        self.assert_error("not json at all", -32700, None)

    def test_invalid_utf8(self):
        responses, _ = self.converse(raw=b'{"jsonrpc":"2.0","id":1,"method":"ping"}\xff\n')
        self.assertEqual((responses[0]["error"]["code"], responses[0]["id"]), (-32700, None))

    def test_invalid_requests(self):
        self.assert_error("[" + rpc(1, "ping") + "]", -32600, None)  # a batch
        self.assert_error('"a string"', -32600, None)
        self.assert_error(json.dumps({"jsonrpc": "2.0", "id": 6}), -32600, 6)  # no method
        self.assert_error(json.dumps({"jsonrpc": "1.0", "id": 7, "method": "ping"}), -32600, 7)
        self.assert_error(json.dumps({"jsonrpc": "2.0", "id": None, "method": "ping"}), -32600, None)
        self.assert_error(json.dumps({"jsonrpc": "2.0", "id": True, "method": "ping"}), -32600, None)

    def test_invalid_params(self):
        line = self.assert_error(call(8, {}, name=FINAL_ID), -32602, 8)  # an unknown tool, named like an id
        self.assertNotIn(FINAL_ID, line)
        self.assert_error(rpc(9, "tools/call", {"arguments": {}}), -32602, 9)
        self.assert_error(rpc(10, "tools/call", {"name": "score_posting", "arguments": [GH, "6001"]}), -32602, 10)
        self.assert_error(json.dumps({"jsonrpc": "2.0", "id": 11, "method": "tools/list", "params": [1]}), -32602, 11)


# ---------------------------------------------------------------- transcript, reads, writes

class TestTranscript(Case):
    def test_every_line_in_both_directions_unaltered(self):
        lines = [init(), "{not json", "", rpc(2, "ping"), notification("notifications/initialized"),
                 call(3, {"board_key": GH, "posting_id": "6001"}), call(4, {"board_key": GH, "posting_id": FINAL_ID}),
                 "[1,2]"]
        raw = b"".join(line.encode("utf-8") + b"\n" for line in lines) + b"\xff\xfe raw bytes\n" + b'{"no newline":1}'
        _, out_lines = self.converse(raw=raw)
        answers = iter(out_lines)
        expected = []
        for line, answered in zip(lines + ["\udcff\udcfe raw bytes", '{"no newline":1}'],
                                  [1, 1, 0, 1, 0, 1, 1, 1, 1, 1]):
            expected.append(("client->server", line))
            expected += [("server->client", next(answers)) for _ in range(answered)]
        got = records(self.fx.root / TRANSCRIPT)
        self.assertEqual([(r["direction"], r["line"]) for r in got], expected)
        self.assertTrue(all(UTC.match(r["utc"]) and set(r) == {"utc", "direction", "line"} for r in got))
        self.assertEqual(got[-4]["line"].encode("utf-8", "surrogateescape"), b"\xff\xfe raw bytes")

    def test_a_new_file_per_start_never_overwritten(self):
        self.converse(rpc(1, "ping"))
        first = (self.fx.root / TRANSCRIPT).read_bytes()
        self.converse(rpc(2, "ping"))  # the same second
        self.assertEqual((self.fx.root / TRANSCRIPT).read_bytes(), first)
        second = self.fx.root / "transcripts/mcp_server_2026-11-20T100000Z_2.jsonl"
        self.assertEqual([r["line"] for r in records(second)][0], rpc(2, "ping"))

    def test_it_writes_nothing_but_its_transcript(self):
        def snapshot():
            return {(str(p), p.stat().st_mtime_ns) for p in self.fx.root.rglob("*") if "transcripts" not in p.parts}

        before = snapshot()
        self.converse(init(), call(2, {"board_key": GH, "posting_id": "6001"}))
        self.assertEqual(snapshot(), before)
        self.assertEqual([p.name for p in (self.fx.root / "transcripts").iterdir()], [Path(TRANSCRIPT).name])

    def test_it_reads_only_the_corpus_the_manifest_the_sealed_ids_and_the_persona(self):
        read = []
        real_text, real_bytes = Path.read_text, Path.read_bytes

        def read_text(path, *args, **kwargs):
            read.append(Path(path).resolve())
            return real_text(path, *args, **kwargs)

        def read_bytes(path):
            read.append(Path(path).resolve())
            return real_bytes(path)

        with mock.patch.object(Path, "read_text", read_text), mock.patch.object(Path, "read_bytes", read_bytes):
            self.converse(init(), call(2, {"board_key": GH, "posting_id": "6001"}),
                          call(3, {"board_key": GH, "posting_id": FINAL_ID}))
        root = self.fx.root
        allowed = {(root / rel).resolve() for _, rel, _ in self.fx.corpus} | {
            (root / name).resolve() for name in ("vault/corpus_manifest.tsv", "vault/final_heldout_ids.tsv",
                                                 "vault/js3_heldout_ids_v2.tsv", "resume_persona.json")}
        self.assertTrue(read)
        self.assertLessEqual(set(read), allowed)

    def test_no_network(self):
        tree = ast.parse(Path(mcp_server.__file__).read_text(encoding="utf-8"))
        imported = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
                    for alias in node.names}
        imported |= {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertLessEqual(imported, {"argparse", "itertools", "json", "sys", "traceback", "datetime", "pathlib",
                                        "agent", "tools"})
        with mock.patch("socket.socket", side_effect=AssertionError("network")):
            responses, _ = self.converse(init(), call(2, {"board_key": GH, "posting_id": "6001"}))
        self.assertFalse(responses[1]["result"]["isError"])


class TestStdout(Case):
    def test_nothing_but_protocol_on_stdout(self):
        lines = [init(), notification("notifications/initialized"), rpc(2, "tools/list"),
                 call(3, {"board_key": GH, "posting_id": "6001"}), "{broken", rpc(4, "nope")]
        done = subprocess.run(server_command(self.fx.root, self.fx.corpus, NOISY),
                              input="".join(line + "\n" for line in lines).encode(), capture_output=True, timeout=60)
        self.assertEqual(done.returncode, 0, done.stderr.decode())
        out_lines = done.stdout.decode("ascii").splitlines()
        self.assertEqual(len(out_lines), 5)
        for line in out_lines:
            message = json.loads(line)
            self.assertEqual(message["jsonrpc"], "2.0")
            self.assertIn("id", message)
            self.assertTrue(("result" in message) ^ ("error" in message))
        self.assertNotIn(b"STRAY", done.stdout)
        self.assertIn(b"STRAY-PRINT", done.stderr)
        self.assertIn(b"STRAY-WRITE", done.stderr)

    def test_even_help_goes_to_stderr(self):
        # The real script, run with --help: it parses its arguments before it opens a transcript or reads a file.
        transcripts = PROJECT / "transcripts"
        existed = transcripts.exists()
        done = subprocess.run([sys.executable, str(PROJECT / "tools/mcp_server.py"), "--help"], capture_output=True,
                              timeout=60)
        self.assertEqual((done.returncode, done.stdout), (0, b""))
        self.assertIn(b"usage: mcp_server.py", done.stderr)
        self.assertEqual(transcripts.exists(), existed)


# ---------------------------------------------------------------- the client

FAKE_SERVER = r'''
import json, sys
def send(message):
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()
while True:
    line = sys.stdin.readline()
    if not line:
        break
    message = json.loads(line)
    if message.get("method") == "initialize":
        sys.stdout.write("this line is not JSON\n")
        send({"jsonrpc": "2.0", "method": "notifications/message", "params": {"level": "info", "data": "hello"}})
        send({"jsonrpc": "2.0", "id": "server-ping", "method": "ping"})
        if json.loads(sys.stdin.readline()) != {"jsonrpc": "2.0", "id": "server-ping", "result": {}}:
            sys.exit(3)
        send({"jsonrpc": "2.0", "id": message["id"], "result": {"protocolVersion": "2025-06-18",
              "capabilities": {"tools": {}}, "serverInfo": {"name": "someone-else", "version": "9"}}})
    elif message.get("method") == "tools/list":
        if message.get("params", {}).get("cursor") is None:
            send({"jsonrpc": "2.0", "id": message["id"], "result": {"tools": [{"name": "a",
                  "inputSchema": {"type": "object"}}], "nextCursor": "page-2"}})
        else:
            send([{"jsonrpc": "2.0", "id": message["id"], "result": {"tools": [{"name": "b",
                  "inputSchema": {"type": "object"}}]}}])
'''


class TestClient(Case):
    def client(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = mcp_client.main(list(argv), out=out, err=err, server_stderr=subprocess.DEVNULL)
        return code, out.getvalue(), err.getvalue()

    def test_end_to_end_against_mcp_server(self):
        path = self.fx.root / "probe.jsonl"
        arguments = json.dumps({"board_key": GH, "posting_id": "6001"})
        code, out, err = self.client("--out", str(path), "--call", "score_posting", "--args", arguments, "--",
                                     *server_command(self.fx.root, self.fx.corpus))
        self.assertEqual(code, 0, err)
        self.assertIn("server: js3-filter-tool-score 1.0.0 (protocol 2025-11-25)\n", out)
        self.assertIn('"name": "score_posting"', out)
        result = json.loads(out.split("result of score_posting:\n", 1)[1])
        self.assertFalse(result["isError"])
        self.assertEqual(json.loads(result["content"][0]["text"])["claims"], CLAIMS_6001)
        mine = records(path)
        sent = [json.loads(r["line"]) for r in mine if r["direction"] == "client->server"]
        self.assertEqual([m["method"] for m in sent], ["initialize", "notifications/initialized", "tools/list",
                                                       "tools/call"])
        self.assertTrue(all(UTC.match(r["utc"]) for r in mine))
        # The server's own transcript holds the very same lines, in each direction.
        (server_file,) = (self.fx.root / "transcripts").iterdir()
        theirs = records(server_file)
        for direction in ("client->server", "server->client"):
            self.assertEqual([r["line"] for r in mine if r["direction"] == direction],
                             [r["line"] for r in theirs if r["direction"] == direction])
        self.assertEqual(len([r for r in mine if r["direction"] == "server->client"]), 3)

    def test_a_refusal_through_the_client(self):
        path = self.fx.root / "probe.jsonl"
        code, out, err = self.client("--out", str(path), "--call", "score_posting", "--args",
                                     json.dumps({"board_key": GH, "posting_id": V2_ID}), "--",
                                     *server_command(self.fx.root, self.fx.corpus))
        self.assertEqual(code, 0, err)
        result = out.split("result of score_posting:\n", 1)[1]
        self.assertTrue(json.loads(result)["isError"])
        self.assertNotIn(V2_ID, result)

    def test_refuses_to_overwrite(self):
        path = self.fx.root / "probe.jsonl"
        path.write_text("an earlier probe\n")
        code, out, err = self.client("--out", str(path), "--", *server_command(self.fx.root, self.fx.corpus))
        self.assertEqual((code, out), (1, ""))
        self.assertIn("refusing to overwrite", err)
        self.assertEqual(path.read_text(), "an earlier probe\n")
        self.assertFalse((self.fx.root / "transcripts").exists())  # the server was never started

    def test_bad_arguments(self):
        path = str(self.fx.root / "probe.jsonl")
        for argv in (["--out", path, "--args", "{}", "--", "x"], ["--out", path, "--call", "t", "--args", "[1]", "--", "x"],
                     ["--out", path, "--call", "t", "--args", "{nope", "--", "x"]):
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()), \
                    self.assertRaises(SystemExit) as raised:
                self.client(*argv)
            self.assertEqual(raised.exception.code, 2)
        self.assertFalse(Path(path).exists())

    def test_a_silent_server_times_out(self):
        path = self.fx.root / "probe.jsonl"
        started = time.monotonic()
        code, _, err = self.client("--out", str(path), "--timeout", "0.5", "--",
                                   sys.executable, "-c", "import time; time.sleep(30)")
        self.assertEqual(code, 1)
        self.assertIn("no response to initialize within 0.5 s", err)
        self.assertLess(time.monotonic() - started, 15)
        self.assertEqual([r["direction"] for r in records(path)], ["client->server"])

    def test_someone_else_s_server(self):
        path = self.fx.root / "probe.jsonl"
        code, out, err = self.client("--out", str(path), "--", sys.executable, "-c", FAKE_SERVER)
        self.assertEqual(code, 0, err)
        self.assertIn("server: someone-else 9 (protocol 2025-06-18)\n", out)
        tools = json.loads(out.split("tools:\n", 1)[1])
        self.assertEqual([t["name"] for t in tools], ["a", "b"])  # nextCursor followed, a batch reply accepted
        self.assertIn("not JSON", err)
        lines = [(r["direction"], r["line"]) for r in records(path)]
        self.assertIn(("server->client", "this line is not JSON"), lines)
        self.assertIn(("client->server", json.dumps({"jsonrpc": "2.0", "id": "server-ping", "result": {}},
                                                    separators=(",", ":"))), lines)


if __name__ == "__main__":
    unittest.main()
