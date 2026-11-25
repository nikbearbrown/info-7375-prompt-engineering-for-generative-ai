"""A Model Context Protocol tool server, written from scratch (stdlib only): one tool, `score_posting`.

Transport: stdio, one JSON-RPC 2.0 message per line (MCP "stdio" transport).
Methods answered: initialize, notifications/initialized, ping, tools/list, tools/call.
Anything else that carries an id gets JSON-RPC error -32601; notifications are ignored.

The one capability: score a posting the agent already collected, with the filter in
FILTER.md (default v1.0). It reads the saved corpus only: no network, no Claude call, and
the tool changes nothing. The server process itself does write one file per session:
the transcript of every line in both directions, to out/mcp/transcripts/ (through policy.write_bytes).

    python -B -m agent3.mcp_server [--filter-version v1.0] [--transcript-name NAME]
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone

from agent3 import corpus, filter as flt, policy

SERVER_INFO = {"name": "js3-filter", "version": "1.0.0"}
SUPPORTED_PROTOCOLS = ["2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"]
ID_PATTERN = r"^(greenhouse|lever|ashby):[a-z0-9-]+:[A-Za-z0-9-]+$"

TOOL = {
    "name": "score_posting",
    "title": "Score one collected job posting with the JS3 filter",
    "description": (
        "Scores one job posting that the Job-Search Agent already collected (saved board responses of "
        "2026-11-10 and 2026-11-24 from Figma/Greenhouse, Spotify/Lever, Snowflake/Ashby) against the "
        "versioned filter in FILTER.md, for the fictional persona Jack Spencer. Returns keep / reject / "
        "cannot_tell, the score (role 0 or 4 + topic groups 0-4 + skills 0-8; keep at >= 6), and every "
        "word that matched with its character offset, so the score can be recomputed by hand. "
        "The score is a keyword filter, not a judgment that the job is worth applying to. "
        "Read-only: it reads saved files and never contacts a job board or any other host."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "posting_id": {"type": "string", "pattern": ID_PATTERN,
                           "description": "Agent posting id, '<ats>:<board>:<native id>', e.g. "
                                          "'greenhouse:figma:5551686004'."},
        },
        "required": ["posting_id"],
        "additionalProperties": False,
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "posting_id": {"type": "string"}, "title": {"type": "string"}, "board": {"type": "string"},
            "filter_version": {"type": "string"},
            "verdict": {"type": "string", "enum": ["keep", "reject", "cannot_tell"]},
            "score": {"type": "integer"}, "threshold": {"type": "integer"},
            "because": {"type": "string"}, "matches": {"type": "object"},
            "still_listed": {"type": "boolean"}, "url": {"type": "string"},
        },
        "required": ["posting_id", "verdict", "score", "filter_version", "because"],
    },
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True,
                    "openWorldHint": False},
}


class Session:
    def __init__(self, cfg: dict, transcript_name: str):
        c = corpus.load()
        self.postings = c["postings"]
        self.missing_boards = sorted({m["board"] for m in c["missing"]})
        self.latest_run = max(s["run_id"] for s in c["sources"])
        self.cfg = cfg
        self.initialized = False
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.transcript = policy.OUT / "mcp" / "transcripts" / f"{stamp}_{transcript_name}.jsonl"
        self.lines = []

    def log(self, direction: str, raw: str):
        self.lines.append(json.dumps({"t": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                                      "dir": direction, "msg": raw}, ensure_ascii=False))
        policy.write_bytes(self.transcript, ("\n".join(self.lines) + "\n").encode("utf-8"))

    # --- the tool -------------------------------------------------------------------------
    def score_posting(self, args) -> dict:
        if not isinstance(args, dict):
            return tool_error("arguments must be an object")
        extra = sorted(set(args) - {"posting_id"})
        if extra:
            return tool_error(f"unexpected argument(s): {extra}; the only argument is posting_id")
        pid = args.get("posting_id")
        if not isinstance(pid, str) or not re.fullmatch(ID_PATTERN, pid):
            return tool_error("posting_id must look like '<ats>:<board>:<native id>'")
        board = pid.rsplit(":", 1)[0]
        if board in self.missing_boards:
            out = {"posting_id": pid, "verdict": "cannot_tell", "score": 0, "filter_version": self.cfg["version"],
                   "because": f"board {board} failed every run (HTTP 404): no data, I cannot tell (A3)"}
            return tool_ok(out)
        p = self.postings.get(pid)
        if p is None:
            return tool_error(f"posting {pid} is not in the collected corpus; no score exists (this is not "
                              "a 'not relevant' answer)")
        r = flt.apply(p, self.cfg)
        out = {"posting_id": pid, "title": r["title"], "board": r["board"], "filter_version": r["filter_version"],
               "verdict": r["verdict"], "score": r["score"], "threshold": self.cfg["threshold"],
               "because": r["because"],
               "matches": {"disqualified_by": r["disqualified_by"], "role": r["role_hits"],
                           "topics": r["topic_hits"], "skills": r["skill_hits"], "not_counted": r["skipped_skills"]},
               "still_listed": p["last_seen_run"] == self.latest_run, "url": p["url"]}
        return tool_ok(out)

    # --- JSON-RPC dispatch ------------------------------------------------------------------
    def handle(self, msg):
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or "method" not in msg:
            return error(msg.get("id") if isinstance(msg, dict) else None, -32600, "Invalid Request")
        method, mid, params = msg["method"], msg.get("id"), msg.get("params") or {}
        is_notification = "id" not in msg
        if method == "notifications/initialized":
            self.initialized = True
            return None
        if is_notification:
            return None
        if method == "initialize":
            asked = params.get("protocolVersion")
            version = asked if asked in SUPPORTED_PROTOCOLS else SUPPORTED_PROTOCOLS[0]
            return result(mid, {"protocolVersion": version, "capabilities": {"tools": {"listChanged": False}},
                                "serverInfo": SERVER_INFO,
                                "instructions": "One read-only tool: score_posting. Scores are keyword-filter "
                                                "output, not judgments."})
        if method == "ping":
            return result(mid, {})
        if method == "tools/list":
            return result(mid, {"tools": [TOOL]})
        if method == "tools/call":
            name = params.get("name")
            if name != TOOL["name"]:
                return error(mid, -32602, f"Unknown tool: {name!r}")
            return result(mid, self.score_posting(params.get("arguments", {})))
        return error(mid, -32601, f"Method not found: {method}")


def tool_ok(structured: dict) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(structured, ensure_ascii=False)}],
            "structuredContent": structured, "isError": False}


def tool_error(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}], "isError": True}


def result(mid, res):
    return {"jsonrpc": "2.0", "id": mid, "result": res}


def error(mid, code, message):
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--filter-version", default="v1.0", choices=sorted(flt.VERSIONS))
    ap.add_argument("--transcript-name", default="session")
    args = ap.parse_args(argv)
    stdin = open(sys.stdin.fileno(), "r", encoding="utf-8", newline="\n", closefd=False)
    stdout = open(sys.stdout.fileno(), "w", encoding="utf-8", newline="\n", closefd=False)
    s = Session(flt.VERSIONS[args.filter_version], re.sub(r"[^A-Za-z0-9_-]", "_", args.transcript_name))
    print(f"js3-filter MCP server ready; transcript -> {s.transcript}", file=sys.stderr, flush=True)
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        s.log("client->server", line)
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            reply = error(None, -32700, "Parse error")
        else:
            reply = s.handle(msg)
        if reply is not None:
            out = json.dumps(reply, ensure_ascii=False)
            s.log("server->client", out)
            stdout.write(out + "\n")
            stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
