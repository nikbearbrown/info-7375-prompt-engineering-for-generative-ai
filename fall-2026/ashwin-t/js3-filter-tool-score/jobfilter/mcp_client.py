"""A from-scratch MCP client over stdio, used to probe ANY tool server (mine or someone else's).

It starts the server command, sends initialize -> notifications/initialized -> tools/list and
then any tools/call requests given, and records every line in both directions with UTC times.

    python3 -m jobfilter.mcp_client OUT.jsonl CALLS.json [--cwd DIR] -- COMMAND [ARGS...]

CALLS.json is a list of {"name": ..., "arguments": {...}}. The transcript is the evidence;
this client never interprets tool output beyond printing it.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path

from .mcp_server import utc

PROTOCOL = "2025-06-18"
CLIENT_INFO = {"name": "js3-probe-client", "version": "1.0.0"}


class Probe:
    def __init__(self, command: list, cwd: str = None, env: dict = None, timeout: float = 60.0):
        self.proc = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True, encoding="utf-8", bufsize=1)
        self.records, self.timeout, self.next_id = [], timeout, 1
        self.stderr_lines = []
        threading.Thread(target=self._drain_stderr, daemon=True).start()

    def _drain_stderr(self):
        for line in self.proc.stderr:
            self.stderr_lines.append(line.rstrip("\n"))

    def _send(self, msg: dict) -> None:
        line = json.dumps(msg, separators=(",", ":"))
        self.records.append({"utc": utc(), "dir": "client->server", "line": line})
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()

    def _read_reply(self, mid) -> dict:
        result = {}

        def reader():
            for line in self.proc.stdout:
                line = line.rstrip("\n")
                self.records.append({"utc": utc(), "dir": "server->client", "line": line})
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(msg, dict) and msg.get("id") == mid and ("result" in msg or "error" in msg):
                    result["msg"] = msg
                    return
        t = threading.Thread(target=reader, daemon=True)
        t.start()
        t.join(self.timeout)
        if "msg" not in result:
            raise TimeoutError(f"no reply to id {mid} within {self.timeout}s")
        return result["msg"]

    def request(self, method: str, params: dict = None) -> dict:
        mid = self.next_id
        self.next_id += 1
        msg = {"jsonrpc": "2.0", "id": mid, "method": method}
        if params is not None:
            msg["params"] = params
        self._send(msg)
        return self._read_reply(mid)

    def notify(self, method: str) -> None:
        self._send({"jsonrpc": "2.0", "method": method})

    def handshake(self) -> tuple:
        init = self.request("initialize", {"protocolVersion": PROTOCOL, "capabilities": {},
                                           "clientInfo": CLIENT_INFO})
        self.notify("notifications/initialized")
        tools = self.request("tools/list", {})
        return init, tools

    def close(self) -> int:
        try:
            self.proc.stdin.close()
            return self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            return self.proc.wait()


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    cwd = None
    if len(argv) > 3 and argv[2] == "--cwd":
        cwd, argv = argv[3], argv[:2] + argv[4:]
    if "--" not in argv or argv.index("--") != 2:
        print(__doc__, file=sys.stderr)
        return 2
    out, calls_file, command = Path(argv[0]), Path(argv[1]), argv[3:]
    calls = json.loads(calls_file.read_text())
    probe = Probe(command, cwd=cwd, env=dict(os.environ))
    try:
        init, tools = probe.handshake()
        print("initialize:", json.dumps(init.get("result", init.get("error")))[:400])
        names = [t["name"] for t in tools.get("result", {}).get("tools", [])]
        print(f"tools/list: {len(names)} tools: {names}")
        for call in calls:
            reply = probe.request("tools/call", call)
            print(f"tools/call {call['name']}:", json.dumps(reply)[:600])
    finally:
        code = probe.close()
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fh:
            for rec in probe.records:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"server exit {code}; {len(probe.records)} lines -> {out}; stderr lines: {len(probe.stderr_lines)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
