"""Minimal MCP tool server over stdio (JSON-RPC 2.0, one message per line).

Usage (from the repo root):
    python3 -m js3.mcp_server

Handles three methods:
- initialize  -> serverInfo {name, version}, capabilities {}
- tools/list  -> one tool, score_posting(title)
- tools/call  -> looks the title up in output/filter_results.json

Matching is exact after trimming and collapsing whitespace, ignoring case.
It does not do substring matching: "Data Engineer" would otherwise match
"Specialist Solutions Architect - Data Engineering".

Score: there is no graded scorer yet, so the score is derived from the filter
result: 100 if the posting passed the filter, 0 if it was rejected or not found.

Errors:
- unknown method                      -> -32601 Method not found
- bad tools/call params / unknown tool -> -32602 Invalid params
- anything else (bad JSON, non-object) -> -32603 Internal error
Messages without an "id" are JSON-RPC notifications and get no response.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "output" / "filter_results.json"

SERVER_NAME = "job-search-agent-3"
SERVER_VERSION = "0.1.0"
DEFAULT_PROTOCOL_VERSION = "2025-06-18"

TOOL = {
    "name": "score_posting",
    "description": (
        "Score a job posting title for relevance to an ML/data engineering job search. "
        "Returns a score 0-100 and a reason."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {"title": {"type": "string", "description": "The job posting title."}},
        "required": ["title"],
    },
}


class RpcError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _norm(text: Any) -> str:
    return " ".join(str(text or "").split()).lower()


def score_posting(title: str, results_path: Path = RESULTS) -> dict:
    with Path(results_path).open("r", encoding="utf-8") as f:
        results = json.load(f)
    wanted = _norm(title)
    for board, rows in results.items():
        for r in rows:
            if _norm(r.get("title")) == wanted:
                return {
                    "found": True,
                    "board": board,
                    "id": r.get("id"),
                    "title": " ".join(str(r.get("title", "")).split()),
                    "score": 100 if r.get("passed") else 0,
                    "passed": r.get("passed"),
                    "reason": r.get("reason"),
                    "matched_words": r.get("matched_words"),
                }
    return {"found": False, "title": title, "score": 0, "reason": "not found in filter results"}


def _initialize(params: dict) -> dict:
    return {
        "protocolVersion": params.get("protocolVersion") or DEFAULT_PROTOCOL_VERSION,
        "capabilities": {},
        "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
    }


def _tools_call(params: dict, results_path: Path) -> dict:
    if params.get("name") != TOOL["name"]:
        raise RpcError(-32602, f"Unknown tool: {params.get('name')!r}")
    args = params.get("arguments")
    if not isinstance(args, dict) or not isinstance(args.get("title"), str):
        raise RpcError(-32602, "Invalid params: 'title' (string) is required")
    result = score_posting(args["title"], results_path)
    return {
        "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
        "structuredContent": result,
        "isError": False,
    }


def handle_line(line: str, results_path: Path = RESULTS) -> dict | None:
    """Return the JSON-RPC response for one input line, or None for no reply."""
    msg_id = None
    try:
        msg = json.loads(line)
        if not isinstance(msg, dict):
            raise ValueError("message must be a JSON object")
        msg_id = msg.get("id")
        if "id" not in msg:
            return None  # notification
        method = msg.get("method")
        params = msg.get("params") or {}
        if not isinstance(params, dict):
            raise RpcError(-32602, "Invalid params: params must be an object")
        if method == "initialize":
            result = _initialize(params)
        elif method == "tools/list":
            result = {"tools": [TOOL]}
        elif method == "tools/call":
            result = _tools_call(params, results_path)
        else:
            raise RpcError(-32601, "Method not found")
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}
    except RpcError as e:
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": e.code, "message": e.message}}
    except Exception as e:  # never crash on bad input
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32603, "message": f"Internal error: {type(e).__name__}: {e}"},
        }


def serve(stdin=sys.stdin, stdout=sys.stdout, results_path: Path = RESULTS) -> None:
    for line in stdin:
        if not line.strip():
            continue
        response = handle_line(line, results_path)
        if response is not None:
            stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            stdout.flush()


if __name__ == "__main__":
    serve()
