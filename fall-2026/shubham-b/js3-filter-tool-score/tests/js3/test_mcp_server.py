"""The MCP tool server: protocol behaviour, the one tool, and its boundaries."""

from __future__ import annotations

import io
import json
import subprocess
import sys

import pytest

from job_search_agent.js3.mcp_server import TOOL, Server, serve, transcript_logger
from tests.conftest import REPO_ROOT

INIT = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "t", "version": "0"},
    },
}
READY = {"jsonrpc": "2.0", "method": "notifications/initialized"}


def _ready() -> Server:
    s = Server(REPO_ROOT)
    s.handle(INIT)
    assert s.handle(READY) is None
    return s


def _call(s: Server, args: object, name: str = "score_posting") -> dict:
    reply = s.handle(
        {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {"name": name, "arguments": args},
        }
    )
    assert reply is not None
    return reply


def test_initialize_echoes_a_supported_version_and_declares_tools_only() -> None:
    reply = Server(REPO_ROOT).handle(INIT)
    assert reply["result"]["protocolVersion"] == "2025-06-18"
    assert set(reply["result"]["capabilities"]) == {"tools"}


def test_unknown_version_gets_the_newest() -> None:
    msg = {**INIT, "params": {**INIT["params"], "protocolVersion": "1999-01-01"}}
    assert Server(REPO_ROOT).handle(msg)["result"]["protocolVersion"] == "2025-11-25"


def test_nothing_but_initialize_and_ping_before_initialized() -> None:
    s = Server(REPO_ROOT)
    assert (
        s.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["error"]["code"]
        == -32600
    )
    assert s.handle({"jsonrpc": "2.0", "id": 2, "method": "ping"})["result"] == {}


def test_lists_exactly_one_read_only_tool() -> None:
    tools = _ready().handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})[
        "result"
    ]["tools"]
    assert [t["name"] for t in tools] == ["score_posting"]
    assert tools[0]["annotations"] == {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }


def test_score_posting_returns_claims_for_a_collected_posting() -> None:
    result = _call(_ready(), {"board": "greenhouse/stripe", "posting_id": "8128744"})[
        "result"
    ]
    assert result["isError"] is False
    out = result["structuredContent"]
    assert out["kept"] is True and out["filter_version"] == "0.3"
    assert {c["claim_id"] for c in out["claims"]} >= {"C1", "C3", "C4", "C5"}
    assert json.loads(result["content"][0]["text"]) == out


@pytest.mark.parametrize(
    "args",
    [
        {"board": "greenhouse/stripe", "posting_id": "../../etc/passwd"},
        {"board": "greenhouse/ramp", "posting_id": "1"},
        {"board": "greenhouse/stripe", "posting_id": "8128744", "extra": 1},
        {"board": "greenhouse/stripe", "posting_id": "999999999"},
        "not an object",
    ],
)
def test_bad_arguments_are_tool_errors(args: object) -> None:
    assert _call(_ready(), args)["result"]["isError"] is True


def test_unknown_tool_and_method_are_protocol_errors() -> None:
    s = _ready()
    assert _call(s, {}, name="apply_to_job")["error"]["code"] == -32602
    assert (
        s.handle({"jsonrpc": "2.0", "id": 3, "method": "resources/list"})["error"][
            "code"
        ]
        == -32601
    )


def test_notifications_get_no_reply_and_bad_lines_get_errors() -> None:
    lines = [
        json.dumps(INIT),
        json.dumps(READY),
        "not json",
        "[1, 2]",
        json.dumps({"jsonrpc": "2.0", "id": 5, "method": "ping"}),
    ]
    out = io.BytesIO()
    serve(
        Server(REPO_ROOT),
        io.BytesIO(("\n".join(lines) + "\n").encode()),
        out,
        lambda d, line: None,
    )
    replies = [json.loads(x) for x in out.getvalue().decode().splitlines()]
    assert [r.get("id") for r in replies] == [1, None, None, 5]
    assert (
        replies[1]["error"]["code"] == -32700 and replies[2]["error"]["code"] == -32600
    )


def test_transcript_only_under_data_js3_mcp(tmp_path: object) -> None:
    for bad in (
        "data/watch/x.jsonl",
        "data/js3/mcp/../../x.jsonl",
        "data/js3/mcp/x.txt",
    ):
        with pytest.raises(SystemExit):
            transcript_logger(REPO_ROOT, bad)


def test_tool_description_says_it_never_acts() -> None:
    assert (
        "never applies, contacts anyone, logs in, or changes any file"
        in TOOL["description"]
    )


@pytest.mark.subprocess
def test_stdio_session_end_to_end() -> None:
    lines = [INIT, READY, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}]
    proc = subprocess.run(
        [sys.executable, "-m", "job_search_agent.js3", "serve"],
        input="\n".join(json.dumps(x) for x in lines) + "\n",
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    replies = [json.loads(x) for x in proc.stdout.splitlines()]
    assert [r["id"] for r in replies] == [1, 2]


@pytest.mark.parametrize("bad_id", [None, {"a": 1}, [1], True])
def test_id_must_be_string_or_integer(bad_id: object) -> None:
    reply = _ready().handle({"jsonrpc": "2.0", "id": bad_id, "method": "ping"})
    assert reply is not None and reply["error"]["code"] == -32600
