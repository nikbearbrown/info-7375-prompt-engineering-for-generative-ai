"""A minimal MCP client over stdio, written from scratch, to talk to a tool server the way any client
would and keep the transcript in both directions: initialize, notifications/initialized, tools/list,
then the tools/call requests it is given. Used to evaluate this folder's server and a server someone
else wrote (chrome-devtools-mcp), TOOLSERVER.md.

  python3 -m js3.mcp_client --out transcripts/<name>.jsonl [--call NAME JSON]... -- <server command...>
"""
import argparse
import datetime
import json
import os
import pathlib
import subprocess
import sys
import threading
import time

HERE = pathlib.Path(__file__).resolve().parent.parent
PROTOCOL = "2025-06-18"


class Client:
    def __init__(self, command, out, env=None, cwd=None):
        self.out = open(out, "w", encoding="utf-8")
        self.proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     text=True, bufsize=1, env=env, cwd=cwd)
        self.next_id = 1
        self.stderr_lines = []
        threading.Thread(target=self._drain_stderr, daemon=True).start()

    def _drain_stderr(self):
        for line in self.proc.stderr:
            self.stderr_lines.append(line.rstrip("\n"))
            self.log("server-stderr", line.rstrip("\n"))

    def log(self, direction, raw):
        self.out.write(json.dumps({"at": datetime.datetime.now().astimezone().isoformat(timespec="milliseconds"),
                                   "dir": direction, "raw": raw}, ensure_ascii=False) + "\n")
        self.out.flush()

    def send(self, msg):
        line = json.dumps(msg, ensure_ascii=False)
        self.log("client->server", line)
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()

    def request(self, method, params=None, timeout=120):
        mid = self.next_id
        self.next_id += 1
        self.send({"jsonrpc": "2.0", "id": mid, "method": method, **({"params": params} if params is not None else {})})
        deadline = time.time() + timeout
        while time.time() < deadline:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError(f"server closed its output while waiting for {method}")
            line = line.rstrip("\n")
            self.log("server->client", line)
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            if msg.get("id") == mid:
                return msg
        raise TimeoutError(method)

    def notify(self, method, params=None):
        self.send({"jsonrpc": "2.0", "method": method, **({"params": params} if params is not None else {})})

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=10)
        except Exception:
            self.proc.kill()
        self.out.close()


def session(command, out, calls=(), env=None, cwd=None, client_name="js3-eval-client"):
    c = Client(command, out, env=env, cwd=cwd)
    try:
        init = c.request("initialize", {"protocolVersion": PROTOCOL, "capabilities": {},
                                        "clientInfo": {"name": client_name, "version": "1.0.0"}})
        c.notify("notifications/initialized")
        tools = c.request("tools/list", {})
        results = [c.request("tools/call", {"name": name, "arguments": args}, timeout=180) for name, args in calls]
        return {"initialize": init, "tools": tools, "calls": results, "stderr": c.stderr_lines}
    finally:
        c.close()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--call", nargs=2, action="append", default=[], metavar=("NAME", "JSON"))
    ap.add_argument("command", nargs=argparse.REMAINDER)
    a = ap.parse_args(argv)
    cmd = a.command[1:] if a.command[:1] == ["--"] else a.command
    r = session(cmd, a.out, [(n, json.loads(j)) for n, j in a.call], env=dict(os.environ))
    print(json.dumps({"server": r["initialize"].get("result", {}).get("serverInfo"),
                      "protocol": r["initialize"].get("result", {}).get("protocolVersion"),
                      "tools": [t["name"] for t in r["tools"].get("result", {}).get("tools", [])],
                      "calls": [("error" if "error" in x else ("isError" if x["result"].get("isError") else "ok"))
                                for x in r["calls"]]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
