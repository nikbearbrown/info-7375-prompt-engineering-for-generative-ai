"""The score_posting MCP server: lifecycle table, request vs task errors, no network, log boundary, WF6.

Offline and deterministic: every test uses tests/fixtures/mcp-run (a hand-made fetch run, example.invalid
URLs, SHA-256s that match its raw files), never a real corpus and never the network.
"""
import ast
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import helpers  # noqa: F401  (puts src/ on sys.path, as for test_policy)

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))

from jsa3 import corpus as corpus_mod  # noqa: E402
from jsa3 import filter as filter_mod  # noqa: E402
from jsa3 import mcp_server  # noqa: E402
import mcp_record  # noqa: E402
import wrong_versions_mcp  # noqa: E402

FIXTURE = PROJECT / "tests" / "fixtures" / "mcp-run"
SERVER_FILE = PROJECT / "src" / "jsa3" / "mcp_server.py"
CFG = json.loads((PROJECT / "config" / "filter.json").read_text(encoding="utf-8"))
CORPUS = corpus_mod.load(FIXTURE)
KEEP_ID = "101"           # ML Engineer, Boston: the first kept posting in the fixture
FORBIDDEN = ("jsa.net", "socket", "ssl", "http", "http.client", "urllib.request", "urllib.error", "ftplib",
             "smtplib", "subprocess", "asyncio")


def msg(ident, method, params=None):
    m = {"jsonrpc": "2.0", "method": method}
    if ident is not None:
        m["id"] = ident
    if params is not None:
        m["params"] = params
    return json.dumps(m)


def ready_server(**kw):
    notes = []
    s = mcp_server.Server(CORPUS, CFG, note=notes.append, **kw)
    s.handle_line(msg(1, "initialize", {"protocolVersion": "2025-11-25", "capabilities": {}}))
    s.handle_line(msg(None, "notifications/initialized"))
    return s, notes


def reply(server, line):
    out = server.handle_line(line)
    return None if out is None else json.loads(out)


def tool_call(server, ident, arguments, name="score_posting"):
    return reply(server, msg(ident, "tools/call", {"name": name, "arguments": arguments}))


class LifecycleTable(unittest.TestCase):
    """The 22-step table of transcripts/EXPECTED-A.md, in process and through a real subprocess."""

    def test_T1_in_process_table_all_steps_match(self):
        results = mcp_record.run_in_process(lambda: mcp_server.Server(CORPUS, CFG), "own", KEEP_ID)
        self.assertEqual(len(results), 22)
        self.assertEqual([r["n"] for r in results if r["verdict"] != "match"], [])

    def test_T2_subprocess_table_all_steps_match(self):
        cmd = [sys.executable, "-I", str(SERVER_FILE), "--corpus", str(FIXTURE)]
        rows, results, stderr, codes = mcp_record.run(cmd, "own", KEEP_ID, quiet=0.4, timeout=10)
        self.assertEqual([r["n"] for r in results if r["verdict"] != "match"], [])
        self.assertEqual(codes, {1: 0, 2: 0})
        self.assertIn("NOT executed", stderr[1])
        dirs = {r["dir"] for r in rows}
        self.assertEqual(dirs, {"meta", "client->server", "server->client"})

    def test_T3_tools_before_initialized_notification_is_32000(self):
        s = mcp_server.Server(CORPUS, CFG)
        self.assertEqual(reply(s, msg(1, "tools/list"))["error"]["code"], -32000)
        self.assertIn("result", reply(s, msg(2, "initialize", {"protocolVersion": "2025-11-25"})))
        self.assertEqual(reply(s, msg(3, "tools/list"))["error"]["code"], -32000)
        self.assertEqual(tool_call(s, 4, {"posting_id": KEEP_ID})["error"]["code"], -32000)
        self.assertIsNone(reply(s, msg(None, "notifications/initialized")))
        self.assertEqual([t["name"] for t in reply(s, msg(5, "tools/list"))["result"]["tools"]], ["score_posting"])

    def test_T4_initialized_notification_before_initialize_does_not_make_ready(self):
        s = mcp_server.Server(CORPUS, CFG)
        self.assertIsNone(reply(s, msg(None, "notifications/initialized")))
        reply(s, msg(1, "initialize", {"protocolVersion": "2025-11-25"}))
        self.assertEqual(reply(s, msg(2, "tools/list"))["error"]["code"], -32000)

    def test_T5_second_initialize_is_refused_and_state_kept(self):
        s, _ = ready_server()
        r = reply(s, msg(9, "initialize", {"protocolVersion": "2025-11-25"}))
        self.assertEqual(r["error"]["code"], -32600)
        self.assertTrue(s.ready)
        half = mcp_server.Server(CORPUS, CFG)
        reply(half, msg(1, "initialize", {"protocolVersion": "2025-11-25"}))
        self.assertEqual(reply(half, msg(2, "initialize", {"protocolVersion": "2025-11-25"}))["error"]["code"], -32600)
        self.assertFalse(half.ready)

    def test_T6_version_negotiation(self):
        for asked in ("2025-11-25", "2024-11-05", "1999-01-01"):
            s = mcp_server.Server(CORPUS, CFG)
            r = reply(s, msg(1, "initialize", {"protocolVersion": asked}))
            self.assertEqual(r["result"]["protocolVersion"], "2025-11-25", asked)
        s = mcp_server.Server(CORPUS, CFG)
        self.assertEqual(reply(s, msg(1, "initialize"))["error"]["code"], -32602)
        self.assertFalse(s.initialized)

    def test_T7_ping_any_state_and_unknown_method_any_state(self):
        s = mcp_server.Server(CORPUS, CFG)
        self.assertEqual(reply(s, msg("p", "ping")), {"jsonrpc": "2.0", "id": "p", "result": {}})
        self.assertEqual(reply(s, msg(2, "jobs/apply"))["error"]["code"], -32601)
        s, _ = ready_server()
        self.assertEqual(reply(s, msg(3, "jobs/apply"))["error"]["code"], -32601)


class RequestVersusTaskErrors(unittest.TestCase):
    def test_E1_success_record_is_the_filter_record(self):
        s, _ = ready_server()
        r = tool_call(s, 7, {"posting_id": KEEP_ID})["result"]
        self.assertIs(r["isError"], False)
        want = filter_mod.evaluate(corpus_mod.by_id(CORPUS)[KEEP_ID], CFG)
        self.assertEqual(r["structuredContent"]["record"], want)
        self.assertEqual(want["verdict"], "keep")
        self.assertEqual(json.loads(r["content"][0]["text"]), r["structuredContent"])
        self.assertEqual(r["structuredContent"]["source"]["corpus_run"], "fixture-mcp-run")
        self.assertEqual(r["structuredContent"]["source"]["raw_sha256"], CORPUS["boards"]["greenhouse/acme"]["sha256"])

    def test_E2_unknown_and_ambiguous_ids_are_task_errors_not_protocol_errors(self):
        s, _ = ready_server()
        for pid, word in (("no-such-posting", "No posting"), ("dup1", "more than one board"), ("", "No posting")):
            r = tool_call(s, 8, {"posting_id": pid})
            self.assertNotIn("error", r, pid)
            self.assertIs(r["result"]["isError"], True, pid)
            self.assertIn(word, r["result"]["content"][0]["text"])

    def test_E3_bad_arguments_and_unknown_tool_are_32602(self):
        s, _ = ready_server()
        for args in ({"posting_id": 5}, {"posting_id": KEEP_ID, "extra": 1}, {}, ["101"], None, {"id": KEEP_ID}):
            self.assertEqual(tool_call(s, 9, args)["error"]["code"], -32602, args)
        self.assertEqual(tool_call(s, 10, {"posting_id": KEEP_ID}, name="apply_to_job")["error"]["code"], -32602)
        self.assertEqual(reply(s, msg(11, "tools/call", ["score_posting"]))["error"]["code"], -32602)

    def test_E4_parse_and_invalid_request(self):
        s, _ = ready_server()
        self.assertEqual(reply(s, "{"), {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error: the line is not JSON"}})
        # an id that can be read is echoed; otherwise id is null (JSON-RPC 2.0 section 5)
        for line, ident in (("{}", None), ("[]", None), ('[{"jsonrpc":"2.0","id":1,"method":"ping"}]', None),
                            ('{"jsonrpc":"1.0","id":1,"method":"ping"}', 1), ('{"jsonrpc":"2.0","id":7}', 7),
                            ('{"jsonrpc":"2.0","id":null,"method":"ping"}', None),
                            ('{"jsonrpc":"2.0","id":true,"method":"ping"}', None)):
            r = reply(s, line)
            self.assertEqual(r["error"]["code"], -32600, line)
            self.assertEqual(r["id"], ident, line)
        self.assertIsNone(reply(s, '{"jsonrpc":"2.0","id":3,"result":{}}'))  # a response object: ignored

    def test_E5_tools_call_notification_is_not_executed_and_not_answered(self):
        s, notes = ready_server()
        calls = []
        real = mcp_server.filter_mod.evaluate
        mcp_server.filter_mod.evaluate = lambda *a: calls.append(a) or real(*a)
        try:
            self.assertIsNone(tool_call(s, None, {"posting_id": KEEP_ID}))
            self.assertEqual(calls, [])
            self.assertTrue(any("NOT executed" in n for n in notes))
            tool_call(s, 12, {"posting_id": KEEP_ID})
            self.assertEqual(len(calls), 1)
        finally:
            mcp_server.filter_mod.evaluate = real

    def test_E6_advertised_tool_declares_read_only_offline_and_strict_schema(self):
        t = mcp_server.TOOL
        self.assertIn("Read-only", t["description"])
        self.assertIn("offline", t["description"])
        self.assertIs(t["inputSchema"]["additionalProperties"], False)
        self.assertEqual(t["inputSchema"]["required"], ["posting_id"])
        self.assertEqual(t["annotations"]["readOnlyHint"], True)
        self.assertEqual(t["annotations"]["openWorldHint"], False)


class WrongVersions(unittest.TestCase):
    def test_W1_WF6_ready_inside_initialize_fails_the_table_at_step_3(self):
        self.assertEqual(wrong_versions_mcp.check(wrong_versions_mcp.ReadyOnInitialize, CORPUS, CFG, KEEP_ID), [3])

    def test_W2_other_planted_versions_are_caught(self):
        self.assertEqual(wrong_versions_mcp.check(wrong_versions_mcp.UnknownIdAsProtocolError, CORPUS, CFG, KEEP_ID), [7])
        self.assertEqual(wrong_versions_mcp.check(wrong_versions_mcp.ReinitializeResets, CORPUS, CFG, KEEP_ID), [15, 16])
        self.assertEqual(wrong_versions_mcp.check(mcp_server.Server, CORPUS, CFG, KEEP_ID), [])


def project_imports(path: Path) -> set:
    """Every module name imported anywhere in one file (top level or inside functions)."""
    names = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
            names.update(f"{node.module}.{a.name}" for a in node.names)
    return names


def transitive_imports(start: Path) -> dict:
    """file -> its imports, following imports that resolve to files under src/."""
    todo, seen = [start], {}
    while todo:
        f = todo.pop()
        if f in seen:
            continue
        seen[f] = project_imports(f)
        for name in seen[f]:
            for cand in (PROJECT / "src" / (name.replace(".", "/") + ".py"),):
                if cand.exists():
                    todo.append(cand)
    return seen


def flagged(names) -> set:
    return {n for n in names if any(n == f or n.startswith(f + ".") for f in FORBIDDEN)}


class NoNetwork(unittest.TestCase):
    def test_N1_ast_scan_of_server_and_everything_it_imports(self):
        files = transitive_imports(SERVER_FILE)
        self.assertEqual({p.relative_to(PROJECT).as_posix() for p in files},
                         {"src/jsa3/mcp_server.py", "src/jsa3/filter.py", "src/jsa3/corpus.py", "src/jsa/boards.py"})
        bad = {p.name: flagged(n) for p, n in files.items() if flagged(n)}
        self.assertEqual(bad, {})

    def test_N2_ast_scan_catches_a_planted_network_import(self):
        d = Path(tempfile.mkdtemp(prefix="mcp-plant-"))
        try:
            (d / "planted.py").write_text("from jsa import net\nimport urllib.request\n", encoding="utf-8")
            self.assertEqual(flagged(project_imports(d / "planted.py")), {"jsa.net", "urllib.request"})
        finally:
            shutil.rmtree(d)

    def test_N3_real_server_process_never_loads_a_network_module(self):
        """-X importtime makes the interpreter itself list every module the real server process imports."""
        lines = [msg(1, "initialize", {"protocolVersion": "2025-11-25"}), msg(None, "notifications/initialized"),
                 msg(2, "tools/list"), msg(3, "tools/call", {"name": "score_posting", "arguments": {"posting_id": KEEP_ID}}),
                 msg(4, "tools/call", {"name": "score_posting", "arguments": {"posting_id": "nope"}})]
        p = subprocess.run([sys.executable, "-I", "-X", "importtime", str(SERVER_FILE), "--corpus", str(FIXTURE)],
                           input=("\n".join(lines) + "\n").encode(), capture_output=True, timeout=30)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(len(p.stdout.decode().splitlines()), 4)
        loaded = {ln.rsplit("|", 1)[1].strip() for ln in p.stderr.decode().splitlines() if ln.startswith("import time:")}
        self.assertIn("jsa3.filter", loaded)
        self.assertIn("jsa.boards", loaded)
        self.assertEqual(flagged(loaded), set())


class Boundaries(unittest.TestCase):
    def test_B1_log_path_must_be_inside_transcripts(self):
        self.assertEqual(mcp_server.log_path_allowed(str(PROJECT / "transcripts" / "x.jsonl")),
                         (PROJECT / "transcripts" / "x.jsonl").resolve())
        for bad in ("/tmp/x.jsonl", str(PROJECT / "transcripts" / ".." / "config" / "x.jsonl"),
                    str(PROJECT / "transcripts"), str(PROJECT / "src" / "x.jsonl")):
            with self.assertRaises(ValueError, msg=bad):
                mcp_server.log_path_allowed(bad)
        err = io.StringIO()
        old, sys.stderr = sys.stderr, err
        try:
            self.assertEqual(mcp_server.main(["--corpus", str(FIXTURE), "--log", "/tmp/mcp-should-not-exist.jsonl"]), 2)
        finally:
            sys.stderr = old
        self.assertFalse(Path("/tmp/mcp-should-not-exist.jsonl").exists())
        self.assertIn("refused", err.getvalue())

    def test_B2_log_keeps_exact_lines_both_directions(self):
        d = Path(tempfile.mkdtemp(prefix="mcp-log-"))
        try:
            s, _ = ready_server()
            sent = [msg(5, "ping"), "{", msg(None, "notifications/initialized")]
            out = io.BytesIO()
            log = mcp_server.Log(d / "log.jsonl")
            mcp_server.serve(s, io.BytesIO(("\n".join(sent) + "\n").encode()), out, log)
            log.close()
            rows = [json.loads(x) for x in (d / "log.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual([r["raw"] for r in rows if r["dir"] == "client->server"], sent)
            self.assertEqual([r["raw"] for r in rows if r["dir"] == "server->client"], out.getvalue().decode().splitlines())
            self.assertEqual([r["dir"] for r in rows], ["client->server", "server->client", "client->server",
                                                       "server->client", "client->server"])
        finally:
            shutil.rmtree(d)

    def test_B3_tampered_corpus_refuses_to_start(self):
        d = Path(tempfile.mkdtemp(prefix="mcp-tamper-"))
        try:
            shutil.copytree(FIXTURE, d / "run")
            raw = d / "run" / "raw" / "greenhouse__acme__a1__200.json"
            raw.write_bytes(raw.read_bytes().replace(b"Boston", b"Bostom"))
            err = io.StringIO()
            old, sys.stderr = sys.stderr, err
            try:
                self.assertEqual(mcp_server.main(["--corpus", str(d / "run")]), 2)
            finally:
                sys.stderr = old
            self.assertIn("SHA-256 does not match", err.getvalue())
        finally:
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
