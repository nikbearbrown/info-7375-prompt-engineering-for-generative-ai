"""Calling Claude: carried over from JS1 agent/claude_judge.py (ask_claude, claude_executable).

Each call is a fresh Claude Code CLI session (claude -p) with no tools, no session
persistence, customizations off (--safe-mode), and the prompt file as the whole system prompt.
Every reply is kept with its metadata. Nothing here repairs or guesses at a reply.
"""
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

CLAUDE_MODEL = "claude-opus-5-5"   # inherited from JS1 (my choice there, over Claude's suggestion of Sonnet)


def claude_executable() -> str:
    exe = shutil.which("claude")
    if not exe:
        raise RuntimeError("Claude Code CLI not found: npm install -g @anthropic-ai/claude-code, then log in")
    p = Path(exe)
    if p.suffix.lower() == ".cmd":  # Windows npm shim; call the native binary to avoid cmd.exe quoting
        native = p.parent / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe"
        if native.exists():
            return str(native)
    return exe


def ask_claude(system_prompt: str, user_prompt: str, model: str = CLAUDE_MODEL, timeout: int = 600) -> dict:
    """One fresh, tool-less conversation. Returns the reply text and call metadata."""
    asked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with tempfile.TemporaryDirectory() as tmp:
        sp = Path(tmp) / "system_prompt.md"
        sp.write_text(system_prompt, encoding="utf-8")
        cmd = [claude_executable(), "-p", "--safe-mode", "--tools", "", "--no-session-persistence",
               "--model", model, "--system-prompt-file", str(sp), "--output-format", "json"]
        proc = subprocess.run(cmd, input=user_prompt, capture_output=True, text=True,
                              encoding="utf-8", timeout=timeout, cwd=tmp)
    meta = {"asked_at_utc": asked_at, "model_requested": model}
    if proc.returncode != 0:
        return {**meta, "call_error": (proc.stderr or proc.stdout).strip()[:500], "raw_text": None}
    env = json.loads(proc.stdout)
    return {
        **meta,
        "models_reported": sorted(env.get("modelUsage", {})),
        "session_id": env.get("session_id"),
        "call_error": env.get("result") if env.get("is_error") else None,
        "raw_text": None if env.get("is_error") else env.get("result", ""),
    }


def parse_json_reply(text: str | None):
    """The reply must be exactly one JSON object. Returns (obj, None) or (None, why rejected)."""
    if text is None:
        return None, "no reply"
    try:
        obj = json.loads(text.strip())
    except json.JSONDecodeError:
        return None, "not a single JSON object (extra text, code fences, or invalid JSON)"
    if not isinstance(obj, dict):
        return None, "JSON is not an object"
    return obj, None
