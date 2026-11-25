"""Offer score_posting to real Claude (Claude Code CLI, headless) and keep both sides of the conversation.

    python3 tools/claude_mcp_session.py --label s1 --prompt-file prompts/mcp-session-s1.md

Writes, under transcripts/ (dated, never edited afterwards):
  <date>-<label>-server.jsonl   every JSON-RPC line the server received and sent (recorded by the server itself)
  <date>-<label>-claude.jsonl   Claude Code's stream-json: the tool_use / tool_result messages and the final answer
  <date>-<label>-meta.json      exact command, CLI version, prompt file, return code

Claude gets NO built-in tools (--tools ""), only this one MCP server (--strict-mcp-config), and only score_posting is
pre-approved. Live: needs a logged-in Claude Code account. Nothing here is a fixture.
"""

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def redact(text):
    """Local paths only (my home folder name); nothing else in a transcript is changed."""
    return text.replace(str(ROOT), "<js3-folder>").replace(str(Path.home()), "~")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--model", default=None)
    a = ap.parse_args()
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    tdir = ROOT / "transcripts"
    tdir.mkdir(exist_ok=True)
    server_log = tdir / f"{stamp}-{a.label}-server.jsonl"
    cfg = {"mcpServers": {"js3": {"command": sys.executable, "args": ["-m", "js3.mcp_server"],
                                  "env": {"PYTHONPATH": str(ROOT), "JS3_MCP_TRANSCRIPT": str(server_log)}}}}
    prompt = (ROOT / a.prompt_file).read_text()
    with tempfile.TemporaryDirectory() as tmp:
        cfg_path = Path(tmp) / "mcp.json"
        cfg_path.write_text(json.dumps(cfg))
        cmd = ["claude", "-p", "--output-format", "stream-json", "--verbose", "--tools", "",
               "--strict-mcp-config", "--mcp-config", str(cfg_path),
               "--allowedTools", "mcp__js3__score_posting"]
        if a.model:
            cmd += ["--model", a.model]
        t0 = time.time()
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=tmp, timeout=600)
    (tdir / f"{stamp}-{a.label}-claude.jsonl").write_text(redact(p.stdout))
    ver = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    meta = {"label": a.label, "utc": stamp, "claude_cli": ver, "prompt_file": a.prompt_file,
            "command": cmd, "returncode": p.returncode, "seconds": round(time.time() - t0, 1),
            "stderr_tail": p.stderr[-2000:], "note": "mcp.json was a temp file: " + json.dumps(cfg)}
    (tdir / f"{stamp}-{a.label}-meta.json").write_text(redact(json.dumps(meta, indent=2)) + "\n")
    final = [json.loads(l) for l in p.stdout.splitlines() if l.strip().startswith("{")]
    res = next((m for m in reversed(final) if m.get("type") == "result"), {})
    print(f"rc={p.returncode} -> transcripts/{stamp}-{a.label}-*")
    print(res.get("result", "(no result message)"))


if __name__ == "__main__":
    main()
