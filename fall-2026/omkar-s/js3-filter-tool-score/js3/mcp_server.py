"""A Model Context Protocol tool server, written from scratch (Chapter 8). Python stdlib only.

    python3 -m js3.mcp_server            # speaks MCP over stdio: one JSON-RPC 2.0 message per line

It offers ONE capability, `score_posting`: run the current FILTER.md filter on one posting, either a
posting already collected (by id) or a posting the client pastes (title, location, content). It returns
the verdict, the score lines and every claim with its evidence label.

What it can touch, by construction:
  reads   filter/CURRENT + filter/*.json, persona/aarav-patel.example.json, data/corpus/<latest>.jsonl.gz
  writes  transcripts/<start>-<pid>.jsonl only (every message in and out), through js3.store
  never   the network, any path taken from a request, any file outside this folder, any write
          outside transcripts/
Messages handled: initialize, notifications/initialized, ping, tools/list, tools/call. Anything else
is answered with JSON-RPC error -32601 (method not found).
"""
import datetime as dt
import json
import os
import re
import sys

from . import data, scorer, store

SERVER_INFO = {"name": "js3-score", "title": "JS3 posting scorer (read-only)", "version": "1.0.0"}
SUPPORTED_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
MAX_LINE = 200_000          # bytes per incoming message
MAX_CONTENT = 50_000        # characters of pasted posting text
ID_RE = re.compile(r"^[A-Za-z0-9-]{1,64}$")

TOOL = {
    "name": "score_posting",
    "title": "Score one job posting with the JS3 filter",
    "description": (
        "Runs the JS3 filter (FILTER.md, current version) on ONE job posting for the fictional candidate "
        "Aarav Patel and returns: verdict (keep / reject / cannot_tell), the score lines that sum to the score, "
        "the gates and, when the verdict is keep, every claim labelled supported / contradicted / insufficient "
        "against the posting text (a rejected posting gets no claims). "
        "Give EITHER posting_id (a posting this agent already collected; optional source like "
        "'greenhouse:toast') OR title + location + content (paste a posting). Read-only: it never fetches, "
        "applies, emails or writes anything except its own transcript log."),
    "inputSchema": {
        "type": "object",
        "properties": {
            "posting_id": {"type": "string", "pattern": ID_RE.pattern, "description": "id of a collected posting"},
            "source": {"type": "string", "description": "optional board key, e.g. greenhouse:klaviyo"},
            "title": {"type": "string", "maxLength": 300},
            "location": {"type": "string", "maxLength": 300},
            "content": {"type": "string", "maxLength": MAX_CONTENT},
        },
        "additionalProperties": False,
    },
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
}


class Server:
    def __init__(self, log_path=None):
        self.initialized = False
        self.protocol = None
        self.cfg = scorer.load_filter()
        self.persona = data.load_persona()
        self._corpus = None
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
        sub = os.environ.get("JS3_MCP_LOG_SUBDIR", "")  # e.g. "e5" -> transcripts/e5/ (still checked by store)
        if sub and not re.match(r"^[A-Za-z0-9_-]{1,32}$", sub):
            sub = ""
        default = os.path.join("transcripts", sub, f"server-{stamp}-{os.getpid()}.jsonl")
        self.log_path = store.check(log_path or default)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    # transcript: every line, both directions, exactly as sent
    def log(self, direction, line):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds"),
                                "dir": direction, "raw": line}, ensure_ascii=False) + "\n")

    def corpus(self):
        if self._corpus is None:
            run, rows = data.load_corpus()
            self._corpus = (run, rows)
        return self._corpus

    @staticmethod
    def _err(mid, code, message, data_=None):
        e = {"code": code, "message": message}
        if data_ is not None:
            e["data"] = data_
        return {"jsonrpc": "2.0", "id": mid, "error": e}

    def handle_line(self, line):
        """One incoming line -> one outgoing message (dict) or None for notifications."""
        if len(line.encode("utf-8")) > MAX_LINE:
            return self._err(None, -32600, f"message larger than {MAX_LINE} bytes")
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            return self._err(None, -32700, f"parse error: {e.msg}")
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
            if isinstance(msg, dict) and ("result" in msg or "error" in msg):
                return None  # a response to us; we never send requests, so ignore it
            return self._err(msg.get("id") if isinstance(msg, dict) else None, -32600, "invalid request")
        method, mid, params = msg["method"], msg.get("id"), msg.get("params") or {}
        is_note = "id" not in msg
        if method == "notifications/initialized":
            self.initialized = True
            return None
        if is_note:
            return None  # other notifications (e.g. cancelled) need no answer
        if method == "initialize":
            req = params.get("protocolVersion")
            self.protocol = req if req in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0]
            return {"jsonrpc": "2.0", "id": mid, "result": {
                "protocolVersion": self.protocol,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
                "instructions": "One read-only tool, score_posting. It scores a posting with Omkar's JS3 filter "
                                f"v{self.cfg['version']} for a FICTIONAL persona. The judgment that a job is worth "
                                "applying to is not this tool's; it only reports what the filter and the posting text say."}}
        if method == "ping":
            return {"jsonrpc": "2.0", "id": mid, "result": {}}
        if self.protocol is None:
            return self._err(mid, -32002, "server not initialized: send initialize first")
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": mid, "result": {"tools": [TOOL]}}
        if method == "tools/call":
            return self.call(mid, params)
        return self._err(mid, -32601, f"method not found: {method}")

    def call(self, mid, params):
        name, args = params.get("name"), params.get("arguments") or {}
        if name != TOOL["name"]:
            return self._err(mid, -32602, f"unknown tool: {name!r}")
        if not isinstance(args, dict):
            return self._err(mid, -32602, "arguments must be an object")
        allowed = set(TOOL["inputSchema"]["properties"])
        extra = sorted(set(args) - allowed)
        if extra:
            return self._err(mid, -32602, f"unexpected arguments: {extra}")
        bad = [k for k, v in args.items() if not isinstance(v, str)]
        if bad:
            return self._err(mid, -32602, f"arguments must be strings: {bad}")
        if "posting_id" in args:
            if not ID_RE.match(args["posting_id"]):
                return self._err(mid, -32602, "posting_id must match " + ID_RE.pattern)
            if any(k in args for k in ("title", "location", "content")):
                return self._err(mid, -32602, "give posting_id OR title/location/content, not both")
            run, rows = self.corpus()
            hits = [p for p in rows if p["id"] == args["posting_id"] and
                    (not args.get("source") or p["source"] == args["source"])]
            if not hits:
                return self._tool_result(mid, f"No collected posting has id {args['posting_id']!r} in corpus {run}. "
                                              "I cannot tell anything about it.", None, is_error=True)
            if len(hits) > 1:
                return self._tool_result(mid, "That id is on more than one board; add source.",
                                         {"sources": [p["source"] for p in hits]}, is_error=True)
            p = hits[0]
        else:
            if not args.get("content") and not args.get("title"):
                return self._err(mid, -32602, "give posting_id, or at least title and content")
            for k, limit in (("content", MAX_CONTENT), ("title", 300), ("location", 300)):
                if len(args.get(k, "")) > limit:
                    return self._err(mid, -32602, f"{k} longer than {limit} characters")
            p = {"id": "pasted", "source": "pasted", "company": "(pasted)", "title": args.get("title", ""),
                 "location": {"name": args.get("location", "")}, "offices": [], "content": args.get("content", ""),
                 "html": args.get("content", ""), "absolute_url": ""}
        rec = scorer.evaluate(p, self.persona, self.cfg)
        out = {"filter_version": self.cfg["version"], "verdict": rec["verdict"], "score": rec["score"],
               "threshold": self.cfg["threshold"], "lines": rec["lines"], "gates": rec["gates"],
               "reasons": rec["reasons"], "title": rec["title"], "location": rec["location"], "source": rec["source"]}
        if rec["verdict"] == "keep":
            cl = scorer.claims(p, rec, self.cfg)
            out["claims"] = cl
            out["shortlist_status"], out["shortlist_reasons"] = scorer.shortlist_status(cl, self.cfg)
        lines = [f"{rec['title']} ({rec['location'] or 'no location'}) → {rec['verdict']}, score {rec['score']} "
                 f"(threshold {self.cfg['threshold']}, filter v{self.cfg['version']})"]
        lines += [f"  {l['rule']} {l['points']:+g}: {l['why']}" for l in rec["lines"]]
        lines += [f"  reason: {r}" for r in rec["reasons"]]
        for c in out.get("claims", []):
            lines.append(f"  claim [{c['label']}] {c['text']}: {c['quote'][:160] or '—'}")
        if out.get("shortlist_status"):
            lines.append(f"  shortlist: {out['shortlist_status']} {'; '.join(out['shortlist_reasons'])}")
        return self._tool_result(mid, "\n".join(lines), out)

    @staticmethod
    def _tool_result(mid, text, structured, is_error=False):
        res = {"content": [{"type": "text", "text": text}], "isError": is_error}
        if structured is not None:
            res["structuredContent"] = structured
        return {"jsonrpc": "2.0", "id": mid, "result": res}


def serve(stdin=sys.stdin, stdout=sys.stdout, log_path=None):
    srv = Server(log_path)
    for line in stdin:
        line = line.rstrip("\n")
        if not line.strip():
            continue
        srv.log("client->server", line)
        try:
            resp = srv.handle_line(line)
        except Exception as e:  # never crash the session; report and go on
            try:
                mid = json.loads(line).get("id")
            except Exception:
                mid = None
            resp = srv._err(mid, -32603, f"internal error: {e.__class__.__name__}")
        if resp is not None:
            out = json.dumps(resp, ensure_ascii=False)
            srv.log("server->client", out)
            stdout.write(out + "\n")
            stdout.flush()


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    serve()
