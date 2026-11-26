"""A stdlib MCP client that records every line in both directions.

python3 mcp_client.py own      -> transcripts/01-own-client.jsonl + .md  (our server, incl. probes)
python3 mcp_client.py claude   -> transcripts/03-claude-mcp-serve.jsonl + .md  (`claude mcp serve`, list only
                                  + at most one read-only call; never Bash/Write/Edit)
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TR = HERE / "transcripts"


class Client:
    def __init__(self, cmd, rec, label):
        self.p = subprocess.Popen(cmd, cwd=HERE, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, text=True, bufsize=1)
        self.rec, self.label, self.next_id = rec, label, 1

    def _rec(self, direction, obj):
        self.rec.append({"t": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "process": self.label,
                         "dir": direction, "msg": obj})

    def send(self, method, params=None, notify=False, raw=None):
        if raw is not None:
            line = raw
            self._rec("client->server", raw)
        else:
            msg = {"jsonrpc": "2.0", "method": method}
            if params is not None:
                msg["params"] = params
            if not notify:
                msg["id"] = self.next_id
                self.next_id += 1
            line = json.dumps(msg)
            self._rec("client->server", msg)
        self.p.stdin.write(line + "\n")
        self.p.stdin.flush()
        if notify:
            return None
        while True:
            out = self.p.stdout.readline()
            if not out:
                self._rec("server->client", "<EOF>")
                return None
            try:
                obj = json.loads(out)
            except json.JSONDecodeError:
                self._rec("server->client", out.rstrip("\n"))
                continue
            self._rec("server->client", obj)
            if "id" in obj:  # skip server-initiated notifications
                return obj

    def initialize(self):
        r = self.send("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                     "clientInfo": {"name": "js3-recording-client", "version": "0.1.0"}})
        self.send("notifications/initialized", notify=True)
        return r

    def close(self):
        self.p.stdin.close()
        try:
            self.p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.p.kill()


HOME = str(Path.home())


def redact(rec):
    """Only change: the local home path is replaced by <HOME> (privacy). Nothing else is edited."""
    return [json.loads(json.dumps(r).replace(HOME, "<HOME>")) for r in rec]


def write(rec, stem, title):
    TR.mkdir(exist_ok=True)
    rec = redact(rec)
    (TR / f"{stem}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rec))
    with (TR / f"{stem}.md").open("w") as f:
        f.write(f"# {title}\n\nRecorded by `mcp_client.py` on {time.strftime('%Y-%m-%d')}. Every line in both "
                f"directions, in order. Raw: `{stem}.jsonl`. Redaction: home path shown as `<HOME>`.\n\n")
        for r in rec:
            arrow = "→ client to server" if r["dir"] == "client->server" else "← server to client"
            body = json.dumps(r["msg"], indent=1)
            if len(body) > 6000:
                body = body[:6000] + "\n... (truncated here; full text in the .jsonl)"
            f.write(f"**{arrow}** · `{r['process']}` · {r['t']}\n\n```json\n{body}\n```\n\n")


def own():
    rec = []
    cmd = [sys.executable, "-m", "jsagent3.mcp_server"]
    # probe in a fresh process: tools/call before initialize
    c0 = Client(cmd, rec, "process-A (no initialize)")
    c0.send("tools/call", {"name": "score_posting", "arguments": {"posting_id": "stripe:8128744"}})
    c0.close()
    c = Client(cmd, rec, "process-B")
    c.initialize()
    c.send("tools/list")
    c.send("tools/call", {"name": "score_posting", "arguments": {"posting_id": "stripe:8128744"}})
    c.send("tools/call", {"name": "score_posting", "arguments": {
        "title": "Electrical Engineer", "body": "Requirements\n- Java, SQL, AWS", "location": "Austin, TX"}})
    c.send("resources/list")
    c.send("tools/call", {"name": "apply_to_job", "arguments": {"posting_id": "stripe:8128744"}})
    c.send("tools/call", {"name": "score_posting", "arguments": {"posting_id": "../../etc/passwd"}})
    c.send("tools/call", {"name": "score_posting", "arguments": {"posting_id": 8128744}})
    c.send("tools/call", {"name": "score_posting", "arguments": {"posting_id": "stripe:8128744", "path": "/etc"}})
    c.send(None, raw="{not json")
    c.close()
    write(rec, "01-own-client", "Transcript 01 — my client ↔ my server (js3-posting-scorer)")


def claude_serve():
    rec = []
    c = Client(["claude", "mcp", "serve"], rec, "claude mcp serve")
    c.initialize()
    lst = c.send("tools/list")
    names = [t["name"] for t in ((lst or {}).get("result") or {}).get("tools", [])]
    # at most one read-only call, only if a Read tool is declared
    if "Read" in names:
        c.send("tools/call", {"name": "Read", "arguments": {"file_path": str(HERE / "FILTER.md"), "limit": 5}})
    c.close()
    write(rec, "03-claude-mcp-serve", "Transcript 03 — my client ↔ `claude mcp serve` (Claude Code 2.1.316)")
    print("claude mcp serve tools:", names)


if __name__ == "__main__":
    {"own": own, "claude": claude_serve}[sys.argv[1]]()
