"""A scripted MCP client (mine, not Claude) that exercises the server including its error paths, and writes the real
message log in both directions. Usage: python scripts/mcp_demo_client.py transcripts/scripted-client-2026-11-25.jsonl"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
out = Path(sys.argv[1])
out.unlink(missing_ok=True)
env = dict(os.environ, PYTHONIOENCODING="utf-8", EARLYBIRD_MCP_LOG=str(out))
p = subprocess.Popen([sys.executable, "-m", "earlybird.mcp_server"], cwd=ROOT, env=env,
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE)
n = 0


def send(obj=None, raw=None, expect_reply=True):
    p.stdin.write((raw if raw is not None else json.dumps(obj)).encode("utf-8") + b"\n")
    p.stdin.flush()
    return json.loads(p.stdout.readline()) if expect_reply else None


def req(method, params=None):
    global n
    n += 1
    return send({"jsonrpc": "2.0", "id": n, "method": method, **({"params": params} if params is not None else {})})


req("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "demo-client", "version": "0"}})
send({"jsonrpc": "2.0", "method": "notifications/initialized"}, expect_reply=False)
req("tools/list")
call = lambda args, name="score_posting": req("tools/call", {"name": name, "arguments": args})  # noqa: E731
call({"posting_id": "8301253", "board": "greenhouse_stripe"})          # a kept posting
call({"posting_id": "8760167002", "board": "greenhouse_databricks"})   # an R5 reject
call({"posting_id": "no-such-id"})                                     # unknown id -> tool error
call({"posting_id": "../../../etc/passwd"})                            # traversal -> tool error
call({"posting_id": "8301253", "board": "greenhouse_stripe", "cmd": "rm -rf /"})  # extra argument -> tool error
call({}, name="send_email")                                            # unknown tool -> protocol error
req("resources/list")                                                  # not declared -> -32601
send(raw="{not json")                                                  # malformed -> -32700
p.stdin.close()
p.wait(timeout=10)
print("messages logged:", len(out.read_text(encoding="utf-8").splitlines()))
