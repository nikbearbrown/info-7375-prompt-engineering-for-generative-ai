"""Run Claude Code (claude -p) as a real MCP client of agent3.mcp_server, and keep both transcripts.

    python -B scripts/claude_as_client.py --name <label> --prompt "<what to ask Claude>"

The server records every JSON-RPC line in both directions (out/mcp/transcripts/*_<label>.jsonl).
This script saves Claude's own event stream (stream-json) next to it as mcp/transcripts/<label>_claude_stream.jsonl.
Claude gets no built-in tools (--tools ""), only this one server (--strict-mcp-config), and
permission for exactly one tool (--allowedTools mcp__js3-filter__score_posting).
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent3.claude import claude_executable, CLAUDE_MODEL  # noqa: E402

SYSTEM = ("You are helping a person triage job postings for a fictional job seeker. You have one tool, "
          "score_posting, from a local MCP server. Use it when asked. Report only what the tool returned; "
          "say clearly that the score is a keyword filter, not a judgment.")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--filter-version", default="v1.0")
    args = ap.parse_args()
    config = {"mcpServers": {"js3-filter": {
        "type": "stdio", "command": sys.executable,
        "args": ["-B", "-m", "agent3.mcp_server", "--filter-version", args.filter_version,
                 "--transcript-name", args.name],
        "env": {"PYTHONPATH": str(ROOT)}}}}
    with tempfile.TemporaryDirectory() as tmp:
        cfg = Path(tmp) / "mcp.json"
        cfg.write_text(json.dumps(config), encoding="utf-8")
        cmd = [claude_executable(), "-p", "--model", CLAUDE_MODEL, "--tools", "", "--strict-mcp-config",
               "--mcp-config", str(cfg), "--allowedTools", "mcp__js3-filter__score_posting",
               "--system-prompt", SYSTEM, "--no-session-persistence",
               "--output-format", "stream-json", "--verbose"]
        proc = subprocess.run(cmd, input=args.prompt, capture_output=True, text=True, encoding="utf-8",
                              cwd=tmp, timeout=600, env={**os.environ, "PYTHONPATH": str(ROOT)})
    out = ROOT / "mcp" / "transcripts" / f"{args.name}_claude_stream.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"cmd": [Path(cmd[0]).name] + cmd[1:], "prompt": args.prompt}) + "\n" + proc.stdout,
                   encoding="utf-8")
    final = [json.loads(l) for l in proc.stdout.splitlines() if l.startswith("{")]
    res = next((e for e in reversed(final) if e.get("type") == "result"), {})
    print("exit", proc.returncode, "| stderr:", proc.stderr.strip()[:300])
    print("result:", (res.get("result") or "")[:1500])
    print("saved", out.relative_to(ROOT))
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
