"""Tests for tool/server.py against tool/TOOL-SERVER.md, written before the server.

    python3 -m unittest discover -s tool/tests

Every test starts the server as a real subprocess (python3 tool/server.py)
and talks to it over stdin/stdout, one JSON line per message, as an MCP client
would. The expected outcome of every test, and the prediction for the run
before the server exists, are recorded in tool/TEST-PREDICTIONS.md.

Groups: P protocol and initialization, N normal calls, E protocol errors,
A argument errors (tool execution errors), X path tricks, B declared
boundaries (imports, runtime audit events, transcripts, integrity, protected
files). The tests read results.json and other files read-only; the only
files they remove are transcripts created by their own server sessions.
Written by Claude Code.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

HERE = Path(__file__).resolve().parents[2]  # js3-filter-tool-score/
SERVER = HERE / "tool" / "server.py"
TRANSCRIPTS = HERE / "tool" / "transcripts"
RESULTS_REL = "runs/filter-v1.1-2026-11-17T21-47-06-167440-0500/results.json"
RESULTS = HERE / RESULTS_REL
RESULTS_SHA256 = "a7f90a74cfd3c82324e55502439684f0234599cde74789fd0736808e2e5edeff"
RUN_ID = "2026-11-17T21-47-06-167440-0500"
PROTOCOL = "2025-11-25"
TIMEOUT = 5.0

# real postings from results.json: (board, posting id, recorded verdict)
SHORTLISTED = ("databricks", "6865698002", "shortlisted")
REJECTED = ("stripe", "8172508", "rejected")
CANNOT_TELL = ("stripe", "5601881", "I cannot tell")
NOT_SHORTLISTED = ("databricks", "8843577002", "not shortlisted")
PLAID = ("plaid", "5d8abedc-018a-4b42-ae1f-0e70b34f2007", "rejected")

PROTECTED = [RESULTS_REL, "runs/filter-2026-11-17T21-47-06-167440-0500/results.json",
             "runs/heldout-v1.1-threshold-2026-11-19T17-31-47-142253-0500/measurement.json",
             "FILTER.md", "job_filter.py", "run_filter.py", "measure_heldout.py", "descriptions.py", "parsers.py",
             "audit", "heldout", "shortlist", "persona"]
FORBIDDEN_MODULES = {"socket", "ssl", "subprocess", "multiprocessing", "concurrent", "asyncio", "urllib", "http",
                     "ftplib", "smtplib", "poplib", "imaplib", "telnetlib", "xmlrpc", "socketserver", "webbrowser",
                     "ctypes", "pty", "shutil", "tempfile", "importlib", "runpy", "pickle", "marshal"}

_created_transcripts = []


def _protected_hashes():
    out = {}
    for rel in PROTECTED:
        p = HERE / rel
        for f in sorted([p] if p.is_file() else (x for x in p.rglob("*") if x.is_file())):
            out[f.relative_to(HERE).as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


_before = {}


def setUpModule():
    _before.update(_protected_hashes())


def tearDownModule():
    for path in _created_transcripts:  # only transcripts made by this test run
        if path.parent == TRANSCRIPTS and path.exists():
            path.unlink()
    after = _protected_hashes()
    changed = sorted(k for k in set(_before) | set(after) if _before.get(k) != after.get(k))
    if changed:
        raise AssertionError(f"protected files changed during the tests: {changed}")


def results_record(board, posting_id):
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    return next(r for r in data["results"] if r["board"] == board and str(r["posting_id"]) == posting_id)


class Session:
    """One server process; send() writes one line, recv() reads one JSON line from stdout."""

    def __init__(self, argv=None, cwd=HERE):
        self.proc = subprocess.Popen(argv or [sys.executable, str(SERVER)], cwd=cwd, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        self.buf = b""
        self.sent, self.received = [], []
        self.stderr = None

    def send(self, message):
        line = message if isinstance(message, str) else json.dumps(message)
        self.sent.append(line)
        try:
            self.proc.stdin.write(line.encode("utf-8") + b"\n")
            self.proc.stdin.flush()
        except BrokenPipeError:
            pass

    def _readline(self, timeout):
        deadline = time.monotonic() + timeout
        while b"\n" not in self.buf:
            left = deadline - time.monotonic()
            if left <= 0:
                return None
            ready, _, _ = select.select([self.proc.stdout], [], [], left)
            if not ready:
                return None
            chunk = os.read(self.proc.stdout.fileno(), 65536)
            if not chunk:
                return b""  # end of output
            self.buf += chunk
        line, self.buf = self.buf.split(b"\n", 1)
        return line

    def recv(self, timeout=TIMEOUT):
        line = self._readline(timeout)
        if line is None:
            raise AssertionError("no response from the server within the timeout")
        if line == b"":
            raise AssertionError("the server closed stdout (it may not exist or may have crashed)")
        text = line.decode("utf-8")
        self.received.append(text)
        return json.loads(text)

    def no_response(self, timeout=0.5):
        line = self._readline(timeout)
        return line is None

    def request(self, method, params=None, id_=1):
        msg = {"jsonrpc": "2.0", "id": id_, "method": method}
        if params is not None:
            msg["params"] = params
        self.send(msg)
        return self.recv()

    def initialize(self, version=PROTOCOL):
        res = self.request("initialize", {"protocolVersion": version, "capabilities": {},
                                          "clientInfo": {"name": "test_server.py", "version": "1"}}, id_=0)
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return res

    def call(self, arguments, name="score_posting", id_=2):
        return self.request("tools/call", {"name": name, "arguments": arguments}, id_=id_)

    def close(self):
        if self.stderr is not None:  # already closed
            return self.proc.returncode
        try:
            self.proc.stdin.close()
        except BrokenPipeError:
            pass
        try:
            code = self.proc.wait(timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()
            code = None
        self.stderr = self.proc.stderr.read().decode("utf-8", "replace")
        rest = self.proc.stdout.read()
        self.buf += rest or b""
        self.proc.stdout.close()
        self.proc.stderr.close()
        for line in self.stderr.splitlines():
            if line.startswith("transcript: "):
                _created_transcripts.append((HERE / line[len("transcript: "):].strip()).resolve())
        return code

    def transcript_path(self):
        for line in (self.stderr or "").splitlines():
            if line.startswith("transcript: "):
                return (HERE / line[len("transcript: "):].strip()).resolve()
        return None


class ServerTest(unittest.TestCase):
    def setUp(self):
        self.s = Session()
        self.addCleanup(self._stop)  # runs even if a subclass's setUp fails

    def _stop(self):
        self.s.close()  # idempotent; also closes the pipes of a server that already exited

    def assertError(self, response, code, id_):
        self.assertEqual(response.get("jsonrpc"), "2.0")
        self.assertIn("error", response, response)
        self.assertNotIn("result", response)
        self.assertEqual(response["error"]["code"], code, response)
        self.assertIsInstance(response["error"]["message"], str)
        self.assertEqual(response.get("id"), id_)

    def assertToolError(self, response, id_=2, contains=None):
        self.assertEqual(response.get("id"), id_)
        self.assertIn("result", response, response)
        result = response["result"]
        self.assertIs(result.get("isError"), True, response)
        text = " ".join(c.get("text", "") for c in result["content"] if c.get("type") == "text")
        self.assertTrue(text.strip())
        self.assertNotIn("Traceback", text)
        if contains:
            self.assertIn(contains.lower(), text.lower())
        return text


# ---------- P: protocol and initialization (TOOL-SERVER.md §2) ----------
class P_Protocol(ServerTest):
    def test_P1_initialize_same_version(self):
        r = self.s.initialize()
        self.assertEqual(r["id"], 0)
        res = r["result"]
        self.assertEqual(res["protocolVersion"], PROTOCOL)
        self.assertEqual(res["capabilities"], {"tools": {"listChanged": False}})
        self.assertEqual(res["serverInfo"], {"name": "js3-score-posting", "version": "1.0.0"})

    def test_P2_initialize_other_version_gets_2025_11_25(self):
        r = self.s.initialize(version="2024-11-05")
        self.assertEqual(r["result"]["protocolVersion"], PROTOCOL)

    def test_P3_initialized_notification_gets_no_response(self):
        self.s.initialize()
        self.assertTrue(self.s.no_response())
        r = self.s.request("ping", id_=9)
        self.assertEqual(r, {"jsonrpc": "2.0", "id": 9, "result": {}})

    def test_P4_tools_before_initialize_refused(self):
        self.assertError(self.s.request("tools/list", id_=1), -32600, 1)
        r = self.s.request("tools/call", {"name": "score_posting",
                                          "arguments": {"board": SHORTLISTED[0], "posting_id": SHORTLISTED[1]}}, id_=2)
        self.assertError(r, -32600, 2)

    def test_P5_ping_before_initialize(self):
        self.assertEqual(self.s.request("ping", id_="p"), {"jsonrpc": "2.0", "id": "p", "result": {}})

    def test_P6_tools_list_one_tool(self):
        self.s.initialize()
        r = self.s.request("tools/list", id_=1)
        tools = r["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        t = tools[0]
        self.assertTrue(t.get("title"))
        self.assertTrue(t.get("description"))
        schema = t["inputSchema"]
        self.assertEqual(schema["type"], "object")
        self.assertEqual(sorted(schema["required"]), ["board", "posting_id"])
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(sorted(schema["properties"]["board"]["enum"]), ["databricks", "plaid", "stripe"])
        self.assertEqual(schema["properties"]["posting_id"]["type"], "string")
        self.assertIn("pattern", schema["properties"]["posting_id"])
        self.assertNotIn("outputSchema", t)
        self.assertNotIn("annotations", t)

    def test_P7_string_ids_echoed(self):
        self.s.initialize()
        r = self.s.request("tools/list", id_="abc")
        self.assertEqual(r["id"], "abc")

    def test_P8_unknown_notification_ignored(self):
        self.s.initialize()
        self.s.send({"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 1}})
        self.assertTrue(self.s.no_response())

    def test_P9_end_of_input_exits_cleanly(self):
        self.s.initialize()
        self.assertEqual(self.s.close(), 0)


# ---------- N: normal calls (§1) ----------
class N_Normal(ServerTest):
    def check_posting(self, board, posting_id, verdict):
        r = self.s.call({"board": board, "posting_id": posting_id})
        res = r["result"]
        self.assertIs(res["isError"], False)
        sc = res["structuredContent"]
        self.assertEqual(sc["record"], results_record(board, posting_id))
        self.assertEqual(sc["record"]["verdict"], verdict)
        self.assertEqual(sc["source"]["file"], RESULTS_REL)
        self.assertEqual(sc["source"]["sha256"], RESULTS_SHA256)
        self.assertEqual(sc["source"]["run_id"], RUN_ID)
        self.assertEqual(sc["source"]["filter_version"], "v1.1")
        self.assertEqual([c["type"] for c in res["content"]], ["text"])
        self.assertEqual(json.loads(res["content"][0]["text"]), sc)

    def test_N1_shortlisted(self):
        self.s.initialize()
        self.check_posting(*SHORTLISTED)

    def test_N2_rejected(self):
        self.s.initialize()
        self.check_posting(*REJECTED)

    def test_N3_cannot_tell(self):
        self.s.initialize()
        self.check_posting(*CANNOT_TELL)

    def test_N4_not_shortlisted_and_plaid(self):
        self.s.initialize()
        self.check_posting(*NOT_SHORTLISTED)
        self.check_posting(*PLAID)

    def test_N5_every_posting_matches_results_json(self):
        self.s.initialize()
        data = json.loads(RESULTS.read_text(encoding="utf-8"))
        for i, rec in enumerate(data["results"]):
            r = self.s.call({"board": rec["board"], "posting_id": str(rec["posting_id"])}, id_=100 + i)
            self.assertEqual(r["id"], 100 + i)
            self.assertEqual(r["result"]["structuredContent"]["record"], rec)
        self.assertEqual(len(data["results"]), 1832)


# ---------- E: protocol errors (§2 errors table) ----------
class E_ProtocolErrors(ServerTest):
    def setUp(self):
        super().setUp()
        self.s.initialize()

    def test_E1_malformed_json(self):
        self.s.send('{"jsonrpc": "2.0", "id": 1, "method": "tools/list"')
        self.assertError(self.s.recv(), -32700, None)

    def test_E2_batch_array(self):
        self.s.send(json.dumps([{"jsonrpc": "2.0", "id": 1, "method": "ping"}]))
        self.assertError(self.s.recv(), -32600, None)

    def test_E3_null_id(self):
        self.s.send({"jsonrpc": "2.0", "id": None, "method": "ping"})
        self.assertError(self.s.recv(), -32600, None)

    def test_E4_missing_or_wrong_jsonrpc(self):
        self.s.send({"id": 4, "method": "ping"})
        self.assertError(self.s.recv(), -32600, 4)
        self.s.send({"jsonrpc": "1.0", "id": 5, "method": "ping"})
        self.assertError(self.s.recv(), -32600, 5)

    def test_E5_unknown_methods(self):
        for i, method in enumerate(["server/discover", "resources/list", "prompts/list", "tools/run"]):
            self.assertError(self.s.request(method, id_=10 + i), -32601, 10 + i)

    def test_E6_unknown_tool(self):
        r = self.s.call({"board": SHORTLISTED[0], "posting_id": SHORTLISTED[1]}, name="read_file", id_=6)
        self.assertError(r, -32602, 6)
        self.assertEqual(r["error"]["message"], "Unknown tool: read_file")
        r = self.s.call({"board": SHORTLISTED[0], "posting_id": SHORTLISTED[1]}, name="Score_Posting", id_=7)
        self.assertError(r, -32602, 7)

    def test_E7_malformed_call_params(self):
        cases = [["score_posting"], {"arguments": {"board": "stripe", "posting_id": "1"}},
                 {"name": "score_posting", "arguments": ["stripe", "1"]},
                 {"name": "score_posting", "arguments": "board=stripe"}, {"name": 5, "arguments": {}}]
        for i, params in enumerate(cases):
            self.assertError(self.s.request("tools/call", params, id_=20 + i), -32602, 20 + i)

    def test_E8_oversized_line_refused_and_server_continues(self):
        self.s.send(json.dumps({"jsonrpc": "2.0", "id": 8, "method": "ping", "params": {"pad": "x" * 70000}}))
        self.assertError(self.s.recv(), -32600, None)
        self.assertEqual(self.s.request("ping", id_=9)["result"], {})

    def test_E9_stdout_only_jsonrpc(self):
        for line in ['not json', '[]', '{"jsonrpc":"2.0","id":1,"method":"nope"}', '"just a string"', '42']:
            self.s.send(line)
            self.s.recv()
        self.s.request("ping", id_=99)
        self.s.close()
        self.assertEqual(self.s.buf, b"", "unexpected extra output on stdout")
        for text in self.s.received:
            msg = json.loads(text)
            self.assertEqual(msg["jsonrpc"], "2.0")
            self.assertEqual(len([k for k in ("result", "error") if k in msg]), 1)


# ---------- A: argument errors are tool execution errors (isError: true) ----------
class A_ArgumentErrors(ServerTest):
    def setUp(self):
        super().setUp()
        self.s.initialize()

    def test_A1_missing_and_extra_arguments(self):
        for i, args in enumerate([{}, {"board": "stripe"}, {"posting_id": "8172508"},
                                  {"board": "stripe", "posting_id": "8172508", "path": "x"}]):
            self.assertToolError(self.s.call(args, id_=30 + i), id_=30 + i)

    def test_A2_wrong_types(self):
        for i, args in enumerate([{"board": "stripe", "posting_id": 8172508}, {"board": ["stripe"], "posting_id": "1"},
                                  {"board": None, "posting_id": "1"}, {"board": "stripe", "posting_id": None}]):
            self.assertToolError(self.s.call(args, id_=40 + i), id_=40 + i)

    def test_A3_unknown_boards(self):
        for i, board in enumerate(["deliberate-bad-name", "Stripe", "STRIPE", "greenhouse", "", " stripe"]):
            self.assertToolError(self.s.call({"board": board, "posting_id": "8172508"}, id_=50 + i), id_=50 + i)

    def test_A4_id_format_per_board(self):
        cases = [("stripe", PLAID[1]), ("databricks", "abc"), ("plaid", "8172508"), ("plaid", PLAID[1].upper()),
                 ("stripe", "1" * 21), ("stripe", "")]
        for i, (board, pid) in enumerate(cases):
            self.assertToolError(self.s.call({"board": board, "posting_id": pid}, id_=60 + i), id_=60 + i)

    def test_A5_unknown_posting(self):
        self.assertToolError(self.s.call({"board": "stripe", "posting_id": "1"}), contains="unknown posting")
        self.assertToolError(self.s.call({"board": "plaid", "posting_id": "00000000-0000-0000-0000-000000000000"}),
                             contains="unknown posting")
        # a real Stripe id asked for under the wrong board is unknown there
        self.assertToolError(self.s.call({"board": "databricks", "posting_id": REJECTED[1]}),
                             contains="unknown posting")


# ---------- X: path tricks (§3) ----------
PATH_TRICKS = ["../../../etc/passwd", "..%2F..%2Fetc%2Fpasswd", "/etc/passwd", "..\\..\\FILTER.md", "8172508\u0000",
               "8172508/../8172508", "results.json", "FILTER.md", "~/.ssh/id_rsa", " 8172508", "8172508\n",
               "file:///etc/passwd", RESULTS_REL]


class X_PathTricks(ServerTest):
    def setUp(self):
        super().setUp()
        self.s.initialize()

    def test_X1_path_like_posting_ids_rejected(self):
        for i, pid in enumerate(PATH_TRICKS):
            text = self.assertToolError(self.s.call({"board": "stripe", "posting_id": pid}, id_=70 + i), id_=70 + i)
            self.assertNotIn("root:", text)

    def test_X2_path_like_boards_rejected(self):
        for i, board in enumerate(["../stripe", "stripe/../../", "/", ".", "..", "runs"]):
            self.assertToolError(self.s.call({"board": board, "posting_id": "8172508"}, id_=90 + i), id_=90 + i)

    def test_X3_path_like_tool_names_are_unknown_tools(self):
        r = self.s.call({"board": "stripe", "posting_id": "8172508"}, name="../score_posting", id_=3)
        self.assertError(r, -32602, 3)


# ---------- B: declared boundaries (§3, §5) ----------
AUDIT_WRAPPER = r"""
import json, runpy, sys
log = open(sys.argv[1], "w", buffering=1)
WATCH = ("open", "os.mkdir", "os.remove", "os.rename", "os.rmdir", "os.chmod", "os.truncate", "shutil.",
         "socket.", "subprocess.", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork", "os.kill",
         "urllib.", "http.", "ftplib.", "smtplib.", "ctypes.")
def hook(event, args):
    if event.startswith(WATCH):
        log.write(json.dumps([event, [a if isinstance(a, (int, str)) or a is None else repr(a) for a in args]],
                             default=str) + "\n")
sys.addaudithook(hook)
server = sys.argv[2]
sys.argv = [server]
runpy.run_path(server, run_name="__main__")
"""


class B_Boundaries(unittest.TestCase):
    def session(self, argv=None, cwd=HERE):
        s = Session(argv, cwd)
        self.addCleanup(s.close)
        return s

    def test_B1_imports_exclude_network_and_process_modules(self):
        tree = ast.parse(SERVER.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                imported.add((node.module or "").split(".")[0])
        self.assertFalse(imported & FORBIDDEN_MODULES, imported & FORBIDDEN_MODULES)
        calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertFalse(calls & {"eval", "exec", "compile", "__import__"})
        attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        # (str/list methods named "replace" or "remove" are allowed; file removal shows up in B2's audit events)
        self.assertFalse(attrs & {"system", "popen", "execv", "execve", "spawnv", "fork", "unlink", "rmtree",
                                  "rename", "chmod", "urlopen", "create_connection"})

    def test_B2_runtime_audit_events_only_expected(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "audit.jsonl"
            s = self.session([sys.executable, "-c", AUDIT_WRAPPER, str(log), str(SERVER)])
            s.initialize()
            s.request("tools/list", id_=1)
            s.call({"board": SHORTLISTED[0], "posting_id": SHORTLISTED[1]}, id_=2)
            for i, pid in enumerate(PATH_TRICKS):
                s.call({"board": "stripe", "posting_id": pid}, id_=10 + i)
            s.call({"board": "../stripe", "posting_id": "1"}, id_=50)
            s.call({"board": "stripe", "posting_id": "1"}, name="read_file", id_=51)
            s.send("not json")
            s.recv()
            self.assertEqual(s.close(), 0)
            events = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
        stdlib = tuple({str(Path(p).resolve()) for p in (sys.base_prefix, sys.prefix, sys.exec_prefix)})
        unexpected, opened_results, opened_transcript = [], 0, 0
        for event, args in events:
            if event == "open":
                path = Path(str(args[0])).resolve() if isinstance(args[0], str) else None
                mode, flags = args[1], args[2] if len(args) > 2 else None
                if path is None:
                    unexpected.append((event, args))
                elif path == RESULTS.resolve() and (mode in ("r", "rb") or (mode is None and flags in (0, os.O_RDONLY))):
                    opened_results += 1
                elif path.parent == TRANSCRIPTS.resolve() and (
                        (isinstance(mode, str) and "x" in mode)
                        or (mode is None and isinstance(flags, int) and flags & os.O_EXCL and flags & os.O_CREAT)):
                    opened_transcript += 1
                elif str(path).startswith(stdlib) or path == SERVER.resolve() or path.parent.name == "__pycache__":
                    pass  # interpreter and module loading
                else:
                    unexpected.append((event, args))
            elif event == "os.mkdir" and Path(str(args[0])).resolve() == TRANSCRIPTS.resolve():
                pass
            else:
                unexpected.append((event, args))
        self.assertEqual(unexpected, [])
        self.assertGreaterEqual(opened_results, 1)
        self.assertEqual(opened_transcript, 1)

    def test_B3_transcript_records_every_line_both_ways(self):
        s = self.session()
        s.initialize()
        s.request("tools/list", id_=1)
        s.call({"board": SHORTLISTED[0], "posting_id": SHORTLISTED[1]}, id_=2)
        s.send("not json")
        s.recv()
        self.assertEqual(s.close(), 0)
        path = s.transcript_path()
        self.assertIsNotNone(path, "the server did not report its transcript path on stderr")
        self.assertEqual(path.parent, TRANSCRIPTS.resolve())
        entries = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        self.assertTrue(all({"t", "dir", "line"} <= set(e) for e in entries))
        self.assertEqual([e["line"] for e in entries if e["dir"] == "in"], s.sent)
        self.assertEqual([e["line"] for e in entries if e["dir"] == "out"], s.received)

    def test_B4_oversized_line_recorded_truncated(self):
        s = self.session()
        s.initialize()
        big = json.dumps({"jsonrpc": "2.0", "id": 8, "method": "ping", "params": {"pad": "y" * 70000}})
        s.send(big)
        s.recv()
        s.close()
        entries = [json.loads(line) for line in s.transcript_path().read_text(encoding="utf-8").splitlines()]
        big_entries = [e for e in entries if e["dir"] == "in" and e.get("truncated")]
        self.assertEqual(len(big_entries), 1)
        e = big_entries[0]
        self.assertEqual(e["length"], len(big.encode("utf-8")))
        self.assertEqual(e["sha256"], hashlib.sha256(big.encode("utf-8")).hexdigest())
        self.assertEqual(e["line"], big[:1024])

    def test_B5_each_session_new_transcript(self):
        a, b = self.session(), self.session()
        a.initialize()
        b.initialize()
        a.close()
        b.close()
        self.assertIsNotNone(a.transcript_path())
        self.assertNotEqual(a.transcript_path(), b.transcript_path())

    def test_B6_refuses_to_start_if_results_file_changed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tool").mkdir()
            shutil.copy2(SERVER, root / "tool" / "server.py")
            fake = root / RESULTS_REL
            fake.parent.mkdir(parents=True)
            fake.write_text('{"results": []}', encoding="utf-8")
            s = self.session([sys.executable, str(root / "tool" / "server.py")], cwd=root)
            s.send({"jsonrpc": "2.0", "id": 0, "method": "initialize",
                    "params": {"protocolVersion": PROTOCOL, "capabilities": {}, "clientInfo": {"name": "t", "version": "1"}}})
            code = s.close()
            self.assertNotEqual(code, 0)
            self.assertEqual(s.buf, b"", "a refusing server must write nothing to stdout")
            self.assertIn("sha256", s.stderr.lower())


if __name__ == "__main__":
    unittest.main()
