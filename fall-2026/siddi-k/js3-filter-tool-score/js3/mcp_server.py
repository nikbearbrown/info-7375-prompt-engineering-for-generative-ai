"""A Model Context Protocol tool server, written from scratch (brief Step 2.3). Standard library only.

Transport: stdio, one JSON-RPC 2.0 message per line, UTF-8. Lifecycle: the 2025-11-25 "legacy" shape the brief
names (initialize -> notifications/initialized -> tools/list -> tools/call). One tool, `score_posting`, which runs
the JS3 filter on one posting already saved in this folder. It reads local files only: no network, and its only
write is the transcript file, which must be inside this folder's evidence/ (policy.check_write).

Run:  python -m js3.mcp_server [--collection RUN_ID] [--config config/filter.v1.json] [--transcript PATH]"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone

from . import collect, policy

SUPPORTED_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26")
SERVER_INFO = {"name": "js3-posting-scorer", "version": "1.0.0"}
BOARDS = ("stripe", "notion", "Canva")
ID_RE = re.compile(r"^[A-Za-z0-9-]{1,64}$")

TOOL = {
    "name": "score_posting",
    "title": "Score one collected job posting",
    "description": (
        "Runs Siddi's JS3 filter (FILTER.md, the version named in the result) on ONE job posting that is already "
        "saved in this folder's collection (boards: stripe, notion, Canva). Returns the filter's verdict "
        "(keep / reject / cannot_tell), the gates the posting failed, its score, and every matched word with the "
        "sentence it came from. It reads local files only: no network access and no writes. The verdict is a "
        "recomputable record of keyword rules, not a judgment that the posting is worth applying to."),
    "inputSchema": {
        "type": "object",
        "properties": {
            "board": {"type": "string", "enum": list(BOARDS), "description": "Which board the posting came from"},
            "posting_id": {"type": "string", "pattern": ID_RE.pattern,
                           "description": "The posting's id on that board, as collected"},
        },
        "required": ["board", "posting_id"],
        "additionalProperties": False,
    },
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
}


def _err(id_, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}}


def _ok(id_, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def _tool_error(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}], "isError": True}


def check_arguments(args) -> str | None:
    """The tool's inputSchema, checked by hand. Returns a reason, or None when the arguments are valid."""
    if not isinstance(args, dict):
        return "arguments must be an object"
    extra = set(args) - {"board", "posting_id"}
    if extra:
        return f"unexpected argument(s): {sorted(extra)}"
    for k in ("board", "posting_id"):
        if k not in args:
            return f"missing required argument {k!r}"
        if not isinstance(args[k], str):
            return f"{k!r} must be a string"
    if args["board"] not in BOARDS:
        return f"board must be one of {list(BOARDS)}"
    if not ID_RE.match(args["posting_id"]):
        return "posting_id must be 1-64 letters, digits or hyphens"
    return None


class Server:
    def __init__(self, cfg: dict, collection_run: str, postings: list[dict]):
        self.cfg, self.run = cfg, collection_run
        self.index = {(p["board"], p["id"]): p for p in postings}
        self.initialized = False          # set by a successful initialize

    def score(self, args: dict) -> dict:
        from . import filter as flt
        p = self.index.get((args["board"], args["posting_id"]))
        if p is None:
            return _tool_error(f"no posting {args['posting_id']!r} on board {args['board']!r} in collection {self.run}")
        rec = flt.evaluate(self.cfg, p)
        out = {"collection_run": self.run, "filter_version": self.cfg["version"], "board": rec["board"],
               "posting_id": rec["id"], "title": rec["title"], "location": rec["location"],
               "verdict": rec["verdict"], "reasons": rec["reasons"], "score": rec["score"],
               "keep_threshold": self.cfg["keep_threshold"],
               "gates": {g: {k: v for k, v in d.items() if k != "sentence"} for g, d in rec["gates"].items()},
               "role_word": rec["parts"]["role_word"] if rec["parts"] else None,
               "skills": [{"skill": s["skill"], "sentence": s["text"]} for s in (rec["parts"] or {}).get("skills", [])],
               "topics": [{"word": t["word"], "sentence": t["text"]} for t in (rec["parts"] or {}).get("topics", [])],
               "label": "record: a deterministic result of FILTER.md's rules, not a judgment"}
        return {"content": [{"type": "text", "text": json.dumps(out, ensure_ascii=False)}], "isError": False}

    def handle(self, msg) -> dict | None:
        """One parsed message -> one response, or None for a notification."""
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
            return _err(msg.get("id") if isinstance(msg, dict) else None, -32600, "Invalid Request")
        method, id_ = msg["method"], msg.get("id")
        is_notification = "id" not in msg
        if is_notification:
            return None                   # notifications/initialized, notifications/cancelled, ...: nothing to say
        params = msg.get("params") or {}
        if method == "initialize":
            asked = params.get("protocolVersion") if isinstance(params, dict) else None
            version = asked if asked in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0]
            self.initialized = True
            return _ok(id_, {"protocolVersion": version, "capabilities": {"tools": {"listChanged": False}},
                             "serverInfo": SERVER_INFO,
                             "instructions": "One read-only tool over postings saved in this folder."})
        if method == "ping":
            return _ok(id_, {})
        if not self.initialized:
            return _err(id_, -32000, "Server not initialized: send initialize first")
        if method == "tools/list":
            return _ok(id_, {"tools": [TOOL]})
        if method == "tools/call":
            if not isinstance(params, dict) or params.get("name") != TOOL["name"]:
                return _err(id_, -32602, f"Unknown tool: {params.get('name') if isinstance(params, dict) else None}")
            reason = check_arguments(params.get("arguments", {}))
            if reason:
                return _ok(id_, _tool_error(f"invalid arguments: {reason}"))
            return _ok(id_, self.score(params["arguments"]))
        return _err(id_, -32601, f"Method not found: {method}")

    def handle_line(self, line: str) -> str | None:
        try:
            msg = json.loads(line)
        except ValueError:
            return json.dumps(_err(None, -32700, "Parse error"))
        if isinstance(msg, list):
            return json.dumps(_err(None, -32600, "Batches are not supported"))
        out = self.handle(msg)
        return None if out is None else json.dumps(out, ensure_ascii=False)


class Transcript:
    def __init__(self, path):
        self.f = open(policy.check_write(path), "a", encoding="utf-8", newline="\n") if path else None

    def log(self, direction: str, raw: str) -> None:
        if self.f:
            t = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            self.f.write(json.dumps({"t": t, "dir": direction, "raw": raw}, ensure_ascii=False) + "\n")
            self.f.flush()


def latest_collection() -> str:
    runs = sorted(d.name for d in (policy.ROOT / "data" / "collections").iterdir() if d.is_dir())
    if not runs:
        raise SystemExit("no collection run under data/collections/")
    return runs[-1]


def serve(server: Server, transcript: Transcript, stdin=None, stdout=None) -> None:
    stdin = stdin or sys.stdin.buffer
    stdout = stdout or sys.stdout.buffer
    for raw in stdin:
        line = raw.decode("utf-8").rstrip("\r\n")
        if not line.strip():
            continue
        transcript.log("client->server", line)
        reply = server.handle_line(line)
        if reply is not None:
            transcript.log("server->client", reply)
            stdout.write(reply.encode("utf-8") + b"\n")
            stdout.flush()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m js3.mcp_server")
    p.add_argument("--collection", default=None)
    p.add_argument("--config", default="config/filter.v1.json")
    p.add_argument("--transcript", default=None, help="JSONL file under evidence/ that records every line both ways")
    a = p.parse_args(argv)
    run = a.collection or latest_collection()
    cfg = json.loads(policy.check_read(a.config).read_text(encoding="utf-8"))
    postings = collect.load_postings(policy.ROOT / "data" / "collections" / run)
    serve(Server(cfg, run, postings), Transcript(a.transcript))
    return 0


if __name__ == "__main__":
    sys.exit(main())
