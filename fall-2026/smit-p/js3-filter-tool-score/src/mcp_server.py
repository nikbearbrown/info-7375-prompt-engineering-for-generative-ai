"""A Model Context Protocol tool server, written from scratch: JSON-RPC 2.0 over stdin/stdout.

    python3 src/mcp_server.py [--run-id live-20261114] [--transcript-name NAME]

Offers ONE tool, score_posting: given a board and a posting id from a saved run, return the
filter's verdict, score and cited evidence. It reads only files under this folder's runs/ and
persona/, never touches the network, and writes only its own transcript under transcripts/.
Every line received and every line sent is appended to transcripts/<name>.jsonl, in order.

Methods: initialize, notifications/initialized, ping, tools/list, tools/call. Anything else is
answered with JSON-RPC error -32601.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import filter as flt  # noqa: E402
from postings import ROOT, load_run  # noqa: E402
from run_filter import load_skills  # noqa: E402

SERVER_INFO = {"name": "js3-score-posting", "version": "1.0.0"}
SUPPORTED_VERSIONS = ["2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"]
BOARDS = ["airbnb", "figma", "spotify", "linear"]
ID_PATTERN = r"^[A-Za-z0-9-]{1,64}$"

TOOL = {
    "name": "score_posting",
    "title": "Score one saved job posting",
    "description": ("Apply the written job filter (FILTER.md, current version) to ONE posting from the "
                    "saved collection run and return its verdict (keep / reject / cannot_tell), the rule "
                    "that decided it, its score, and the exact posting text quoted as evidence. Read-only: "
                    "uses saved data, no network, no side effects. The verdict is a record of a written "
                    "rule, not a judgment about whether the job is worth applying to."),
    "inputSchema": {
        "type": "object",
        "properties": {
            "board": {"type": "string", "enum": BOARDS, "description": "Which job board."},
            "posting_id": {"type": "string", "pattern": ID_PATTERN,
                           "description": "The posting's id on that board, as saved in the run."},
        },
        "required": ["board", "posting_id"],
        "additionalProperties": False,
    },
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True,
                    "openWorldHint": False},
}


class Server:
    def __init__(self, run_id, transcript_path):
        postings, _, _ = load_run(run_id)
        self.run_id = run_id
        self.by_key = {(p["board"], p["id"]): p for p in postings}
        self.skills = load_skills()
        self.transcript_path = transcript_path
        self.initialized = False

    def log(self, direction, line):
        rec = {"at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds"),
               "direction": direction, "message": line}
        with open(self.transcript_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def send(self, obj):
        line = json.dumps(obj, ensure_ascii=False)
        self.log("server->client", line)
        sys.stdout.write(line + "\n")
        sys.stdout.flush()

    def error(self, req_id, code, message):
        self.send({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})

    def tool_result(self, req_id, payload, is_error=False):
        self.send({"jsonrpc": "2.0", "id": req_id, "result": {
            "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=1)}],
            "isError": is_error}})

    def call_score_posting(self, req_id, args):
        if not isinstance(args, dict) or set(args) - {"board", "posting_id"}:
            return self.tool_result(req_id, {"error": "arguments must be exactly board and posting_id"}, True)
        board, pid = args.get("board"), args.get("posting_id")
        if board not in BOARDS:
            return self.tool_result(req_id, {"error": f"board must be one of {BOARDS}"}, True)
        if not isinstance(pid, str) or not re.match(ID_PATTERN, pid):
            return self.tool_result(req_id, {"error": "posting_id must match " + ID_PATTERN}, True)
        posting = self.by_key.get((board, pid))
        if posting is None:
            return self.tool_result(req_id, {"error": f"no posting {pid} on {board} in run {self.run_id}"}, True)
        v = flt.judge(posting, self.skills)
        self.tool_result(req_id, {
            "label": "RECORD (written rule, recomputable) - not a judgment of whether the job is worth applying to",
            "run_id": self.run_id, "board": board, "posting_id": pid, "title": posting["title"],
            "location": posting["location"], "url": posting["url"],
            "verdict": v["verdict"], "rule": v["rule"], "reason": v["reason"], "score": v["score"],
            "skills": v["skills"], "evidence": v["evidence"], "filter_version": v["filter_version"]})

    def handle(self, msg):
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or "method" not in msg:
            if isinstance(msg, dict) and "id" in msg and "method" not in msg:
                return  # a response from the client; this server sends no requests, so ignore it
            return self.error(msg.get("id") if isinstance(msg, dict) else None, -32600, "invalid request")
        method, req_id, params = msg["method"], msg.get("id"), msg.get("params") or {}
        is_notification = "id" not in msg
        if method == "initialize":
            asked = params.get("protocolVersion")
            version = asked if asked in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0]
            return self.send({"jsonrpc": "2.0", "id": req_id, "result": {
                "protocolVersion": version, "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
                "instructions": "One read-only tool over a saved job-board run. Verdicts are records of a written rule."}})
        if method == "notifications/initialized":
            self.initialized = True
            return None
        if is_notification:
            return None  # other notifications (e.g. cancelled) need no answer
        if method == "ping":
            return self.send({"jsonrpc": "2.0", "id": req_id, "result": {}})
        if method == "tools/list":
            return self.send({"jsonrpc": "2.0", "id": req_id, "result": {"tools": [TOOL]}})
        if method == "tools/call":
            if params.get("name") != TOOL["name"]:
                return self.error(req_id, -32602, f"unknown tool {params.get('name')!r}")
            return self.call_score_posting(req_id, params.get("arguments"))
        return self.error(req_id, -32601, f"method not found: {method}")

    def serve(self):
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            self.log("client->server", line)
            try:
                msg = json.loads(line)
            except ValueError:
                self.error(None, -32700, "parse error")
                continue
            self.handle(msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="live-20261114")
    ap.add_argument("--transcript-name",
                    default="server-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    a = ap.parse_args()
    if not re.match(r"^[A-Za-z0-9_.-]{1,80}$", a.transcript_name):
        sys.exit("bad transcript name")
    os.makedirs(os.path.join(ROOT, "transcripts"), exist_ok=True)
    Server(a.run_id, os.path.join(ROOT, "transcripts", a.transcript_name + ".jsonl")).serve()


if __name__ == "__main__":
    main()
