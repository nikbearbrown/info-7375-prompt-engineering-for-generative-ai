"""The tool server over real stdio, driven by the from-scratch test client (not Claude)."""
import json
import re
import sys
from pathlib import Path

import pytest

from js3.mcp_client import StdioClient

ROOT = Path(__file__).resolve().parent.parent
SERVER = [sys.executable, str(ROOT / "js3" / "mcp_server.py")]


@pytest.fixture(scope="module")
def client():
    c = StdioClient(SERVER, cwd="/")  # cwd outside the folder: the server must not depend on it
    yield c
    c.close()


def test_initialize_and_list(client):
    r = client.initialize("2025-06-18")
    assert r["result"]["protocolVersion"] == "2025-06-18"
    assert r["result"]["capabilities"] == {"tools": {"listChanged": False}}
    tools = client.request("tools/list")["result"]["tools"]
    assert [t["name"] for t in tools] == ["score_posting"]          # exactly one capability
    assert tools[0]["annotations"]["readOnlyHint"] is True


def test_unknown_protocol_version_gets_servers_latest(client):
    assert client.request("initialize", {"protocolVersion": "1999-01-01", "capabilities": {},
                                         "clientInfo": {"name": "x", "version": "0"}})["result"]["protocolVersion"] == "2025-11-25"


def test_call_success_matches_direct_scoring(client):
    from js3.corpus import load_corpus
    from js3.filter import load_filter, score_posting
    r = client.request("tools/call", {"name": "score_posting", "arguments": {"posting_id": "greenhouse:databricks:8091041002"}})
    assert r["result"]["isError"] is False
    text = r["result"]["content"][0]["text"]
    direct = score_posting(load_corpus()["greenhouse:databricks:8091041002"], load_filter("v1.0"))
    assert direct["arithmetic"] in text and f"-> {direct['verdict']}" in text


def test_bare_id_resolves(client):
    r = client.request("tools/call", {"name": "score_posting", "arguments": {"posting_id": "8091041002"}})
    assert "greenhouse:databricks:8091041002" in r["result"]["content"][0]["text"]


def test_unknown_id_is_tool_error_not_guess(client):
    r = client.request("tools/call", {"name": "score_posting", "arguments": {"posting_id": "greenhouse:databricks:0"}})
    assert r["result"]["isError"] is True and r["result"]["content"][0]["text"].startswith("I cannot tell")


@pytest.mark.parametrize("params,code", [
    ({"name": "delete_posting", "arguments": {"posting_id": "1"}}, -32602),
    ({"name": "score_posting", "arguments": {}}, -32602),
    ({"name": "score_posting", "arguments": {"posting_id": 8091041002}}, -32602),
    ({"name": "score_posting", "arguments": {"posting_id": "1", "path": "/etc/passwd"}}, -32602),
    ({"name": "score_posting", "arguments": {"posting_id": "1", "filter_version": "../../x"}}, -32602),
])
def test_invalid_calls_are_protocol_errors(client, params, code):
    assert client.request("tools/call", params)["error"]["code"] == code


def test_unknown_method_and_parse_error(client):
    assert client.request("resources/list")["error"]["code"] == -32601
    assert client.send_raw("{not json")["error"]["code"] == -32700


def test_source_has_no_network_exec_or_write_tools():
    src = (ROOT / "js3" / "mcp_server.py").read_text()
    imports = set(re.findall(r"^\s*(?:import|from)\s+([\w.]+)", src, re.M))
    assert not imports & {"socket", "urllib", "urllib.request", "http", "http.client", "subprocess", "requests", "shutil"}
    # the only file opened for writing is the wire log
    assert src.count('open("a"') == 1 and "write_text" not in src and "unlink" not in src
