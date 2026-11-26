"""js3-postings: a read-only MCP tool server, written from scratch (no MCP SDK).

Transport: stdio, one JSON-RPC 2.0 message per line (the MCP stdio transport).
Methods handled: initialize, notifications/initialized, ping, tools/list, tools/call.
Every message in both directions is appended to mcp/logs/transcript-<date>.jsonl.

Tools (both read-only; nothing here writes, sends or fetches outside this folder):
  search_postings(query, limit)   title search over data/postings.jsonl
  score_posting(key, version)     run filter/filter-<version>.json on one posting, return the claims
The only file this server writes is its own transcript log under mcp/logs/.
"""
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from agent import filter as F  # noqa: E402

PROTOCOL = "2025-06-18"
DATA = os.path.join(ROOT, "data", "postings.jsonl")
FILTER_DIR = os.path.join(ROOT, "filter")
LOG_DIR = os.environ.get("JS3_MCP_LOG_DIR") or os.path.join(ROOT, "mcp", "logs")
VERSION_RE = re.compile(r"^v[0-9][a-z0-9]{0,3}$")
MAX_LIMIT = 20

TOOLS = [
    {"name": "search_postings",
     "description": "Search the saved job postings (a local snapshot of 1,595 postings) by words in the title. "
                    "Read-only. Returns key, company, title and location for at most `limit` postings.",
     "inputSchema": {"type": "object", "properties": {
         "query": {"type": "string", "description": "words that must all appear in the title (case-insensitive)"},
         "limit": {"type": "integer", "minimum": 1, "maximum": MAX_LIMIT, "default": 10}},
         "required": ["query"], "additionalProperties": False},
     "annotations": {"readOnlyHint": True, "openWorldHint": False}},
    {"name": "score_posting",
     "description": "Score one saved posting with a versioned filter (filter/filter-<version>.json). Read-only. "
                    "Returns the decision (keep / reject / cannot tell) and every claim with its label "
                    "(supported / contradicted / insufficient) and the evidence quoted from the posting.",
     "inputSchema": {"type": "object", "properties": {
         "key": {"type": "string", "description": "posting key from search_postings, e.g. greenhouse/pinterest/123"},
         "version": {"type": "string", "description": "filter version, e.g. v1 or v2", "default": "v2"}},
         "required": ["key"], "additionalProperties": False},
     "annotations": {"readOnlyHint": True, "openWorldHint": False}},
]

_postings = None


def postings():
    global _postings
    if _postings is None:
        _postings = {}
        with open(DATA, encoding="utf-8") as fh:
            for line in fh:
                p = json.loads(line)
                _postings[p["key"]] = p
    return _postings


def log(direction, msg):
    os.makedirs(LOG_DIR, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc)
    with open(os.path.join(LOG_DIR, f"transcript-{now:%Y-%m-%d}.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"t": now.isoformat(timespec="seconds"), "dir": direction, "msg": msg},
                            ensure_ascii=False) + "\n")


def text_result(obj, is_error=False):
    return {"content": [{"type": "text", "text": json.dumps(obj, ensure_ascii=False, indent=1)}], "isError": is_error}


def search_postings(args):
    query = str(args.get("query", "")).strip()
    limit = args.get("limit", 10)
    if not query:
        return text_result({"error": "query is empty"}, True)
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_LIMIT:
        return text_result({"error": f"limit must be an integer from 1 to {MAX_LIMIT}"}, True)
    words = query.lower().split()
    hits = [p for p in postings().values() if all(w in p["title"].lower() for w in words)]
    return text_result({"total_matches": len(hits), "returned": min(limit, len(hits)),
                        "postings": [{"key": p["key"], "company": p["board"], "title": p["title"],
                                      "location": p["location"]} for p in hits[:limit]]})


def score_posting(args):
    key, version = str(args.get("key", "")), str(args.get("version", "v2"))
    if not VERSION_RE.match(version):
        return text_result({"error": "version must look like v1, v2 or v2a"}, True)
    path = os.path.join(FILTER_DIR, f"filter-{version}.json")
    if not os.path.isfile(path):
        return text_result({"error": f"no filter version {version}"}, True)
    p = postings().get(key)
    if p is None:
        return text_result({"error": f"no saved posting with key {key!r}"}, True)
    r = F.score(p, F.load(path))
    return text_result({"key": key, "title": p["title"], "location": p["location"], "url": p["url"],
                        "filter": version, "score": r["score"], "decision": r["decision"],
                        "abstain_reasons": r["abstain_reasons"], "claims": r["claims"]})


HANDLERS = {"search_postings": search_postings, "score_posting": score_posting}


def handle(msg):
    method, mid = msg.get("method"), msg.get("id")
    if mid is None:  # a notification (e.g. notifications/initialized): no reply
        return None
    if method == "initialize":
        result = {"protocolVersion": PROTOCOL, "capabilities": {"tools": {"listChanged": False}},
                  "serverInfo": {"name": "js3-postings", "version": "1.0.0"},
                  "instructions": "Read-only access to a saved snapshot of job postings and the JS3 filter."}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = msg.get("params") or {}
        fn = HANDLERS.get(params.get("name"))
        if fn is None:
            return {"jsonrpc": "2.0", "id": mid,
                    "error": {"code": -32602, "message": f"unknown tool {params.get('name')!r}"}}
        args = params.get("arguments") or {}
        if not isinstance(args, dict):
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": "arguments must be an object"}}
        try:
            result = fn(args)
        except Exception as e:  # report the failure to the client, never crash the session
            result = text_result({"error": f"{type(e).__name__}: {e}"}, True)
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {method}"}}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
            log("server->client", reply)
            sys.stdout.write(json.dumps(reply) + "\n")
            sys.stdout.flush()
            continue
        log("client->server", msg)
        reply = handle(msg)
        if reply is not None:
            log("server->client", reply)
            sys.stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
