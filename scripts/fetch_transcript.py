"""Run the official 'fetch' MCP server (installed in a separate Python >= 3.11.5 environment) and record a real transcript in both
directions, plus an audit-hook trace of what its process touches (the same method as my own server's evaluation).

    python3 scripts/fetch_transcript.py --python <env>/bin/python --out evidence/mcp/fetch_run/default
    python3 scripts/fetch_transcript.py --python <env>/bin/python --out evidence/mcp/fetch_run/restricted \
        -- --allowed-hosts boards-api.greenhouse.io api.lever.co --no-readability-js

Everything after "--" is passed to mcp-server-fetch. The audit hook (jsagent/audithook.py) is installed before the server's
modules load. A child process (npm, node) is seen only as a subprocess event, not traced inside.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
ET = ZoneInfo("America/New_York")
URLS = [
    "https://boards-api.greenhouse.io/v1/boards/samsara/jobs/8141959",  # a real posting from the snapshot, JSON
    "https://example.com/",                                              # a plain HTML page
    "http://169.254.169.254/latest/meta-data/",                         # the cloud metadata address it says it refuses
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--python", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("server_args", nargs="*")
    a = ap.parse_args()
    out = Path(a.out)
    if (out / "transcript.jsonl").exists():
        sys.exit(f"refused: {out / 'transcript.jsonl'} already exists")
    out.mkdir(parents=True, exist_ok=True)

    boot = ("import sys; sys.path.insert(0, %r); import jsagent.audithook as h; h.install(); "
            "sys.argv = ['mcp-server-fetch'] + %r; import runpy; runpy.run_module('mcp_server_fetch', run_name='__main__')"
            % (str(ROOT), a.server_args))
    stderr = (out / "server_audit.txt").open("w")
    proc = subprocess.Popen([a.python, "-B", "-c", boot], cwd=out, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=stderr, text=True, bufsize=1)
    log = (out / "transcript.jsonl").open("w")

    def record(direction, raw):
        log.write(json.dumps({"dir": direction, "t": datetime.now(ET).isoformat(timespec="milliseconds"), "raw": raw}) + "\n")
        log.flush()

    def send(msg, wait_id=None):
        raw = json.dumps(msg)
        record("client->server", raw)
        proc.stdin.write(raw + "\n")
        proc.stdin.flush()
        while wait_id is not None:  # read until the reply with this id (the server may send notifications first)
            line = proc.stdout.readline()
            if not line:
                return None
            record("server->client", line.rstrip("\n"))
            m = json.loads(line)
            if m.get("id") == wait_id:
                return m

    send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
          "params": {"protocolVersion": "2025-11-25", "capabilities": {},
                     "clientInfo": {"name": "js3-transcript-client", "version": "1.0"}}}, 1)
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, 2)
    for i, url in enumerate(URLS, 3):
        send({"jsonrpc": "2.0", "id": i, "method": "tools/call",
              "params": {"name": "fetch", "arguments": {"url": url, "max_length": 800}}}, i)
    send({"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": "apply_to_job", "arguments": {}}}, 9)
    proc.stdin.close()
    try:
        proc.wait(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
    stderr.close()
    log.close()
    print(f"wrote {out}/transcript.jsonl and server_audit.txt; server exit code {proc.returncode}")


if __name__ == "__main__":
    main()
