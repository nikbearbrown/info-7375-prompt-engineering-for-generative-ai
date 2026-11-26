"""A recorder between a real MCP client (Claude Code) and my tool server. It starts the server exactly as the transcripts do
(python3 -B, audit hook installed before load) and relays every line in both directions unchanged, appending each one, with its
direction and time, to evidence/mcp/claude_client/transcript.jsonl. The server's audit trace goes to server_audit.txt.

The server itself stays write-free: only this recorder, which belongs to the client side, writes the log.
Started by Claude Code through .mcp.json in this folder.
"""
import json
import os
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(os.environ.get("JS3_CLIENT_LOG_DIR", ROOT / "evidence" / "mcp" / "claude_client"))
ET = ZoneInfo("America/New_York")
BOOT = ("import jsagent.audithook as h; h.install(); import runpy; "
        "runpy.run_module('jsagent.mcp_server', run_name='__main__')")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    log = (OUT / "transcript.jsonl").open("a")
    audit = (OUT / "server_audit.txt").open("a")
    lock = threading.Lock()
    session = datetime.now(ET).isoformat(timespec="seconds")

    def record(direction, raw):
        with lock:
            log.write(json.dumps({"session": session, "dir": direction,
                                  "t": datetime.now(ET).isoformat(timespec="milliseconds"), "raw": raw}) + "\n")
            log.flush()

    audit.write(f"--- session {session}\n")
    audit.flush()
    proc = subprocess.Popen([sys.executable, "-B", "-c", BOOT], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=audit, text=True, bufsize=1)

    def server_to_client():
        for line in proc.stdout:
            record("server->client", line.rstrip("\n"))
            sys.stdout.write(line)
            sys.stdout.flush()

    t = threading.Thread(target=server_to_client, daemon=True)
    t.start()
    for line in sys.stdin:
        record("client->server", line.rstrip("\n"))
        proc.stdin.write(line)
        proc.stdin.flush()
    proc.stdin.close()
    proc.wait()
    t.join(timeout=5)
    log.close()
    audit.close()


if __name__ == "__main__":
    main()
