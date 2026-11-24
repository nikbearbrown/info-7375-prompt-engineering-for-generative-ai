"""A read-only MCP tool server over one saved run, written from scratch (stdlib only).

Transport: stdio, one JSON-RPC 2.0 message per line (MCP stdio transport).
Methods: initialize, notifications/initialized, ping, tools/list, tools/call.

    python3 -m agent.mcp_server          # run from js3-filter-tool-score/

What it can touch:
  - reads   evidence/run-20261123-185425Z/raw/*.json, examples/persona.example.json
  - writes  ONE file, the call log (default out/mcp-calls.jsonl; JS3_MCP_LOG may move it, but
            only to somewhere inside out/). Nothing else is written.
  - no network, no subprocess, no tool that sends, applies, emails or changes anything.
Every tool is a pure lookup over data already on disk (readOnlyHint, closed world).
Logs go to the log file and stderr; stdout carries only protocol messages.
"""

from __future__ import annotations

import json
import os
import sys
import time
import traceback
from pathlib import Path

from agent import filter as F
from agent import shortlist as SL
from agent.postings import load_run

ROOT = Path.cwd().resolve()
NAME, VERSION = "js3-job-filter", "0.1.0"
SUPPORTED = ["2025-06-18", "2025-03-26", "2024-11-05"]
MAX_LIMIT = 50


class ToolError(Exception):
    """A problem with the call (bad uid, bad argument): returned as isError, not a protocol error."""


# --- data, loaded once --------------------------------------------------------
POSTINGS = {p["uid"]: p for p in load_run(F.RUN)}
SKILLS = json.loads(Path(F.PERSONA).read_text(encoding="utf-8"))["skills"]


def _posting(args) -> dict:
    uid = args.get("uid")
    if not isinstance(uid, str) or not uid:
        raise ToolError("'uid' is required, e.g. 'affirm:8032173003'")
    if uid not in POSTINGS:
        raise ToolError(f"no posting {uid!r} in run {F.RUN}")
    return POSTINGS[uid]


# --- tools ----------------------------------------------------------------------
def search_postings(args) -> dict:
    q = args.get("query")
    if not isinstance(q, str) or not q.strip():
        raise ToolError("'query' is required (a word or phrase to find in titles)")
    limit = args.get("limit", 10)
    if not isinstance(limit, int) or not 1 <= limit <= MAX_LIMIT:
        raise ToolError(f"'limit' must be an integer from 1 to {MAX_LIMIT}")
    board = args.get("board")
    ql = q.lower()
    hits = [p for p in POSTINGS.values() if ql in p["title"].lower() and (board is None or p["board"] == board)]
    return {"run": F.RUN, "query": q, "board": board, "total": len(hits),
            "results": [{"uid": p["uid"], "board": p["board"], "title": p["title"], "location": p["location"]}
                        for p in hits[:limit]]}


def get_posting(args) -> dict:
    p = _posting(args)
    return {k: p[k] for k in ("uid", "board", "title", "location", "url", "updated", "text")}


def judge_posting(args) -> dict:
    return F.judge(_posting(args), SKILLS)


def shortlist_entry(args) -> dict:
    p = _posting(args)
    d = F.judge(p, SKILLS)
    e = SL.entry([p], SKILLS, d["score"])
    e["filter_keep"] = d["keep"]
    return e


UID = {"type": "string", "description": "Posting id '<board>:<id>', e.g. 'affirm:8032173003'."}
READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
TOOLS = {
    "search_postings": (search_postings, {
        "description": "Find postings in the saved Nov 23, 2026 run whose title contains a phrase (case-insensitive). "
                       "Searches only robinhood, affirm and wealthfront as collected; no live requests.",
        "inputSchema": {"type": "object", "properties": {
            "query": {"type": "string", "description": "Phrase to find in the title."},
            "board": {"type": "string", "enum": ["robinhood", "affirm", "wealthfront"]},
            "limit": {"type": "integer", "minimum": 1, "maximum": MAX_LIMIT, "default": 10}},
            "required": ["query"], "additionalProperties": False}}),
    "get_posting": (get_posting, {
        "description": "Return one posting's title, location, URL and full plain text from the saved run.",
        "inputSchema": {"type": "object", "properties": {"uid": UID}, "required": ["uid"],
                        "additionalProperties": False}}),
    "judge_posting": (judge_posting, {
        "description": "Run the FILTER.md v1.2 filter on one posting for the fictional persona Sam Rivera "
                       "(new grad SWE, US). Returns keep, score, gates, rule points, years and 'cannot tell' fields.",
        "inputSchema": {"type": "object", "properties": {"uid": UID}, "required": ["uid"],
                        "additionalProperties": False}}),
    "shortlist_entry": (shortlist_entry, {
        "description": "Five claims about one posting (role, years, entry level, US, skill), each labeled supported / "
                       "contradicted / insufficient with verbatim quotes, plus which list it would go in.",
        "inputSchema": {"type": "object", "properties": {"uid": UID}, "required": ["uid"],
                        "additionalProperties": False}}),
}


def tool_list() -> list[dict]:
    return [{"name": n, "title": n.replace("_", " "), **spec, "annotations": READ_ONLY} for n, (_, spec) in TOOLS.items()]


# --- protocol -------------------------------------------------------------------
class RpcError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code, self.message = code, message


def handle(msg: dict, log) -> dict | None:
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
        raise RpcError(-32600, "invalid request")
    method, params = msg["method"], msg.get("params") or {}
    is_note = "id" not in msg
    t0 = time.time()
    entry = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "method": method}

    if method == "initialize":
        asked = params.get("protocolVersion")
        result = {"protocolVersion": asked if asked in SUPPORTED else SUPPORTED[0],
                  "capabilities": {"tools": {"listChanged": False}},
                  "serverInfo": {"name": NAME, "version": VERSION},
                  "instructions": "Read-only lookups over one saved job-board run (Nov 23, 2026). "
                                  "Nothing here applies, sends, or changes anything."}
        entry["client"] = params.get("clientInfo")
    elif method.startswith("notifications/"):
        result = None
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": tool_list()}
    elif method == "tools/call":
        name, args = params.get("name"), params.get("arguments") or {}
        entry.update(tool=name, arguments=args)
        if name not in TOOLS:
            log({**entry, "error": "unknown tool"})
            raise RpcError(-32602, f"unknown tool: {name!r}")
        try:
            data = TOOLS[name][0](args)
            result = {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}],
                      "structuredContent": data, "isError": False}
        except ToolError as e:
            result = {"content": [{"type": "text", "text": str(e)}], "isError": True}
        entry["is_error"] = result["isError"]
    else:
        raise RpcError(-32601, f"method not found: {method}")

    entry["ms"] = round((time.time() - t0) * 1000, 1)
    log(entry)
    return None if is_note else {"jsonrpc": "2.0", "id": msg["id"], "result": result}


def log_path() -> Path:
    p = Path(os.environ.get("JS3_MCP_LOG", "out/mcp-calls.jsonl"))
    p = (ROOT / p).resolve() if not p.is_absolute() else p.resolve()
    out = (ROOT / "out").resolve()
    if out not in p.parents:
        raise SystemExit(f"refusing to log to {p}: the log must be inside {out}")
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def main() -> int:
    path = log_path()
    with path.open("a", encoding="utf-8") as lf:
        def log(row):
            lf.write(json.dumps(row, ensure_ascii=False) + "\n")
            lf.flush()
            print(f"[{NAME}] {row.get('method')} {row.get('tool', '')} {row.get('ms', '')}ms", file=sys.stderr)

        for line in sys.stdin:
            if not line.strip():
                continue
            msg_id = None
            try:
                msg = json.loads(line)
                msg_id = msg.get("id") if isinstance(msg, dict) else None
                reply = handle(msg, log)
            except json.JSONDecodeError:
                reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
                log({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "method": None, "error": "parse error"})
            except RpcError as e:
                is_note = isinstance(msg, dict) and "id" not in msg   # never reply to a notification
                reply = None if is_note else {"jsonrpc": "2.0", "id": msg_id, "error": {"code": e.code, "message": e.message}}
            except Exception as e:   # never crash the session on a bug: report it as an internal error
                traceback.print_exc(file=sys.stderr)
                reply = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32603, "message": f"internal error: {e}"}}
            if reply is not None:
                sys.stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
                sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
