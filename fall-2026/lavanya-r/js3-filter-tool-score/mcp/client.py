"""A scripted MCP client, written from scratch: it starts any stdio MCP server,
walks the handshake, lists tools, makes a fixed set of calls, and saves the
whole conversation in both directions.

    python3 -B mcp/client.py --out transcripts/01-scripted-client-own-server.jsonl
    python3 -B mcp/client.py --out transcripts/x.jsonl --calls calls.json -- <server cmd...>

Default server: python3 -B mcp/server.py. Default calls (for that server):
a normal search, a bad argument, an unknown tool, then an unknown method.
--calls takes a JSON list of {"name", "arguments"}; the unknown-tool and
unknown-method probes are always added after them.

Transcript lines: {"t", "dir": "client->server" | "server->client", "line"}.
The --out path must resolve inside this js3 folder.
"""

import argparse
import datetime
import json
import os
import pathlib
import subprocess
import sys

JS3 = pathlib.Path(os.path.realpath(__file__)).parent.parent
PROTOCOL = "2025-06-18"
DEFAULT_SERVER = [sys.executable, "-B", "mcp/server.py"]
DEFAULT_CALLS = [
    {"name": "search_postings",
     "arguments": {"query": "MLflow", "board": "greenhouse/databricks",
                   "limit": 3}},
    {"name": "search_postings", "arguments": {"query": "MLflow", "limit": 99}},
]


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec="milliseconds")


class Client:
    def __init__(self, cmd, out_path):
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, cwd=str(JS3),
                                     text=True, encoding="utf-8")
        self.out = open(out_path, "w", encoding="utf-8")
        self.next_id = 1

    def _record(self, direction, line):
        self.out.write(json.dumps({"t": now(), "dir": direction,
                                   "line": line}) + "\n")
        self.out.flush()

    def send(self, method, params=None, notify=False):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            msg["id"] = self.next_id
            self.next_id += 1
        line = json.dumps(msg)
        self._record("client->server", line)
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()
        if notify:
            return None
        # Read until the response with our id (skip server notifications).
        while True:
            reply = self.proc.stdout.readline()
            if not reply:
                raise RuntimeError(f"server closed stdout during {method}")
            reply = reply.rstrip("\n")
            self._record("server->client", reply)
            parsed = json.loads(reply)
            if parsed.get("id") == msg["id"]:
                return parsed

    def close(self):
        self.proc.stdin.close()
        code = self.proc.wait(timeout=10)
        self.out.close()
        return code


def run(cmd, out_path, calls):
    c = Client(cmd, out_path)
    summary = []
    init = c.send("initialize", {
        "protocolVersion": PROTOCOL, "capabilities": {},
        "clientInfo": {"name": "js3-scripted-client", "version": "0.1.0"}})
    summary.append(("initialize", init.get("error") or
                    init["result"].get("serverInfo")))
    c.send("notifications/initialized", notify=True)
    tools = c.send("tools/list", {})
    names = [t["name"] for t in tools.get("result", {}).get("tools", [])]
    summary.append(("tools/list", tools.get("error") or names))
    for call in calls + [{"name": "no_such_tool", "arguments": {}}]:
        r = c.send("tools/call", call)
        res = r.get("result", {})
        summary.append((f"tools/call {call['name']}",
                        r.get("error") or ("isError" if res.get("isError")
                                           else "ok")))
    r = c.send("no/such_method", {})
    summary.append(("no/such_method", r.get("error")))
    summary.append(("server exit code", c.close()))
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--calls")
    ap.add_argument("cmd", nargs="*")
    a = ap.parse_args(argv)
    out = pathlib.Path(a.out)
    out = pathlib.Path(os.path.realpath(out if out.is_absolute()
                                        else pathlib.Path.cwd() / out))
    if JS3 not in out.parents:
        sys.exit(f"refusing --out outside the js3 folder: {a.out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    calls = json.loads(pathlib.Path(a.calls).read_text()) if a.calls \
        else DEFAULT_CALLS
    for step, result in run(a.cmd or DEFAULT_SERVER, out, calls):
        print(f"{step}: {result}")
    print(f"transcript: {out.relative_to(JS3)}")


if __name__ == "__main__":
    main()
