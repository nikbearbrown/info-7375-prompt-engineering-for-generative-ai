"""Record a stdio tool-server session in both directions, without changing a byte.

  python3 -m jobwatch.mcp_tap --log transcripts/NAME.jsonl -- python3 -m jobwatch.mcp_server

The host starts the tap as if it were the server. The tap starts the real server, passes every
line from the host to the server and every line from the server to the host, and appends each
line to the log with its direction and a UTC time. The server itself writes nothing; the tap's
only write is the log, which must be a new file inside this folder's transcripts/."""

import argparse
import datetime
import json
import subprocess
import sys
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = PROJECT_ROOT / "transcripts"


def allowed_log(path):
    path = Path(path)
    resolved = (path if path.is_absolute() else Path.cwd() / path).resolve()
    if resolved.parent != TRANSCRIPTS.resolve() or resolved.suffix != ".jsonl" or resolved.exists():
        raise SystemExit(f"refused: the log must be a new .jsonl file directly inside {TRANSCRIPTS}")
    return resolved


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m jobwatch.mcp_tap")
    parser.add_argument("--log", required=True)
    parser.add_argument("server", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.server[1:] if args.server[:1] == ["--"] else args.server
    log_path = allowed_log(args.log)
    lock = threading.Lock()
    log = open(log_path, "x", encoding="utf-8")
    seq = [0]

    def record(direction, line):
        with lock:
            seq[0] += 1
            stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")
            log.write(json.dumps({"seq": seq[0], "at": stamp, "direction": direction,
                                  "line": line.rstrip("\n")}, ensure_ascii=False) + "\n")
            log.flush()

    record("tap", "start " + json.dumps(command))
    child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1,
                             cwd=PROJECT_ROOT)

    def server_to_host():
        for line in child.stdout:
            record("server->host", line)
            sys.stdout.write(line)
            sys.stdout.flush()

    reader = threading.Thread(target=server_to_host, daemon=True)
    reader.start()
    for line in sys.stdin:
        record("host->server", line)
        child.stdin.write(line)
        child.stdin.flush()
    child.stdin.close()
    reader.join(timeout=10)
    code = child.wait(timeout=10)
    record("tap", f"input closed; server exited with code {code}")
    log.close()
    return code


if __name__ == "__main__":
    sys.exit(main())
