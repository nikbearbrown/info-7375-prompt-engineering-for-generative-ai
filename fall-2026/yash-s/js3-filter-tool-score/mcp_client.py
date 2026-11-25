"""A minimal tool-protocol client that records the whole conversation, both directions.

    python3 mcp_client.py --steps mcp/probes/own-server.json --out mcp/transcripts/<name>.jsonl \\
        -- python3 mcp_server.py

Starts the server command as a child process, then: initialize, the
notifications/initialized notification, tools/list, and every step in the steps
file. A step is either {"tool": name, "arguments": {...}} for a tools/call,
{"request": method, "params": {...}} for any other request, or {"raw": "text"}
for a line sent exactly as written (to probe error handling). Every line sent and
received is written to --out with a timestamp and its direction. If the server
sends a request of its own, the client records it and answers "method not found":
this client grants a server nothing.

Used for my own server and for the other server I evaluate. It runs nothing
except the one command given after "--".
"""
import argparse
import datetime
import json
import select
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLIENT_INFO = {"name": "yash-js3-probe-client", "version": "1.0.0"}


class Session:
    def __init__(self, command, out_path, cwd=None, timeout=20.0):
        self.out = open(out_path, "x", encoding="utf-8")
        self.proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     cwd=cwd, text=True, encoding="utf-8", bufsize=1)
        self.timeout, self.next_id, self._buf = timeout, 1, ""
        where = Path(cwd or Path.cwd()).resolve()
        shown = str(where.relative_to(HERE)) if where.is_relative_to(HERE) else "(a folder outside this project)"
        self.log("meta", json.dumps({"command": command, "cwd_relative_to_project": shown}))

    def log(self, direction, raw):
        t = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")
        self.out.write(json.dumps({"t": t, "dir": direction, "raw": raw}, ensure_ascii=False) + "\n")
        self.out.flush()

    def send_line(self, line):
        self.log("client->server", line)
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()

    def read_line(self):
        ready, _, _ = select.select([self.proc.stdout], [], [], self.timeout)
        if not ready:
            return None
        line = self.proc.stdout.readline()
        if line == "":
            return None
        line = line.rstrip("\n")
        self.log("server->client", line)
        return line

    def wait_for(self, want_id):
        """Read until the reply with this id (or, for want_id None, the next reply)."""
        while True:
            line = self.read_line()
            if line is None:
                self.log("note", f"no reply within {self.timeout}s or the server closed stdout")
                return None
            try:
                msg = json.loads(line)
            except ValueError:
                self.log("note", "the server wrote a line that is not JSON")
                continue
            if isinstance(msg, dict) and "method" in msg and "id" in msg:  # a request from the server
                self.send_line(json.dumps({"jsonrpc": "2.0", "id": msg["id"],
                                           "error": {"code": -32601, "message": "this client offers no capabilities"}}))
                continue
            if isinstance(msg, dict) and "method" in msg:  # a notification from the server
                continue
            if want_id is None or (isinstance(msg, dict) and msg.get("id") == want_id):
                return msg

    def request(self, method, params=None):
        i, self.next_id = self.next_id, self.next_id + 1
        msg = {"jsonrpc": "2.0", "id": i, "method": method}
        if params is not None:
            msg["params"] = params
        self.send_line(json.dumps(msg, ensure_ascii=False))
        return self.wait_for(i)

    def notify(self, method, params=None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        self.send_line(json.dumps(msg))

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=10)
        except Exception:
            self.proc.kill()
        err = self.proc.stderr.read()
        self.proc.stdout.close()
        self.proc.stderr.close()
        if err:  # tracebacks print full file paths; the home folder is recorded as "~"
            self.log("server-stderr", err.replace(str(Path.home()), "~"))
        self.log("meta", json.dumps({"exit_code": self.proc.returncode}))
        self.out.close()


def run(command, steps, out_path, cwd=None, protocol_version="2025-06-18", handshake=True):
    """With handshake=False the steps do everything, so a probe can call tools before
    initializing. Extra step kinds: {"notify": method}, and {"raw_repeat": [text, n]},
    which sends text repeated n times on one line."""
    s = Session(command, out_path, cwd=cwd)
    summary = []
    try:
        if handshake:
            init = s.request("initialize", {"protocolVersion": protocol_version, "capabilities": {},
                                            "clientInfo": CLIENT_INFO})
            summary.append(("initialize", init))
            s.notify("notifications/initialized")
            summary.append(("tools/list", s.request("tools/list")))
        for step in steps:
            if s.proc.poll() is not None:
                s.log("note", f"the server has exited (code {s.proc.returncode}); remaining steps not sent")
                summary.append(("(server exited)", None))
                break
            if "tool" in step:
                summary.append((f"tools/call {step['tool']}",
                                s.request("tools/call", {"name": step["tool"], "arguments": step.get("arguments", {})})))
            elif "request" in step:
                summary.append((step["request"], s.request(step["request"], step.get("params"))))
            elif "notify" in step:
                s.notify(step["notify"], step.get("params"))
                summary.append((f"notify {step['notify']}", {"result": "(no reply expected)"}))
            elif "raw" in step:
                s.send_line(step["raw"])
                summary.append(("raw", s.wait_for(None)))
            elif "raw_repeat" in step:
                text, n = step["raw_repeat"]
                s.send_line(text * n)
                summary.append((f"raw {text!r} x {n}", s.wait_for(None)))
    finally:
        s.close()
    return summary


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--" not in argv:
        print("usage: mcp_client.py --steps FILE --out FILE [--cwd DIR] -- SERVER COMMAND...", file=sys.stderr)
        return 2
    cut = argv.index("--")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--steps", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cwd")
    ap.add_argument("--protocol-version", default="2025-06-18")
    args = ap.parse_args(argv[:cut])
    spec = json.loads(Path(args.steps).read_text(encoding="utf-8"))
    summary = run(argv[cut + 1:], spec["steps"], args.out, cwd=args.cwd, protocol_version=args.protocol_version,
                  handshake=spec.get("handshake", True))
    for name, reply in summary:
        if reply is None:
            print(f"{name:34} no reply")
        elif "error" in reply:
            print(f"{name:34} error {reply['error'].get('code')}: {reply['error'].get('message')}")
        else:
            res = reply.get("result", {})
            extra = " isError" if isinstance(res, dict) and res.get("isError") else ""
            print(f"{name:34} ok{extra}")
    print(f"transcript: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
