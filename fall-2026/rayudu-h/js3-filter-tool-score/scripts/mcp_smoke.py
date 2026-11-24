"""A scripted MCP session through the logging tap, including requests a client should not make.

    python scripts/mcp_smoke.py [--server js3|filesystem ...]

Writes transcripts/smoke-<time>.jsonl (both directions, verbatim). Standard library only.
"""
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SINCE = "2026-11-07T184247-live"

SESSION = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize",
     "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "mcp_smoke.py", "version": "1"}}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
     "params": {"name": "search_new_postings", "arguments": {"since_snapshot": SINCE, "limit": 3}}},
    # requests a compatible client is not entitled to have honored:
    {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
     "params": {"name": "search_new_postings", "arguments": {"since_snapshot": SINCE, "board": "../../etc/passwd"}}},
    {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
     "params": {"name": "search_new_postings", "arguments": {"since_snapshot": SINCE, "limit": 500}}},
    {"jsonrpc": "2.0", "id": 6, "method": "tools/call",
     "params": {"name": "search_new_postings", "arguments": {"since_snapshot": SINCE, "threshold": 0}}},
    {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "write_file", "arguments": {"path": "x"}}},
    {"jsonrpc": "2.0", "id": 8, "method": "resources/read", "params": {"uri": "file:///etc/passwd"}},
    "{this line is not JSON",
    {"jsonrpc": "2.0", "id": 9, "method": "ping"},
]


def main() -> int:
    out = ROOT / "transcripts"
    out.mkdir(exist_ok=True)
    log = out / f"smoke-{dt.datetime.now().strftime('%Y-%m-%dT%H%M%S')}.jsonl"
    tap = [sys.executable, str(ROOT / "scripts" / "mcp_tap.py"), "--log", str(log), "--",
           sys.executable, str(ROOT / "scripts" / "run_mcp_server.py")]
    proc = subprocess.Popen(tap, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
    replies = []
    for msg in SESSION:
        line = msg if isinstance(msg, str) else json.dumps(msg)
        proc.stdin.write(line + "\n")
        proc.stdin.flush()
        if isinstance(msg, dict) and "id" not in msg:
            time.sleep(0.2)                                   # a notification: no reply expected
            continue
        replies.append(json.loads(proc.stdout.readline()))
    proc.stdin.close()
    proc.wait(timeout=20)
    for r in replies:
        tag = "error " + str(r["error"]["code"]) if "error" in r else (
            "isError" if r.get("result", {}).get("isError") else "ok")
        print(r.get("id"), tag)
    print("transcript:", log.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
