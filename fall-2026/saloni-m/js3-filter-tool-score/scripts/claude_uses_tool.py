"""Claude Code as the MCP client of my server. A real Claude call; the response is saved with its date.

    python3 scripts/claude_uses_tool.py

Claude gets only my two tools (--strict-mcp-config, every built-in tool disallowed). The server
writes its own transcript of what Claude Code sent and what it answered (out/mcp/transcripts/),
and this script saves Claude's final answer and metadata to out/mcp/claude-client-<UTC>.json.
"""
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
BUILTINS = "Bash,Edit,Write,Read,Glob,Grep,WebFetch,WebSearch,NotebookEdit,Task,TodoWrite,SlashCommand,Skill,BashOutput,KillShell"
PROMPT = ("You have two tools from an MCP server called js3. Use search_postings to find postings whose title "
          "contains 'data engineer'. Then call score_posting on the first result's uid. Report the uid, title, score, "
          "decision, and the rules that fired, exactly as the tools returned them. Do not add anything the tools "
          "did not return.")


def main():
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    cfg = {"mcpServers": {"js3": {"type": "stdio", "command": sys.executable, "args": ["-m", "js3.mcp_server"],
                                  "env": {"PYTHONPATH": HERE}}}}
    with tempfile.TemporaryDirectory() as cwd:
        cfg_path = os.path.join(cwd, "mcp.json")
        with open(cfg_path, "w") as f:
            json.dump(cfg, f)
        before = set(os.listdir(os.path.join(HERE, "out", "mcp", "transcripts")))
        proc = subprocess.run(
            ["claude", "-p", PROMPT, "--model", MODEL, "--output-format", "json", "--strict-mcp-config",
             "--mcp-config", cfg_path, "--allowedTools", "mcp__js3__search_postings,mcp__js3__score_posting",
             "--disallowedTools", BUILTINS],
            cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=300)
    after = sorted(set(os.listdir(os.path.join(HERE, "out", "mcp", "transcripts"))) - before)
    try:
        meta = json.loads(proc.stdout)
    except json.JSONDecodeError:
        meta = {"unparsed_stdout": proc.stdout[-3000:], "stderr": proc.stderr[-3000:]}
    rec = {"ran_at_utc": stamp, "model_requested": MODEL, "prompt": PROMPT, "claude_code_version": _version(),
           "server_transcripts": after, "returncode": proc.returncode,
           "result": meta.get("result"), "models_used": sorted(meta.get("modelUsage", {}) or {}),
           "num_turns": meta.get("num_turns"), "is_error": meta.get("is_error"), "session_id": meta.get("session_id")}
    if "unparsed_stdout" in meta:
        rec.update(meta)
    out = os.path.join(HERE, "out", "mcp", f"claude-client-{stamp}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2, ensure_ascii=False)
    print(json.dumps(rec, indent=2, ensure_ascii=False))


def _version():
    try:
        return subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as e:  # noqa: BLE001
        return f"unknown: {e}"


if __name__ == "__main__":
    main()
