"""One fresh `claude -p` conversation per call, hardened the same way as JS1/JS2's judge
(jsagent/claude_judge.call_claude): no tools, no settings, no MCP, no slash commands, no saved
session, an empty working directory. The only difference: the caller names the system prompt."""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import tempfile


def call(prompt: str, system: str, model: str = "sonnet", timeout: float = 240.0) -> dict:
    cmd = ["claude", "-p", prompt, "--model", model, "--tools", "", "--setting-sources", "",
           "--strict-mcp-config", "--no-session-persistence", "--disable-slash-commands",
           "--system-prompt", system, "--output-format", "json"]
    started = dt.datetime.now(dt.timezone.utc).astimezone()
    with tempfile.TemporaryDirectory() as empty:
        proc = subprocess.run(cmd, cwd=empty, capture_output=True, text=True, timeout=timeout)
    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError:
        envelope = {"is_error": True, "result": proc.stdout[-2000:], "stderr": proc.stderr[-2000:]}
    return {"started_at": started.isoformat(timespec="seconds"), "exit_code": proc.returncode,
            "model_requested": model, "models_used": sorted((envelope.get("modelUsage") or {}).keys()),
            "duration_ms": envelope.get("duration_ms"), "is_error": envelope.get("is_error", proc.returncode != 0),
            "result": envelope.get("result", "")}
