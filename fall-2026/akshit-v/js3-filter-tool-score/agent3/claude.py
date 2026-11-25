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


def ask_claude_isolated(system_prompt: str, user_prompt: str, mcp_servers: dict | None = None,
                        allowed_tools=(), model: str = CLAUDE_MODEL, timeout: int = 600) -> dict:
    """The one call shape used by every held-out experiment condition, so that only the measured object differs.

    --safe-mode cannot be used here because it also turns MCP off, and the tool-list condition needs
    MCP. Instead every condition gets: no setting sources, no slash commands/skills, no built-in tools,
    the prompt as the whole system prompt, and --strict-mcp-config with an explicit server list
    ({} = no tools). Returns the reply text, the tool calls Claude made, and metadata.
    """
    asked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with tempfile.TemporaryDirectory() as tmp:
        sp = Path(tmp) / "system_prompt.md"
        sp.write_text(system_prompt, encoding="utf-8")
        cfg = Path(tmp) / "mcp.json"
        cfg.write_text(json.dumps({"mcpServers": mcp_servers or {}}), encoding="utf-8")
        cmd = [claude_executable(), "-p", "--model", model, "--tools", "", "--setting-sources", "",
               "--disable-slash-commands", "--strict-mcp-config", "--mcp-config", str(cfg),
               "--no-session-persistence", "--system-prompt-file", str(sp),
               "--output-format", "stream-json", "--verbose"]
        if allowed_tools:
            cmd += ["--allowedTools", ",".join(allowed_tools)]
        proc = subprocess.run(cmd, input=user_prompt, capture_output=True, text=True,
                              encoding="utf-8", timeout=timeout, cwd=tmp)
    meta = {"asked_at_utc": asked_at, "model_requested": model, "mcp_servers": sorted(mcp_servers or {}),
            "allowed_tools": list(allowed_tools)}
    events = [json.loads(l) for l in proc.stdout.splitlines() if l.startswith("{")]
    res = next((e for e in reversed(events) if e.get("type") == "result"), None)
    tool_calls = [{"name": c.get("name"), "input": c.get("input")}
                  for e in events if e.get("type") == "assistant"
                  for c in (e.get("message", {}).get("content") or []) if c.get("type") == "tool_use"]
    if proc.returncode != 0 or res is None:
        return {**meta, "call_error": (proc.stderr or proc.stdout).strip()[:500], "raw_text": None,
                "tool_calls": tool_calls}
    return {**meta, "models_reported": sorted(res.get("modelUsage", {})), "session_id": res.get("session_id"),
            "call_error": res.get("result") if res.get("is_error") else None,
            "raw_text": None if res.get("is_error") else res.get("result", ""), "tool_calls": tool_calls}


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
