"""The JS3 MCP server (job_agent/mcp_server.py): the lifecycle, the error codes, the one tool, the requests a client
is not entitled to, read-only behavior, and the transcript.

Every saved answer here is a CONSTRUCTED fixture written into a temporary copy of the repo, except where a test says it
reads the real saved answers. The process tests run the documented command, python3 -B -m job_agent.mcp_server, in
that copy, with a small environment that does not stop bytecode writes by itself, so only -B and the code decide what
gets written.
"""

import gzip
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from job_agent import filter as flt
from job_agent import filter_run, mcp_server, providers
from job_agent.errors import Refused
from job_agent.mcp_server import BOARDS, MAX_CALLS, Server

from .loop_helpers import REPO, ashby_job, body, greenhouse_job, lever_job
from .test_filter_run import save

RUN_ID = "2026-11-20T000000Z"
KEPT_ID = "11111111-1111-4111-8111-111111111111"
REJECTED_ID = "22222222-2222-4222-8222-222222222222"
HIDDEN_ID = "33333333-3333-4333-8333-333333333333"
LEVER_ID = "44444444-4444-4444-8444-444444444444"
UNKNOWN_ID = "00000000-0000-4000-8000-000000000000"
GOOD = "We build APIs and design SQL schemas for our backend."
CHILD_ENV = {"PATH": "/usr/bin:/bin", "LANG": "en_US.UTF-8"}
INIT = {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}}
COMMAND = [sys.executable, "-B", "-m", "job_agent.mcp_server"]


def fixture_repo(root: Path) -> Path:
    """A copy of the code, the persona and FILTER.md, with constructed saved answers for the three real boards."""
    shutil.copytree(REPO / "job_agent", root / "job_agent", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(REPO / "persona", root / "persona")
    shutil.copy2(REPO / "FILTER.md", root / "FILTER.md")
    runs = root / "runs"
    ashby = [ashby_job(KEPT_ID, descriptionPlain=GOOD), ashby_job(REJECTED_ID, title="Senior Software Engineer"),
             ashby_job(HIDDEN_ID, title="Software Engineer, Hidden", descriptionPlain="We build APIs\u200b in Go.")]
    save(runs, RUN_ID, "ashby-openai", body("ashby", ashby))
    save(runs, RUN_ID, "greenhouse-verkada", body("greenhouse", [greenhouse_job(7)]))
    save(runs, RUN_ID, "lever-palantir", body("lever", [lever_job(LEVER_ID)]))
    (root / "js3" / "mcp" / "transcripts").mkdir(parents=True)
    return root


def snapshot(root: Path) -> dict:
    """Every folder's modification time and every file's size, modification time and SHA-256."""
    state = {}
    for folder, _, files in os.walk(root):
        rel = os.path.relpath(folder, root)
        state[rel + "/"] = os.stat(folder).st_mtime_ns
        for name in files:
            path = os.path.join(folder, name)
            with open(path, "rb") as handle:
                state[os.path.join(rel, name)] = (os.lstat(path).st_size, os.lstat(path).st_mtime_ns,
                                                  hashlib.sha256(handle.read()).hexdigest())
    return state


def req(rid, method, params=None):
    message = {"jsonrpc": "2.0", "id": rid, "method": method}
    if params is not None:
        message["params"] = params
    return message


def note(method, params=None):
    message = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        message["params"] = params
    return message


def call(rid, arguments, name="score_posting"):
    return req(rid, "tools/call", {"name": name, "arguments": arguments})


def args(board="ashby-openai", posting_id=KEPT_ID, **extra):
    return {"board": board, "posting_id": posting_id, **extra}


def code(answer):
    return answer["error"]["code"]


def text(answer):
    return answer["result"]["content"][0]["text"]


def payload(answer):
    return json.loads(text(answer))


class Fixture(unittest.TestCase):
    def setUp(self):
        self.root = fixture_repo(Path(tempfile.mkdtemp(prefix="job-agent-mcp-")))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def ready(self) -> Server:
        server = Server(self.root)
        server.handle(req(1, "initialize", INIT))
        server.handle(note("notifications/initialized"))
        return server


class LifecycleTest(Fixture):
    def test_a_fresh_server_refuses_every_request_but_initialize(self):
        server = Server(self.root)
        for rid, method in enumerate(("tools/list", "tools/call", "resources/read", "bad"), 1):
            answer = server.handle(req(rid, method, {}))
            self.assertEqual((code(answer), answer["id"]), (-32000, rid), method)
        self.assertEqual((server.initialized, server.ready), (False, False))

    def test_a_notification_before_initialize_changes_nothing(self):
        server = Server(self.root)
        self.assertIsNone(server.handle(note("notifications/initialized")))
        self.assertFalse(server.ready)
        server.handle(req(1, "initialize", INIT))
        self.assertEqual(code(server.handle(req(2, "tools/list"))), -32000)

    def test_tools_wait_for_the_initialized_notification(self):
        server = Server(self.root)
        self.assertIn("result", server.handle(req(1, "initialize", INIT)))
        self.assertEqual((server.initialized, server.ready), (True, False))
        answer = server.handle(req(2, "tools/list"))
        self.assertEqual(code(answer), -32000)
        self.assertIn("not ready", answer["error"]["message"])
        self.assertEqual(code(server.handle(call(3, args()))), -32000)
        self.assertIsNone(server.handle(note("notifications/initialized")))
        self.assertTrue(server.ready)
        self.assertIn("result", server.handle(req(4, "tools/list")))

    def test_initialize_is_accepted_once(self):
        server = self.ready()
        answer = server.handle(req(2, "initialize", INIT))
        self.assertEqual(code(answer), -32000)
        self.assertEqual((server.initialized, server.ready), (True, True))

    def test_initialize_needs_its_params(self):
        server = Server(self.root)
        for params in (None, [], {}, {**INIT, "protocolVersion": 7}, {**INIT, "clientInfo": {"name": "x"}},
                       {k: v for k, v in INIT.items() if k != "capabilities"}):
            answer = server.handle(req(1, "initialize", params))
            self.assertEqual(code(answer), -32602, params)
            self.assertFalse(server.initialized)
        self.assertIn("result", server.handle(req(2, "initialize", INIT)))

    def test_the_version_answer_is_the_one_supported_version(self):
        for requested in ("2025-11-25", "2024-11-05", "not-a-version"):
            result = Server(self.root).handle(req(1, "initialize", {**INIT, "protocolVersion": requested}))["result"]
            self.assertEqual(result["protocolVersion"], "2025-11-25")
            self.assertEqual(result["capabilities"], {"tools": {"listChanged": False}})
            self.assertEqual(result["serverInfo"]["name"], "job-search-agent")
            self.assertNotIn("instructions", result)  # no server text goes into the client's context

    def test_a_request_named_like_the_notification_is_not_the_notification(self):
        server = Server(self.root)
        server.handle(req(1, "initialize", INIT))
        self.assertEqual(code(server.handle(req(2, "notifications/initialized"))), -32000)
        self.assertFalse(server.ready)


class MessageTest(Fixture):
    def test_parse_errors_have_id_null(self):
        server = self.ready()
        for line in (b"{", b'{"jsonrpc": "2.0", "id": 1, "method": "tools/list"', b"\xff\xfe not UTF-8",
                     b"[" * 20000, b'{"jsonrpc": "2.0", "id": NaN, "method": "tools/list"}', b"\xef\xbb\xbf{}"):
            answer = server.handle_line(line)
            self.assertEqual((code(answer), answer["id"]), (-32700, None), line[:40])

    def test_invalid_requests_have_id_null(self):
        server = self.ready()
        for message in ({}, [], [req(1, "tools/list")], "tools/list", {"jsonrpc": "1.0", "id": 1, "method": "x"},
                        {"jsonrpc": "2.0", "id": 1}, {"jsonrpc": "2.0", "id": 1, "method": ""},
                        {"jsonrpc": "2.0", "id": None, "method": "tools/list"},
                        {"jsonrpc": "2.0", "id": True, "method": "tools/list"},
                        {"jsonrpc": "2.0", "id": 1.5, "method": "tools/list"},
                        {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": "x"},
                        {"jsonrpc": "2.0", "id": 1, "result": {}}):
            answer = server.handle(message)
            self.assertEqual((code(answer), answer["id"]), (-32600, None), message)

    def test_notifications_are_never_answered_and_a_tool_call_without_id_never_runs(self):
        server = self.ready()
        for message in (note("notifications/initialized"), note("notifications/cancelled", {"requestId": 1}),
                        note("notifications/anything"), note("tools/call", {"name": "score_posting",
                                                                            "arguments": args()})):
            self.assertIsNone(server.handle(message))
            self.assertIsNone(server.handle_line(json.dumps(message).encode("utf-8")))
        self.assertEqual(server.calls, 0)

    def test_ids_come_back_exactly(self):
        server = self.ready()
        for rid in ("a-1", 0, 7, 2 ** 40):
            self.assertIs(type(server.handle(req(rid, "tools/list"))["id"]), type(rid))
            self.assertEqual(server.handle(req(rid, "tools/list"))["id"], rid)

    def test_unknown_methods_after_ready_are_method_not_found(self):
        server = self.ready()
        for method in ("resources/read", "resources/list", "prompts/list", "ping", "update_state"):
            self.assertEqual(code(server.handle(req(9, method, {"uri": "file:///etc/passwd"}))), -32601, method)

    def test_an_internal_error_is_answered_on_stderr_and_does_not_end_the_server(self):
        server = self.ready()
        original = mcp_server.score_posting
        mcp_server.score_posting = lambda *a: 1 / 0
        self.addCleanup(setattr, mcp_server, "score_posting", original)
        stderr = sys.stderr
        sys.stderr = open(os.devnull, "w")
        self.addCleanup(lambda: (sys.stderr.close(), setattr(sys, "stderr", stderr)))
        answer = server.handle_line(json.dumps(call(5, args())).encode("utf-8"))
        self.assertEqual((code(answer), answer["id"]), (-32603, 5))
        self.assertIn("result", server.handle(req(6, "tools/list")))


class ToolTest(Fixture):
    def test_tools_list_advertises_one_read_only_tool(self):
        tools = self.ready().handle(req(2, "tools/list"))["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting"])
        schema = tools[0]["inputSchema"]
        self.assertEqual(schema["properties"]["board"]["enum"], list(BOARDS))
        self.assertEqual(schema["required"], ["board", "posting_id"])
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(schema["properties"]["posting_id"]["pattern"], "^(?:" + mcp_server.POSTING_ID_PATTERN + ")$")
        self.assertEqual(tools[0]["annotations"], {"readOnlyHint": True, "openWorldHint": False})

    def test_a_kept_posting_gives_its_record(self):
        answer = self.ready().handle(call(2, args()))
        self.assertIs(answer["result"]["isError"], False)
        data = payload(answer)
        posting = providers.read("ashby", 200, body("ashby", [ashby_job(KEPT_ID, descriptionPlain=GOOD)]))[0]
        expected = flt.judge(posting, flt.load_profile(self.root / "persona" / "jane-doe.json"),
                             flt.load_rules(self.root / "FILTER.md", version="1.0"), board="ashby-openai")
        self.assertEqual(data["record"], json.loads(json.dumps(expected)))
        self.assertEqual(data["summary"], {"fate": "kept", "deciding_rule": None, "deciding_quote": None,
                                           "score": 65, "cannot_tell": None})
        self.assertEqual(sorted(data["record"]["topics"]), ["APIs", "Backend", "Databases"])
        self.assertEqual((data["source"]["run"], data["source"]["postings_in_answer"], data["source"]["live"]),
                         (RUN_ID, 3, False))
        self.assertEqual(data["source"]["saved_answer"], f"runs/{RUN_ID}/boards/ashby-openai/attempt-1.json.gz")
        self.assertEqual(data["filter"]["version"], "1.0")
        self.assertEqual(data["filter"]["sha256"], hashlib.sha256((self.root / "FILTER.md").read_bytes()).hexdigest())

    def test_a_rejected_posting_gives_its_deciding_rule_and_quote(self):
        data = payload(self.ready().handle(call(2, args(posting_id=REJECTED_ID))))
        self.assertEqual((data["summary"]["fate"], data["summary"]["deciding_rule"], data["summary"]["deciding_quote"]),
                         ("rejected", "R3", "Senior Software Engineer"))
        self.assertIsNone(data["summary"]["score"])

    def test_the_other_boards_are_read_too(self):
        server = self.ready()
        self.assertEqual(payload(server.handle(call(2, args("greenhouse-verkada", "7"))))["record"]["fate"], "kept")
        self.assertEqual(payload(server.handle(call(3, args("lever-palantir", LEVER_ID))))["record"]["fate"], "kept")

    def test_an_unknown_posting_is_a_tool_result_marked_as_an_error(self):
        answer = self.ready().handle(call(2, args(posting_id=UNKNOWN_ID)))
        self.assertNotIn("error", answer)
        self.assertIs(answer["result"]["isError"], True)
        self.assertIn(f"is not in the newest saved answer of board ashby-openai (run {RUN_ID}, 3 postings)",
                      text(answer))

    def test_an_unknown_tool_or_a_call_that_fails_its_request_schema_is_a_protocol_error(self):
        server = self.ready()
        answer = server.handle(call(2, args(), name="update_state"))
        self.assertEqual((code(answer), answer["error"]["message"]), (-32602, "Unknown tool: update_state"))
        for params in ([], {"arguments": args()}, {"name": 5}, {"name": "score_posting", "arguments": ["x"]},
                       {"name": "score_posting", "arguments": "x"}):
            self.assertEqual(code(server.handle(req(3, "tools/call", params))), -32602, params)
        self.assertEqual(code(server.handle(req(4, "tools/list", []))), -32602)

    def test_arguments_that_fail_the_input_schema_are_tool_errors_that_never_echo_the_value(self):
        server = self.ready()
        cases = {"extra": args(profile="private/real-resume.json"), "missing": {"board": "ashby-openai"},
                 "board not listed": args(board="greenhouse-no-such-board-js2-test"), "board a list": args(board=["x"]),
                 "traversal": args(posting_id="../../../../etc/passwd"), "newline": args(posting_id=KEPT_ID + "\n"),
                 "upper case": args(posting_id="ABCDEF12-1111-4111-8111-111111111111"), "a number": args(posting_id=7), "empty": {}}
        for label, arguments in cases.items():
            answer = server.handle(call(2, arguments))
            self.assertIs(answer["result"]["isError"], True, label)
            self.assertTrue(text(answer).startswith("Invalid arguments for score_posting"), label)
            for value in ("etc/passwd", "private/real-resume", "no-such-board"):
                self.assertNotIn(value, text(answer), label)
        self.assertIn("not allowed: profile", text(server.handle(call(3, cases["extra"]))))

    def test_a_board_without_a_saved_answer_or_with_a_broken_one_is_a_tool_error(self):
        shutil.rmtree(self.root / "runs" / RUN_ID / "boards" / "lever-palantir")
        answer = self.ready().handle(call(2, args("lever-palantir", LEVER_ID)))
        self.assertIs(answer["result"]["isError"], True)
        self.assertIn("no saved HTTP 200 answer", text(answer))
        path = self.root / "runs" / RUN_ID / "boards" / "greenhouse-verkada" / "attempt-1.json.gz"
        path.write_bytes(gzip.compress(b'{"jobs": []}', mtime=0))
        answer = self.ready().handle(call(3, args("greenhouse-verkada", "7")))
        self.assertIs(answer["result"]["isError"], True)
        self.assertIn("SHA-256", text(answer))
        self.assertNotIn(str(self.root.resolve()), text(answer))  # paths are shown relative to the repo
        path.write_bytes(b"\x1f\x8b\x08 a broken gzip stream")
        answer = self.ready().handle(call(4, args("greenhouse-verkada", "7")))
        self.assertIs(answer["result"]["isError"], True)

    def test_hidden_characters_are_dropped_from_the_result(self):
        posting = providers.read("ashby", 200, body("ashby", [ashby_job(
            HIDDEN_ID, title="Software Engineer, Hidden", descriptionPlain="We build APIs\u200b in Go.")]))[0]
        own = flt.judge(posting, flt.load_profile(), flt.load_rules(version="1.0"), board="ashby-openai")
        self.assertIn("\u200b", own["topics"]["APIs"]["sentence"])  # the filter keeps it; the server must not
        answer = self.ready().handle(call(2, args(posting_id=HIDDEN_ID)))
        self.assertNotIn("\u200b", text(answer))
        self.assertEqual(payload(answer)["record"]["topics"]["APIs"]["sentence"], "We build APIs in Go.")

    def test_a_session_answers_at_most_max_calls_tool_calls(self):
        server = self.ready()
        for n in range(MAX_CALLS):
            server.handle(call(n + 2, {}))
        answer = server.handle(call(99, args()))
        self.assertIs(answer["result"]["isError"], True)
        self.assertIn(f"budget of {MAX_CALLS} tool calls", text(answer))

    def test_the_boards_are_the_real_boards_of_boards_json(self):
        listed = json.loads((REPO / "boards.json").read_text(encoding="utf-8"))["boards"]
        real = {f"{b['system']}-{b['name']}": {k: b[k] for k in ("system", "name", "company")} for b in listed
                if not b.get("deliberate_failure")}
        self.assertEqual(BOARDS, real)

    @unittest.skipUnless((REPO / "runs").exists(), "no saved runs in this copy of the repo")
    def test_every_id_in_the_real_saved_answers_fits_the_pattern(self):
        boards = [dict(b) for b in BOARDS.values()]
        for source in filter_run.newest_answers(REPO / "runs", boards):
            if source["run"] is None:
                continue
            ids = [p["id"] for p in providers.read(source["system"], 200, source["body"])]
            self.assertTrue(ids)
            self.assertEqual([i for i in ids if not mcp_server.POSTING_ID.fullmatch(i)], [], source["key"])


class TranscriptGuardTest(Fixture):
    def refused(self, given, cwd=None):
        with self.assertRaises(Refused, msg=given):
            mcp_server.transcript_path(given, self.root, cwd=cwd or self.root)

    def test_a_jsonl_file_directly_inside_the_folder_is_allowed(self):
        folder = (self.root / "js3" / "mcp" / "transcripts").resolve()
        self.assertEqual(mcp_server.transcript_path("js3/mcp/transcripts/a.jsonl", self.root, cwd=self.root),
                         folder / "a.jsonl")
        self.assertEqual(mcp_server.transcript_path(str(folder / "b.jsonl"), self.root), folder / "b.jsonl")

    def test_every_other_path_is_refused(self):
        outside = Path(tempfile.mkdtemp(prefix="job-agent-mcp-outside-"))
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        (self.root / "js3" / "mcp" / "transcripts-evil").mkdir()
        (self.root / "js3" / "mcp" / "transcripts" / "sub").mkdir()
        (self.root / "js3" / "mcp" / "transcripts" / "dir.jsonl").mkdir()
        os.symlink(outside / "x.jsonl", self.root / "js3" / "mcp" / "transcripts" / "link.jsonl")
        for given in (str(outside / "x.jsonl"), "js3/mcp/transcripts/../x.jsonl", "js3/mcp/transcripts/x.txt",
                      "js3/mcp/transcripts/x", "js3/mcp/transcripts-evil/x.jsonl", "js3/mcp/transcripts/sub/x.jsonl",
                      "js3/mcp/transcripts/dir.jsonl", "js3/mcp/transcripts/link.jsonl", "x.jsonl",
                      "state/seen.jsonl"):
            self.refused(given)
        self.assertFalse((outside / "x.jsonl").exists())

    def test_a_transcripts_folder_that_is_a_link_or_missing_is_refused(self):
        folder = self.root / "js3" / "mcp" / "transcripts"
        shutil.rmtree(folder)
        self.refused("js3/mcp/transcripts/a.jsonl")
        outside = Path(tempfile.mkdtemp(prefix="job-agent-mcp-outside-"))
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        os.symlink(outside, folder)
        self.refused("js3/mcp/transcripts/a.jsonl")

    def test_main_refuses_before_reading_anything(self):
        stdin, stdout = BytesIO(json.dumps(req(1, "initialize", INIT)).encode("utf-8") + b"\n"), BytesIO()
        stderr = sys.stderr
        sys.stderr = open(os.devnull, "w")
        try:
            status = mcp_server.main(["--transcript", "/tmp/job-agent-mcp-never.jsonl"], stdin, stdout, self.root)
        finally:
            sys.stderr.close()
            sys.stderr = stderr
        self.assertEqual((status, stdout.getvalue(), stdin.tell()), (3, b"", 0))
        self.assertFalse(Path("/tmp/job-agent-mcp-never.jsonl").exists())


SESSION = [json.dumps(m).encode("utf-8") for m in (
    req(1, "tools/list"), req(2, "initialize", INIT), note("notifications/initialized"), req(3, "tools/list"),
    call(4, args()), call(5, args(posting_id=REJECTED_ID)), call(6, args(posting_id=UNKNOWN_ID)),
    call(7, args(), name="update_state"), call(8, args(profile="x")), call(9, args(posting_id="../../etc/passwd")),
    req(10, "resources/read", {"uri": "file:///etc/passwd"}),
    note("tools/call", {"name": "score_posting", "arguments": args()}))] + [b'{"jsonrpc": "2.0", "id": 11', b"\xff"]
ANSWERED = 12  # every line but the two notifications


class ProcessTest(Fixture):
    """The real process, as a client starts it, in the fixture copy."""

    def run_server(self, *extra, lines=SESSION):
        return subprocess.run(COMMAND + list(extra), cwd=str(self.root), env=CHILD_ENV, capture_output=True,
                              input=b"".join(line + b"\n" for line in lines), timeout=60)

    def protocol_lines(self, stdout: bytes) -> list:
        lines = stdout.decode("utf-8").splitlines()
        for line in lines:
            message = json.loads(line)
            self.assertEqual(message["jsonrpc"], "2.0")
            self.assertEqual(len({"result", "error"} & set(message)), 1)
        return lines

    def test_without_transcript_nothing_is_written_and_stdout_carries_protocol_only(self):
        before = snapshot(self.root)
        done = self.run_server()
        self.assertEqual((done.returncode, done.stderr), (0, b""))
        self.assertEqual(len(self.protocol_lines(done.stdout)), ANSWERED)
        self.assertEqual(snapshot(self.root), before)

    def test_with_transcript_only_that_file_is_written_and_it_holds_every_line_in_order(self):
        before = snapshot(self.root)
        done = self.run_server("--transcript", "js3/mcp/transcripts/t.jsonl")
        self.assertEqual((done.returncode, done.stderr), (0, b""))
        after = snapshot(self.root)
        changed = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
        self.assertEqual(changed, {"js3/mcp/transcripts/", "js3/mcp/transcripts/t.jsonl"})
        entries = [json.loads(line) for line in (self.root / "js3/mcp/transcripts/t.jsonl").read_text().splitlines()]
        self.assertEqual((entries[0]["event"], entries[-1]["event"], entries[-1]["reason"]),
                         ("start", "end", "stdin closed"))
        received = [e["text"] for e in entries if e.get("dir") == "in"]
        self.assertEqual(received, [line.decode("utf-8", "backslashreplace") for line in SESSION])
        self.assertEqual([e["text"] for e in entries if e.get("dir") == "out"], self.protocol_lines(done.stdout))
        self.assertEqual([e.get("utf8", True) for e in entries if e.get("dir") == "in"][-1], False)
        order = [e["dir"] for e in entries if "dir" in e]
        self.assertEqual(order[:4], ["in", "out", "in", "out"])  # each answer right after the line it answers
        self.assertEqual(len(order), len(SESSION) + ANSWERED)
        times = [e["at"] for e in entries]
        self.assertEqual(times, sorted(times))

    def test_a_refused_transcript_path_stops_before_anything_is_read_or_written(self):
        outside = Path(tempfile.mkdtemp(prefix="job-agent-mcp-outside-"))
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        before = snapshot(self.root)
        for given in (str(outside / "x.jsonl"), "js3/mcp/transcripts/../../../x.jsonl", "js3/mcp/transcripts/x.md"):
            done = self.run_server("--transcript", given)
            self.assertEqual((done.returncode, done.stdout), (3, b""), given)
            self.assertIn(b"refused", done.stderr)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertEqual(snapshot(self.root), before)

    def test_sigterm_ends_the_session_and_the_transcript_says_so(self):
        proc = subprocess.Popen(COMMAND + ["--transcript", "js3/mcp/transcripts/term.jsonl"], cwd=str(self.root),
                                env=CHILD_ENV, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: proc.poll() is None and proc.kill())
        proc.stdin.write(json.dumps(req(1, "initialize", INIT)).encode("utf-8") + b"\n")
        proc.stdin.flush()
        self.assertIn(b'"id": 1', proc.stdout.readline())
        proc.send_signal(signal.SIGTERM)
        self.assertEqual(proc.wait(timeout=20), 0)
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            stream.close()
        entries = [json.loads(line) for line in (self.root / "js3/mcp/transcripts/term.jsonl").read_text().splitlines()]
        self.assertEqual((entries[-1]["event"], entries[-1]["reason"]), ("end", "SIGTERM"))


if __name__ == "__main__":
    unittest.main()
