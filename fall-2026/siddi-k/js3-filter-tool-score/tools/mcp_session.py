"""Record one real session: the Claude CLI (as MCP client) talks to js3.mcp_server, and both sides are saved.

Writes evidence/mcp/<stamp>/: prompt.txt, argv.json, server-transcript.jsonl (every line, both directions, written
by the server itself), claude-stream.jsonl (the CLI's stream-json: its tool_use and tool_result messages),
stderr.txt. Usage: python tools/mcp_session.py [--prompt-file FILE]"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from js3 import claude_cli, policy  # noqa: E402

DEFAULT_PROMPT = """Use the score_posting tool to look up two postings from my job-search agent's collection:
Stripe posting 8415333 and Notion posting 06e1d3a8-2706-4ed9-9fe6-8b69607de18e.
For each, say in one sentence what the filter decided and which matched words drove that.
Then say, in one sentence, whether the tool's result tells you either posting is worth applying to, and why.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt-file")
    a = ap.parse_args()
    prompt = Path(a.prompt_file).read_text(encoding="utf-8") if a.prompt_file else DEFAULT_PROMPT
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    out = f"evidence/mcp/{stamp}"
    cfg = claude_cli.js3_mcp_config(f"{out}/server-transcript.jsonl")
    policy.write_bytes(f"{out}/prompt.txt", prompt.encode("utf-8"))
    argv, stdout, stderr, code = claude_cli.run(prompt, ["--allowedTools", "mcp__js3__score_posting"],
                                                output_format="stream-json", mcp_config=cfg)
    shown = [x if not x.endswith("mcp.json") else "<tmp>/mcp.json" for x in argv]
    shown[0] = "claude"
    policy.write_bytes(f"{out}/argv.json", (json.dumps({"argv": shown, "mcp_config": cfg, "exit_code": code,
                                                        "started_utc": stamp}, indent=2) + "\n").encode("utf-8"))
    policy.write_bytes(f"{out}/claude-stream.jsonl", stdout)
    policy.write_bytes(f"{out}/stderr.txt", stderr.encode("utf-8"))
    print(f"exit {code}; wrote {out}/")
    return code


if __name__ == "__main__":
    sys.exit(main())
