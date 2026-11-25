"""Evaluate MY server (earlybird/mcp_server.py) the way scripts/eval_fetch_server.py evaluates someone else's:
what it declares vs what it does. Usage: python scripts/eval_own_server.py evaluations/earlybird-score/results.json"""
import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1])
res = {}

# 1. Declared imports: static. Does the server (or anything it imports from earlybird) reach for a network library?
NET = {"urllib", "urllib.request", "http", "http.client", "requests", "httpx", "socket", "ftplib", "smtplib", "ssl"}
found = {}
for f in ["mcp_server", "rule", "claims", "boards", "resume"]:
    tree = ast.parse((ROOT / "earlybird" / f"{f}.py").read_text(encoding="utf-8"))
    mods = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            mods |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            mods.add(n.module)
    found[f] = sorted(mods & NET)
res["network_imports_by_module"] = found

# 2. Runtime: after the server's own start-up patch, every connect path fails (connect_ex got past v1 of the guard).
code = "\n".join([
    "import socket", "from earlybird import mcp_server as m",
    "srv = socket.socket(); srv.bind(('127.0.0.1', 0)); srv.listen(1); port = srv.getsockname()[1]",
    "m.disable_network()", "out = []",
    "for name, fn in (('connect', lambda s: s.connect(('127.0.0.1', port))), ('connect_ex', lambda s: s.connect_ex(('127.0.0.1', port)) == 0), ('create_connection', lambda s: socket.create_connection(('127.0.0.1', port)))):",
    "    try:", "        out.append(name + ':' + ('CONNECTED' if fn(socket.socket()) else 'refused'))",
    "    except OSError:", "        out.append(name + ':refused')", "print(' '.join(out))"])
res["connect_paths_after_patch"] = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True).stdout.strip()


# 3. Filesystem: hash every file in the project (except the private folder and pycache) before/after a full scripted run.
def tree_hash():
    h = {}
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and "private" not in p.parts and ".git" not in p.parts:
            h[str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return h


before = tree_hash()
env = dict(os.environ, PYTHONIOENCODING="utf-8")
env.pop("EARLYBIRD_MCP_LOG", None)
tmp = ROOT / "evaluations" / "earlybird-score" / "_scratch.jsonl"
subprocess.run([sys.executable, "scripts/mcp_demo_client.py", str(tmp)], cwd=ROOT, env=env, capture_output=True)
tmp.unlink(missing_ok=True)
after = tree_hash()
res["files_changed_by_a_full_run_with_log_pointed_at_scratch"] = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))

# 4. Protocol: tools before initialize; huge line; a client asking for capabilities it was not offered.
def session(msgs, log=None):
    p = subprocess.Popen([sys.executable, "-m", "earlybird.mcp_server"], cwd=ROOT, env=env, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate(("\n".join(json.dumps(m) if not isinstance(m, str) else m for m in msgs) + "\n").encode(), timeout=60)
    return [json.loads(x) for x in out.decode().splitlines()], err.decode()[-300:]


r, _ = session([{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "score_posting", "arguments": {"posting_id": "8301253", "board": "greenhouse_stripe"}}}])
res["tool_call_before_initialize_answered"] = "result" in r[0] and not r[0]["result"].get("isError", False)
r, _ = session([{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {"roots": {}, "sampling": {}, "elicitation": {}}, "clientInfo": {"name": "x", "version": "0"}}}])
res["server_capabilities_declared"] = r[0]["result"]["capabilities"]
r, err = session(["x" * 5_000_000, {"jsonrpc": "2.0", "id": 2, "method": "ping"}])
res["5MB_line_answered_then_server_still_alive"] = [m.get("error", {}).get("code", "ok") for m in r]

# 5. What a tool result tells the model about the persona (data exposure by design).
r, _ = session([{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "score_posting", "arguments": {"posting_id": "8760167002", "board": "greenhouse_databricks"}}}])
body = json.loads(r[0]["result"]["content"][0]["text"])
res["persona_facts_in_result_text"] = {"justification": body["justification"]}
OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(res, indent=1, ensure_ascii=False))
