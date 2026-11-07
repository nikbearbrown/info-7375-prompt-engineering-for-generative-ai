"""The two ways the judge reaches Claude. The network and the claude command are replaced
by fakes here; every reply below is CONSTRUCTED, not Claude output."""

import io
import json
import subprocess
import unittest
import urllib.error
from pathlib import Path

from jobwatch import transports
from jobwatch.errors import JudgeError

MODEL_URL = "https://api.anthropic.com/v1/messages"
SECRET = "sk-ant-test-SECRET-0000"


class FakeResponse:
    def __init__(self, payload, status=200):
        self.body = json.dumps(payload).encode()
        self.status = status
        self.headers = {"Content-Type": "application/json"}

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def api_payload(text, stop_reason="end_turn"):
    return {
        "id": "msg_constructed",
        "type": "message",
        "role": "assistant",
        "model": "claude-opus-5-5",
        "content": [{"type": "thinking", "thinking": "", "signature": "x"}, {"type": "text", "text": text}],
        "stop_reason": stop_reason,
        "usage": {"input_tokens": 900, "output_tokens": 120},
    }


class ApiTransportTest(unittest.TestCase):
    def test_posts_the_fixed_request_to_the_model_endpoint(self):
        seen = []

        def opener(req, timeout):
            seen.append(req)
            return FakeResponse(api_payload('{"ok": true}'))

        send = transports.api_send("claude-opus-5-5", api_key=SECRET, opener=opener)
        reply = send("SYSTEM TEXT", "USER JSON")
        self.assertEqual(reply, '{"ok": true}')
        self.assertEqual(reply.meta["model"], "claude-opus-5-5")
        [req] = seen
        self.assertEqual((req.get_method(), req.full_url), ("POST", MODEL_URL))
        self.assertEqual(req.get_header("X-api-key"), SECRET)
        body = json.loads(req.data)
        self.assertEqual(body["system"], "SYSTEM TEXT")
        self.assertEqual(body["messages"], [{"role": "user", "content": "USER JSON"}])
        self.assertNotIn("tools", body)

    def test_without_a_key_nothing_is_sent(self):
        seen = []
        send = transports.api_send("claude-opus-5-5", api_key="", opener=lambda req, timeout: seen.append(req))
        with self.assertRaises(JudgeError):
            send("s", "u")
        self.assertEqual(seen, [])

    def test_errors_never_contain_the_key(self):
        failures = [
            urllib.error.HTTPError(MODEL_URL, 401, f"bad key {SECRET}", {}, io.BytesIO(SECRET.encode())),
            urllib.error.URLError(f"connection reset {SECRET}"),
        ]
        for failure in failures:
            def opener(req, timeout, failure=failure):
                raise failure
            send = transports.api_send("claude-opus-5-5", api_key=SECRET, opener=opener)
            with self.subTest(failure=type(failure).__name__), self.assertRaises(JudgeError) as caught:
                send("s", "u")
            self.assertNotIn(SECRET, str(caught.exception))

    def test_a_refusal_is_an_error_not_a_verdict(self):
        send = transports.api_send("claude-opus-5-5", api_key=SECRET,
                                   opener=lambda req, timeout: FakeResponse(api_payload("", "refusal")))
        with self.assertRaises(JudgeError):
            send("s", "u")


class ClaudeCodeTransportTest(unittest.TestCase):
    def runner_returning(self, stdout, returncode=0):
        calls = []

        def run(cmd, **kwargs):
            cwd = Path(kwargs["cwd"])
            calls.append({"cmd": cmd, "kwargs": kwargs, "cwd_listing": sorted(p.name for p in cwd.iterdir())})
            return subprocess.CompletedProcess(cmd, returncode, stdout=stdout, stderr="")
        return run, calls

    def test_runs_claude_without_tools_settings_mcp_or_saved_sessions(self):
        run, calls = self.runner_returning(json.dumps(
            {"type": "result", "is_error": False, "result": '{"ok": true}', "session_id": "s1", "total_cost_usd": 0.01}))
        send = transports.claude_code_send("claude-opus-5-5", runner=run)
        reply = send("SYSTEM TEXT", "USER JSON")
        self.assertEqual(reply, '{"ok": true}')
        [call] = calls
        cmd = call["cmd"]
        self.assertEqual(cmd[:2], ["claude", "-p"])
        for flag, value in (("--tools", ""), ("--setting-sources", ""), ("--system-prompt", "SYSTEM TEXT"),
                            ("--model", "claude-opus-5-5"), ("--output-format", "json")):
            self.assertEqual(cmd[cmd.index(flag) + 1], value, flag)
        for flag in ("--strict-mcp-config", "--disable-slash-commands", "--no-session-persistence"):
            self.assertIn(flag, cmd)
        self.assertEqual(call["kwargs"]["input"], "USER JSON")
        self.assertEqual(call["cwd_listing"], [], "claude must run in an empty directory")

    def test_failures_are_errors(self):
        for stdout, code in (("", 1), ("not json", 0),
                             (json.dumps({"type": "result", "is_error": True, "result": "API Error"}), 0)):
            run, _ = self.runner_returning(stdout, code)
            with self.subTest(stdout=stdout, code=code), self.assertRaises(JudgeError):
                transports.claude_code_send("claude-opus-5-5", runner=run)("s", "u")


if __name__ == "__main__":
    unittest.main()
