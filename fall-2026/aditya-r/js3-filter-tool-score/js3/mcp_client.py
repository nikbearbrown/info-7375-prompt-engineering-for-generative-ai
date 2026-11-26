"""A tiny stdio MCP *client*, written from scratch, that records every line in both directions.

It is used by the tests, by the evaluation of the other server (evaluations/), and as the
fallback client if Claude integration is unavailable. It is NOT Claude. Transcripts it makes
are labeled "client: js3 test client" in transcripts/.

  .venv/bin/python -m js3.mcp_client --log out.jsonl -- <server command...>   (runs a fixed script of requests)
"""
import datetime as dt
import json
import subprocess
import sys


class StdioClient:
    def __init__(self, argv, log_path=None, cwd=None, env=None, on_request=None):
        self.proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     text=True, cwd=cwd, env=env, bufsize=1)
        self.log_path, self.next_id, self.lines = log_path, 1, []
        self.on_request = on_request  # answers server->client requests (e.g. roots/list); None -> -32601

    def _log(self, direction, line):
        rec = {"t": dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds"), "dir": direction, "line": line}
        self.lines.append(rec)
        if self.log_path:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def send_raw(self, line, expect_reply=True):
        self._log("client->server", line)
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()
        if not expect_reply:
            return None
        while True:
            out = self.proc.stdout.readline()
            if not out:
                raise RuntimeError("server closed stdout; stderr: " + self.proc.stderr.read()[-2000:])
            out = out.rstrip("\n")
            self._log("server->client", out)
            msg = json.loads(out)
            if "id" in msg and ("result" in msg or "error" in msg):
                return msg
            if "id" in msg and "method" in msg:  # a server->client request: answer it, keep waiting
                result = self.on_request(msg) if self.on_request else None
                reply = ({"jsonrpc": "2.0", "id": msg["id"], "result": result} if result is not None else
                         {"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32601, "message": "Method not found"}})
                line = json.dumps(reply)
                self._log("client->server", line)
                self.proc.stdin.write(line + "\n")
                self.proc.stdin.flush()
            # notifications from the server are logged and skipped

    def request(self, method, params=None):
        msg = {"jsonrpc": "2.0", "id": self.next_id, "method": method}
        if params is not None:
            msg["params"] = params
        self.next_id += 1
        return self.send_raw(json.dumps(msg))

    def notify(self, method, params=None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        self.send_raw(json.dumps(msg), expect_reply=False)

    def initialize(self, version="2025-11-25", capabilities=None):
        r = self.request("initialize", {"protocolVersion": version, "capabilities": capabilities or {},
                                        "clientInfo": {"name": "js3-test-client", "version": "1.0.0"}})
        self.notify("notifications/initialized")
        return r

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=10)
        except Exception:
            self.proc.kill()
