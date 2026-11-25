"""A read-only MCP tool server for Job-Search Agent 3, written from scratch (Python standard library only).

    python mcp_server/server.py            # JSON-RPC 2.0, one message per line on stdin/stdout

Lifecycle (Chapter 8): `initialize` (request) -> `notifications/initialized` (notification) -> ready.
Tool operations are refused until ready. One tool, `score_posting(posting_id)`, returns the
FILTER.md v2 verdict, its reason and, for accepted postings, the C1-C4 claims with quotes.

What it reads: only `out3/filter-run-v2/results.json` and `out3/filter-run-v2/shortlist.json` inside
this assignment folder, loaded once at start. The posting_id is a key into that data; it is never
used to build a path. What it writes: only its own transcript, `mcp_server/transcripts/<date>-<client>.jsonl`.
No network, no subprocess, no other file access.

Error layers: -32700 parse error, -32600 invalid request, -32601 unknown method, -32602 bad params,
-32000 used before ready. A well-formed call that finds nothing (unknown or malformed posting_id) is
a tool result with isError: true, not a JSON-RPC error.
"""
import datetime
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "out3" / "filter-run-v2"
TRANSCRIPTS = HERE / "transcripts"

SERVER_INFO = {"name": "js3-score-posting", "version": "1.0.0"}
SUPPORTED_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
POSTING_ID = re.compile(r"^(greenhouse|ashby):[a-z0-9-]{1,64}:[A-Za-z0-9-]{1,64}$")

TOOL = {
    "name": "score_posting",
    "title": "Score one collected job posting",
    "description": ("Return the SAVED FILTER.md v2 verdict (accept / reject / abstain) for one posting collected "
                    "on 2026-11-10, its reason, and for an accepted posting the C1-C4 claims (US-based, Uses "
                    "<skill>, Sponsors visas, Remote) as computed then, labeled supported / contradicted / "
                    "insufficient with exact quotes. This is a stored rule verdict, not a fresh judgment of fit, "
                    "and the claim labels were not checked by hand. It reads only the saved v2 run and cannot "
                    "fetch new or updated postings."),
    "inputSchema": {
        "type": "object",
        "properties": {"posting_id": {
            "type": "string",
            "description": "system:board:id, e.g. greenhouse:faire:8806617002",
            "pattern": POSTING_ID.pattern}},
        "required": ["posting_id"],
        "additionalProperties": False,
    },
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True,
                    "openWorldHint": False},
}


def load_data(data_dir=DATA):
    results = json.loads((Path(data_dir) / "results.json").read_text(encoding="utf-8"))
    shortlist = json.loads((Path(data_dir) / "shortlist.json").read_text(encoding="utf-8"))
    by_id = {r["posting_id"]: r for r in results["results"]}
    claims = {e["posting_id"]: e for e in shortlist["shortlist"]}
    return results["filter"], by_id, claims


class Transcript:
    """Every message in both directions, timestamped. Lines before initialize are held until the client names itself."""

    def __init__(self, directory=TRANSCRIPTS, clock=None):
        self.directory = Path(directory)
        self.clock = clock or (lambda: datetime.datetime.now().astimezone())
        self.path = None
        self.pending = []

    def name(self, client_name):
        safe = re.sub(r"[^A-Za-z0-9_-]+", "-", str(client_name or "unknown"))[:40].strip("-") or "unknown"
        self.path = self.directory / f"{self.clock().date().isoformat()}-{safe}.jsonl"
        self._flush()

    def write(self, direction, raw=None, message=None):
        record = {"ts": self.clock().isoformat(timespec="milliseconds"), "pid": os.getpid(), "dir": direction}
        if message is not None:
            record["message"] = message
        else:
            record["raw"] = raw
        self.pending.append(record)
        if self.path:
            self._flush()

    def close(self):
        if self.path is None and self.pending:
            self.name("unknown")
        self._flush()

    def _flush(self):
        if not self.path or not self.pending:
            return
        self.directory.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as fh:
            for record in self.pending:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.pending = []


class Server:
    def __init__(self, data=None):
        self.filter_name, self.results, self.claims = data or load_data()
        self.initialized = False
        self.ready = False
        self.client = None

    def handle(self, message):
        """One parsed message in, one response dict or None (for a notification) out."""
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or not isinstance(message.get("method"), str):
            ident = message.get("id") if isinstance(message, dict) and isinstance(message.get("id"), (str, int)) else None
            return error(ident, -32600, "Invalid request")
        method, params = message["method"], message.get("params", {})
        if "id" not in message:
            if method == "notifications/initialized" and self.initialized:
                self.ready = True
            return None
        ident = message["id"]
        if method == "initialize":
            return self.initialize(ident, params)
        if method == "ping":
            return result(ident, {})
        if not self.initialized or not self.ready:
            return error(ident, -32000, "Server not ready: send initialize, then notifications/initialized")
        if method == "tools/list":
            return result(ident, {"tools": [TOOL]})
        if method == "tools/call":
            return self.call(ident, params)
        return error(ident, -32601, f"Method not found: {method}")

    def initialize(self, ident, params):
        if not isinstance(params, dict):
            return error(ident, -32602, "initialize params must be an object")
        requested = params.get("protocolVersion")
        self.client = (params.get("clientInfo") or {}).get("name") if isinstance(params.get("clientInfo"), dict) else None
        self.initialized = True
        version = requested if requested in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0]
        return result(ident, {"protocolVersion": version, "capabilities": {"tools": {"listChanged": False}},
                              "serverInfo": SERVER_INFO,
                              "instructions": ("Read-only except that the server appends every message to its own "
                                               "transcript log inside its folder. One tool: score_posting(posting_id), "
                                               "which returns a SAVED FILTER.md v2 verdict for postings collected on "
                                               "2026-11-10, not a fresh judgment of fit.")})

    def call(self, ident, params):
        if not isinstance(params, dict) or not isinstance(params.get("name"), str):
            return error(ident, -32602, "tools/call params must name a tool")
        if params["name"] != TOOL["name"]:
            return error(ident, -32602, f"Unknown tool: {params['name']}")
        args = params.get("arguments", {})
        if not isinstance(args, dict) or set(args) != {"posting_id"} or not isinstance(args["posting_id"], str):
            return error(ident, -32602, "arguments must be exactly {\"posting_id\": <string>}")
        pid = args["posting_id"]
        if not POSTING_ID.match(pid):
            return tool_error(ident, f"Refused: {pid!r} is not a posting id of the form system:board:id. "
                                     "Nothing was read.")
        row = self.results.get(pid)
        if row is None:
            return tool_error(ident, f"No posting {pid} in the saved FILTER.md v2 run.")
        out = {"filter": self.filter_name, "posting_id": pid, "title": row["title"], "location": row["location"],
               "verdict": row["verdict"], "abstain": row["abstain"], "reason": row["reason"],
               "url": row["url"], "claims": None}
        if pid in self.claims:
            out["rank"] = self.claims[pid]["rank"]
            out["claims"] = [{k: c[k] for k in ("claim", "text", "label", "field", "quote")}
                             for c in self.claims[pid]["claims"]]
        else:
            out["claims_note"] = "Claims are labeled only for accepted postings."
        return result(ident, {"content": [{"type": "text", "text": json.dumps(out, ensure_ascii=False, indent=2)}],
                              "structuredContent": out, "isError": False})


def result(ident, value):
    return {"jsonrpc": "2.0", "id": ident, "result": value}


def error(ident, code, text):
    return {"jsonrpc": "2.0", "id": ident, "error": {"code": code, "message": text}}


def tool_error(ident, text):
    return result(ident, {"content": [{"type": "text", "text": text}], "isError": True})


def serve(stdin, stdout, server=None, transcript=None):
    server = server or Server()
    transcript = transcript or Transcript()
    try:
        for raw in stdin:
            line = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else raw
            line = line.rstrip("\r\n")
            if not line.strip():
                continue
            transcript.write("in", raw=line)
            try:
                message = json.loads(line)
            except ValueError:
                response = error(None, -32700, "Parse error")
            else:
                was_initialized = server.initialized
                response = server.handle(message)
                if server.initialized and not was_initialized and transcript.path is None:
                    transcript.name(server.client)
            if response is not None:
                transcript.write("out", message=response)
                data = (json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8")
                if hasattr(stdout, "buffer"):
                    stdout.buffer.write(data)
                else:
                    stdout.write(data.decode("utf-8"))
                stdout.flush()
    finally:
        transcript.close()


def main():
    serve(sys.stdin.buffer, sys.stdout)


if __name__ == "__main__":
    main()
