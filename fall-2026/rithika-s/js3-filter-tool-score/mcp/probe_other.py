"""Probe the course's Week 8 teaching server (lessons/08-mcp-from-scratch/code/main.py).
Sends fixed JSON-RPC lines over stdio and logs both directions. Read-only: does not modify the lesson."""
import json, subprocess, sys, datetime, pathlib
SERVER = pathlib.Path.home() / "info-7375-prompt-engineering-for-generative-ai/lessons/08-mcp-from-scratch/code/main.py"
steps = [
    ("tools/list before initialize", {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}),
    ("initialize", {"jsonrpc": "2.0", "id": 2, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "rithika-probe", "version": "1"}}}),
    ("tools/list before initialized notice", {"jsonrpc": "2.0", "id": 3, "method": "tools/list"}),
    ("notifications/initialized", {"jsonrpc": "2.0", "method": "notifications/initialized"}),
    ("tools/list", {"jsonrpc": "2.0", "id": 4, "method": "tools/list"}),
    ("lookup office", {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "lookup", "arguments": {"key": "office"}}}),
    ("lookup missing key", {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "lookup", "arguments": {"key": "no-such-key"}}}),
    ("lookup extra arg path", {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "lookup", "arguments": {"key": "office", "path": "../../etc/passwd"}}}),
    ("undeclared tool", {"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": {"name": "delete_record", "arguments": {}}}),
    ("ping", {"jsonrpc": "2.0", "id": 9, "method": "ping"}),
]
lines = [json.dumps(m) for _, m in steps] + ["{not valid json"]
proc = subprocess.run([sys.executable, str(SERVER), "--stdio"], input="\n".join(lines) + "\n", capture_output=True, text=True, timeout=20)
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
out = pathlib.Path("transcripts") / f"teaching-server-probe-{stamp}.jsonl"
with out.open("w") as f:
    for line in lines:
        f.write(json.dumps({"dir": "out", "line": line}) + "\n")
    for line in proc.stdout.splitlines():
        f.write(json.dumps({"dir": "in", "line": line}) + "\n")
    f.write(json.dumps({"returncode": proc.returncode, "stderr_tail": proc.stderr[-400:]}) + "\n")
print("sent", len(lines), "lines; got", len(proc.stdout.splitlines()), "reply lines; exit", proc.returncode)
for line in proc.stdout.splitlines():
    print(" <-", line[:160])
print("stderr tail:", proc.stderr[-300:] or "(none)")
print("transcript:", out)
