"""Phase 5e: run another tool server with our scripted client, in a sandbox, once.

    python scripts/run_other_server.py <sandbox dir> <server entry .js> <out dir>

The server runs as `node <entry> <sandbox>/allowed` from <sandbox>, with an environment holding
only PATH and HOME=<sandbox>/home (no secrets). The client first probes with server/discover
(protocol 2026-07-28), as Claude Code 2.1.332 did in our probe; on an error or no answer within
5 s it falls back to initialize (2025-11-25) and notifications/initialized. Then tools/list, then
one harmless call: list_allowed_directories if the server lists it, else read_text_file on
<sandbox>/allowed/hello.txt. Every line both ways is logged verbatim by scripts/mcp_client.py to
<out dir>/<UTC>-transcript.jsonl; <out dir>/<UTC>-run.json records the setup.
"""
import importlib.util
import json
import os
import platform
import queue
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mcp_client", HERE / "mcp_client.py")
mcp_client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_client)

MODERN = {"io.modelcontextprotocol/protocolVersion": "2026-07-28", "io.modelcontextprotocol/clientCapabilities": {},
          "io.modelcontextprotocol/clientInfo": {"name": "jobwatch-js3-scripted-client", "version": "1.0.0"}}


def main(sandbox, entry, out_dir):
    sandbox, out_dir = Path(sandbox), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    env = {"PATH": os.environ["PATH"], "HOME": str(sandbox / "home")}
    argv = ["node", entry, str(sandbox / "allowed")]
    c = mcp_client.StdioClient(argv, str(sandbox), env, str(out_dir / f"{ts}-transcript.jsonl"), timeout=20)
    era, meta = "modern", {"_meta": MODERN}
    try:
        r = c.request("server/discover", {"_meta": MODERN}, "discover-1", timeout=5)
        if "error" in r:
            era = "legacy"
    except queue.Empty:
        era = "legacy"
    if era == "legacy":
        meta = {}
        init = c.request("initialize", {"protocolVersion": "2025-11-25", "capabilities": {},
                                        "clientInfo": {"name": "jobwatch-js3-scripted-client", "version": "1.0.0"}}, 1)
        c.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    tools = c.request("tools/list", dict(meta), 2)
    names = [t["name"] for t in tools.get("result", {}).get("tools", [])]
    if "list_allowed_directories" in names:
        call = {"name": "list_allowed_directories", "arguments": {}}
    else:
        call = {"name": "read_text_file", "arguments": {"path": str(sandbox / "allowed" / "hello.txt")}}
    result = c.request("tools/call", {**call, **meta}, 3)
    code = c.close()
    node = subprocess.run(["node", "--version"], capture_output=True, text=True, env=env).stdout.strip()
    run = {"utc": ts, "argv": argv, "cwd": str(sandbox), "env_keys": sorted(env), "node": node, "platform": platform.platform(),
           "era_used": era, "initialize_result": init.get("result") if era == "legacy" else None,
           "tools_listed": names, "call": call, "call_is_error": result.get("result", {}).get("isError"),
           "server_exit_code": code, "server_stderr": "".join(c.stderr)}
    (out_dir / f"{ts}-run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(json.dumps({k: run[k] for k in ("era_used", "tools_listed", "call", "call_is_error", "server_exit_code")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
