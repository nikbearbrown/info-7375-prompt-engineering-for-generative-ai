"""A minimal MCP stdio client for probing a tool server, mine or someone else's (Chapter 8 evaluations).

    python3 -m js3.mcp_client probe-mine      # my server: handshake, list, good calls, 9 hostile/edge calls
    python3 -m js3.mcp_client probe-claude    # Anthropic's `claude mcp serve`: handshake + tools/list ONLY

Every message is logged in both directions to transcripts/client-<name>-<time>.jsonl. probe-claude sends
no tools/call at all: the server exposes tools that run shell commands and write files, and evaluating it
must not use them.
"""
import datetime as dt
import json
import os
import subprocess
import sys
import time

from . import store

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Client:
    def __init__(self, cmd, name, cwd=BASE, env=None):
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
        self.log_path = store.check(f"transcripts/client-{name}-{stamp}.jsonl")
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        self.p = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, bufsize=1, env=env)
        self.next_id = 1

    def log(self, direction, raw):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds"),
                                "dir": direction, "raw": raw}, ensure_ascii=False) + "\n")

    def send_raw(self, raw):
        self.log("client->server", raw)
        self.p.stdin.write(raw + "\n")
        self.p.stdin.flush()

    def read(self, timeout=30):
        t0 = time.monotonic()
        while time.monotonic() - t0 < timeout:
            line = self.p.stdout.readline()
            if not line:
                return None
            line = line.rstrip("\n")
            if not line.strip():
                continue
            self.log("server->client", line)
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue  # a non-JSON line on stdout is itself a finding; it is in the log
        return None

    def request(self, method, params=None, timeout=30):
        mid = self.next_id
        self.next_id += 1
        msg = {"jsonrpc": "2.0", "id": mid, "method": method}
        if params is not None:
            msg["params"] = params
        self.send_raw(json.dumps(msg))
        while True:
            r = self.read(timeout)
            if r is None or r.get("id") == mid:
                return r

    def notify(self, method, params=None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        self.send_raw(json.dumps(msg))

    def close(self):
        try:
            self.p.stdin.close()
            self.p.wait(timeout=10)
        except Exception:
            self.p.kill()
        err = self.p.stderr.read() if self.p.stderr else ""
        if err:
            self.log("server-stderr", err[-4000:])


INIT = {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "js3-probe", "version": "1.0"}}


def probe_mine():
    c = Client([sys.executable, "-m", "js3.mcp_server"], "mine")
    results = []

    def rec(label, r):
        results.append({"probe": label, "response": r})

    rec("tools/list BEFORE initialize", c.request("tools/list"))
    rec("initialize", c.request("initialize", INIT))
    c.notify("notifications/initialized")
    rec("ping", c.request("ping"))
    rec("tools/list", c.request("tools/list"))
    rec("call by id (Toast SWE II Backend)", c.request("tools/call", {"name": "score_posting", "arguments": {"posting_id": "8334794"}}))
    rec("call pasted posting", c.request("tools/call", {"name": "score_posting", "arguments": {
        "title": "Software Engineer I", "location": "Boston, MA",
        "content": "About us: we build tools. Requirements: 1+ years of professional experience with Python and SQL. "
                   "You have shipped services on AWS. " * 6}}))
    rec("hostile: path traversal as posting_id", c.request("tools/call", {"name": "score_posting", "arguments": {"posting_id": "../../../../etc/passwd"}}))
    rec("hostile: unknown tool 'apply_to_job'", c.request("tools/call", {"name": "apply_to_job", "arguments": {"posting_id": "8334794"}}))
    rec("hostile: extra argument 'url'", c.request("tools/call", {"name": "score_posting", "arguments": {"posting_id": "8334794", "url": "https://example.com"}}))
    rec("edge: wrong type", c.request("tools/call", {"name": "score_posting", "arguments": {"posting_id": 8334794}}))
    rec("edge: id not collected", c.request("tools/call", {"name": "score_posting", "arguments": {"posting_id": "999999999"}}))
    rec("edge: unknown method resources/list", c.request("resources/list"))
    c.send_raw("{not json")
    rec("edge: malformed JSON", c.read())
    rec("edge: content over 50,000 chars", c.request("tools/call", {"name": "score_posting", "arguments": {"title": "x", "content": "a" * 50001}}))
    rec("edge: both id and pasted text", c.request("tools/call", {"name": "score_posting", "arguments": {"posting_id": "8334794", "title": "x"}}))
    c.close()
    return c.log_path, results


def probe_claude():
    """Anthropic's Claude Code as an MCP server. Handshake and tools/list only; no tool is called."""
    c = Client(["claude", "mcp", "serve"], "claude-mcp-serve")
    results = [{"probe": "initialize", "response": c.request("initialize", INIT, timeout=60)}]
    c.notify("notifications/initialized")
    results.append({"probe": "tools/list", "response": c.request("tools/list", timeout=60)})
    results.append({"probe": "resources/list", "response": c.request("resources/list", timeout=30)})
    results.append({"probe": "prompts/list", "response": c.request("prompts/list", timeout=30)})
    c.close()
    return c.log_path, results


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    which = argv[0] if argv else "probe-mine"
    path, results = (probe_mine if which == "probe-mine" else probe_claude)()
    for r in results:
        resp = r["response"] or {}
        short = json.dumps(resp.get("error") or resp.get("result"), ensure_ascii=False)[:160]
        print(f"{r['probe']:<42} {short}")
    print("transcript:", os.path.relpath(path, BASE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
