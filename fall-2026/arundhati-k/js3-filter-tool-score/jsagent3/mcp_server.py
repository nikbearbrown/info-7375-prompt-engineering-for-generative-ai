"""A from-scratch Model Context Protocol tool server (stdio, newline-delimited JSON-RPC 2.0), stdlib only.

One capability: score_posting. It is read-only: it reads data/postings.json (built from the saved raw snapshot)
and the filter file, and never touches the network or writes anything except its own transcript log, which is
kept inside this folder. Run:  python3 -m jsagent3.mcp_server [--log out/transcripts/x.jsonl]
"""
import json
import sys
import time
from pathlib import Path

from .evidence import justify
from .filter import HERE, decide, load_rules

PROTOCOL = "2025-06-18"
TOOL = {
    "name": "score_posting",
    "title": "Score one job posting against FILTER.md",
    "description": ("Score one job posting for the fictional persona Rohan Desai (Java/Spring backend, early career) "
                    "using the versioned keyword filter in FILTER.md. Give either posting_id (from the saved local "
                    "snapshot, e.g. 'stripe:8128744') or title+body(+location) as pasted text. Returns keep/reject, "
                    "the reason, matched words, and each shortlist claim labeled supported / contradicted / "
                    "insufficient against the posting text. Read-only: no network, no writes."),
    "inputSchema": {
        "type": "object",
        "properties": {
            "posting_id": {"type": "string", "description": "id like 'stripe:8128744' from the local snapshot"},
            "title": {"type": "string"}, "body": {"type": "string"}, "location": {"type": "string"},
        },
        "additionalProperties": False,
    },
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
}


def _err(i, code, msg):
    return {"jsonrpc": "2.0", "id": i, "error": {"code": code, "message": msg}}


class Server:
    def __init__(self, postings, rules=None, log=None):
        self.postings = postings
        self.rules = rules or load_rules()
        self.log = log
        self.initialized = False

    def _tool_result(self, i, obj, is_error=False):
        text = obj if isinstance(obj, str) else json.dumps(obj, indent=1)
        return {"jsonrpc": "2.0", "id": i,
                "result": {"content": [{"type": "text", "text": text}], "isError": is_error}}

    def _score(self, i, args):
        if not isinstance(args, dict) or set(args) - set(TOOL["inputSchema"]["properties"]):
            return self._tool_result(i, "unexpected arguments; allowed: posting_id or title/body/location", True)
        if any(not isinstance(v, str) for v in args.values()):
            return self._tool_result(i, "all arguments must be strings", True)
        if "posting_id" in args:
            p = self.postings.get(args["posting_id"])
            if p is None:
                return self._tool_result(i, f"no posting with id {args['posting_id']!r} in the local snapshot", True)
        elif "title" in args:
            p = {"id": "pasted", "board": "pasted", "title": args["title"], "body": args.get("body", ""),
                 "location": args.get("location", ""), "url": None}
        else:
            return self._tool_result(i, "give posting_id, or title (+ body, location)", True)
        d = decide(p, self.rules)
        claims = justify(p, d, self.rules) if d["keep"] else []
        return self._tool_result(i, {"posting": {k: p.get(k) for k in ("id", "title", "location", "url")},
                                     "decision": d, "claims": claims, "filter_version": self.rules["version"]})

    def handle(self, msg):
        i, method = msg.get("id"), msg.get("method")
        if i is None:  # notification: never reply
            if method == "notifications/initialized":
                self.initialized = True
            return None
        if method == "initialize":
            return {"jsonrpc": "2.0", "id": i, "result": {
                "protocolVersion": PROTOCOL,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "js3-posting-scorer", "version": "0.1.0"},
                "instructions": "One read-only tool. It scores postings; it cannot apply, email, or fetch."}}
        if method == "ping":
            return {"jsonrpc": "2.0", "id": i, "result": {}}
        if not self.initialized:
            return _err(i, -32002, "server not initialized: send initialize and notifications/initialized first")
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": i, "result": {"tools": [TOOL]}}
        if method == "tools/call":
            params = msg.get("params") or {}
            if params.get("name") != TOOL["name"]:
                return _err(i, -32602, f"unknown tool: {params.get('name')!r}")
            return self._score(i, params.get("arguments") or {})
        return _err(i, -32601, f"method not found: {method}")

    def handle_line(self, line):
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            return json.dumps(_err(None, -32700, f"parse error: {e}"))
        r = self.handle(msg)
        return None if r is None else json.dumps(r)

    def _log(self, direction, line):
        if self.log:
            with open(self.log, "a") as f:
                f.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "dir": direction,
                                    "msg": json.loads(line) if line.strip().startswith("{") else line}) + "\n")

    def serve(self, inp=sys.stdin, out=sys.stdout):
        for line in inp:
            if not line.strip():
                continue
            self._log("client->server", line)
            r = self.handle_line(line)
            if r is not None:
                self._log("server->client", r)
                out.write(r + "\n")
                out.flush()


def load_postings(path=HERE / "data" / "postings.json"):
    if not Path(path).exists():
        from .collect import collect
        posts, _ = collect(HERE / "data" / "raw" / "2026-11-25", offline=True)
        Path(path).write_text(json.dumps(posts))
    return {p["id"]: p for p in json.loads(Path(path).read_text())}


def main(argv=None):
    argv = argv or sys.argv[1:]
    log = None
    if "--log" in argv:
        log = Path(argv[argv.index("--log") + 1]).resolve()
        if HERE not in log.parents:
            sys.exit("--log must be inside this folder")
        log.parent.mkdir(parents=True, exist_ok=True)
    Server(load_postings(), log=log).serve()


if __name__ == "__main__":
    main()
