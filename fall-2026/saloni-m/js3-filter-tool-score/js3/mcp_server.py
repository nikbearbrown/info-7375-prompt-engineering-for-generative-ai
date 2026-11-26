"""A Model Context Protocol tool server written from scratch: JSON-RPC 2.0 over stdio, one JSON
message per line. Standard library only; no MCP SDK.

    python3 -m js3.mcp_server

It offers two read-only tools over the latest local snapshot:
  score_posting   — run FILTER.md on one posting (by uid, or on a title + text you pass in)
  search_postings — find collected postings whose title contains words, with their filter score

What it can touch: it reads FILTER.md and out/snapshots/ (inside this folder). It writes one
transcript file per session under out/mcp/transcripts/, through the JS2 write policy. It opens
no network connection, starts no process, and has no tool that sends or changes anything.
Every message in and out is appended to the transcript before it is acted on / after it is sent.
"""
import datetime as dt
import json
import os
import sys

from js3.collect import HERE, latest_snapshot, load_postings
from js3.filter import load_filter, score
from js3.policy import Policy
from js3.text import words

SERVER_INFO = {"name": "js3-filter-score", "version": "1.0.0"}
SUPPORTED_VERSIONS = ["2025-06-18", "2025-03-26", "2024-11-05"]
MAX_TEXT = 50_000
MAX_RESULTS = 20

TOOLS = [
    {
        "name": "score_posting",
        "title": "Score one posting with FILTER.md",
        "description": ("Apply the job-search filter (FILTER.md, read-only) to one posting and return the score, "
                        "keep/reject, and every rule that fired with the words that fired it. Give either `uid` "
                        "(a posting in the local snapshot, e.g. 'greenhouse:anthropic:5432575008') or `title` and "
                        "`text`. Reads local files only; sends nothing anywhere."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "uid": {"type": "string", "description": "system:board:id of a collected posting"},
                "title": {"type": "string", "maxLength": 300},
                "text": {"type": "string", "maxLength": MAX_TEXT},
            },
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "search_postings",
        "title": "Search collected postings by title words",
        "description": ("Return up to `limit` (max 20) postings from the local snapshot whose title contains every "
                        "word in `query`, each with its filter score and decision. Kept postings first. "
                        "Searches the snapshot on disk; it does not fetch new postings."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "minLength": 1, "maxLength": 200},
                "limit": {"type": "integer", "minimum": 1, "maximum": MAX_RESULTS, "default": 10},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
]


class RpcError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code, self.message = code, message


class Server:
    def __init__(self, transcript_dir=os.path.join(HERE, "out", "mcp", "transcripts")):
        self.policy = Policy(HERE, os.path.join(HERE, "out"), [])
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        self.transcript = os.path.join(transcript_dir, f"{stamp}-server.jsonl")
        self.policy.write_bytes(self.transcript, b"")
        self.flt = load_filter()
        self.snapshot = latest_snapshot()
        self._posts = None
        self.initialized = False

    @property
    def posts(self):
        if self._posts is None:
            self._posts = {p["uid"]: p for p in load_postings(self.snapshot)}
        return self._posts

    def log(self, direction, raw):
        if self.policy.check_write(self.transcript).outcome != "allow":
            return
        rec = {"t": dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds"), "dir": direction, "raw": raw}
        with open(self.transcript, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # -- JSON-RPC ---------------------------------------------------------------------------
    def handle_line(self, line):
        """Return the response line to write, or None for a notification."""
        self.log("client->server", line)
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            return self._error(None, -32700, f"parse error: {e.msg}")
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
            if isinstance(msg, dict) and ("result" in msg or "error" in msg):
                return None  # a response to a request we never send; ignore
            return self._error(msg.get("id") if isinstance(msg, dict) else None, -32600, "invalid request")
        is_note = "id" not in msg
        try:
            result = self.dispatch(msg["method"], msg.get("params") or {})
        except RpcError as e:
            return None if is_note else self._error(msg.get("id"), e.code, e.message)
        if is_note:
            return None
        return json.dumps({"jsonrpc": "2.0", "id": msg["id"], "result": result}, ensure_ascii=False)

    def _error(self, id_, code, message):
        return json.dumps({"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}})

    def dispatch(self, method, params):
        if method == "initialize":
            asked = params.get("protocolVersion")
            version = asked if asked in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0]
            return {"protocolVersion": version, "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": SERVER_INFO,
                    "instructions": "Read-only job-posting filter. Tools read a local snapshot; nothing is sent or changed."}
        if method == "notifications/initialized":
            self.initialized = True
            return None
        if method.startswith("notifications/"):
            return None
        if method == "ping":
            return {}
        if method == "tools/list":
            return {"tools": TOOLS}
        if method == "tools/call":
            return self.call_tool(params.get("name"), params.get("arguments") or {})
        raise RpcError(-32601, f"method not found: {method}")

    # -- tools ------------------------------------------------------------------------------
    def call_tool(self, name, args):
        tool = next((t for t in TOOLS if t["name"] == name), None)
        if tool is None:
            raise RpcError(-32602, f"unknown tool: {name!r}")
        if not isinstance(args, dict):
            raise RpcError(-32602, "arguments must be an object")
        extra = set(args) - set(tool["inputSchema"]["properties"])
        if extra:
            return _tool_error(f"unexpected argument(s): {sorted(extra)}")
        try:
            data = self.score_posting(args) if name == "score_posting" else self.search_postings(args)
        except ValueError as e:
            return _tool_error(str(e))
        return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, indent=1)}],
                "structuredContent": data, "isError": False}

    def score_posting(self, args):
        if "uid" in args:
            if "title" in args or "text" in args:
                raise ValueError("give uid, or title and text, not both")
            p = self.posts.get(args["uid"])
            if p is None:
                raise ValueError(f"no posting {args['uid']!r} in snapshot {os.path.basename(self.snapshot)}")
        else:
            title, text = args.get("title"), args.get("text", "")
            if not isinstance(title, str) or not title.strip():
                raise ValueError("give uid, or a non-empty title (and optionally text)")
            if not isinstance(text, str) or len(text) > MAX_TEXT or len(title) > 300:
                raise ValueError(f"title must be <= 300 chars and text a string <= {MAX_TEXT} chars")
            p = {"uid": None, "title": title, "text": text}
        r = score(p, self.flt)
        r["snapshot"] = os.path.basename(self.snapshot) if p.get("uid") else None
        r["url"] = p.get("url")
        return r

    def search_postings(self, args):
        q = args.get("query")
        limit = args.get("limit", 10)
        if not isinstance(q, str) or not q.strip() or len(q) > 200:
            raise ValueError("query must be a non-empty string of at most 200 chars")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_RESULTS:
            raise ValueError(f"limit must be an integer from 1 to {MAX_RESULTS}")
        qw = set(words(q))
        hits = [score(p, self.flt) for p in self.posts.values() if qw <= set(words(p["title"]))]
        hits.sort(key=lambda r: (r["decision"] != "keep", -r["score"], r["title"]))
        return {"query": q, "snapshot": os.path.basename(self.snapshot), "total_matches": len(hits),
                "results": [{k: r[k] for k in ("uid", "title", "score", "decision", "vetoed")} for r in hits[:limit]]}


def _tool_error(message):
    return {"content": [{"type": "text", "text": message}], "isError": True}


def main():
    server = Server()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        out = server.handle_line(line)
        if out is not None:
            sys.stdout.write(out + "\n")
            sys.stdout.flush()
            server.log("server->client", out)


if __name__ == "__main__":
    main()
