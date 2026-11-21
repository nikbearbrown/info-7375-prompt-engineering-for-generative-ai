"""Ways to get a model reply. Every adapter labels where its text came from.

- ClaudeCLIAdapter: calls the Claude Code CLI (`claude -p`). Live model output.
- RecordedAdapter: replays real Claude replies saved word for word with their
  date and prompt. It never invents a reply; a missing one is an error.
- ScriptedAdapter: fixed text for tests and deliberate failure cases. Labelled
  as a fixture, never as model output.
"""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


class ModelUnavailable(Exception):
    """No reply could be obtained (not logged in, missing recording, timeout)."""


class ScriptedAdapter:
    def __init__(self, replies, label="scripted fixture (not model output)"):
        self.replies = list(replies)
        self.label = label
        self.calls = 0

    def propose(self, qid, prompt, attempt):
        self.calls += 1
        if attempt >= len(self.replies):
            raise ModelUnavailable("scripted adapter has no more replies")
        return self.replies[attempt]


class RecordedAdapter:
    def __init__(self, path):
        self.path = Path(path)
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.provenance = data.get("provenance", {})
        self.responses = data.get("responses", {})
        self.label = ("recorded Claude reply, replayed: "
                      + self.provenance.get("source", "unknown source")
                      + ", " + self.provenance.get("date", "undated"))
        self.calls = 0

    def propose(self, qid, prompt, attempt):
        self.calls += 1
        if attempt > 0:
            raise ModelUnavailable("only one recorded reply exists per question")
        if qid not in self.responses:
            raise ModelUnavailable(f"no recorded reply for {qid}")
        return self.responses[qid]


def find_claude():
    return os.environ.get("SPONSORSQL_CLAUDE_BIN") or shutil.which("claude")


class ClaudeCLIAdapter:
    def __init__(self, binary=None, timeout=180):
        self.binary = binary or find_claude()
        self.timeout = timeout
        self.label = f"live Claude Code CLI ({self.binary or 'not found'})"
        self.calls = 0

    def propose(self, qid, prompt, attempt):
        self.calls += 1
        if not self.binary:
            raise ModelUnavailable("claude CLI not found; set SPONSORSQL_CLAUDE_BIN")
        # Run from an empty folder so the model can't open project files such as the
        # answer keys (independent review, finding 14).
        try:
            with tempfile.TemporaryDirectory(prefix="sponsorsql-cli-") as empty:
                done = subprocess.run(
                    [self.binary, "-p", prompt, "--output-format", "json", "--max-turns", "1"],
                    capture_output=True, text=True, timeout=self.timeout, check=False, cwd=empty)
        except subprocess.TimeoutExpired as exc:
            raise ModelUnavailable("claude CLI timed out") from exc
        except OSError as exc:
            raise ModelUnavailable(f"claude CLI could not start: {exc}") from exc
        try:
            reply = json.loads(done.stdout)
        except json.JSONDecodeError as exc:
            raise ModelUnavailable(f"claude CLI gave non-JSON output: {done.stderr[-200:]}") from exc
        if reply.get("is_error") or done.returncode != 0:
            raise ModelUnavailable(f"claude CLI error: {reply.get('result', '')[:200]}")
        return reply.get("result", "")
