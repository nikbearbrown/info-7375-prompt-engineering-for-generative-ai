import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from js3 import mcp_server as srv

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture
def results(tmp_path):
    path = tmp_path / "filter_results.json"
    path.write_text(json.dumps({
        "databricks": [
            {"id": 1, "title": "Senior Recruiter", "passed": False, "reason": "hard_reject",
             "matched_words": {"role": [], "topic": [], "reject": ["recruiter"]}},
        ],
        "stripe": [
            {"id": 2, "title": "  Machine Learning Engineer,  Radar ", "passed": True, "reason": "title_match",
             "matched_words": {"role": ["machine learning"], "topic": [], "reject": []}},
            {"id": 3, "title": "Machine Learning Engineer, Radar", "passed": True, "reason": "title_match",
             "matched_words": {"role": ["machine learning"], "topic": [], "reject": []}},
        ],
    }))
    return path


def call(obj, results_path):
    line = obj if isinstance(obj, str) else json.dumps(obj)
    return srv.handle_line(line, results_path)


def tool_call(title, results_path):
    return call({"jsonrpc": "2.0", "id": 9, "method": "tools/call",
                 "params": {"name": "score_posting", "arguments": {"title": title}}}, results_path)


def test_initialize_returns_server_name_version_and_empty_capabilities(results):
    r = call({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}, results)
    assert r["id"] == 1
    assert r["result"]["serverInfo"] == {"name": "job-search-agent-3", "version": "0.1.0"}
    assert r["result"]["capabilities"] == {}


def test_tools_list_returns_score_posting(results):
    r = call({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, results)
    tools = r["result"]["tools"]
    assert [t["name"] for t in tools] == ["score_posting"]
    schema = tools[0]["inputSchema"]
    assert schema["required"] == ["title"]
    assert schema["properties"]["title"]["type"] == "string"
    assert "0-100" in tools[0]["description"]


def test_tools_call_known_title_returns_first_match_case_insensitive(results):
    r = tool_call("MACHINE LEARNING ENGINEER, RADAR", results)
    out = r["result"]["structuredContent"]
    assert out["found"] is True
    assert out["id"] == 2                      # first match, whitespace-normalised
    assert out["passed"] is True and out["reason"] == "title_match" and out["score"] == 100
    assert out["matched_words"]["role"] == ["machine learning"]
    assert json.loads(r["result"]["content"][0]["text"]) == out


def test_tools_call_rejected_title_scores_zero(results):
    out = tool_call("senior recruiter", results)["result"]["structuredContent"]
    assert out["found"] is True and out["passed"] is False and out["score"] == 0


def test_tools_call_unknown_title_returns_score_zero(results):
    out = tool_call("Underwater Basket Weaver", results)["result"]["structuredContent"]
    assert out == {"found": False, "title": "Underwater Basket Weaver", "score": 0,
                   "reason": "not found in filter results"}


def test_tools_call_does_not_substring_match(results):
    out = tool_call("Machine Learning Engineer", results)["result"]["structuredContent"]
    assert out["found"] is False


def test_unknown_method_returns_32601(results):
    r = call({"jsonrpc": "2.0", "id": 5, "method": "resources/list"}, results)
    assert r["error"]["code"] == -32601
    assert r["error"]["message"] == "Method not found"
    assert r["id"] == 5


def test_bad_tool_params_return_32602(results):
    r = call({"jsonrpc": "2.0", "id": 6, "method": "tools/call",
              "params": {"name": "score_posting", "arguments": {}}}, results)
    assert r["error"]["code"] == -32602
    r = call({"jsonrpc": "2.0", "id": 7, "method": "tools/call",
              "params": {"name": "delete_everything", "arguments": {"title": "x"}}}, results)
    assert r["error"]["code"] == -32602


@pytest.mark.parametrize("bad", ["{not json", "[]", "42", '"just a string"', '{"id": 1, "params": "x"}'])
def test_malformed_input_returns_32603_or_error_without_crashing(bad, results):
    r = call(bad, results)
    assert "error" in r
    assert r["error"]["code"] in (-32603, -32602)


def test_missing_results_file_is_an_error_not_a_crash(tmp_path):
    r = tool_call("Data Engineer", tmp_path / "missing.json")
    assert r["error"]["code"] == -32603


def test_notification_gets_no_response(results):
    assert call({"jsonrpc": "2.0", "method": "notifications/initialized"}, results) is None


def test_serve_keeps_going_after_bad_line(results):
    stdin = io.StringIO('garbage\n\n{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n')
    stdout = io.StringIO()
    srv.serve(stdin, stdout, results)
    replies = [json.loads(line) for line in stdout.getvalue().splitlines()]
    assert [r.get("error", {}).get("code") for r in replies] == [-32603, None]
    assert replies[1]["result"]["tools"][0]["name"] == "score_posting"


def test_server_over_real_subprocess_stdio():
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "js3.mcp_server"],
        input='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\nnot json\n',
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert proc.returncode == 0
    first, second = [json.loads(line) for line in proc.stdout.splitlines()]
    assert first["result"]["serverInfo"]["name"] == "job-search-agent-3"
    assert second["error"]["code"] == -32603
