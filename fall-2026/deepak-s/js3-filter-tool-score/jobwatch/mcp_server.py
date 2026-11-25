"""The JS3 tool server: JSON-RPC 2.0 over stdio, Model Context Protocol revision 2026-07-28.
Written from scratch with the standard library (no MCP SDK).

    python -m jobwatch mcp-server --dataset data/postings-<run-id>.jsonl [--version v1]

Revision choice: the Phase 5 probe recorded that Claude Code 2.1.332's first message is
server/discover with protocolVersion 2026-07-28 (evidence/mcp/probe/20261125T211913Z.jsonl), so by
Deepak's pre-set rule this server targets 2026-07-28 only (evidence/mcp/SPEC_NOTES.md).

Methods:
  server/discover   supported versions, capabilities {"tools": {}}, serverInfo, ttlMs, cacheScope
  tools/list        one tool, score_posting, with ttlMs and cacheScope
  tools/call        score_posting(posting_key): the filter's decision, score, matched rules with
                    quotes, reasons; an abstention is returned as "I cannot tell: <reason>"
Every request must carry params._meta with io.modelcontextprotocol/protocolVersion and
io.modelcontextprotocol/clientCapabilities (else -32602). A version other than 2026-07-28 gets
UnsupportedProtocolVersionError -32022 with data {supported, requested}. `initialize` (the
2025-11-25 handshake) gets -32601 naming the supported versions. Unknown methods get -32601,
unparseable lines -32700, non-request objects -32600, an unknown tool -32602. A bad argument
(missing, not a string, not a posting key of the dataset) is a tool execution error with
isError true. Notifications get no response.

It reads only data/ and runs/ through tools.read_file, opens no network, and writes only its own
transcript, evidence/mcp/transcripts/<UTC start>.jsonl, through tools.write_file (append): every
line in and out, verbatim, with the UTC time and the direction. stdout carries only JSON-RPC
messages, one per line. posting_key is never used as a path: it is looked up in the dataset.
"""
import json
import re
import sys
from datetime import datetime, timezone

from jobwatch import filter as flt
from jobwatch.policy import Policy
from jobwatch.tools import Tools

PROTOCOL = "2026-07-28"
SUPPORTED = [PROTOCOL]
SERVER_INFO = {"name": "jobwatch-js3", "version": "1.0.0"}
META_VERSION = "io.modelcontextprotocol/protocolVersion"
META_CAPS = "io.modelcontextprotocol/clientCapabilities"
KEY_RE = re.compile(r"^(greenhouse|lever|ashby):[A-Za-z0-9_-]+:[A-Za-z0-9-]+$")
TOOL = {
    "name": "score_posting",
    "title": "Score one collected job posting",
    "description": ("Runs the JS3 filter (FILTER.md v1) on one posting of the committed dataset and returns "
                    "keep, reject or 'I cannot tell', the score, the matched rules with their quotes, and the reasons. "
                    "Read-only; it fetches nothing."),
    "inputSchema": {"type": "object",
                    "properties": {"posting_key": {"type": "string",
                                                   "description": "<system>:<slug>:<posting id>, e.g. greenhouse:stripe:8187574"}},
                    "required": ["posting_key"], "additionalProperties": False},
}


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class Server:
    def __init__(self, root, dataset_path, version="v1", out=None):
        start = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        self.transcript = f"evidence/mcp/transcripts/{start}.jsonl"
        self.tools = Tools(Policy(root, read_dirs=("data", "runs"), write_dirs=("evidence/mcp/transcripts",)),
                           append_names=(f"{start}.jsonl",))
        self.dataset_path = dataset_path
        self.rules = flt.VERSIONS[version]
        self.out = out or sys.stdout
        self._lines = None
        self._log("note", f"server started: protocol {PROTOCOL}, dataset {dataset_path}, filter {version}", first=True)

    # --- transcript ------------------------------------------------------------------------------
    def _log(self, direction, line, first=False):
        rec = (json.dumps({"t": _now(), "dir": direction, "line": line}, ensure_ascii=False) + "\n").encode("utf-8")
        self.tools.write_file(self.transcript, rec, mode="replace" if first else "append")

    def send(self, msg):
        line = json.dumps(msg, ensure_ascii=False, separators=(",", ":"))
        self._log("out", line)
        self.out.write(line + "\n")
        self.out.flush()

    # --- data --------------------------------------------------------------------------------------
    def lines(self):
        if self._lines is None:
            data = self.tools.read_file(self.dataset_path).decode("utf-8")
            self._lines = {}
            for raw in data.splitlines():
                if raw.strip():
                    ln = json.loads(raw)
                    self._lines[ln["key"]] = ln
        return self._lines

    # --- messages ----------------------------------------------------------------------------------
    def error(self, id_, code, message, data=None):
        err = {"code": code, "message": message}
        if data is not None:
            err["data"] = data
        self.send({"jsonrpc": "2.0", "id": id_, "error": err})

    def result(self, id_, body):
        body = {"resultType": "complete", **body, "_meta": {"io.modelcontextprotocol/serverInfo": SERVER_INFO}}
        self.send({"jsonrpc": "2.0", "id": id_, "result": body})

    def handle_line(self, raw):
        self._log("in", raw)
        try:
            msg = json.loads(raw)
        except ValueError:
            return self.error(None, -32700, "Parse error: the line is not JSON")
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
            id_ = msg.get("id") if isinstance(msg, dict) and isinstance(msg.get("id"), (str, int)) else None
            if isinstance(msg, dict) and "method" not in msg and ("result" in msg or "error" in msg):
                return None  # a response sent to the server: nothing was asked, nothing to answer
            return self.error(id_, -32600, "Invalid Request: expected a JSON-RPC 2.0 request or notification")
        method, params = msg["method"], msg.get("params")
        if "id" not in msg:
            return None  # a notification (for example notifications/cancelled): no response
        id_ = msg["id"]
        if not isinstance(id_, (str, int)) or isinstance(id_, bool):
            return self.error(None, -32600, "Invalid Request: id must be a string or an integer")
        if method == "initialize":
            return self.error(id_, -32601, f"initialize is not supported: this server speaks protocol versions "
                                           f"{', '.join(SUPPORTED)} only (per-request _meta, server/discover)",
                              {"supported": SUPPORTED})
        if method not in ("server/discover", "tools/list", "tools/call"):
            return self.error(id_, -32601, f"Method not found: {method}")
        meta = params.get("_meta") if isinstance(params, dict) else None
        if not isinstance(meta, dict) or META_VERSION not in meta or META_CAPS not in meta:
            return self.error(id_, -32602, f"Invalid params: _meta must carry {META_VERSION} and {META_CAPS}")
        if meta[META_VERSION] not in SUPPORTED:
            return self.error(id_, -32022, "Unsupported protocol version",
                              {"supported": SUPPORTED, "requested": meta[META_VERSION]})
        if method == "server/discover":
            return self.result(id_, {"supportedVersions": SUPPORTED, "capabilities": {"tools": {}},
                                     "instructions": "One read-only tool, score_posting, over a committed dataset of job postings.",
                                     "ttlMs": 300000, "cacheScope": "public"})
        if method == "tools/list":
            return self.result(id_, {"tools": [TOOL], "ttlMs": 300000, "cacheScope": "public"})
        return self.call(id_, params)

    def call(self, id_, params):
        name, args = params.get("name"), params.get("arguments", {})
        if not isinstance(name, str):
            return self.error(id_, -32602, "Invalid params: tools/call needs a tool name")
        if name != TOOL["name"]:
            return self.error(id_, -32602, f"Unknown tool: {name}")
        if not isinstance(args, dict):
            return self.error(id_, -32602, "Invalid params: arguments must be an object")
        key = args.get("posting_key")
        extra = sorted(set(args) - {"posting_key"})
        if not isinstance(key, str) or extra:
            return self.tool_error(id_, "posting_key is required and must be a string; no other argument is accepted"
                                   + (f" (got {', '.join(extra)})" if extra else ""))
        if not KEY_RE.match(key):
            return self.tool_error(id_, "posting_key must look like <system>:<slug>:<posting id>, "
                                        "for example greenhouse:stripe:8187574")
        line = self.lines().get(key)
        if line is None:
            return self.tool_error(id_, f"no posting with key {key} in {self.dataset_path}")
        o = flt.evaluate(line, self.rules)
        decision = "I cannot tell" if o["decision"] == "abstain" else o["decision"]
        structured = {"posting_key": key, "title": line["title"], "location": line["location"], "filter_version": self.rules.version,
                      "decision": decision, "score": o["score"], "threshold": self.rules.threshold, "reasons": o["reasons"],
                      "matched_rules": [{"rule": m["rule"], "field": m["field"], "quote": m["quote"],
                                         "start": m["start"], "end": m["end"]} for m in o["matched"]]}
        summary = (f"{decision.upper()} (score {o['score']}, T={self.rules.threshold}): {'; '.join(o['reasons'])}. "
                   f"Matched: " + (", ".join(f"{m['rule']} \"{m['quote']}\" ({m['field']})" for m in o["matched"]) or "none"))
        return self.result(id_, {"content": [{"type": "text", "text": summary}], "structuredContent": structured, "isError": False})

    def tool_error(self, id_, text):
        return self.result(id_, {"content": [{"type": "text", "text": text}], "isError": True})

    def serve(self, stdin):
        for raw in stdin:
            raw = raw.rstrip("\n")
            if raw.strip():
                self.handle_line(raw)
        self._log("note", "end of input; server exits")
        return 0
