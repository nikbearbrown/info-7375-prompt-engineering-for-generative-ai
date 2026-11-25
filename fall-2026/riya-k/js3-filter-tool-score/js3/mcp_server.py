"""A Model Context Protocol tool server, from scratch: JSON-RPC 2.0 over stdio, one JSON message per line.

    python3 -m js3.mcp_server                      # speak MCP on stdin/stdout
    JS3_MCP_TRANSCRIPT=transcripts/x.jsonl python3 -m js3.mcp_server   # also record both directions

Methods: initialize, notifications/initialized, ping, tools/list, tools/call. One tool: score_posting.

What it can touch (TOOLSERVER.md has the evaluation):
  - reads: the JS2 corpus files and filters/filter-v1.json, nothing else;
  - writes: only the transcript file, and only if it is inside this folder's transcripts/ directory;
  - network: none. It never applies, emails, messages, logs in, or changes any data.
"""

import json
import os
import sys
import time
from pathlib import Path

from . import corpus, evidence, filter as F

ROOT = Path(__file__).resolve().parent.parent
SUPPORTED_VERSIONS = ["2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"]
SERVER_INFO = {"name": "js3-score-posting", "version": "1.0.0"}
BOARDS = [f"{s}:{b}" for s, b, _ in corpus.BOARDS]

TOOL = {
    "name": "score_posting",
    "title": "Score one saved job posting with filter v1",
    "description": ("Apply Riya's FILTER.md v1 to ONE posting from the saved JS2 corpus (2026-11-10). Returns the "
                    "decision (kept / rejected / cannot_tell), the score and which words counted, the gates that "
                    "failed, and each claim labeled supported / contradicted / insufficient with the quoted text. "
                    "Read-only and offline: it does not fetch anything, and it cannot apply to, email or contact anyone."),
    "inputSchema": {
        "type": "object",
        "properties": {
            "board": {"type": "string", "enum": BOARDS, "description": "system:board, e.g. greenhouse:anthropic"},
            "id": {"type": "string", "description": "posting id as the board gives it"},
        },
        "required": ["board", "id"],
        "additionalProperties": False,
    },
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
}

_state = {"posts": None, "flt": None}


def _posts():
    if _state["posts"] is None:
        _state["posts"] = corpus.by_key(corpus.load())
        _state["flt"] = F.load_filter()
    return _state["posts"], _state["flt"]


def score_posting(args):
    if not isinstance(args, dict) or set(args) - {"board", "id"} or not {"board", "id"} <= set(args):
        return _tool_error("arguments must be exactly {board, id}")
    board, pid = args["board"], args["id"]
    if board not in BOARDS:
        return _tool_error(f"unknown board '{board}'; known: {BOARDS}. Boards with no data: {corpus.MISSING}")
    posts, flt = _posts()
    p = posts.get((board, str(pid)))
    if p is None:
        return _tool_error(f"no posting {pid} on {board} in the 2026-11-10 corpus. I cannot tell anything about it.")
    rec = F.apply(p, flt, evidence.claims)
    rec["claims"] = evidence.claims(p, flt)
    return {"content": [{"type": "text", "text": json.dumps(rec, ensure_ascii=False)}], "isError": False}


def _tool_error(msg):
    return {"content": [{"type": "text", "text": msg}], "isError": True}


def handle(msg):
    """One JSON-RPC message in -> one response (or None for a notification)."""
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or "method" not in msg:
        return {"jsonrpc": "2.0", "id": msg.get("id") if isinstance(msg, dict) else None,
                "error": {"code": -32600, "message": "Invalid Request"}}
    mid, method, params = msg.get("id"), msg["method"], msg.get("params") or {}
    if mid is None:  # notification (e.g. notifications/initialized): no reply
        return None
    if method == "initialize":
        asked = params.get("protocolVersion")
        result = {"protocolVersion": asked if asked in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0],
                  "capabilities": {"tools": {"listChanged": False}}, "serverInfo": SERVER_INFO,
                  "instructions": "One read-only tool over a saved, offline corpus. Decisions are records from a "
                                  "written filter; the judgment that a posting is worth applying to stays with the human."}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": [TOOL]}
    elif method == "tools/call":
        if params.get("name") != "score_posting":
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": f"Unknown tool: {params.get('name')}"}}
        result = score_posting(params.get("arguments"))
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Method not found: {method}"}}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def _transcript():
    path = os.environ.get("JS3_MCP_TRANSCRIPT")
    if not path:
        return None
    p = (ROOT / path).resolve() if not os.path.isabs(path) else Path(path).resolve()
    allowed = (ROOT / "transcripts").resolve()
    if allowed not in p.parents:
        sys.stderr.write(f"refusing to write transcript outside {allowed}: {p}\n")
        return None
    p.parent.mkdir(parents=True, exist_ok=True)
    return open(p, "a")


def main():
    log = _transcript()

    def record(direction, line):
        if log:
            log.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "dir": direction,
                                  "msg": line}, ensure_ascii=False) + "\n")
            log.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        record("client->server", line)
        try:
            msg = json.loads(line)
        except ValueError:
            resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        else:
            try:
                resp = handle(msg)
            except Exception as e:  # never crash the session; report it
                resp = {"jsonrpc": "2.0", "id": msg.get("id"), "error": {"code": -32603, "message": f"Internal error: {e}"}}
        if resp is not None:
            out = json.dumps(resp, ensure_ascii=False)
            record("server->client", out)
            sys.stdout.write(out + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
