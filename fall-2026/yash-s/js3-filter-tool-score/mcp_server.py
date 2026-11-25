"""A small tool server for the JS3 filter, written from scratch with the standard library.

    python3 mcp_server.py [--results runs/<run>/results.json] [--no-transcript]

It speaks the Model Context Protocol's message shape over stdio: one JSON-RPC 2.0
message per line on stdin and stdout. Methods: initialize, ping, tools/list,
tools/call, and the notifications/initialized notification. Anything else gets
a JSON-RPC error.

Two tools, both read-only:

  score_posting          score one posting's text with FILTER.md v1.1 (pure computation)
  search_saved_postings  look up decisions in one saved filter run

What it can touch, all fixed at start-up by whoever launches it, never by the client:
  reads   rules/*.json, the fictional persona's skills (from the JS2 folder), and one
          saved results.json plus its summary.json, inside this folder
  writes  one transcript file per session in mcp/transcripts/, inside this folder
No network, no subprocess, no environment secrets, and no file path from a client
is ever opened. The agent never applies, emails, messages or logs in.
"""
import argparse
import datetime
import html
import json
import os
import re
import sys
import traceback
from pathlib import Path

import job_filter as J

HERE = Path(__file__).resolve().parent
DEFAULT_RESULTS = HERE / "runs" / "filter-v1.1-2026-11-18T212545Z" / "results.json"
TRANSCRIPT_DIR = HERE / "mcp" / "transcripts"
SERVER_INFO = {"name": "yash-js3-job-filter", "version": "1.0.0"}
PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")  # newest first
MAX_LINE = 1_000_000
BOARDS = ["Anthropic", "Databricks", "OpenAI"]

INSTRUCTIONS = ("Read-only tools over Yash Saraf's JS3 job filter (FILTER.md v1.1) for the fictional persona Priya Nair. "
                "A score is screening output, not a judgment that a posting is worth applying to: 'review' means a "
                "person must read the posting. This server cannot apply, email, message, log in, write files for you, "
                "or reach the network. It keeps a transcript of every message in its own folder.")

READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}

TOOLS = [
    {
        "name": "score_posting",
        "title": "Score one posting with FILTER.md v1.1",
        "description": ("Scores one job posting's text with the JS3 filter (FILTER.md Version 1.1) for the fictional "
                        "persona Priya Nair, and returns the decision (confirmed / review / rejected), the score out of "
                        "100 with its parts, and every reason. Pure computation on the text you send: nothing is "
                        "fetched or sent anywhere. The server keeps a transcript of every message, including this "
                        "text, in its own folder, so do not send private documents."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "minLength": 1, "maxLength": 300, "description": "The job title"},
                "location": {"type": "string", "maxLength": 1000,
                             "description": "Location text; separate several with ';' or '|'"},
                "description": {"type": "string", "minLength": 1, "maxLength": 100000,
                                "description": "The posting text, as HTML or plain text"},
            },
            "required": ["title", "description"],
            "additionalProperties": False,
        },
        "annotations": {"title": "Score one posting", **READ_ONLY},
    },
    {
        "name": "search_saved_postings",
        "title": "Search the saved filter run",
        "description": ("Looks up postings in one saved run of the JS3 filter over 2,418 postings collected on "
                        "2026-11-10 from three public job boards. Filters by decision, board, minimum score, and a "
                        "word in the title. Returns at most 20 postings, highest score first. The postings may no "
                        "longer be open."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "decision": {"type": "string", "enum": ["confirmed", "review", "rejected"]},
                "board": {"type": "string", "enum": BOARDS},
                "min_score": {"type": "integer", "minimum": 0, "maximum": 100},
                "title_contains": {"type": "string", "minLength": 1, "maxLength": 100,
                                   "description": "Case-insensitive text that must appear in the title"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 20, "description": "Default 10"},
            },
            "additionalProperties": False,
        },
        "annotations": {"title": "Search saved results", **READ_ONLY},
    },
]


# ------------------------------------------------------------ argument checks

def validate(schema, args):
    """The small part of JSON Schema these two tools use. Returns a list of problems."""
    if not isinstance(args, dict):
        return ["arguments must be an object"]
    problems = []
    props = schema.get("properties", {})
    for name in schema.get("required", []):
        if name not in args:
            problems.append(f"missing required argument '{name}'")
    for name, value in args.items():
        if name not in props:
            if schema.get("additionalProperties") is False:
                problems.append(f"unknown argument '{name}'")
            continue
        p = props[name]
        if p["type"] == "string":
            if not isinstance(value, str):
                problems.append(f"'{name}' must be a string")
                continue
            if len(value) < p.get("minLength", 0):
                problems.append(f"'{name}' is too short")
            if len(value) > p.get("maxLength", 10 ** 9):
                problems.append(f"'{name}' is longer than {p['maxLength']} characters")
        elif p["type"] == "integer":
            if isinstance(value, bool) or not isinstance(value, int):
                problems.append(f"'{name}' must be an integer")
                continue
            if value < p.get("minimum", -10 ** 9) or value > p.get("maximum", 10 ** 9):
                problems.append(f"'{name}' must be between {p['minimum']} and {p['maximum']}")
        if "enum" in p and value not in p["enum"]:
            problems.append(f"'{name}' must be one of {p['enum']}")
    return problems


# ------------------------------------------------------------------ the tools

def as_markup(text):
    """HTML is passed through; plain text becomes one line per <br>, so headings still count."""
    if re.search(r"<\s*(p|div|li|ul|ol|br|h[1-6])\b", text, re.IGNORECASE):
        return text
    return html.escape(text).replace("\n", "<br>")


def score_posting(rules, args):
    posting = {"board": "submitted", "id": "submitted", "title": args["title"].strip(),
               "location": (args.get("location") or "").strip(), "url": "", "markup": as_markup(args["description"]),
               "source_run": "submitted by the client", "source_file": "submitted by the client"}
    r = J.evaluate(posting, rules)
    return {
        "filter_version": rules["filter"]["version"],
        "decision": r["decision"], "decision_step": r["decision_step"], "score": r["score"],
        "threshold": rules["filter"]["scoring"]["threshold"], "points": r["points"],
        "role": r["role"], "role_match": r["role_match"], "topics": r["topics"], "skills": r["skills"],
        "location_status": r["location_status"], "experience_status": r["experience_status"],
        "experience_reason": r["experience_reason"],
        "hard_exclusions": r["hard_exclusions"], "review_reasons": r["review_reasons"],
        "note": ("Screening by FILTER.md v1.1 for the fictional persona Priya Nair. 'review' means a person must read "
                 "the posting; a score is not a judgment that it is worth applying to."),
    }


def search_saved_postings(saved, args):
    rows = saved["results"]
    if "decision" in args:
        rows = [r for r in rows if r["decision"] == args["decision"]]
    if "board" in args:
        rows = [r for r in rows if r["board"] == args["board"]]
    if "min_score" in args:
        rows = [r for r in rows if r["score"] >= args["min_score"]]
    if "title_contains" in args:
        needle = args["title_contains"].lower()
        rows = [r for r in rows if needle in r["title"].lower()]
    rows = sorted(rows, key=lambda r: (-r["score"], r["board"], str(r["id"])))
    limit = args.get("limit", 10)
    return {
        "data": saved["about"], "total_matching": len(rows), "returned": min(limit, len(rows)),
        "postings": [{"board": r["board"], "id": r["id"], "title": r["title"], "location": r["location"],
                      "decision": r["decision"], "score": r["score"],
                      "reasons": r["hard_exclusions"] or r["review_reasons"], "url": r["url"]} for r in rows[:limit]],
    }


def load_saved(results_path):
    results_path = Path(results_path).resolve()
    if not results_path.is_relative_to(HERE):
        raise SystemExit("refusing a results file outside this project folder")
    results = json.loads(results_path.read_text(encoding="utf-8"))
    summary_path = results_path.parent / "summary.json"
    about = f"saved filter run '{results_path.parent.name}'"
    if summary_path.exists():
        s = json.loads(summary_path.read_text(encoding="utf-8"))
        runs = sorted({x["run"] for x in s.get("inputs", {}).get("saved_responses", [])})
        about += (f", FILTER.md v{s.get('filter_version')}, run at {s.get('run_at')}, over saved board responses "
                  f"from {', '.join(runs)}")
    return {"results": results, "about": about}


# ------------------------------------------------------------------ transcript

class Transcript:
    """Every line in both directions, exactly as sent, one JSON record per line.
    This is the server's only file write, and it can only go inside this folder."""

    def __init__(self, folder=TRANSCRIPT_DIR):
        folder = Path(folder).resolve()
        if not folder.is_relative_to(HERE):
            raise SystemExit("refusing a transcript folder outside this project folder")
        folder.mkdir(parents=True, exist_ok=True)
        now = datetime.datetime.now(datetime.timezone.utc)
        self.path = folder / f"server-session-{now:%Y-%m-%dT%H%M%S}Z-{os.getpid()}.jsonl"
        self._f = open(self.path, "x", encoding="utf-8")

    def write(self, direction, raw):
        t = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")
        self._f.write(json.dumps({"t": t, "dir": direction, "raw": raw}, ensure_ascii=False) + "\n")
        self._f.flush()

    def close(self):
        self._f.close()


# ------------------------------------------------------------------ protocol

def error(id_, code, message):
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}}


def ok(id_, result):
    return {"jsonrpc": "2.0", "id": id_, "result": result}


class Server:
    def __init__(self, rules, saved):
        self.rules, self.saved = rules, saved
        self.initialized = False
        self.client_info = None
        self.protocol_version = None

    def handle_line(self, line):
        """One line in, at most one message out (None for notifications)."""
        if len(line) > MAX_LINE:
            return error(None, -32600, "Invalid Request: message too large")
        try:
            msg = json.loads(line)
        except ValueError:
            return error(None, -32700, "Parse error")
        except RecursionError:  # found 2026-11-25 by the robustness probe: deep nesting crashed the server
            return error(None, -32700, "Parse error: nested too deeply")
        if isinstance(msg, list):
            return error(None, -32600, "Invalid Request: batches are not supported")
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":
            return error(None, -32600, "Invalid Request")
        if "method" not in msg:
            return None  # a response to a request this server never sends: ignore it
        method, has_id, id_ = msg["method"], "id" in msg, msg.get("id")
        if not isinstance(method, str):
            return error(id_ if has_id else None, -32600, "Invalid Request: method must be a string")
        if not has_id:
            return None  # notifications/initialized, notifications/cancelled, or anything else: no reply
        if isinstance(id_, bool) or not isinstance(id_, (str, int)):
            return error(None, -32600, "Invalid Request: id must be a string or an integer")
        params = msg.get("params", {})
        if not isinstance(params, dict):
            return error(id_, -32602, "Invalid params: params must be an object")
        if method == "initialize":
            return ok(id_, self.initialize(params))
        if method == "ping":
            return ok(id_, {})
        if not self.initialized:
            return error(id_, -32002, "Server not initialized: send initialize first")
        if method == "tools/list":
            return ok(id_, {"tools": TOOLS})
        if method == "tools/call":
            return self.call(id_, params)
        return error(id_, -32601, f"Method not found: {method}")

    def initialize(self, params):
        asked = params.get("protocolVersion")
        self.protocol_version = asked if asked in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0]
        self.client_info = params.get("clientInfo")
        self.initialized = True
        return {"protocolVersion": self.protocol_version, "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO, "instructions": INSTRUCTIONS}

    def call(self, id_, params):
        name, args = params.get("name"), params.get("arguments", {})
        tool = next((t for t in TOOLS if t["name"] == name), None)
        if tool is None:
            return error(id_, -32602, f"Unknown tool: {name!r}")
        problems = validate(tool["inputSchema"], args)
        if problems:
            return ok(id_, {"content": [{"type": "text", "text": "Invalid arguments: " + "; ".join(problems)}],
                            "isError": True})
        try:
            out = score_posting(self.rules, args) if name == "score_posting" else search_saved_postings(self.saved, args)
        except Exception:  # never send a stack trace to the client
            traceback.print_exc(file=sys.stderr)
            return ok(id_, {"content": [{"type": "text", "text": "The tool failed on this input."}], "isError": True})
        return ok(id_, {"content": [{"type": "text", "text": json.dumps(out, indent=1, ensure_ascii=False)}],
                        "isError": False})


def serve(server, stdin, stdout, transcript=None):
    for line in stdin:
        line = line.rstrip("\r\n")
        if not line.strip():
            continue
        if transcript:
            transcript.write("client->server", line)
        try:
            reply = server.handle_line(line)
        except Exception:  # one bad message must never stop the server
            traceback.print_exc(file=sys.stderr)
            reply = error(None, -32603, "Internal error")
        if reply is not None:
            out = json.dumps(reply, ensure_ascii=False)
            stdout.write(out + "\n")
            stdout.flush()
            if transcript:
                transcript.write("server->client", out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results", default=str(DEFAULT_RESULTS))
    ap.add_argument("--no-transcript", action="store_true")
    args = ap.parse_args(argv)
    server = Server(J.load_rules(), load_saved(args.results))
    transcript = None if args.no_transcript else Transcript()
    if transcript:
        print(f"transcript: {transcript.path.relative_to(HERE)}", file=sys.stderr)
    stdin = open(sys.stdin.fileno(), encoding="utf-8", errors="replace", closefd=False)
    try:
        serve(server, stdin, sys.stdout, transcript)
    finally:
        if transcript:
            transcript.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
