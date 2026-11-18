"""A minimal MCP client, written from scratch, that records every message in both directions.

    # our server, a fixed session including deliberate bad requests
    python3 src/mcp_client.py stdio-session --name client-session-1

    # someone else's server over Streamable HTTP (allow-listed host only)
    python3 src/mcp_client.py http --url https://learn.microsoft.com/api/mcp --name mslearn-1 \
        [--call TOOL --args '{"query": "..."}']

Transcripts go to transcripts/<name>.jsonl. The client never calls a tool it was not told to.
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTTP_ALLOWED_HOSTS = {"learn.microsoft.com"}
CLIENT_INFO = {"name": "js3-handmade-client", "version": "1.0.0"}
PROTOCOL_VERSION = "2025-06-18"


class Transcript:
    def __init__(self, name):
        os.makedirs(os.path.join(ROOT, "transcripts"), exist_ok=True)
        self.path = os.path.join(ROOT, "transcripts", name + ".jsonl")
        if os.path.exists(self.path):
            sys.exit(f"{self.path} exists; use a new name")

    def log(self, direction, message, **extra):
        rec = {"at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds"),
               "direction": direction, "message": message, **extra}
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


class StdioConnection:
    def __init__(self, cmd, transcript):
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, cwd=ROOT)
        self.t = transcript

    def send_raw(self, line):
        self.t.log("client->server", line)
        self.p.stdin.write(line + "\n")
        self.p.stdin.flush()

    def read(self):
        line = self.p.stdout.readline().strip()
        self.t.log("server->client", line)
        return json.loads(line)

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=10)


class HttpConnection:
    """Streamable HTTP: each JSON-RPC message is one POST; the reply is JSON or an SSE stream."""

    def __init__(self, url, transcript):
        host = urllib.parse.urlparse(url).hostname
        if urllib.parse.urlparse(url).scheme != "https" or host not in HTTP_ALLOWED_HOSTS:
            sys.exit(f"{url} is not on the client's allow-list")
        self.url, self.t, self.session = url, transcript, None

    def post(self, obj):
        body = json.dumps(obj)
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
                   "MCP-Protocol-Version": PROTOCOL_VERSION, "User-Agent": "INFO7375-JS3-student-client"}
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        self.t.log("client->server", body, http={"method": "POST", "url": self.url,
                                                 "session_header_sent": bool(self.session)})
        req = urllib.request.Request(self.url, data=body.encode(), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode("utf-8", "replace")
            ctype = r.headers.get("Content-Type", "")
            self.session = r.headers.get("Mcp-Session-Id") or self.session
            self.t.log("server->client", raw, http={"status": r.status, "content_type": ctype,
                                                    "session_id_returned": r.headers.get("Mcp-Session-Id")})
        if not raw.strip():
            return None
        if "text/event-stream" in ctype:
            data = [ln[5:].strip() for ln in raw.splitlines() if ln.startswith("data:")]
            return json.loads(data[-1]) if data else None
        return json.loads(raw)


def stdio_session(name):
    t = Transcript(name)
    c = StdioConnection([sys.executable, "src/mcp_server.py", "--transcript-name", name + "-server-side"], t)

    def rpc(i, method, params=None):
        msg = {"jsonrpc": "2.0", "id": i, "method": method}
        if params is not None:
            msg["params"] = params
        c.send_raw(json.dumps(msg))
        return c.read()

    rpc(1, "initialize", {"protocolVersion": PROTOCOL_VERSION, "capabilities": {}, "clientInfo": CLIENT_INFO})
    c.send_raw(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}))
    rpc(2, "tools/list")
    rpc(3, "tools/call", {"name": "score_posting", "arguments": {"board": "figma", "posting_id": "5691911004"}})
    rpc(4, "tools/call", {"name": "score_posting", "arguments": {"board": "figma", "posting_id": "6242561004"}})
    # deliberate bad requests: what a compatible client might try that it is not entitled to
    rpc(5, "tools/call", {"name": "score_posting", "arguments": {"board": "figma", "posting_id": "../../persona/aarav-patel.resume"}})
    rpc(6, "tools/call", {"name": "score_posting", "arguments": {"board": "../persona", "posting_id": "x"}})
    rpc(7, "tools/call", {"name": "score_posting", "arguments": {"board": "figma", "posting_id": "5691911004", "write_to": "/tmp/x"}})
    rpc(8, "tools/call", {"name": "read_file", "arguments": {"path": "persona/aarav-patel.resume.json"}})
    rpc(9, "resources/list")
    c.send_raw("{this is not json")
    c.read()
    rpc(10, "tools/call", {"name": "score_posting", "arguments": {"board": "figma", "posting_id": "0000000000"}})
    rpc(11, "ping")
    c.close()
    print(f"wrote {os.path.relpath(t.path, ROOT)}")


def http_session(url, name, call=None, args=None, extra=None):
    t = Transcript(name)
    c = HttpConnection(url, t)
    c.post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": PROTOCOL_VERSION, "capabilities": {}, "clientInfo": CLIENT_INFO}})
    c.post({"jsonrpc": "2.0", "method": "notifications/initialized"})
    listed = c.post({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    for tool in (listed or {}).get("result", {}).get("tools", []):
        print("tool:", tool["name"], "| annotations:", tool.get("annotations"))
    if call:
        c.post({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": call, "arguments": args or {}}})
    for i, (method, params) in enumerate(extra or [], start=4):
        c.post({"jsonrpc": "2.0", "id": i, "method": method, "params": params})
    print(f"wrote {os.path.relpath(t.path, ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["stdio-session", "http"])
    ap.add_argument("--name", required=True)
    ap.add_argument("--url")
    ap.add_argument("--call")
    ap.add_argument("--args", default="{}")
    ap.add_argument("--extra", default="[]", help='JSON list of [method, params] sent after the call')
    a = ap.parse_args()
    if a.mode == "stdio-session":
        stdio_session(a.name)
    else:
        http_session(a.url, a.name, a.call, json.loads(a.args), json.loads(a.extra))


if __name__ == "__main__":
    main()
