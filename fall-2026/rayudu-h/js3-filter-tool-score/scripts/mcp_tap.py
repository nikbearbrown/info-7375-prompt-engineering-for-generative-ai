"""A logging stdio tap for any MCP server: the client talks to the tap, the tap talks to the server,
and every line in both directions is written to a JSONL transcript with a timestamp.

    python scripts/mcp_tap.py --log transcripts/x.jsonl -- <server command...>

Directions: "client->server", "server->client", and "server-stderr". The tap changes nothing in
the messages; it only copies them. Standard library only.
"""
import argparse
import datetime as dt
import json
import subprocess
import sys
import threading


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    lock = threading.Lock()
    log = open(a.log, "a", encoding="utf-8")

    def record(direction: str, line: str) -> None:
        entry = {"t": dt.datetime.now().astimezone().isoformat(timespec="milliseconds"), "dir": direction}
        text = line.rstrip("\n")
        try:
            entry["msg"] = json.loads(text)
        except json.JSONDecodeError:
            entry["raw"] = text
        with lock:
            log.write(json.dumps(entry, ensure_ascii=False) + "\n")
            log.flush()

    record("tap", json.dumps({"started": cmd}))
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, bufsize=1)

    def pump_out():
        for line in proc.stdout:
            record("server->client", line)
            sys.stdout.write(line)
            sys.stdout.flush()

    def pump_err():
        for line in proc.stderr:
            record("server-stderr", line)

    threads = [threading.Thread(target=pump_out, daemon=True), threading.Thread(target=pump_err, daemon=True)]
    for t in threads:
        t.start()
    try:
        for line in sys.stdin:
            record("client->server", line)
            proc.stdin.write(line)
            proc.stdin.flush()
    except (BrokenPipeError, KeyboardInterrupt):
        pass
    finally:
        try:
            proc.stdin.close()
        except BrokenPipeError:
            pass
        proc.wait(timeout=10)
        for t in threads:
            t.join(timeout=5)
        record("tap", json.dumps({"server_exit_code": proc.returncode}))
        log.close()
    return proc.returncode or 0


if __name__ == "__main__":
    sys.exit(main())
