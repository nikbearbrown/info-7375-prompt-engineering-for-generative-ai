"""Default phone line to Claude: one `claude -p` run per posting, on the user's Claude Code subscription (D18).

Why not only the API: most people pay for a Claude subscription, not API credits (Isaac,
2026-10-31), and a TA for this course already has Claude Code. The judge doesn't change; this
file only provides the same ask(system, user) -> Reply as claude_api.py.

What keeps this a single question and not an agent: all tools off, no MCP, no saved session,
no settings or CLAUDE.md loaded, and a fresh empty temp folder as the working directory. Each call
is therefore a fresh conversation (what the sampling report needs) that can read, write and send
nothing except its answer.
"""

import json
import os
import shutil
import subprocess
import tempfile

from ..common.errors import ClaudeCallError
from .claude import MODEL, Reply

TIMEOUT_S = 300
# Removed from the child's environment: with an API key present, Claude Code would bill API credits
# instead of the subscription, and a base URL could point it at a host we never allowed.
_DROP_ENV = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL")


def find_claude() -> str | None:
    """Its own function so tests can make Claude Code 'not installed' and never start a real call."""
    return shutil.which("claude")


def command(exe: str, system: str) -> list[str]:
    """The exact flags, in one place, so the README and the tests can show what Claude was allowed to do."""
    return [exe, "-p", "--model", MODEL,
            "--tools", "",                     # no Read/Bash/Web: it answers, it can't act
            "--no-session-persistence",        # nothing saved, nothing resumed: a fresh conversation
            # No user/project settings, hooks or CLAUDE.md. Measured 2026-10-31: 608 input tokens with
            # this flag vs 2,819 without, where Claude quoted Isaac's own AGENTS.md back.
            "--setting-sources", "",
            "--strict-mcp-config",             # no MCP servers/connectors either (none loaded today; future-proof)
            "--output-format", "json",         # gives result + stop_reason + model, not just text
            "--system-prompt", system]         # replaces Claude Code's own system prompt


def make_ask():
    exe = find_claude()
    if exe is None:
        raise ClaudeCallError("claude CLI not found: install Claude Code and log in, or use --claude-via api")
    env = {k: v for k, v in os.environ.items() if k not in _DROP_ENV}

    def ask(system: str, user: str) -> Reply:
        # The question goes in on stdin, not as an argument: a JD can be longer than an argument
        # may be, and stdin never shows up in the process list.
        with tempfile.TemporaryDirectory(prefix="claude-judge-") as cwd:
            try:
                proc = subprocess.run(command(exe, system), input=user, capture_output=True,
                                      text=True, cwd=cwd, env=env, timeout=TIMEOUT_S)
            except subprocess.TimeoutExpired:
                raise ClaudeCallError(f"claude -p timed out after {TIMEOUT_S} s") from None
        try:
            out = json.loads(proc.stdout)
        except json.JSONDecodeError:
            detail = (proc.stderr or proc.stdout).strip()[:300]
            raise ClaudeCallError(f"claude -p exited {proc.returncode} without JSON output: {detail}") from None
        if proc.returncode != 0 or out.get("is_error"):
            raise ClaudeCallError(f"claude -p failed ({out.get('subtype')}): {str(out.get('result'))[:300]}")
        models = list(out.get("modelUsage") or {})
        usage = out.get("usage") or {}
        meta = {
            "via": "cli",
            # Recorded, not trusted: if Claude Code ever served another model, the raw file shows it.
            "model": models[0] if len(models) == 1 else models,
            "session_id": out.get("session_id"),
            "num_turns": out.get("num_turns"),
            "usage": {"input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens")},
        }
        return Reply(out.get("result") or "", out.get("stop_reason"), meta)

    return ask
