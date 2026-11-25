"""The two ways the judge can reach Claude. Each returns send(system, user) -> reply text.

claude-code  Runs `claude -p` with every tool, MCP server, settings source, slash command,
             and saved session turned off, in an empty temporary directory. Uses the Claude
             Code login the course provides. Claude Code adds its own context to the request
             (see README.md, "Known limits").
api          One POST to https://api.anthropic.com/v1/messages through jobwatch.net (allow-list,
             no redirects), using ANTHROPIC_API_KEY. The key is sent only in the x-api-key
             header and never appears in an error message or a saved file.
"""

import json
import os
import subprocess
import tempfile
import urllib.error

from jobwatch import net
from jobwatch.errors import JudgeError

CHOICES = ("claude-code", "api")
DEFAULT = "claude-code"
DEFAULT_MODEL = "claude-opus-5-5"
API_VERSION = "2026-10-21"
FALLBACK_BETA = "server-side-fallback-2026-07-01"
EFFORT = "medium"
MAX_TOKENS = 16000


class Reply(str):
    """Reply text plus metadata about the call that produced it (model, usage, cost)."""

    def __new__(cls, text, meta):
        reply = super().__new__(cls, text)
        reply.meta = meta
        return reply


def api_send(model, *, api_key=None, opener=None):
    def send(system, user):
        key = os.environ.get("ANTHROPIC_API_KEY", "") if api_key is None else api_key
        if not key:
            raise JudgeError("ANTHROPIC_API_KEY is not set; nothing was sent")
        body = {
            "model": model,
            "max_tokens": MAX_TOKENS,
            "system": system,
            "messages": [{"role": "user", "content": user}],
            "output_config": {"effort": EFFORT},
            "fallbacks": "default",
        }
        headers = {
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": API_VERSION,
            "anthropic-beta": FALLBACK_BETA,
        }
        try:
            with net.request("POST", net.MODEL_URL, data=json.dumps(body).encode("utf-8"),
                             headers=headers, opener=opener, timeout=600) as response:
                payload = json.loads(response.read())
        except urllib.error.HTTPError as error:
            raise JudgeError(f"Claude API returned HTTP {error.code}") from None
        except (urllib.error.URLError, OSError, ValueError) as error:
            raise JudgeError(f"Claude API request failed ({type(error).__name__})") from None
        stop = payload.get("stop_reason")
        if stop != "end_turn":
            raise JudgeError(f"Claude API stopped with stop_reason {stop!r}; no verdict")
        text = "".join(block.get("text", "") for block in payload.get("content", []) if block.get("type") == "text")
        return Reply(text, {"transport": "api", "requested_model": model, "model": payload.get("model"),
                            "message_id": payload.get("id"), "usage": payload.get("usage")})
    return send


def claude_code_send(model, *, runner=subprocess.run):
    def send(system, user):
        command = [
            "claude", "-p",
            "--model", model,
            "--system-prompt", system,
            "--tools", "",
            "--setting-sources", "",
            "--strict-mcp-config",
            "--disable-slash-commands",
            "--no-session-persistence",
            "--output-format", "json",
        ]
        env = dict(os.environ, CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1")
        with tempfile.TemporaryDirectory(prefix="jobwatch-judge-") as empty_dir:
            try:
                done = runner(command, input=user, capture_output=True, text=True,
                              cwd=empty_dir, env=env, timeout=600)
            except (OSError, subprocess.SubprocessError) as error:
                raise JudgeError(f"could not run claude -p ({type(error).__name__})") from None
        if done.returncode != 0:
            raise JudgeError(f"claude -p exited with code {done.returncode}")
        try:
            out = json.loads(done.stdout)
        except ValueError:
            raise JudgeError("claude -p did not print a JSON result") from None
        if not isinstance(out, dict) or out.get("is_error") or not isinstance(out.get("result"), str):
            raise JudgeError("claude -p reported an error instead of a reply")
        return Reply(out["result"], {"transport": "claude-code", "requested_model": model,
                                     "session_id": out.get("session_id"), "usage": out.get("usage"),
                                     "total_cost_usd": out.get("total_cost_usd")})
    return send


def get(name, model=DEFAULT_MODEL):
    if name == "api":
        return api_send(model)
    if name == "claude-code":
        return claude_code_send(model)
    raise ValueError(f"unknown judge transport {name!r}; choose one of {CHOICES}")
