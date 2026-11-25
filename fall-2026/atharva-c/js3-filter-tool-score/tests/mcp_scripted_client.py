"""A scripted MCP client: starts agent/mcp_server.py and records every message both ways.

This is NOT a model talking to the server; it is a fixed script, for a raw-protocol
transcript. The client transcript with Claude Code is recorded separately.

    python3 -m tests.mcp_scripted_client evidence/mcp/scripted-transcript.jsonl
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "scripted-client", "version": "0"}}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "search_postings",
                                                                     "arguments": {"query": "Software Engineer I,", "limit": 5}}},
    {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "judge_posting",
                                                                     "arguments": {"uid": "affirm:7727320003"}}},
    {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "shortlist_entry",
                                                                     "arguments": {"uid": "robinhood:7263592"}}},
    {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "get_posting", "arguments": {"uid": "nope:1"}}},
    {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "apply_to_job",
                                                                     "arguments": {"uid": "affirm:8032173003"}}},
]


def main(out: str) -> int:
    env = dict(os.environ, JS3_MCP_LOG="out/mcp-scripted-calls.jsonl")
    p = subprocess.Popen([sys.executable, "-m", "agent.mcp_server"], cwd=ROOT, env=env, text=True,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    rows = []
    for msg in SCRIPT:
        rows.append({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "dir": "client->server", "msg": msg})
        p.stdin.write(json.dumps(msg) + "\n")
        p.stdin.flush()
        if "id" in msg:
            reply = json.loads(p.stdout.readline())
            rows.append({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "dir": "server->client", "msg": reply})
    p.stdin.close()
    p.wait(timeout=5)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(f"{len(rows)} messages -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "evidence/mcp/scripted-transcript.jsonl"))
