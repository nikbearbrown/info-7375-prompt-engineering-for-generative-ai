"""Record a real transcript with the JS3 tool server: start it as a subprocess, speak the protocol over its stdin/stdout, and
save every line in both directions, plus the server's audit trace (every non-import file open, any network or process event).

    python3 scripts/mcp_transcript.py --call samsara:1234567 --call palantir:<uuid> [--out evidence/mcp]

Writes <out>/transcript.jsonl (one line per message: direction, time, message) and <out>/server_audit.txt (stderr).
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
ET = ZoneInfo("America/New_York")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--call", action="append", default=[], help="board:posting_id to score")
    ap.add_argument("--out", default=str(ROOT / "evidence" / "mcp"))
    a = ap.parse_args()
    out = Path(a.out)
    if (out / "transcript.jsonl").exists():
        sys.exit(f"refused: {out / 'transcript.jsonl'} already exists")
    out.mkdir(parents=True, exist_ok=True)

    # The audit hook goes in before any jsagent module is imported, so import-time reads (the persona file) are seen too.
    boot = ("import jsagent.audithook as h; h.install(); import runpy; "
            "runpy.run_module('jsagent.mcp_server', run_name='__main__')")
    stderr = (out / "server_audit.txt").open("w")
    # -B: without it the interpreter writes a .pyc cache (seen in the second dry run), so "writes no files" would be false.
    proc = subprocess.Popen([sys.executable, "-B", "-c", boot], cwd=ROOT, env=dict(os.environ), stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=stderr, text=True, bufsize=1)
    log = (out / "transcript.jsonl").open("w")

    def record(direction, raw):
        log.write(json.dumps({"dir": direction, "t": datetime.now(ET).isoformat(timespec="milliseconds"), "raw": raw}) + "\n")
        log.flush()

    def send(raw, expect_reply=True):
        record("client->server", raw)
        proc.stdin.write(raw + "\n")
        proc.stdin.flush()
        if expect_reply:
            line = proc.stdout.readline().rstrip("\n")
            record("server->client", line)
            return json.loads(line)
        return None

    rid = iter(range(1, 1000))

    def req(method, params=None):
        m = {"jsonrpc": "2.0", "id": next(rid), "method": method}
        if params is not None:
            m["params"] = params
        return send(json.dumps(m))

    req("tools/list")  # before initialize: must be refused
    req("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "js3-transcript-client", "version": "1.0"}})
    send(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}), expect_reply=False)
    req("ping")
    req("tools/list")
    for c in a.call:
        board, pid = c.split(":", 1)
        req("tools/call", {"name": "score_posting", "arguments": {"board": board, "posting_id": pid}})
    req("tools/call", {"name": "score_posting", "arguments": {"board": "samsara-does-not-exist", "posting_id": "1"}})
    req("tools/call", {"name": "score_posting", "arguments": {"board": "kraken", "posting_id": "1"}})
    req("tools/call", {"name": "score_posting", "arguments": {"board": "samsara", "posting_id": "0"}})
    req("tools/call", {"name": "score_posting", "arguments": {"board": "samsara", "posting_id": 123}})
    req("tools/call", {"name": "score_posting", "arguments": {"board": "../../etc", "posting_id": "passwd"}})
    req("tools/call", {"name": "apply_to_job", "arguments": {"board": "samsara", "posting_id": "1"}})
    req("resources/list")
    send("{this is not json")
    proc.stdin.close()
    proc.wait(timeout=30)
    stderr.close()
    log.close()
    lines = (out / "transcript.jsonl").read_text().splitlines()
    print(f"wrote {out}/transcript.jsonl ({len(lines)} lines) and server_audit.txt; server exit code {proc.returncode}")


if __name__ == "__main__":
    main()
