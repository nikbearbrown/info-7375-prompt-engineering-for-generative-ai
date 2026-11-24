"""A logging tap for a stdio MCP server: it sits between a client (say,
Claude Code) and the server, relays every byte unchanged in both directions,
and records each line in a JSONL transcript.

    JS3_TAP_LOG=transcripts/x.jsonl python3 -B mcp/tap.py -- <server command...>

Each transcript line: {"t": ISO time, "dir": "client->server" |
"server->client", "line": the raw line (without its newline)}.
The log path must resolve inside this js3 folder, or the tap refuses to start.
The server's stderr passes straight through and is not recorded.
"""

import datetime
import json
import os
import pathlib
import subprocess
import sys
import threading

JS3 = pathlib.Path(os.path.realpath(__file__)).parent.parent


def log_path():
    raw = os.environ.get("JS3_TAP_LOG")
    if not raw:
        sys.exit("tap: set JS3_TAP_LOG to a .jsonl path inside the js3 folder")
    p = pathlib.Path(raw)
    if not p.is_absolute():
        p = JS3 / p
    real = pathlib.Path(os.path.realpath(p))
    if JS3 not in real.parents:
        sys.exit(f"tap: refusing log path outside the js3 folder: {raw}")
    return real


def main(argv):
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    if not argv:
        sys.exit("usage: tap.py -- <server command...>")
    path = log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    out = open(path, "a", encoding="utf-8")

    def record(direction, raw):
        with lock:
            out.write(json.dumps({
                "t": datetime.datetime.now(datetime.timezone.utc)
                .isoformat(timespec="milliseconds"),
                "dir": direction,
                "line": raw.decode("utf-8", "replace").rstrip("\r\n")}) + "\n")
            out.flush()

    child = subprocess.Popen(argv, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, cwd=str(JS3))

    def client_to_server():
        for raw in iter(sys.stdin.buffer.readline, b""):
            record("client->server", raw)
            try:
                child.stdin.write(raw)
                child.stdin.flush()
            except BrokenPipeError:
                break
        try:
            child.stdin.close()
        except OSError:
            pass

    threading.Thread(target=client_to_server, daemon=True).start()
    for raw in iter(child.stdout.readline, b""):
        record("server->client", raw)
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
    code = child.wait()
    out.close()
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
