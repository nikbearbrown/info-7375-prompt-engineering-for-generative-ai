"""A minimal MCP-style tool server, written from scratch with the standard library (JS3 Step 5).

Transport: stdio, one JSON-RPC 2.0 message per line (no embedded newlines). Nothing but protocol messages goes to stdout;
logs go to stderr. Methods: initialize, notifications/initialized, ping, tools/list, tools/call. One tool: score_posting.

    python3 -B -m jsagent.mcp_server               # serve on stdin/stdout

Start it with -B: otherwise the Python interpreter itself writes a bytecode cache (.pyc), and the process is no longer
write-free even though the tool's code never writes (found by the audit trace, second dry run, 2026-11-25).

The tool's declared behavior (in TOOL below) is checked against its actual behavior by tests/test_js3_mcp.py and by the
audit-hook trace in evidence/mcp/ (scripts/mcp_transcript.py installs jsagent/audithook.py before this module loads).
"""
import json
import re
import sys

from . import filter as flt, providers, shortlist, snapshot

PROTOCOL_VERSIONS = ["2025-06-18", "2025-03-26", "2024-11-05"]  # newest first
SERVER_INFO = {"name": "js3-score-posting", "title": "JS3 posting scorer", "version": "1.0.0"}
POSTING_ID_RE = re.compile(r"^[A-Za-z0-9-]{1,64}$")

TOOL = {
    "name": "score_posting",
    "title": "Score one saved job posting",
    "description": (
        "Scores one job posting from the saved 2026-11-25 snapshot against FILTER.md v1.2 for the fictional persona Evan "
        "Gordon. Returns the bucket (kept / rejected / cannot_tell), the 0-100 score and its parts, each rule's result with "
        "the quoted evidence, and every claim labeled supported / contradicted / insufficient. Reads only the saved snapshot "
        "and the persona file; makes no network requests, writes no files, and gives the same answer for the same input. "
        "If the board was not observed or the posting is not in the snapshot, it says so instead of guessing. It does not "
        "decide whether a job is worth applying to."),
    "inputSchema": {
        "type": "object",
        "properties": {
            "board": {"type": "string", "pattern": providers.BOARD_RE.pattern,
                      "description": "Board name as in config/boards.json, e.g. 'samsara' or 'palantir'"},
            "posting_id": {"type": "string", "pattern": POSTING_ID_RE.pattern,
                           "description": "The posting's id on that board (Greenhouse number or Lever UUID), as a string"},
        },
        "required": ["board", "posting_id"],
        "additionalProperties": False,
    },
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
}


class RpcError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code, self.message = code, message


class Server:
    def __init__(self, postings=None, outcomes=None):
        self._postings, self._outcomes = postings, outcomes
        self._index = None
        self.initialized = False

    # ------------------------------------------------------------------ data
    def _load(self):
        if self._index is None:
            if self._postings is None:
                self._postings, self._outcomes = snapshot.load()
            self._index = {(p["board"], p["id"]): p for p in self._postings}
        return self._index

    # ------------------------------------------------------------------ the tool
    def score_posting(self, board, posting_id):
        index = self._load()
        outcome = self._outcomes.get(board)
        if outcome is None:
            return True, f"Board '{board}' is not one of the snapshot's boards: {sorted(self._outcomes)}."
        if outcome != "observed":
            return True, (f"Board '{board}' was {outcome} in the 2026-11-25 snapshot, so I cannot tell anything about its "
                          f"postings, including whether any would fit.")
        p = index.get((board, posting_id))
        if p is None:
            return True, f"Posting '{posting_id}' is not in the snapshot for board '{board}'. I cannot tell anything about it."
        r = flt.evaluate(p)
        out = {k: r[k] for k in ("board", "id", "title", "location", "url", "filter_version", "bucket", "score",
                                 "score_parts", "rules", "missing", "topic_words", "years", "years_phrase", "visa",
                                 "closest_call")}
        out["snapshot"] = "snapshot/2026-11-25"
        out["claims"] = shortlist.claims(r)
        return False, out

    def _tools_call(self, params):
        name, args = params.get("name"), params.get("arguments")
        if name != TOOL["name"]:
            raise RpcError(-32602, f"Unknown tool: {name!r}")
        if not isinstance(args, dict):
            raise RpcError(-32602, "arguments must be an object")
        extra = set(args) - set(TOOL["inputSchema"]["properties"])
        if extra:
            raise RpcError(-32602, f"unexpected arguments: {sorted(extra)}")
        board, pid = args.get("board"), args.get("posting_id")
        if not isinstance(board, str) or not providers.BOARD_RE.match(board):
            raise RpcError(-32602, "board must be a string matching " + providers.BOARD_RE.pattern)
        if not isinstance(pid, str) or not POSTING_ID_RE.match(pid):
            raise RpcError(-32602, "posting_id must be a string matching " + POSTING_ID_RE.pattern)
        is_error, out = self.score_posting(board, pid)
        if is_error:
            return {"content": [{"type": "text", "text": out}], "isError": True}
        return {"content": [{"type": "text", "text": json.dumps(out, sort_keys=True)}], "structuredContent": out,
                "isError": False}

    # ------------------------------------------------------------------ JSON-RPC
    def handle(self, msg):
        """One parsed message in, one response dict out (or None for a notification)."""
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
            return _error(msg.get("id") if isinstance(msg, dict) else None, -32600, "Invalid Request")
        method, rid, params = msg["method"], msg.get("id"), msg.get("params") or {}
        if "id" not in msg:  # notification: never answered
            if method == "notifications/initialized":
                self.initialized = True
            return None
        try:
            if method == "initialize":
                asked = params.get("protocolVersion")
                self.initialized = True  # the client's notifications/initialized follows; tools are usable after this reply
                return _result(rid, {"protocolVersion": asked if asked in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0],
                                     "capabilities": {"tools": {"listChanged": False}}, "serverInfo": SERVER_INFO,
                                     "instructions": "One read-only tool, score_posting. The judgment about a job stays the user's."})
            if method == "ping":
                return _result(rid, {})
            if method in ("tools/list", "tools/call") and not self.initialized:
                raise RpcError(-32002, "Server not initialized: send initialize first")
            if method == "tools/list":
                return _result(rid, {"tools": [TOOL]})
            if method == "tools/call":
                return _result(rid, self._tools_call(params))
            raise RpcError(-32601, f"Method not found: {method}")
        except RpcError as e:
            return _error(rid, e.code, e.message)

    def handle_line(self, line):
        try:
            msg = json.loads(line)
        except ValueError:
            return _error(None, -32700, "Parse error")
        if isinstance(msg, list):
            return _error(None, -32600, "Batches are not supported (removed in protocol 2025-06-18)")
        return self.handle(msg)


def _result(rid, result):
    return {"jsonrpc": "2.0", "id": rid, "result": result}


def _error(rid, code, message):
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}}


def main():
    server = Server()
    for line in sys.stdin:
        if not line.strip():
            continue
        resp = server.handle_line(line)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
