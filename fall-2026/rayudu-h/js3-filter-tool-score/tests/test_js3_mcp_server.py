"""The tool server: what it declares versus what it does (EVAL-OWN-SERVER.md cites these tests)."""
import hashlib
import io
import json
import socket

import pytest

from conftest import ROOT
from js3 import mcp_server
from jsagent.policy import Refused

SINCE = "2026-11-07T184247-live"


@pytest.fixture(scope="module")
def srv():
    return mcp_server.Server(ROOT)


def call(srv, mid, method, params=None):
    msg = {"jsonrpc": "2.0", "id": mid, "method": method}
    if params is not None:
        msg["params"] = params
    return srv.handle_line(json.dumps(msg))


def tool(srv, args):
    return call(srv, 9, "tools/call", {"name": "search_new_postings", "arguments": args})["result"]


# ---- handshake ----------------------------------------------------------------------------------
def test_initialize_echoes_a_supported_version(srv):
    r = call(srv, 1, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                     "clientInfo": {"name": "t", "version": "0"}})["result"]
    assert r["protocolVersion"] == "2025-06-18"
    assert r["capabilities"] == {"tools": {"listChanged": False}}


def test_initialize_answers_its_own_latest_for_an_unknown_version(srv):
    r = call(srv, 1, "initialize", {"protocolVersion": "1999-01-01"})["result"]
    assert r["protocolVersion"] == mcp_server.SUPPORTED_VERSIONS[0]


def test_notifications_get_no_reply(srv):
    assert srv.handle_line(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})) is None


# ---- declared: one read-only tool with a closed schema --------------------------------------------
def test_tools_list_declares_exactly_one_read_only_tool(srv):
    tools = call(srv, 2, "tools/list")["result"]["tools"]
    assert [t["name"] for t in tools] == ["search_new_postings"]
    t = tools[0]
    assert t["annotations"] == {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True,
                                "openWorldHint": False}
    assert t["inputSchema"]["additionalProperties"] is False
    props = t["inputSchema"]["properties"]
    assert not any(k in props for k in ("path", "url", "file", "threshold", "query"))


# ---- actual: the schema is enforced, not just declared ----------------------------------------------
@pytest.mark.parametrize("args, fragment", [
    ({"since_snapshot": SINCE, "board": "../../etc/passwd"}, "board must be one of"),
    ({"since_snapshot": SINCE, "limit": 500}, "limit must be an integer from 1 to 20"),
    ({"since_snapshot": SINCE, "limit": True}, "limit must be an integer"),
    ({"since_snapshot": SINCE, "path": "/etc/passwd"}, "unknown argument 'path'"),
    ({}, "missing required argument 'since_snapshot'"),
    ({"since_snapshot": "2026-11-20T213031-live"}, "since_snapshot must be one of"),
])
def test_bad_arguments_are_tool_errors(srv, args, fragment):
    r = tool(srv, args)
    assert r["isError"] is True and fragment in r["content"][0]["text"]


def test_unknown_tool_unknown_method_and_bad_json(srv):
    assert call(srv, 3, "tools/call", {"name": "write_file", "arguments": {}})["error"]["code"] == -32602
    assert call(srv, 4, "resources/list")["error"]["code"] == -32601
    assert srv.handle_line("{not json")["error"]["code"] == -32700
    assert srv.handle_line(json.dumps({"id": 5, "method": "ping"}))["error"]["code"] == -32600


# ---- actual: the answer -------------------------------------------------------------------------------
def test_a_call_returns_kept_new_postings_and_the_missing_boards(srv):
    r = tool(srv, {"since_snapshot": SINCE})
    out = r["structuredContent"]
    assert "isError" not in r and out["upto_snapshot"] == "2026-11-20T213031-live"
    assert 1 <= out["returned"] <= 10 and all(p["decision"] == "kept" for p in out["postings"])
    assert {b["board"] for b in out["boards_without_result"]} == {"ashby:notion-does-not-exist-js2", "ashby:openai"}
    assert out["boards_with_result"] == ["greenhouse:anthropic", "ashby:notion", "ashby:perplexity"]   # added after
    # transcript claude-2026-11-22T161613: the client could not tell whether Notion was covered
    assert all(len(p["untrusted_posting_snippet"]) <= mcp_server.SNIPPET_CHARS for p in out["postings"])
    scores = [p["score"] for p in out["postings"]]
    assert scores == sorted(scores, reverse=True)
    for k in srv.tool["outputSchema"]["required"]:
        assert k in out


def test_never_returns_the_personas_contact_details(srv):
    text = json.dumps(tool(srv, {"since_snapshot": "2026-10-31T191245-live", "decision": "all", "limit": 20}))
    for secret in ("priya.nair@example.com", "555-0163", "linkedin.com/in/priyanair", "github.com/priyanair"):
        assert secret not in text


# ---- actual: read-only and offline ----------------------------------------------------------------------
def _folder_hash():
    h = hashlib.sha256()
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT)
        if p.is_file() and not set(rel.parts) & {".venv", "__pycache__", ".pytest_cache", "transcripts"}:
            h.update(str(rel).encode()); h.update(p.read_bytes())
    return h.hexdigest()


def test_a_whole_session_writes_nothing_and_opens_no_socket(monkeypatch):
    def no_network(*a, **k):
        raise AssertionError("the server tried to open a network connection")
    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)
    before = _folder_hash()
    lines = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
             {"jsonrpc": "2.0", "method": "notifications/initialized"},
             {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
             {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
              "params": {"name": "search_new_postings", "arguments": {"since_snapshot": SINCE}}}]
    out = io.StringIO()
    mcp_server.serve(stdin=io.StringIO("\n".join(json.dumps(x) for x in lines) + "\n"), stdout=out, root=ROOT)
    replies = [json.loads(x) for x in out.getvalue().splitlines()]
    assert [r["id"] for r in replies] == [1, 2, 3]            # the notification got no reply
    assert _folder_hash() == before


def test_the_policy_refuses_writes_and_requests():
    pol = mcp_server.ReadOnlyPolicy(ROOT)
    with pytest.raises(Refused):
        pol.check_write(ROOT / "runs" / "x.txt")
    with pytest.raises(Refused):
        pol.check_request("GET", "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs")
    with pytest.raises(Refused):
        pol.check_read(ROOT.parent / "js2-loop-tools-diff" / "README.md")


def test_the_server_source_has_no_writer_network_or_subprocess():
    src = (ROOT / "js3" / "mcp_server.py").read_text()
    for banned in ("import socket", "import urllib", "import subprocess", "open(", "http.client", ".write_text",
                   ".write_bytes"):
        assert banned not in src, banned
