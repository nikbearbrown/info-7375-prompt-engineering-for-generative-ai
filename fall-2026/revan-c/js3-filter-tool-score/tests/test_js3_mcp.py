"""JS3 tool-server tests, written from FILTER.md v1 section 7 (0e15e65) before the server exists.

Rows 1-6 are the predicted state table in FILTER.md. Postings are CONSTRUCTED fixtures.
"""
import ast
import json
import os
import pathlib
import subprocess
import sys

from jsfilter import filter as F
from jsfilter.mcp_server import Server
from js3_support import ROOT, gh_body, gh_job, resume

SERVER_SRC = ROOT / "jsfilter" / "mcp_server.py"


def make_server():
    boards = [F.load_board("klaviyo", "greenhouse",
                           gh_body(gh_job(501, title="Backend Engineer",
                                          content="<p>Backend API work. Python, SQL, AWS.</p>")),
                           "fixture.body")]
    return Server(resume(), boards)


def req(method, id_, params=None):
    msg = {"jsonrpc": "2.0", "id": id_, "method": method}
    if params is not None:
        msg["params"] = params
    return msg


INIT = req("initialize", 2, {"protocolVersion": "2025-11-25", "capabilities": {},
                             "clientInfo": {"name": "test", "version": "0"}})
READY = {"jsonrpc": "2.0", "method": "notifications/initialized"}


def ready_server():
    s = make_server()
    s.handle(INIT)
    assert s.handle(READY) is None
    return s


def call(s, args, id_=5, name="score_posting"):
    return s.handle(req("tools/call", id_, {"name": name, "arguments": args}))


# ---- FILTER.md section 7, predicted state table ------------------------------------------

def test_row1_tools_list_before_initialize_is_32000():
    s = make_server()
    r = s.handle(req("tools/list", 1))
    assert r["id"] == 1 and r["error"]["code"] == -32000
    assert (s.initialized, s.ready) == (False, False)


def test_row2_initialize_declares_and_is_not_ready():
    s = make_server()
    r = s.handle(INIT)
    assert r["id"] == 2
    assert r["result"]["protocolVersion"] == "2025-11-25"
    assert r["result"]["capabilities"] == {"tools": {}}
    assert r["result"]["serverInfo"]["name"]
    assert (s.initialized, s.ready) == (True, False)


def test_row3_tools_list_after_initialize_before_notification_is_32000():
    s = make_server()
    s.handle(INIT)
    r = s.handle(req("tools/list", 3))
    assert r["id"] == 3 and r["error"]["code"] == -32000
    assert (s.initialized, s.ready) == (True, False)


def test_row4_initialized_notification_makes_ready_without_response():
    s = make_server()
    s.handle(INIT)
    assert s.handle(READY) is None
    assert (s.initialized, s.ready) == (True, True)


def test_row4b_early_notification_changes_nothing():
    s = make_server()
    assert s.handle(READY) is None
    assert (s.initialized, s.ready) == (False, False)


def test_row5_bad_arguments_are_32602():
    s = ready_server()
    for args in ([], {"board": "klaviyo"}, {"board": "klaviyo", "id": 501},
                 {"board": "klaviyo", "id": "501", "extra": "x"}, {"board": "lever", "id": "501"}):
        r = call(s, args)
        assert r["id"] == 5 and r["error"]["code"] == -32602, args


def test_row6_unknown_posting_is_tool_error_not_protocol_error():
    s = ready_server()
    r = call(s, {"board": "klaviyo", "id": "999"}, id_=6)
    assert r["id"] == 6 and "error" not in r
    assert r["result"]["isError"] is True


# ---- Other codes in FILTER.md section 7 ----------------------------------------------------

def test_invalid_request_parse_error_unknown_method_unknown_tool():
    s = ready_server()
    assert s.handle({"id": 9})["error"]["code"] == -32600
    assert s.handle({"id": 9})["id"] is None
    assert json.loads(s.handle_line("{"))["error"]["code"] == -32700
    assert s.handle(req("bad/method", 10))["error"]["code"] == -32601
    assert call(s, {"board": "klaviyo", "id": "501"}, name="delete_posting")["error"]["code"] == -32602


def test_tools_list_declares_one_read_only_tool_matching_call_validation():
    s = ready_server()
    tools = s.handle(req("tools/list", 7))["result"]["tools"]
    assert [t["name"] for t in tools] == ["score_posting"]
    schema = tools[0]["inputSchema"]
    assert schema["required"] == ["board", "id"]
    assert schema["additionalProperties"] is False
    assert set(schema["properties"]["board"]["enum"]) == {"klaviyo", "duolingo", "patchmypc"}


# ---- Evidence ledger: the returned score is the filter's score -----------------------------

def test_returned_score_recomputes_from_the_saved_posting():
    s = ready_server()
    r = call(s, {"board": "klaviyo", "id": "501"})
    assert r["result"]["isError"] is False
    payload = json.loads(r["result"]["content"][0]["text"])
    loaded = F.load_board("klaviyo", "greenhouse",
                          gh_body(gh_job(501, title="Backend Engineer",
                                         content="<p>Backend API work. Python, SQL, AWS.</p>")), "fixture.body")
    direct = F.score_posting(resume(), loaded["postings"][0])
    for key in ("total", "fate", "components", "failed_rules", "source_path"):
        assert payload[key] == direct[key], key


# ---- Capability ledger: no write, no network ---------------------------------------------

def test_server_source_imports_no_network_or_process_modules_and_never_writes():
    # The server and the filter module it calls are both checked; file reads go through
    # pathlib read_bytes in jsfilter/filter.py, so neither file needs open().
    for path in (SERVER_SRC, ROOT / "jsfilter" / "filter.py"):
        _check_source(path)


def _check_source(path):
    tree = ast.parse(path.read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not imported & {"socket", "http", "urllib", "requests", "subprocess", "shutil", "jsloop"}
    src = path.read_text()
    for forbidden in ("write_text", "write_bytes", ".write(", "open(", "unlink", "mkdir", "rename"):
        if forbidden == ".write(":
            # stdout is the protocol channel; that is the only permitted write.
            assert src.count(".write(") == src.count("sys.stdout.write("), forbidden
        else:
            assert forbidden not in src, forbidden


def test_stdio_session_writes_no_files(tmp_path):
    lines = [INIT, READY, req("tools/list", 3),
             req("tools/call", 4, {"name": "score_posting", "arguments": {"board": "klaviyo", "id": "0"}})]
    before = sorted(p.name for p in tmp_path.iterdir())
    proc = subprocess.run(
        [sys.executable, "-m", "jsfilter.mcp_server", "--root", str(ROOT)],
        input="\n".join(json.dumps(m) for m in lines) + "\n", capture_output=True, text=True,
        cwd=tmp_path, env={**os.environ, "PYTHONPATH": str(ROOT)}, timeout=60)
    assert proc.returncode == 0, proc.stderr
    out = [json.loads(line) for line in proc.stdout.splitlines()]
    assert [m["id"] for m in out] == [2, 3, 4]   # notification got no response
    assert sorted(p.name for p in tmp_path.iterdir()) == before
