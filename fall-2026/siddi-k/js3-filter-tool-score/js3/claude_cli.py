"""Running the real `claude` CLI, isolated as in JS1 (config/claude_cmd.txt there): a new empty temp directory per
call, built-in tools off, pinned model, UTF-8 both ways, stdout saved unmodified. The binary comes from CLAUDE_BIN
or PATH."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import policy

MODEL = "claude-sonnet-5-5"
BASE_ARGV = ["-p", "--model", MODEL, "--tools", "", "--no-session-persistence", "--strict-mcp-config",
             "--setting-sources", "project"]


def claude_bin() -> str:
    exe = os.environ.get("CLAUDE_BIN") or shutil.which("claude")
    if not exe:
        raise SystemExit("claude CLI not found: set CLAUDE_BIN or put claude on PATH")
    return exe


def run(prompt: str, extra_argv: list[str], output_format: str = "json", mcp_config: dict | None = None,
        timeout: float = 600.0) -> tuple[list[str], bytes, str, int]:
    """Returns (argv as run, raw stdout, stderr text, exit code)."""
    with tempfile.TemporaryDirectory(prefix="js3-claude-", ignore_cleanup_errors=True) as tmp:
        argv = [claude_bin(), *BASE_ARGV, "--output-format", output_format, *extra_argv]
        if output_format == "stream-json":
            argv.append("--verbose")
        if mcp_config is not None:
            cfg_path = Path(tmp) / "mcp.json"
            cfg_path.write_text(json.dumps(mcp_config), encoding="utf-8")
            argv += ["--mcp-config", str(cfg_path)]
        proc = subprocess.run(argv, input=prompt.encode("utf-8"), capture_output=True, cwd=tmp, timeout=timeout)
    return argv, proc.stdout, proc.stderr.decode("utf-8", "replace"), proc.returncode


def js3_mcp_config(transcript_rel: str, extra_args: list[str] | None = None) -> dict:
    """The --mcp-config entry that starts this folder's server, with its transcript inside evidence/."""
    transcript = policy.check_write(transcript_rel)
    return {"mcpServers": {"js3": {
        "type": "stdio", "command": sys.executable,
        "args": ["-m", "js3.mcp_server", "--transcript", str(transcript), *(extra_args or [])],
        "env": {"PYTHONPATH": str(policy.ROOT), "PYTHONIOENCODING": "utf-8"}}}}


def envelope_result(stdout: bytes) -> tuple[str | None, str | None]:
    """(result text, error) from a --output-format json envelope. Nothing is repaired."""
    try:
        env = json.loads(stdout.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None, "stdout is not a UTF-8 JSON envelope"
    if not isinstance(env, dict) or env.get("is_error") is not False or not isinstance(env.get("result"), str):
        return None, "error envelope or no result string"
    return env["result"], None
