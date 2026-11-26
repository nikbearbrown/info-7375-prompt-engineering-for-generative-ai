"""Record a stdio MCP session in both directions without changing it.

Usage: python tools/mcp_tap.py --log PATH -- COMMAND [ARGS...]

The tap starts COMMAND, relays each line from its own stdin to COMMAND's stdin and each line from COMMAND's
stdout to its own stdout, and appends every line to PATH as JSONL: {"t": UTC time, "dir": "client->server" |
"server->client", "raw": the exact line}. It does not parse, edit, or drop messages. This file, not the server,
does the writing, so the server under test stays write-free (FILTER.md section 7).
"""
import argparse
import datetime
import json
import pathlib
import subprocess
import sys
import threading

_lock = threading.Lock()


def _log(fh, direction, raw):
    entry = {"t": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds"),
             "dir": direction, "raw": raw.rstrip("\n")}
    with _lock:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        fh.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("command", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    cmd = args.command[1:] if args.command[:1] == ["--"] else args.command
    path = pathlib.Path(args.log)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        _log(fh, "tap", json.dumps({"event": "start", "command": cmd}))
        child = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)

        def pump_out():
            for line in child.stdout:
                _log(fh, "server->client", line)
                sys.stdout.write(line)
                sys.stdout.flush()

        t = threading.Thread(target=pump_out, daemon=True)
        t.start()
        try:
            for line in sys.stdin:
                _log(fh, "client->server", line)
                child.stdin.write(line)
                child.stdin.flush()
        except (BrokenPipeError, KeyboardInterrupt):
            pass
        finally:
            try:
                child.stdin.close()
            except BrokenPipeError:
                pass
            code = child.wait()
            t.join(timeout=5)
            _log(fh, "tap", json.dumps({"event": "exit", "returncode": code}))


if __name__ == "__main__":
    main()
