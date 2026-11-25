"""tools/mcp_server.py, run as a subprocess and spoken to over stdio, one JSON line per message.

Each test sends real protocol lines and reads real replies. The safety tests run the server
under a wrapper that installs a CPython audit hook (sys.addaudithook) before the server
starts, and replaces the socket constructors with ones that record and refuse. The hook sees
every file open, mkdir, rename, remove and socket event in the process, including ones made by
code the server imports.

Test transcripts go to evidence/mcp/test-runs/ (gitignored) and are deleted after each test.
"""

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

from agent import PROJECT_DIR
from agent import filter as flt
from tools import mcp_server

SERVER = PROJECT_DIR / "tools" / "mcp_server.py"
LOG_ROOT = PROJECT_DIR / "evidence" / "mcp"
TEST_LOG = LOG_ROOT / "test-runs"
RUN = PROJECT_DIR / "evidence" / "runs" / "live-text-1"

NOTION_KEEP = "85947779-6b87-466a-98bc-30a640448c28"  # v0.2 keep: "Software Engineer, Early Career (AI)"
STRIPE_REJECT = "8144196"                              # v0.2 reject at G4: "AI Engineer", "4+ years"

EXPECTED_TOOL = {
    "name": "score_posting",
    "description": ("Score one saved posting against FILTER.md v0.2. Read-only; uses the committed corpus "
                    "evidence/runs/live-text-1; no network. Also reads the fictional persona file "
                    "../js1-contract-and-watch/persona/cole-palmer.example.json. Every call's arguments and "
                    "results are logged to evidence/mcp/."),
    "inputSchema": {
        "type": "object",
        "properties": {
            "board": {"type": "string", "enum": ["greenhouse/stripe", "ashby/notion", "ashby/linear"]},
            "posting_id": {"type": "string"},
        },
        "required": ["board", "posting_id"],
        "additionalProperties": False,
    },
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
}

INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                   "clientInfo": {"name": "pytest", "version": "0"}}}
INITIALIZED = {"jsonrpc": "2.0", "method": "notifications/initialized"}


def call(id_, board, posting_id, **extra):
    return {"jsonrpc": "2.0", "id": id_, "method": "tools/call",
            "params": {"name": "score_posting", "arguments": {"board": board, "posting_id": posting_id, **extra}}}


# The wrapper runs before the server: audit hook first, then socket refused, then the server.
WRAPPER = r"""
import atexit, json, os, sys
events = []
WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC
def hook(event, args):
    if event == "open":
        path, mode, flags = args
        events.append({"event": "open", "path": str(path), "write": bool((flags or 0) & WRITE_FLAGS)})
    elif event in ("os.mkdir", "os.rename", "os.remove", "os.rmdir", "os.symlink", "os.link",
                   "os.truncate", "os.chmod", "shutil.rmtree", "shutil.move", "shutil.copyfile"):
        events.append({"event": event, "path": str(args[0])})
    elif event.startswith(("socket.", "subprocess.", "os.system", "os.exec", "os.posix_spawn",
                           "os.fork", "urllib.", "http.client.")):
        events.append({"event": event, "path": None})
sys.addaudithook(hook)
import socket
def refuse(*a, **k):
    events.append({"event": "patched-socket-call", "path": None})
    raise OSError("network refused by test")
for name in ("socket", "create_connection", "create_server", "getaddrinfo", "socketpair", "fromfd"):
    setattr(socket, name, refuse)
atexit.register(lambda: sys.stderr.write("AUDIT-JSON " + json.dumps(events) + "\n"))
import runpy
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
"""


@dataclass
class Session:
    proc: subprocess.CompletedProcess
    replies: list
    transcripts: list

    def audit(self) -> list[dict]:
        line = next(l for l in self.proc.stderr.decode().splitlines() if l.startswith("AUDIT-JSON "))
        return json.loads(line[len("AUDIT-JSON "):])

    def tool_payload(self, id_) -> dict:
        reply = next(r for r in self.replies if r.get("id") == id_)
        assert reply["result"]["isError"] is False, reply
        content = reply["result"]["content"]
        assert len(content) == 1 and content[0]["type"] == "text"
        return json.loads(content[0]["text"])


def run_session(*lines, wrapper=False, env=None, log_dir=TEST_LOG) -> Session:
    before = set(TEST_LOG.glob("transcript-*.jsonl"))
    data = b"".join((l if isinstance(l, bytes) else (l if isinstance(l, str) else json.dumps(l)).encode()) + b"\n"
                    for l in lines)
    # No -B: the server must keep bytecode out of the tree on its own, as it does under mcp-config.json.
    head = [sys.executable, "-c", WRAPPER] if wrapper else [sys.executable]
    proc = subprocess.run(head + [str(SERVER), "--log-dir", str(log_dir)], input=data, capture_output=True,
                          timeout=120, cwd=PROJECT_DIR, env=env)
    replies = [json.loads(l) for l in proc.stdout.splitlines() if l.strip()]
    return Session(proc, replies, sorted(set(TEST_LOG.glob("transcript-*.jsonl")) - before))


@pytest.fixture(autouse=True)
def clean_test_transcripts():
    before = set(TEST_LOG.glob("transcript-*.jsonl"))
    yield
    for path in set(TEST_LOG.glob("transcript-*.jsonl")) - before:
        path.unlink()
    if TEST_LOG.exists() and not any(TEST_LOG.iterdir()):
        TEST_LOG.rmdir()
    if LOG_ROOT.exists() and not any(LOG_ROOT.iterdir()):
        LOG_ROOT.rmdir()


@pytest.fixture(scope="module")
def filter_v02(tmp_path_factory):
    """agent.filter's own v0.2 run over the committed corpus, keyed by (board, str(id))."""
    out = tmp_path_factory.mktemp("filter-v02")
    flt.run_filter(RUN, out, mode="v0.2")
    rows = [json.loads(l) for l in (out / "results.jsonl").read_text().splitlines()]
    return {(r["board"], str(r["id"])): r for r in rows}


def records(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines()]


def tree(root: Path) -> dict:
    out = {}
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            p = Path(dirpath) / name
            st = p.lstat()
            out[str(p.relative_to(root))] = (st.st_size, st.st_mtime_ns)
    return out


# ---------- handshake and listing ----------

def test_initialize_handshake_echoes_supported_version_and_states_its_own_otherwise():
    s = run_session(INIT, INITIALIZED, {"jsonrpc": "2.0", "id": 2, "method": "ping"},
                    {**INIT, "id": 3, "params": {**INIT["params"], "protocolVersion": "1999-01-01"}})
    assert s.proc.returncode == 0
    assert [r["id"] for r in s.replies] == [1, 2, 3]  # notifications/initialized got no reply
    first = s.replies[0]["result"]
    assert first == {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}},
                     "serverInfo": {"name": "js3-filter", "version": "0.1.0"}}
    assert s.replies[1]["result"] == {}
    assert s.replies[2]["result"]["protocolVersion"] == mcp_server.PROTOCOL_VERSIONS[0] == "2025-11-25"


def test_tools_list_declares_exactly_one_tool_with_the_stated_schema():
    s = run_session(INIT, INITIALIZED, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = s.replies[1]["result"]["tools"]
    assert len(tools) == 1
    assert tools[0] == EXPECTED_TOOL


# ---------- the tool ----------

def test_valid_calls_match_agent_filter_v02_result_on_every_board(filter_v02):
    linear_id = next(pid for (board, pid) in filter_v02 if board == "ashby/linear")
    cases = [(10, "ashby/notion", NOTION_KEEP), (11, "greenhouse/stripe", STRIPE_REJECT),
             (12, "ashby/linear", linear_id)]
    s = run_session(INIT, INITIALIZED, *[call(i, b, p) for i, b, p in cases])
    assert s.proc.returncode == 0
    for id_, board, pid in cases:
        got, want = s.tool_payload(id_), filter_v02[(board, pid)]
        for key in ("verdict", "gates", "first_failing_gate", "first_unknown_gate", "score",
                    "near_threshold", "text_status", "text_chars", "title"):
            assert got[key] == want[key], (board, pid, key)
        assert (got["board"], got["posting_id"]) == (board, pid)
        assert got["rules"] == {"mode": "v0.2", "changes": ["C1", "C2", "C3", "C4", "C5", "C6"],
                                "contract": flt.CONTRACT_V02, "filter_md_git_blob": mcp_server.FROZEN_FILTER_BLOB,
                                "frozen_commit": "f3edf99"}
        assert got["corpus"] == {"path": "evidence/runs/live-text-1", "run_id": "run-20261122T042828Z-07c6f0"}
    # the two demo postings really are a keep and a G4 reject, with the matched span shown
    assert s.tool_payload(10)["verdict"] == "keep"
    stripe = s.tool_payload(11)
    assert stripe["verdict"] == "reject" and stripe["first_failing_gate"] == "G4"
    assert "4+ years" in stripe["gates"]["G4"]["matched"]


def test_unknown_id_board_or_bad_arguments_are_tool_errors_not_crashes():
    s = run_session(INIT, INITIALIZED,
                    call(2, "ashby/notion", "no-such-id"),
                    call(3, "lever/acme", "1"),
                    call(4, "greenhouse/stripe", STRIPE_REJECT, extra="x"),
                    {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                     "params": {"name": "score_posting", "arguments": {"board": "greenhouse/stripe", "posting_id": 8144196}}},
                    {"jsonrpc": "2.0", "id": 6, "method": "tools/call",
                     "params": {"name": "score_posting", "arguments": {"board": "greenhouse/stripe"}}},
                    {"jsonrpc": "2.0", "id": 7, "method": "ping"})
    assert s.proc.returncode == 0
    by_id = {r["id"]: r for r in s.replies}
    expected_text = {2: "no posting with id 'no-such-id' on board 'ashby/notion'",
                     3: "unknown board 'lever/acme'",
                     4: "unexpected argument(s): extra",
                     5: "posting_id must be a non-empty string",
                     6: "posting_id must be a non-empty string"}
    for id_, fragment in expected_text.items():
        result = by_id[id_]["result"]
        assert result["isError"] is True, id_
        assert fragment in result["content"][0]["text"], id_
        assert "Traceback" not in result["content"][0]["text"]
    assert by_id[7]["result"] == {}  # still serving after five bad calls


def test_unknown_tool_name_is_invalid_params():
    s = run_session(INIT, {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                           "params": {"name": "delete_everything", "arguments": {}}})
    assert s.replies[1]["error"]["code"] == -32602


def test_filter_md_not_matching_the_frozen_blob_is_refused(tmp_path):
    assert mcp_server.git_blob_sha1(b"hello\n") == "ce013625030ba8dba906f756967f9e9ca394464a"  # git's own value
    assert mcp_server.rules_version()["filter_md_git_blob"] == mcp_server.FROZEN_FILTER_BLOB
    changed = tmp_path / "FILTER.md"
    changed.write_bytes(mcp_server.FILTER_MD.read_bytes() + b"\n")
    with pytest.raises(mcp_server.ToolInputError, match="not the v0.2 frozen at f3edf99"):
        mcp_server.rules_version(changed)


def test_unloadable_corpus_is_a_tool_error(tmp_path):
    server = mcp_server.Server(mcp_server.Corpus(run_dir=tmp_path / "missing"))
    reply = server.handle(json.dumps(call(1, "ashby/notion", NOTION_KEEP)).encode())
    assert reply["result"]["isError"] is True
    assert "cannot load the saved corpus" in reply["result"]["content"][0]["text"]


# ---------- JSON-RPC errors ----------

def test_unknown_method_is_32601_and_unknown_notification_gets_no_reply():
    s = run_session(INIT, {"jsonrpc": "2.0", "id": "abc", "method": "resources/list"},
                    {"jsonrpc": "2.0", "method": "notifications/whatever"},
                    {"jsonrpc": "2.0", "id": 9, "method": "ping"})
    assert [r["id"] for r in s.replies] == [1, "abc", 9]
    assert s.replies[1]["error"]["code"] == -32601
    assert s.replies[1]["error"]["data"] == "resources/list"


def test_malformed_lines_are_32700_and_the_server_keeps_serving():
    s = run_session(INIT, "{not json", b"\xff\xfe not utf-8", '{"jsonrpc": "2.0", "id": 4, "method": "ping"',
                    "[1, 2]", {"jsonrpc": "2.0", "id": 6, "method": "ping"})
    assert s.proc.returncode == 0
    assert [(r["id"], r.get("error", {}).get("code")) for r in s.replies] == [
        (1, None), (None, -32700), (None, -32700), (None, -32700), (None, -32600), (6, None)]


# ---------- safety ----------

def test_server_opens_no_socket_and_runs_no_process():
    s = run_session(INIT, INITIALIZED, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                    call(3, "ashby/notion", NOTION_KEEP), call(4, "ashby/notion", "missing"), wrapper=True)
    assert s.proc.returncode == 0, s.proc.stderr.decode()
    assert s.tool_payload(3)["verdict"] == "keep"  # the session did real work under the hook
    network = [e for e in s.audit() if e["path"] is None]
    assert network == []


def test_server_writes_only_inside_evidence_mcp():
    before = tree(PROJECT_DIR)
    s = run_session(INIT, INITIALIZED, call(2, "ashby/notion", NOTION_KEEP), call(3, "greenhouse/stripe", STRIPE_REJECT),
                    "{bad", wrapper=True)
    after = tree(PROJECT_DIR)
    assert s.proc.returncode == 0, s.proc.stderr.decode()
    changed = {k for k in before.keys() | after.keys() if before.get(k) != after.get(k)}
    assert changed, "expected the transcript to appear"
    assert all(k.startswith("evidence/mcp/") for k in changed), sorted(changed)
    # the audit hook covers the whole filesystem, not just this folder
    log_root = str(LOG_ROOT.resolve())
    writes = [e for e in s.audit() if (e["event"] == "open" and e["write"]) or e["event"].startswith(("os.", "shutil."))]
    assert writes and all(e["path"].startswith(log_root) for e in writes), writes
    opened_for_write = [e["path"] for e in writes if e["event"] == "open"]
    assert opened_for_write == [str(s.transcripts[0].resolve())]


def test_server_reads_only_the_corpus_filter_md_and_persona_besides_python_code():
    s = run_session(INIT, call(2, "greenhouse/stripe", STRIPE_REJECT), wrapper=True)
    assert s.proc.returncode == 0, s.proc.stderr.decode()
    code = (".py", ".pyc", ".so", ".pth")
    reads = {e["path"] for e in s.audit()
             if e["event"] == "open" and not e["write"] and not e["path"].endswith(code) and not Path(e["path"]).is_dir()}
    allowed = {str(mcp_server.FILTER_MD), str(flt.DEFAULT_PERSONA.resolve())}
    run_root = str(RUN.resolve()) + os.sep
    assert reads, "expected data reads"
    assert all(p in allowed or p.startswith(run_root) for p in reads), sorted(reads)


def test_log_dir_outside_evidence_mcp_is_refused_before_anything_is_written(tmp_path):
    proc = subprocess.run([sys.executable, str(SERVER), "--log-dir", str(tmp_path / "elsewhere")],
                          input=json.dumps(INIT).encode() + b"\n", capture_output=True, timeout=60, cwd=PROJECT_DIR)
    assert proc.returncode == 2
    assert proc.stdout == b""
    assert not (tmp_path / "elsewhere").exists()
    assert b"must be inside" in proc.stderr


# ---------- transcript ----------

def test_transcript_logs_every_message_both_ways_with_time_and_direction_and_no_environment():
    secret = "sentinel-value-7f3a91-should-never-be-logged"
    env = {**os.environ, "JS3_TEST_SECRET": secret}
    lines = [INIT, INITIALIZED, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
             call(3, "ashby/notion", NOTION_KEEP), "{bad", {"jsonrpc": "2.0", "id": 5, "method": "nope"}]
    s = run_session(*lines, env=env)
    assert len(s.transcripts) == 1
    recs = records(s.transcripts[0])
    inbound = [r for r in recs if r["direction"] == "client->server"]
    outbound = [r for r in recs if r["direction"] == "server->client"]
    meta = [r for r in recs if r["direction"] == "meta"]
    assert len(inbound) == len(lines) == 6
    assert [r["message"] for r in outbound] == s.replies and len(outbound) == 5
    assert [m["event"] for m in meta] == ["start", "end"] and len(recs) == 13
    assert inbound[4]["raw"] == "{bad" and inbound[4]["message"] is None
    assert inbound[0]["message"] == INIT
    assert all(re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z", r["ts"]) for r in recs)
    text = s.transcripts[0].read_text()
    assert secret not in text and "JS3_TEST_SECRET" not in text
    assert str(Path.home()) not in json.dumps(meta)  # no paths or environment in the meta records
