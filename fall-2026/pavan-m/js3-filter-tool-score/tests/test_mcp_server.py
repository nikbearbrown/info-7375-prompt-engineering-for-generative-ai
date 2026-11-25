
import json
from agent.mcp_server import handle

FILLER = " ".join(["team"] * 60)


def req(method, params=None, id=1):
    m = {"jsonrpc": "2.0", "id": id, "method": method}
    if params is not None:
        m["params"] = params
    return m


def test_initialize_declares_tools():
    r = handle(req("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                  "clientInfo": {"name": "test", "version": "0"}}, id=7))
    assert r["jsonrpc"] == "2.0"
    assert r["id"] == 7
    assert "tools" in r["result"]["capabilities"]
    assert r["result"]["serverInfo"]["name"]
    assert r["result"]["protocolVersion"]


def test_initialized_notification_gets_no_reply():
    r = handle({"jsonrpc": "2.0", "method": "notifications/initialized"})
    assert r is None


def test_tools_list_has_exactly_score_posting():
    r = handle(req("tools/list"))
    tools = r["result"]["tools"]
    assert [t["name"] for t in tools] == ["score_posting"]
    assert set(tools[0]["inputSchema"]["required"]) == {"title", "location", "content"}


def test_tools_call_scores_with_filter_v1_1():
    r = handle(req("tools/call", {"name": "score_posting", "arguments": {
        "title": "Software Engineer", "location": "San Francisco, CA",
        "content": "Java, Kafka, Docker and AWS. " + FILLER}}))
    content = r["result"]["content"]
    body = json.loads(content[0]["text"])
    assert content[0]["type"] == "text"
    assert r["result"].get("isError") is not True
    assert body["decision"] == "KEEP" and body["score"] == 10


def test_tools_call_uses_v1_1_years_cutoff():
    r = handle(req("tools/call", {"name": "score_posting", "arguments": {
        "title": "Software Engineer", "location": "San Francisco, CA",
        "content": "Java, Kafka, Docker and AWS. 5+ years of experience. " + FILLER}}))
    body = json.loads(r["result"]["content"][0]["text"])
    assert body["decision"] == "REJECT"


def test_missing_argument_is_a_tool_error_not_a_crash():
    r = handle(req("tools/call", {"name": "score_posting", "arguments": {"title": "Software Engineer"}}))
    assert r["result"]["isError"] is True


def test_unknown_tool_is_a_protocol_error():
    r = handle(req("tools/call", {"name": "apply_to_job", "arguments": {}}))
    assert r["error"]["code"] == -32602


def test_unknown_method_is_method_not_found():
    r = handle(req("resources/list"))
    assert r["error"]["code"] == -32601
