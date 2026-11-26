"""A minimal MCP client, from scratch, that saves the real transcript in both directions.

    python3 scripts/mcp_client.py own      # my server, under the audit wrapper
    python3 scripts/mcp_client.py claude   # Claude Code's own server: `claude mcp serve`

Sends: initialize -> notifications/initialized -> tools/list -> a scripted set of tools/call
(including ones that should fail) -> ping. Writes out/mcp/client-<name>-<UTC>.jsonl with every
line sent and received, each with a timestamp.
"""
import datetime as dt
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_INFO = {"name": "js3-handwritten-client", "version": "1.0.0"}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


class Client:
    def __init__(self, cmd, cwd, log_path, env=None):
        self.proc = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True, bufsize=1, env=env)
        self.log = open(log_path, "w", encoding="utf-8")
        self.next_id = 1

    def _send(self, msg):
        line = json.dumps(msg)
        self.log.write(json.dumps({"t": now(), "dir": "client->server", "raw": line}) + "\n")
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()

    def request(self, method, params=None):
        msg = {"jsonrpc": "2.0", "id": self.next_id, "method": method}
        if params is not None:
            msg["params"] = params
        self.next_id += 1
        self._send(msg)
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError(f"server closed stdout; stderr: {self.proc.stderr.read()[:2000]}")
            self.log.write(json.dumps({"t": now(), "dir": "server->client", "raw": line.rstrip()}) + "\n")
            try:
                resp = json.loads(line)
            except json.JSONDecodeError:
                continue
            if resp.get("id") == msg["id"]:
                return resp

    def notify(self, method, params=None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        self._send(msg)

    def raw(self, line):
        """Send a line that is not valid JSON-RPC, and read one reply."""
        self.log.write(json.dumps({"t": now(), "dir": "client->server", "raw": line}) + "\n")
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()
        reply = self.proc.stdout.readline()
        self.log.write(json.dumps({"t": now(), "dir": "server->client", "raw": reply.rstrip()}) + "\n")
        return reply

    def close(self):
        self.proc.stdin.close()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        self.log.close()


def handshake(c):
    init = c.request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": CLIENT_INFO})
    c.notify("notifications/initialized")
    tools = c.request("tools/list")
    return init, tools


def run_own(stamp):
    log = os.path.join(HERE, "out", "mcp", f"client-own-{stamp}.jsonl")
    audit = os.path.join(HERE, "out", "mcp", f"audit-own-{stamp}.jsonl")
    c = Client([sys.executable, os.path.join(HERE, "scripts", "audited.py"), audit, "js3.mcp_server"],
               HERE, log, env={**os.environ, "PYTHONPATH": HERE})
    init, tools = handshake(c)
    calls = [
        ("score_posting", {"uid": "greenhouse:anthropic:5432575008"}),
        ("score_posting", {"title": "HTML Email Developer", "text": "We build emails. " * 30}),
        ("search_postings", {"query": "data engineer", "limit": 5}),
        ("score_posting", {"uid": "greenhouse:anthropic:does-not-exist"}),
        ("search_postings", {"query": "ml", "limit": 500}),
        ("score_posting", {"uid": "x", "path": "../../../../etc/passwd"}),
        ("write_file", {"path": "out/x.txt", "text": "hi"}),
    ]
    results = [(n, a, c.request("tools/call", {"name": n, "arguments": a})) for n, a in calls]
    c.request("ping")
    c.request("resources/list")
    c.raw("this is not json")
    c.close()
    return log, audit, init, tools, results


def run_claude(stamp):
    """Claude Code's built-in MCP server. Only tools/list and one read of a file in this folder."""
    log = os.path.join(HERE, "out", "mcp", f"client-claude-mcp-serve-{stamp}.jsonl")
    c = Client(["claude", "mcp", "serve"], HERE, log)
    init, tools = handshake(c)
    names = [t["name"] for t in tools.get("result", {}).get("tools", [])]
    results = []
    if "Read" in names:
        results.append(("Read", c.request("tools/call", {"name": "Read", "arguments": {"file_path": os.path.join(HERE, "FILTER.md"), "limit": 5}})))
    c.request("ping")
    c.close()
    return log, init, tools, results


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "own"
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(os.path.join(HERE, "out", "mcp"), exist_ok=True)
    if which == "own":
        log, audit, init, tools, results = run_own(stamp)
        print("initialize ->", json.dumps(init["result"])[:300])
        print("tools ->", [t["name"] for t in tools["result"]["tools"]])
        for n, a, r in results:
            res = r.get("result") or {}
            print(f"call {n} {json.dumps(a)[:70]} -> " + ("RPC error " + json.dumps(r["error"]) if "error" in r
                  else f"isError={res.get('isError')} " + res["content"][0]["text"][:120].replace("\n", " ")))
        print("transcript:", os.path.relpath(log, HERE), "\naudit:", os.path.relpath(audit, HERE))
    else:
        log, init, tools, results = run_claude(stamp)
        print("initialize ->", json.dumps(init.get("result") or init)[:400])
        for t in tools.get("result", {}).get("tools", []):
            print(f"  {t['name']:<16} annotations={t.get('annotations')}  {t.get('description', '')[:90]!r}")
        for n, r in results:
            print(f"call {n} ->", json.dumps(r)[:400])
        print("transcript:", os.path.relpath(log, HERE))


if __name__ == "__main__":
    main()
