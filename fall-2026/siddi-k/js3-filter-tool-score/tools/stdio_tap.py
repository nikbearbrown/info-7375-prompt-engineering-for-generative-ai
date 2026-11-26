"""A transparent stdio tap: start a server command, pass every line through unchanged in both directions, and log
each line with a timestamp. Lets us keep a two-way transcript of a server that keeps none (the course server).

Usage (as the command inside an --mcp-config): python tools/stdio_tap.py --log evidence/... -- CMD ARGS..."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from js3 import policy  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    real = policy.check_write(a.log)
    real.parent.mkdir(parents=True, exist_ok=True)       # the first course-server session failed without this
    log = open(real, "a", encoding="utf-8", newline="\n")
    lock = threading.Lock()

    def record(direction: str, raw: bytes) -> None:
        with lock:
            t = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            log.write(json.dumps({"t": t, "dir": direction, "raw": raw.decode("utf-8", "replace").rstrip("\r\n")},
                                 ensure_ascii=False) + "\n")
            log.flush()

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def server_to_client():
        for line in proc.stdout:
            record("server->client", line)
            sys.stdout.buffer.write(line)
            sys.stdout.buffer.flush()

    threading.Thread(target=server_to_client, daemon=True).start()
    for line in sys.stdin.buffer:
        record("client->server", line)
        proc.stdin.write(line)
        proc.stdin.flush()
    proc.stdin.close()
    return proc.wait()


if __name__ == "__main__":
    sys.exit(main())
