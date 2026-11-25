"""The tool server, driven by the scripted client (scripts/mcp_client.py) in a subprocess.

Written by Claude Code (claude-opus-5-5), 2026-11-25. The dataset here is SEEDED (two hand-built
postings in a tmp folder). Covers: server/discover, tools/list, tools/call, malformed JSON, an
invalid request, an unknown method, an unknown tool, bad arguments, a path-traversal posting_key,
an unknown protocol version, missing _meta, the legacy initialize, a notification, and the
verbatim two-way transcript.
"""
import importlib.util
import json
import os
import sys

import pytest

import js3kit
from filter_checks import line

spec = importlib.util.spec_from_file_location("mcp_client", js3kit.ROOT / "scripts" / "mcp_client.py")
mcp_client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_client)

META = {"io.modelcontextprotocol/protocolVersion": "2026-07-28", "io.modelcontextprotocol/clientCapabilities": {},
        "io.modelcontextprotocol/clientInfo": {"name": "SEEDED-test-client", "version": "0"}}


@pytest.fixture
def server(tmp_path):
    (tmp_path / "data").mkdir()
    lines = [line(title="ML Engineer", location="Boston", body=("<p>We use PyTorch.</p>",), key="greenhouse:seeded:1"),
             line(title="ML Engineer", location=None, body=("<p>We use PyTorch.</p>",), key="greenhouse:seeded:2")]
    (tmp_path / "data" / "postings-SEEDED.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines))
    (tmp_path / "secret.txt").write_text("SEEDED secret outside data/")
    env = {**os.environ, "PYTHONPATH": str(js3kit.ROOT)}
    c = mcp_client.StdioClient([sys.executable, "-m", "jobwatch", "mcp-server", "--dataset", "data/postings-SEEDED.jsonl"],
                               str(tmp_path), env, str(tmp_path / "client-transcript.jsonl"), timeout=20)
    yield c, tmp_path
    if c.proc.poll() is None:
        c.close()


def call(c, args, id_=5, name="score_posting"):
    return c.request("tools/call", {"name": name, "arguments": args, "_meta": META}, id_)


def test_discover_list_and_call(server):
    c, _ = server
    d = c.request("server/discover", {"_meta": META}, 1)["result"]
    assert d["supportedVersions"] == ["2026-07-28"] and d["capabilities"] == {"tools": {}} and d["resultType"] == "complete"
    assert d["ttlMs"] >= 0 and d["cacheScope"] == "public" and d["_meta"]["io.modelcontextprotocol/serverInfo"]["name"] == "jobwatch-js3"
    tl = c.request("tools/list", {"_meta": META}, 2)["result"]
    assert [t["name"] for t in tl["tools"]] == ["score_posting"] and tl["ttlMs"] >= 0
    r = call(c, {"posting_key": "greenhouse:seeded:1"}, 3)["result"]
    assert r["isError"] is False and r["structuredContent"]["decision"] == "keep" and r["structuredContent"]["score"] == 8
    assert {m["rule"] for m in r["structuredContent"]["matched_rules"]} == {"R02", "L01", "T02"}
    r = call(c, {"posting_key": "greenhouse:seeded:2"}, 4)["result"]
    assert r["structuredContent"]["decision"] == "I cannot tell" and "location missing or empty" in r["structuredContent"]["reasons"][0]


def test_malformed_json_invalid_request_and_unknown_method(server):
    c, _ = server
    c.send("{not json")
    assert c.next_message()["error"]["code"] == -32700
    c.send(json.dumps({"jsonrpc": "1.0", "id": 7, "method": "tools/list"}))
    assert c.wait_for(7)["error"]["code"] == -32600
    assert c.request("prompts/list", {"_meta": META}, 8)["error"]["code"] == -32601
    assert c.request("ping", {"_meta": META}, 9)["error"]["code"] == -32601


def test_unknown_tool_is_a_protocol_error_and_bad_arguments_are_tool_errors(server):
    c, _ = server
    e = call(c, {"posting_key": "greenhouse:seeded:1"}, 10, name="delete_everything")["error"]
    assert e["code"] == -32602 and "Unknown tool" in e["message"]
    for i, args in enumerate([{}, {"posting_key": 7}, {"posting_key": "greenhouse:seeded:1", "path": "/etc"}]):
        r = call(c, args, 20 + i)["result"]
        assert r["isError"] is True
    assert c.request("tools/call", {"name": "score_posting", "arguments": "x", "_meta": META}, 30)["error"]["code"] == -32602


@pytest.mark.parametrize("key", ["../secret.txt", "../../../../etc/passwd", "greenhouse:seeded:../../secret",
                                 "data/postings-SEEDED.jsonl", "greenhouse:seeded:999"])
def test_path_traversal_and_unknown_keys_read_nothing_outside_data(server, key):
    c, tmp = server
    r = call(c, {"posting_key": key}, 40)["result"]
    assert r["isError"] is True and "SEEDED secret" not in json.dumps(r)


def test_unknown_version_missing_meta_and_legacy_initialize(server):
    c, _ = server
    e = c.request("tools/list", {"_meta": {**META, "io.modelcontextprotocol/protocolVersion": "1900-01-01"}}, 50)["error"]
    assert e["code"] == -32022 and e["data"] == {"supported": ["2026-07-28"], "requested": "1900-01-01"}
    assert c.request("tools/list", {}, 51)["error"]["code"] == -32602
    assert c.request("tools/list", None, 52)["error"]["code"] == -32602
    e = c.request("initialize", {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "x", "version": "0"}}, 53)["error"]
    assert e["code"] == -32601 and e["data"] == {"supported": ["2026-07-28"]}


def test_notification_gets_no_response(server):
    c, _ = server
    c.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    c.send({"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 1}})
    assert c.silent_for(1.0)


def test_transcript_records_every_line_in_and_out_verbatim_and_nothing_else_is_written(server):
    c, tmp = server
    c.request("server/discover", {"_meta": META}, 1)
    c.send("{not json")
    c.next_message()
    call(c, {"posting_key": "greenhouse:seeded:1"}, 2)
    assert c.close() == 0
    (t,) = list((tmp / "evidence" / "mcp" / "transcripts").glob("*.jsonl"))
    srv = [json.loads(x) for x in t.read_text().splitlines()]
    cli = [json.loads(x) for x in (tmp / "client-transcript.jsonl").read_text().splitlines()]
    assert [r["line"] for r in srv if r["dir"] == "in"] == [r["line"] for r in cli if r["dir"] == "out"]
    assert [r["line"] for r in srv if r["dir"] == "out"] == [r["line"] for r in cli if r["dir"] == "in"]
    written = sorted(p.relative_to(tmp).as_posix() for p in tmp.rglob("*") if p.is_file())
    assert written == ["client-transcript.jsonl", "data/postings-SEEDED.jsonl", t.relative_to(tmp).as_posix(), "secret.txt"]


def test_server_module_imports_no_network_or_subprocess():
    import ast
    tree = ast.parse((js3kit.ROOT / "jobwatch" / "mcp_server.py").read_text())
    names = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    names |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    assert not names & {"socket", "ssl", "urllib.request", "http.client", "subprocess", "jobwatch.judge_cli", "jobwatch.claude_judge"}
