"""The tool server, held to what reports/tool-evaluation.md says about it.

Every claim in that report's "what it actually does" table is a claim about
this code, so each one is a test here rather than a sentence there.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from toolserver import server

PKG = Path(__file__).resolve().parents[1] / "toolserver"


def call(method, params=None, msg_id=1):
    msg = {"jsonrpc": "2.0", "id": msg_id, "method": method}
    if params is not None:
        msg["params"] = params
    return server.handle(msg)


# --- the protocol ---------------------------------------------------------

def test_initialize_reports_a_name_and_a_protocol_version():
    r = call("initialize")["result"]
    assert r["serverInfo"]["name"] == "js3-score-posting"
    assert r["protocolVersion"] == "2024-11-05"
    assert r["capabilities"]["tools"]["listChanged"] is False


def test_tools_list_declares_exactly_one_tool():
    tools = call("tools/list")["result"]["tools"]
    assert [t["name"] for t in tools] == ["score_posting"]
    schema = tools[0]["inputSchema"]
    assert schema["required"] == ["text"]
    assert schema["additionalProperties"] is False
    assert set(schema["properties"]) == {"text"}


def test_a_notification_gets_no_reply():
    assert server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


def test_an_unknown_method_is_32601():
    with pytest.raises(server.RpcError) as e:
        call("resources/list")
    assert e.value.code == -32601


def test_an_unknown_tool_is_32602():
    with pytest.raises(server.RpcError) as e:
        call("tools/call", {"name": "read_file", "arguments": {"path": "/etc/passwd"}})
    assert e.value.code == -32602


# --- what a compatible client is not entitled to --------------------------

def test_additional_properties_false_is_enforced_not_merely_declared():
    """A schema is a document; a document stops nothing."""
    out = call("tools/call", {
        "name": "score_posting",
        "arguments": {"text": "hello", "path": "../../etc/passwd"},
    })["result"]
    assert out["isError"] is True
    assert "path" in out["content"][0]["text"]


def test_there_is_no_argument_that_names_a_location():
    tools = call("tools/list")["result"]["tools"]
    props = tools[0]["inputSchema"]["properties"]
    assert set(props) == {"text"}, (
        "the server's whole confinement story is that there is nothing to confine"
    )


def test_empty_text_is_an_error_and_not_a_zero():
    out = call("tools/call", {"name": "score_posting", "arguments": {"text": ""}})["result"]
    assert out["isError"] is True
    assert "not a score of 0" in out["content"][0]["text"]


def test_text_with_nothing_scoreable_really_is_a_zero():
    out = call("tools/call", {
        "name": "score_posting",
        "arguments": {"text": "We are looking for a friendly person."},
    })["result"]
    assert out["isError"] is False
    payload = json.loads(out["content"][0]["text"])
    assert payload["total"] == 0 and payload["evidence"] == []


# --- the structural claims ------------------------------------------------

SOURCES = sorted(PKG.rglob("*.py"))


def test_the_package_opens_no_file():
    for path in SOURCES:
        src = path.read_text(encoding="utf-8")
        for needle in ("open(", ".read_text", ".write_text", ".read_bytes"):
            assert needle not in src, f"{path.name} contains {needle}"


@pytest.mark.parametrize("module", ["socket", "urllib", "http", "requests", "ssl"])
def test_the_package_imports_nothing_that_could_reach_the_network(module):
    pattern = re.compile(rf"^\s*(?:import|from)\s+{module}\b", re.MULTILINE)
    for path in SOURCES:
        assert not pattern.search(path.read_text(encoding="utf-8")), path.name


def test_the_package_reads_no_environment_variable_and_calls_no_model():
    for path in SOURCES:
        src = path.read_text(encoding="utf-8").lower()
        for needle in ("os.environ", "getenv", "anthropic", "openai", "api_key"):
            assert needle not in src, f"{path.name} mentions {needle}"


def test_every_point_awarded_carries_the_sentence_behind_it():
    out = call("tools/call", {
        "name": "score_posting",
        "arguments": {"text": "We build a public API in Python.\n- 5+ years required\n"},
    })["result"]
    payload = json.loads(out["content"][0]["text"])
    assert payload["evidence"]
    for e in payload["evidence"]:
        assert e["sentence"].strip()
        assert e["word"].lower() in e["sentence"].lower()
    assert payload["total"] == sum(e["points"] for e in payload["evidence"])
