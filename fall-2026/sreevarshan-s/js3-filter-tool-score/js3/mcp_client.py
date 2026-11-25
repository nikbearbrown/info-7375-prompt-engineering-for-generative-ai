"""Run js3.mcp_server as a subprocess and record a request/response transcript.

Usage (from the repo root):
    python3 -m js3.mcp_client

Sends initialize, tools/list, and two tools/call(score_posting) requests over
the server's stdio, one JSON line each: "Data Engineer" (no exact match, so it
shows the not-found path) and "Machine Learning Engineer, Radar" (a found,
passed posting). Writes every request and response to output/mcp_transcript.txt.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPT = ROOT / "output" / "mcp_transcript.txt"

REQUESTS = [
    {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "js3-mcp-client", "version": "0.1.0"},
        },
    },
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    {
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "score_posting", "arguments": {"title": "Data Engineer"}},
    },
    {
        "jsonrpc": "2.0", "id": 4, "method": "tools/call",
        "params": {"name": "score_posting", "arguments": {"title": "Machine Learning Engineer, Radar"}},
    },
]


def run(transcript: Path = TRANSCRIPT, requests: list[dict] = REQUESTS) -> list[dict]:
    proc = subprocess.Popen(
        [sys.executable, "-B", "-m", "js3.mcp_server"],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    lines: list[str] = []
    responses: list[dict] = []
    try:
        for req in requests:
            out = json.dumps(req)
            proc.stdin.write(out + "\n")
            proc.stdin.flush()
            reply = proc.stdout.readline()
            if not reply:
                raise RuntimeError(f"server closed stdout; stderr: {proc.stderr.read()}")
            lines += [f"REQUEST  {out}", f"RESPONSE {reply.rstrip()}", ""]
            responses.append(json.loads(reply))
    finally:
        proc.stdin.close()
        proc.wait(timeout=10)

    header = [
        "MCP transcript: js3.mcp_client -> js3.mcp_server (subprocess, stdio, JSON-RPC 2.0)",
        f"Server command: {Path(sys.executable).name} -B -m js3.mcp_server",
        f"Server exit code: {proc.returncode}",
        "",
    ]
    transcript.parent.mkdir(parents=True, exist_ok=True)
    transcript.write_text("\n".join(header + lines), encoding="utf-8")
    return responses


if __name__ == "__main__":
    run()
    print(f"wrote {TRANSCRIPT}")
