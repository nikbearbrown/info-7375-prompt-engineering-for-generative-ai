"""js3-postings: a Model Context Protocol tool server, written from scratch.

Transport: stdio, JSON-RPC 2.0, one JSON message per line (MCP stdio).
Methods: initialize, notifications/initialized, ping, tools/list, tools/call.
Everything else gets JSON-RPC error -32601. Logs go to stderr only;
stdout carries protocol messages and nothing else.

Tools (registry TOOLS below):
    search_postings   read-only search over the frozen JS3 corpus

What it can touch: it reads the saved raw responses of one live run inside
this folder (CORPUS_DIR, fixed in code, resolved from this file's location).
It takes no path argument, opens no socket and writes no file.

    python3 -B mcp/server.py
"""

import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(os.path.realpath(__file__)).parent
JS3 = HERE.parent
sys.path.insert(0, str(JS3))

from agent import corpus  # noqa: E402

SERVER_INFO = {"name": "js3-postings", "version": "0.1.0"}
SUPPORTED_VERSIONS = ["2025-06-18", "2025-03-26", "2024-11-05"]
CORPUS_DIR = (JS3 / "runs" / "2026-11-24T220432Z-live").resolve()

PARSE_ERROR, INVALID_REQUEST = -32700, -32600
METHOD_NOT_FOUND, INVALID_PARAMS, INTERNAL_ERROR = -32601, -32602, -32603


def log(*a):
    print("[js3-postings]", *a, file=sys.stderr, flush=True)


class ParamsError(ValueError):
    """Arguments don't fit the tool's inputSchema -> JSON-RPC -32602."""


# ---------------------------------------------------------------- corpus

_CACHE = {}


def _corpus():
    if "posts" not in _CACHE:
        # Containment: the corpus dir must sit inside this js3 folder.
        if JS3.resolve() not in CORPUS_DIR.parents:
            raise RuntimeError("corpus dir outside the js3 folder; refusing")
        _CACHE["posts"] = corpus.load(CORPUS_DIR)
        log(f"loaded {len(_CACHE['posts'])} postings from {CORPUS_DIR.name}")
    return _CACHE["posts"]


def _word(term):
    body = r"\s+".join(re.escape(p) for p in term.split())
    return re.compile(r"(?<!\w)" + body + r"(?!\w)", re.IGNORECASE)


# ---------------------------------------------------------------- tools

def search_postings(args):
    query = args.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ParamsError("'query' must be a non-empty string")
    if len(query) > 200:
        raise ParamsError("'query' longer than 200 characters")
    board = args.get("board")
    if board is not None and not isinstance(board, str):
        raise ParamsError("'board' must be a string like 'greenhouse/databricks'")
    limit = args.get("limit", 10)
    if isinstance(limit, bool) or not isinstance(limit, int) \
            or not 1 <= limit <= 20:
        raise ParamsError("'limit' must be an integer from 1 to 20")
    extra = set(args) - {"query", "board", "limit"}
    if extra:
        raise ParamsError(f"unknown argument(s): {sorted(extra)}")

    pat = _word(query.strip())
    posts = _corpus()
    if board is not None:
        posts = [p for p in posts if f"{p['ats']}/{p['board']}" == board]
        if not posts:
            raise ParamsError(f"no board {board!r} in the corpus")
    hits = []
    for p in posts:
        where = [f for f in ("title", "text") if pat.search(p[f] or "")]
        if where:
            hits.append({"key": p["key"], "title": p["title"],
                         "locations": p["locations"], "url": p["url"],
                         "matched_in": where})
    return {"count_total": len(hits), "results": hits[:limit]}


TOOLS = {
    "search_postings": {
        "fn": search_postings,
        "spec": {
            "name": "search_postings",
            "title": "Search saved job postings",
            "description": (
                "Read-only search over the job postings saved by the JS3 "
                "collection run of 2026-11-24 (6 public boards, 3,117 "
                "postings). Matches a whole word or phrase, ignoring case, "
                "in the posting title and text. Fetches nothing live."),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "minLength": 1,
                              "maxLength": 200,
                              "description": "word or phrase to find"},
                    "board": {"type": "string",
                              "description": "optional 'ats/board', e.g. "
                                             "'greenhouse/databricks'"},
                    "limit": {"type": "integer", "minimum": 1,
                              "maximum": 20, "default": 10},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
            "annotations": {"readOnlyHint": True, "openWorldHint": False},
        },
    },
}


# ---------------------------------------------------------------- protocol

def _error(id_, code, message):
    return {"jsonrpc": "2.0", "id": id_,
            "error": {"code": code, "message": message}}


def _result(id_, result):
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def handle(msg):
    """One parsed message in, one response dict out (or None for a
    notification)."""
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" \
            or not isinstance(msg.get("method"), str):
        return _error(msg.get("id") if isinstance(msg, dict) else None,
                      INVALID_REQUEST, "not a JSON-RPC 2.0 request")
    method, id_ = msg["method"], msg.get("id")
    params = msg.get("params") or {}
    is_notification = "id" not in msg

    if is_notification:
        log(f"notification {method}")
        return None

    if not isinstance(params, dict):
        return _error(id_, INVALID_PARAMS, "params must be an object")

    if method == "initialize":
        asked = params.get("protocolVersion")
        version = asked if asked in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0]
        return _result(id_, {
            "protocolVersion": version,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
            "instructions": "Read-only search over saved job postings. "
                            "Nothing is fetched live and nothing is written."})
    if method == "ping":
        return _result(id_, {})
    if method == "tools/list":
        return _result(id_, {"tools": [t["spec"] for t in TOOLS.values()]})
    if method == "tools/call":
        name, args = params.get("name"), params.get("arguments") or {}
        if not isinstance(args, dict):
            return _error(id_, INVALID_PARAMS, "arguments must be an object")
        tool = TOOLS.get(name)
        if tool is None:
            return _result(id_, {"isError": True, "content": [
                {"type": "text", "text": f"unknown tool {name!r}"}]})
        try:
            out = tool["fn"](args)
        except ParamsError as e:
            return _error(id_, INVALID_PARAMS, str(e))
        except Exception as e:  # tool failure is a result, not a crash
            log(f"tool {name} failed: {e!r}")
            return _result(id_, {"isError": True, "content": [
                {"type": "text", "text": f"tool error: {e}"}]})
        return _result(id_, {
            "content": [{"type": "text", "text": json.dumps(out)}],
            "structuredContent": out, "isError": False})
    return _error(id_, METHOD_NOT_FOUND, f"method not found: {method}")


def main():
    log(f"starting, protocol {SUPPORTED_VERSIONS[0]}")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            reply = _error(None, PARSE_ERROR, f"parse error: {e}")
        else:
            try:
                reply = handle(msg)
            except Exception as e:
                log(f"internal error: {e!r}")
                reply = _error(msg.get("id") if isinstance(msg, dict)
                               else None, INTERNAL_ERROR, "internal error")
        if reply is not None:
            sys.stdout.write(json.dumps(reply) + "\n")
            sys.stdout.flush()
    log("stdin closed, exiting")


if __name__ == "__main__":
    main()
