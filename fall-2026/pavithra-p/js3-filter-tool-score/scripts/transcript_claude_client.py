"""Offers my tool server to Claude (Claude Code in print mode as the MCP client) and keeps both sides of the transcript.

* Claude's side: the CLI's stream-json output, saved unchanged to transcripts/claude-client-<time>.jsonl.
* The server's side: every line it received and sent, in transcripts/server-<time>.jsonl (written by the server).

Claude gets only this one tool: `--tools ""` turns off every built-in tool, `--strict-mcp-config` loads no other MCP
server, and `--allowedTools` names the one tool it may call without asking. It runs from an empty temporary folder so
no project file becomes part of its context. A real call: it needs `claude` signed in.

    python3 scripts/transcript_claude_client.py
"""
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from agent import config  # noqa: E402
from agent.policy import Policy  # noqa: E402

PROMPT = """Use the score_posting tool to score these two saved job postings:
1. board "ashby:ramp", job_id "d8925f84-562f-470c-a5bd-4f6c20009361"
2. board "greenhouse:figma", job_id "5802956004"
For each, report the verdict, the score and the reason exactly as the tool gave them.
Then answer in one or two sentences: could this tool apply to either job, or show you the full posting text?
Answer only from what the tool declares and returns."""


def main():
    policy = Policy()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = policy.check_write(config.ROOT / "transcripts" / f"claude-client-{stamp}.jsonl")
    with tempfile.TemporaryDirectory() as empty:
        cfg = os.path.join(empty, "mcp.json")
        with open(cfg, "w") as f:
            json.dump({"mcpServers": {"jobscore": {"command": sys.executable, "args": [os.path.join(HERE, "serve.py")]}}}, f)
        cmd = ["claude", "-p", "--output-format", "stream-json", "--verbose", "--mcp-config", cfg, "--strict-mcp-config",
               "--tools", "", "--allowedTools", "mcp__jobscore__score_posting", "--no-session-persistence"]
        done = subprocess.run(cmd, input=PROMPT, capture_output=True, text=True, timeout=300, cwd=empty)
    header = {"type": "js3-meta", "at": stamp, "command": cmd[:4] + ["<temporary mcp.json>"] + cmd[5:],
              "prompt": PROMPT, "exit": done.returncode, "stderr": done.stderr[-2000:]}
    policy.write_text(out, json.dumps(header) + "\n" + done.stdout)
    for line in done.stdout.splitlines():
        msg = json.loads(line)
        if msg.get("type") == "assistant":
            for part in msg["message"]["content"]:
                if part.get("type") == "tool_use":
                    print("Claude -> tool_use", part["name"], json.dumps(part["input"]))
                elif part.get("type") == "text":
                    print("Claude says:", part["text"])
        elif msg.get("type") == "user":
            for part in msg["message"]["content"]:
                if isinstance(part, dict) and part.get("type") == "tool_result":
                    print("tool_result ->", json.dumps(part.get("content"))[:200])
        elif msg.get("type") == "system" and msg.get("subtype") == "init":
            print("tools Claude had:", msg.get("tools"), "| MCP servers:", msg.get("mcp_servers"), "| model:", msg.get("model"))
    print(f"exit {done.returncode}; Claude's side: {os.path.relpath(out, HERE)}; the server's side: transcripts/server-*.jsonl")
    return done.returncode


if __name__ == "__main__":
    sys.exit(main())
