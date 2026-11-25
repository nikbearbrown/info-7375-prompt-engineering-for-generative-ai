"""job_agent.mcp_server over a real subprocess: stdin in, stdout out, transcript in tmp_path."""

import json
import os
import subprocess
import sys
from pathlib import Path

from job_agent import inputs
from job_agent.common.paths import Paths
from job_agent.judges import rule
from job_agent.watch.boards import greenhouse

REPO = Path(__file__).resolve().parents[1]
INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}}
INITIALIZED = {"jsonrpc": "2.0", "method": "notifications/initialized"}


def _run(lines, tmp_path):
    env = dict(os.environ, JSA_MCP_TRANSCRIPT_DIR=str(tmp_path / "tx"))
    payload = "".join((l if isinstance(l, str) else json.dumps(l)) + "\n" for l in lines)
    proc = subprocess.run([sys.executable, "-m", "job_agent.mcp_server"], input=payload.encode(),
                          capture_output=True, cwd=REPO, env=env, timeout=120)
    out = [json.loads(l) for l in proc.stdout.decode().splitlines() if l.strip()]
    return {r["id"]: r for r in out}, out, proc


def _call(msg_id, args, name="score_posting"):
    return {"jsonrpc": "2.0", "id": msg_id, "method": "tools/call", "params": {"name": name, "arguments": args}}


def _newest(board):
    return sorted((REPO / "evidence" / "raw").glob(f"*/{board}_content.json"), key=lambda p: p.parent.name)[-1]


def test_handshake_ping_and_list(tmp_path):
    by_id, out, proc = _run([INIT, INITIALIZED, {"jsonrpc": "2.0", "id": 2, "method": "ping"},
                             {"jsonrpc": "2.0", "id": 3, "method": "tools/list"}], tmp_path)
    assert proc.returncode == 0
    assert [r["id"] for r in out] == [1, 2, 3]
    assert by_id[1]["result"]["protocolVersion"] == "2025-03-26"
    assert by_id[1]["result"]["serverInfo"] == {"name": "job-search-agent", "version": "js3"}
    assert by_id[2]["result"] == {}
    (tool,) = by_id[3]["result"]["tools"]
    assert tool["name"] == "score_posting"
    assert "striqe" not in tool["inputSchema"]["properties"]["board"]["enum"]
    assert tool["annotations"] == {"readOnlyHint": True, "openWorldHint": False}


def test_score_posting_matches_rule_judge(tmp_path):
    posting = greenhouse.parse(_newest("stripe").read_bytes())[0]
    by_id, _, _ = _run([INIT, INITIALIZED, _call(5, {"board": "stripe", "posting_id": str(posting.id)}),
                        _call(6, {"board": "stripe", "posting_id": "nope"})], tmp_path)
    p = Paths()
    expected = json.loads(json.dumps(rule.judge(posting, inputs.load_criteria(p.default_resume, p.default_profile, p)).verdict))
    assert by_id[5]["result"]["isError"] is False
    assert by_id[5]["result"]["structuredContent"] == expected
    assert by_id[6]["result"]["isError"] is True


def test_bad_input_gets_errors_and_server_keeps_going(tmp_path):
    by_id, out, proc = _run([INIT, _call(10, {"board": "../../etc", "posting_id": "1"}),
                             _call(11, {"board": "stripe"}), _call(12, {"board": "stripe", "posting_id": "1", "x": 1}),
                             _call(13, {"board": "stripe", "posting_id": "1"}, name="rm"),
                             {"jsonrpc": "2.0", "id": 14, "method": "nope"}, "not json {",
                             {"jsonrpc": "2.0", "id": 15, "method": "ping"}], tmp_path)
    assert proc.returncode == 0
    for i in (10, 11, 12, 13):
        assert by_id[i]["error"]["code"] == -32602
    assert by_id[14]["error"]["code"] == -32601
    assert by_id[None]["error"]["code"] == -32700
    assert by_id[15]["result"] == {}


def test_transcript_has_every_message(tmp_path):
    sent = [INIT, INITIALIZED, {"jsonrpc": "2.0", "id": 2, "method": "ping"}]
    _, out, _ = _run(sent, tmp_path)
    (f,) = (tmp_path / "tx").glob("mcp-*.jsonl")
    entries = [json.loads(l) for l in f.read_text().splitlines()]
    assert [e["dir"] for e in entries] == ["in", "out", "in", "in", "out"]
    assert [e["msg"] for e in entries if e["dir"] == "in"] == sent
    assert [e["msg"] for e in entries if e["dir"] == "out"] == out
