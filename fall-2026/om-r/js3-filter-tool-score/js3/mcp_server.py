"""js3-score: an MCP-shaped tool server, written from scratch (stdlib only).

Wire format: MCP protocol version 2025-06-18, stdio transport.
  - One JSON-RPC 2.0 message per line on stdin/stdout, UTF-8, no embedded
    newlines. Nothing but MCP messages goes to stdout; logs go to stderr.
  - Lifecycle: initialize -> notifications/initialized -> tools/list ->
    tools/call. ping is answered at any time.
  - Errors, per the 2025-06-18 split: unknown tool and invalid arguments
    -> JSON-RPC -32602; failures while running the tool -> a result with
    isError: true.
  - Not implemented: the 2026-07-28 "modern" per-request-_meta protocol
    (no initialize; server/discover). A modern client probing
    server/discover gets -32601, which that spec treats as "legacy server,
    fall back to initialize".
  - JSON-RPC batch arrays are refused (-32600).

ONE tool, score_posting: a posting (board + id from the committed evidence of
run 20261121T132140Z, or ad hoc title + content) -> filter v1.1.0 (rules 1-4)
-> if, and only if, the filter says "relevant": one real Claude judgment via
js3.shortlist (shortlist-v1), every claim grounded by js3.grounding.

Every inbound line and every outbound line is appended verbatim to a wire log
(logs/mcp/server_<stamp>_<pid>.jsonl) BEFORE it is processed / sent. All
writes are confined to write_root (default logs/mcp/).

    python3 -m js3.mcp_server        # speaks MCP on stdin/stdout
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from js3 import filter_v110, minischema, shortlist
from js3.postings import load_run

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOG_DIR = ROOT / "logs" / "mcp"
PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "js3-score", "title": "JS3 posting scorer (filter v1.1.0 + shortlist-v1)",
               "version": "0.1.0"}
BOARDS = ["gitlab", "stripe", "palantir"]

INPUT_SCHEMA = {
    "type": "object",
    "description": "Either {board, id} for a posting in the committed 2026-11-21 evidence, "
                   "or {title, content} for an ad hoc posting. Not both.",
    "properties": {
        "board": {"type": "string", "enum": BOARDS},
        "id": {"type": ["string", "integer"]},
        "title": {"type": "string", "minLength": 1},
        "content": {"type": "string"},
    },
    "additionalProperties": False,
    # Each branch is CLOSED (its own properties + additionalProperties: false),
    # so a key from the other mode fails that branch. Found, then fixed
    # (2026-11-22): the branches used to list only required keys, so
    # {board, id, title} and {board, id, content} validated and the extra key
    # was silently ignored (logs/27 before, logs/28 after).
    "oneOf": [
        {"required": ["board", "id"], "properties": {"board": {}, "id": {}}, "additionalProperties": False},
        {"required": ["title", "content"], "properties": {"title": {}, "content": {}},
         "additionalProperties": False},
    ],
}

_STR_OR_NULL = {"type": ["string", "null"]}
_CLAIM = {
    "type": "object",
    "required": ["claim", "quote", "label", "field", "quote_label", "contradicted_by", "contradicted_by_field"],
    "properties": {
        "claim": {"type": "string"},
        "quote": _STR_OR_NULL,
        "label": {"type": "string", "enum": ["supported", "contradicted", "insufficient"]},
        "field": {"type": ["string", "null"], "enum": ["title", "content", None]},
        "quote_label": {"type": "string", "enum": ["supported", "insufficient"]},
        "contradicted_by": _STR_OR_NULL,
        "contradicted_by_field": {"type": ["string", "null"], "enum": ["title", "content", None]},
    },
    "additionalProperties": False,
}
OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["posting", "filter", "judgment"],
    "properties": {
        "posting": {
            "type": "object", "required": ["source", "board", "id", "title", "url"],
            "properties": {"source": {"type": "string", "enum": ["committed_evidence", "adhoc"]},
                           "board": {"type": "string"}, "id": {"type": ["string", "integer"]},
                           "title": {"type": "string"}, "url": _STR_OR_NULL},
            "additionalProperties": False},
        "filter": {
            "type": "object", "required": ["version", "bucket", "reasons", "eligibility_flags"],
            "properties": {"version": {"type": "string"},
                           "bucket": {"type": "string", "enum": ["relevant", "rejected", "insufficient_data"]},
                           "reasons": {"type": "array", "items": {"type": "string"}},
                           "eligibility_flags": {"type": "array", "items": {
                               "type": "object", "required": ["kind", "quote"],
                               "properties": {"kind": {"type": "string", "enum": ["graduation", "clearance"]},
                                              "quote": {"type": "string"}},
                               "additionalProperties": False}}},
            "additionalProperties": False},
        "judgment": {
            "type": ["object", "null"],
            "description": "null when the filter bucket is not 'relevant' (Claude is not called).",
            "required": ["model", "prompt_version", "verdict", "claims", "message_id", "transcript"],
            "properties": {"model": {"type": "string"}, "prompt_version": {"type": "string"},
                           "verdict": {"type": "string", "enum": ["relevant", "not relevant"]},
                           "claims": {"type": "array", "items": _CLAIM},
                           "message_id": {"type": "string"}, "transcript": {"type": "string"}},
            "additionalProperties": False},
    },
    "additionalProperties": False,
}

TOOL = {
    "name": "score_posting",
    "title": "Score a job posting for Priya Nair",
    "description": (
        "Runs one posting through filter v1.1.0 (FILTER.md rules 1-4). If the filter bucket is "
        "'relevant', makes ONE real Claude judgment (claude-opus-5-5, prompt shortlist-v1) and "
        "returns the verdict with every claim grounded against the posting text "
        "(supported / contradicted / insufficient). If the bucket is not 'relevant', Claude is not "
        "called and judgment is null. Persona is fixed (JS1 resume.json, fictional). Each judged "
        "call is billed, non-deterministic, and writes a transcript under logs/mcp/."),
    "inputSchema": INPUT_SCHEMA,
    "outputSchema": OUTPUT_SCHEMA,
    # Hints only; MCP clients MUST treat annotations as untrusted unless the server is trusted.
    "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False,
                    "openWorldHint": True},
}


class RpcError(Exception):
    def __init__(self, code, message, data=None):
        super().__init__(message)
        self.code, self.message, self.data = code, message, data


class Server:
    def __init__(self, client_factory=shortlist.get_client, log_dir=None, write_root=None, resume=None):
        self.log_dir = Path(log_dir or os.environ.get("JS3_MCP_LOG_DIR") or DEFAULT_LOG_DIR)
        self.write_root = Path(write_root or self.log_dir).resolve()
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.wire_log = self.log_dir / f"server_{stamp}_{os.getpid()}.jsonl"
        self.client_factory = client_factory
        self._resume = resume
        self._postings = None
        self.initialized = False   # True once initialize has been answered

    # ---- confined writes ------------------------------------------------
    def _append(self, path, line):
        path = Path(path).resolve()
        if not path.is_relative_to(self.write_root):
            raise PermissionError(f"write outside {self.write_root}: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def _log(self, direction, raw):
        at = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        self._append(self.wire_log, json.dumps({"at": at, "dir": direction, "raw": raw}, ensure_ascii=False))

    # ---- one line in, at most one line out -------------------------------
    def handle_line(self, raw):
        self._log("client->server", raw)
        resp = self._dispatch(raw)
        if resp is None:
            return None
        out = json.dumps(resp, ensure_ascii=False, separators=(",", ":"))
        self._log("server->client", out)
        return out

    def _dispatch(self, raw):
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError as e:
            return _error(None, -32700, f"Parse error: {e}")
        if isinstance(msg, list):
            return _error(None, -32600, "Invalid Request: JSON-RPC batches are not supported")
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
            return _error(msg.get("id") if isinstance(msg, dict) else None, -32600, "Invalid Request")
        if "id" not in msg:   # notification: never answered
            if msg["method"] == "notifications/initialized":
                pass
            return None
        rid = msg["id"]
        if rid is None or isinstance(rid, bool) or not isinstance(rid, (str, int)):
            return _error(None, -32600, "Invalid Request: id must be a string or integer, not null")
        try:
            return {"jsonrpc": "2.0", "id": rid, "result": self._method(msg["method"], msg.get("params") or {})}
        except RpcError as e:
            return _error(rid, e.code, e.message, e.data)
        except Exception as e:   # bug in this server: reported, never hidden
            return _error(rid, -32603, f"Internal error: {type(e).__name__}: {e}")

    def _method(self, method, params):
        if method == "ping":
            return {}
        if method == "initialize":
            self.initialized = True
            return {"protocolVersion": PROTOCOL_VERSION,   # the only version supported; echoed if requested
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": SERVER_INFO,
                    "instructions": "One tool, score_posting. Judged calls are billed and not idempotent."}
        if not self.initialized:
            raise RpcError(-32600, "Invalid Request: send initialize first")
        if method == "tools/list":
            return {"tools": [TOOL]}
        if method == "tools/call":
            return self._call(params)
        raise RpcError(-32601, f"Method not found: {method}")

    # ---- the one tool ----------------------------------------------------
    def _call(self, params):
        if not isinstance(params, dict) or params.get("name") != TOOL["name"]:
            raise RpcError(-32602, f"Unknown tool: {params.get('name') if isinstance(params, dict) else params!r}")
        args = params.get("arguments", {})
        errs = minischema.errors(args, INPUT_SCHEMA, "arguments")
        if errs:
            raise RpcError(-32602, "Invalid arguments for score_posting", {"errors": errs})

        posting, source = self._posting(args)
        if posting is None:
            return _tool_error(f"No posting {args['board']} {args['id']!r} in the committed evidence "
                               f"of run 20261121T132140Z.")
        f = filter_v110.classify(posting)
        out = {"posting": {"source": source, "board": posting["board"], "id": posting["id"],
                           "title": f["title"] or "", "url": posting.get("url")},
               "filter": {"version": f["filter_version"], "bucket": f["bucket"], "reasons": f["reasons"],
                          "eligibility_flags": f.get("eligibility_flags") or []},
               "judgment": None}
        if f["bucket"] == "relevant":
            try:
                client = self.client_factory()
            except shortlist.MissingAPIKey as e:
                return _tool_error(f"Filter bucket is 'relevant' but no judgment was made: {e}")
            r = shortlist.judge(posting, self.resume(), client,
                                transcript_dir=self.log_dir / "judge_transcripts")
            if r["status"] != "ok":
                return _tool_error(f"Judgment unavailable ({r['status']}): {r['error']}. "
                                   f"Transcript: {r['transcript']}")
            out["judgment"] = {"model": r["served_model"], "prompt_version": r["prompt_version"],
                               "verdict": r["verdict"], "claims": r["claims"],
                               "message_id": r["message_id"], "transcript": r["transcript"]}
            text = shortlist.render(r)
        else:
            text = f"filter {f['filter_version']}: {f['bucket']} - Claude not called.\n" + \
                   "\n".join(f"  {x}" for x in f["reasons"])
        bad = minischema.errors(out, OUTPUT_SCHEMA)
        if bad:   # the server never sends structuredContent that breaks its own declared schema
            raise RpcError(-32603, "Internal error: result does not match declared outputSchema", {"errors": bad})
        return {"content": [{"type": "text", "text": json.dumps(out, ensure_ascii=False)},
                            {"type": "text", "text": text}],
                "structuredContent": out, "isError": False}

    def _posting(self, args):
        if "board" in args:
            if self._postings is None:
                _, ps, _ = load_run(shortlist.RUN_REPORT, ROOT)
                self._postings = {(p["board"], str(p["id"])): p for p in ps}
            return self._postings.get((args["board"], str(args["id"]))), "committed_evidence"
        h = hashlib.sha256((args["title"] + "\0" + args["content"]).encode()).hexdigest()[:12]
        return {"board": "adhoc", "id": f"adhoc-{h}", "title": args["title"], "content": args["content"],
                "url": None}, "adhoc"

    def resume(self):
        if self._resume is None:
            self._resume = json.loads(shortlist.RESUME_PATH.read_text())
        return self._resume


def _error(rid, code, message, data=None):
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": rid, "error": err}


def _tool_error(text):
    return {"content": [{"type": "text", "text": text}], "isError": True}


def main():
    proto_out = sys.stdout                 # the only handle MCP messages go to
    sys.stdout = sys.stderr                # anything else that prints lands on stderr
    server = Server()
    print(f"js3-score MCP server {SERVER_INFO['version']} (protocol {PROTOCOL_VERSION}); "
          f"wire log: {server.wire_log}", file=sys.stderr, flush=True)
    for line in sys.stdin:                 # EOF on stdin -> exit
        line = line.rstrip("\n")
        if line.endswith("\r"):
            line = line[:-1]
        if not line.strip():
            continue
        out = server.handle_line(line)
        if out is not None:
            proto_out.write(out + "\n")
            proto_out.flush()


if __name__ == "__main__":
    main()
