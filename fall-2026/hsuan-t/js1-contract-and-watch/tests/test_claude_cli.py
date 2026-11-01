"""The `claude -p` phone line (D18), with subprocess faked: no test starts a real Claude Code run.

What matters here is what the child process is allowed to do (no tools, no session, no settings,
no API key in its environment) and that every way it can fail becomes a ClaudeCallError, which the
judge turns into that posting's error verdict instead of a crash.
"""

import json
import subprocess

import pytest

from job_agent.common.errors import ClaudeCallError
from job_agent.judges import claude_cli


class FakeRun:
    """Records the subprocess call and returns a prepared result."""

    def __init__(self, stdout="", returncode=0, stderr="", timeout=False):
        self.result = subprocess.CompletedProcess([], returncode, stdout, stderr)
        self.timeout = timeout
        self.calls = []

    def __call__(self, args, **kw):
        self.calls.append((args, kw))
        if self.timeout:
            raise subprocess.TimeoutExpired(args, kw.get("timeout"))
        return self.result


def _cli_json(**over):
    out = {"type": "result", "subtype": "success", "is_error": False, "result": '{"ok": true}',
           "stop_reason": "end_turn", "num_turns": 1, "session_id": "s1",
           "modelUsage": {"claude-sonnet-5-5": {}}, "usage": {"input_tokens": 10, "output_tokens": 5}}
    return json.dumps({**out, **over})


@pytest.fixture
def installed(monkeypatch):
    monkeypatch.setattr(claude_cli, "find_claude", lambda: "/usr/local/bin/claude")


def _ask_with(monkeypatch, fake):
    monkeypatch.setattr(claude_cli.subprocess, "run", fake)
    return claude_cli.make_ask()


def test_not_installed_is_a_claude_error():
    with pytest.raises(ClaudeCallError, match="claude CLI not found"):
        claude_cli.make_ask()


def test_claude_is_asked_once_with_no_tools_no_session_no_settings(installed, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-real")
    fake = FakeRun(_cli_json())
    reply = _ask_with(monkeypatch, fake)("SYSTEM PROMPT", "the posting")
    (args, kw), = fake.calls
    assert args[:4] == ["/usr/local/bin/claude", "-p", "--model", "claude-sonnet-5-5"]
    assert args[args.index("--tools") + 1] == ""
    assert args[args.index("--setting-sources") + 1] == ""
    assert "--no-session-persistence" in args and "--strict-mcp-config" in args
    assert args[args.index("--system-prompt") + 1] == "SYSTEM PROMPT"
    assert kw["input"] == "the posting"                         # the question goes in on stdin
    assert "ANTHROPIC_API_KEY" not in kw["env"]                 # subscription, never API credits
    assert reply.text == '{"ok": true}' and reply.stop_reason == "end_turn"
    assert reply.meta["via"] == "cli" and reply.meta["model"] == "claude-sonnet-5-5"


def test_each_call_runs_in_its_own_empty_folder(installed, monkeypatch, tmp_path):
    fake = FakeRun(_cli_json())
    ask = _ask_with(monkeypatch, fake)
    ask("s", "u"), ask("s", "u")
    folders = [kw["cwd"] for _, kw in fake.calls]
    assert folders[0] != folders[1] and "claude-judge-" in folders[0]


@pytest.mark.parametrize("fake, message", [
    (FakeRun(timeout=True), "timed out"),
    (FakeRun("Error: not logged in", returncode=1), "without JSON output"),
    (FakeRun(_cli_json(is_error=True, subtype="error_during_execution", result="usage limit reached"), returncode=1),
     "usage limit reached"),
])
def test_every_failure_becomes_a_claude_error(installed, monkeypatch, fake, message):
    with pytest.raises(ClaudeCallError, match=message):
        _ask_with(monkeypatch, fake)("s", "u")


def test_stop_reason_is_passed_through_for_the_judge_to_check(installed, monkeypatch):
    reply = _ask_with(monkeypatch, FakeRun(_cli_json(stop_reason="max_tokens")))("s", "u")
    assert reply.stop_reason == "max_tokens"     # claude.judge turns anything but end_turn into an error
