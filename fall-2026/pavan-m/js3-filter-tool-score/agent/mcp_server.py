"""A Model Context Protocol tool server written from scratch (no MCP SDK). No network.

    .venv/bin/python -m agent.mcp_server [--transcript out/transcripts/<name>.jsonl]

Transport: JSON-RPC 2.0 over stdio, one JSON message per line (UTF-8). Only protocol
messages are written to stdout, each followed by a flush; logging goes to stderr.

It offers exactly one tool, score_posting, which scores one posting with agent/filter.py
using config/filter_v1_1.json (FILTER.md v1.1 = v1.0 with years_cutoff 5), read through
policy.check_read on every call. The tool is read-only: it never fetches, applies, or
writes anything. The only file the server writes is its transcript, through
policy.check_write: one line per message in either direction,
    {"ts": <UTC ISO time>, "direction": "in" | "out", "message": <the JSON message>}
(an unparseable incoming line is recorded as the raw string).

handle(message) is pure apart from reading the config: it takes one parsed message and
returns the reply dict, or None for a notification. It never writes the transcript; the
stdio loop (serve) does that, so tests can call handle() without creating files.
"""

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

from agent.filter import resolve_config, score_posting
from agent.policy import PolicyError, append_line, check_read, make_dir, write_new

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FILTER_CONFIG = "config/filter_v1_1.json"

# MCP protocol versions this server implements, oldest to newest. Everything used here
# (initialize, ping, tools/list, tools/call, tool annotations, isError) exists in all three.
SUPPORTED_VERSIONS = ["2024-11-05", "2025-03-26", "2025-06-18"]
LATEST_VERSION = max(SUPPORTED_VERSIONS)  # ISO dates sort as strings

SERVER_INFO = {"name": "js3-job-filter", "version": "1.1"}
CAPABILITIES = {"tools": {"listChanged": False}}

# JSON-RPC 2.0 error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

TOOL_NAME = "score_posting"
FIELDS = ("title", "location", "content")
MAX_FIELD_CHARS = 200_000  # a guard against oversized input; real postings are far smaller

SCORE_POSTING_TOOL = {
    "name": TOOL_NAME,
    "title": "Score a job posting (FILTER.md v1.1)",
    "description": (
        "Score one job posting against Pavan's written filter, FILTER.md v1.1 (v1.0 rules "
        "with the years-of-experience reject cutoff lowered to 5), for the fictional persona "
        "Alex Morgan. Returns JSON with decision (KEEP, REJECT or CANNOT TELL), score, "
        "title_points, location_points, matched technical categories, flags, and reasons "
        "naming the FILTER.md rule behind each point. Deterministic keyword rules, no model "
        "call. Read-only: it does not fetch postings, apply to jobs, or store anything. "
        "Pass the posting text as given; HTML in content is unescaped and stripped."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "maxLength": MAX_FIELD_CHARS,
                      "description": "Job title, e.g. 'Software Engineer, Backend'."},
            "location": {"type": "string", "maxLength": MAX_FIELD_CHARS,
                         "description": "Location as the posting states it, e.g. "
                                        "'San Francisco, CA' or 'New York, NY; Remote, US'."},
            "content": {"type": "string", "maxLength": MAX_FIELD_CHARS,
                        "description": "Full job description, plain text or HTML. Fewer "
                                       "than 50 words gives CANNOT TELL (FILTER.md 2.6)."},
        },
        "required": list(FIELDS),
        "additionalProperties": False,
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": False},
}


def log(*args):
    print("[mcp_server]", *args, file=sys.stderr, flush=True)


# ---------- JSON-RPC helpers ----------

def _result(msg_id, result):
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _error(msg_id, code, message, data=None):
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": msg_id, "error": err}


def _valid_id(value):
    # MCP: a request id is a string or an integer, never null; bool is not an integer here.
    return isinstance(value, str) or (isinstance(value, int) and not isinstance(value, bool))


def _tool_error(text):
    return {"content": [{"type": "text", "text": text}], "isError": True}


# ---------- Methods ----------

def _initialize(params):
    requested = params.get("protocolVersion")
    version = requested if requested in SUPPORTED_VERSIONS else LATEST_VERSION
    if version != requested:
        log(f"client asked for protocolVersion {requested!r}; offering {version}")
    return {
        "protocolVersion": version,
        "capabilities": CAPABILITIES,
        "serverInfo": SERVER_INFO,
        "instructions": "One read-only tool, score_posting, applies FILTER.md v1.1 to one posting.",
    }


def _load_filter_config(root=PROJECT_ROOT):
    with open(check_read(Path(root) / FILTER_CONFIG, root), encoding="utf-8") as f:
        overrides = json.load(f)
    if not isinstance(overrides, dict):
        raise ValueError(f"{FILTER_CONFIG} must be a JSON object")
    resolve_config(overrides)  # raises ValueError on an unknown key or bad value
    return overrides


def _validate_arguments(arguments):
    """Return a reason string if the arguments do not match inputSchema, else None."""
    if not isinstance(arguments, dict):
        return f"arguments must be an object, got {type(arguments).__name__}"
    problems = []
    missing = [f for f in FIELDS if f not in arguments]
    if missing:
        problems.append("missing required argument(s): " + ", ".join(missing))
    for f in FIELDS:
        if f in arguments and not isinstance(arguments[f], str):
            problems.append(f"argument '{f}' must be a string, got "
                            f"{type(arguments[f]).__name__ if arguments[f] is not None else 'null'}")
        elif f in arguments and len(arguments[f]) > MAX_FIELD_CHARS:
            problems.append(f"argument '{f}' is longer than {MAX_FIELD_CHARS} characters")
    extra = sorted(set(arguments) - set(FIELDS))
    if extra:
        problems.append("unexpected argument(s): " + ", ".join(extra))
    return "; ".join(problems) or None


def _tools_call(msg_id, params):
    name = params.get("name")
    if not isinstance(name, str):
        return _error(msg_id, INVALID_PARAMS, "tools/call needs params.name as a string")
    if name != TOOL_NAME:
        return _error(msg_id, INVALID_PARAMS, f"Unknown tool: {name}",
                      {"available_tools": [TOOL_NAME]})
    arguments = params.get("arguments", {})
    problem = _validate_arguments(arguments)
    if problem:
        return _result(msg_id, _tool_error(f"{TOOL_NAME}: {problem}"))
    try:
        config = _load_filter_config()
    except (OSError, ValueError, PolicyError) as e:
        log(f"filter config unavailable: {type(e).__name__}: {e}")
        return _result(msg_id, _tool_error(
            f"{TOOL_NAME}: filter config {FILTER_CONFIG} unavailable: {type(e).__name__}: {e}"))
    posting = {f: arguments[f] for f in FIELDS}
    scored = score_posting(posting, config)
    return _result(msg_id, {
        "content": [{"type": "text", "text": json.dumps(scored, ensure_ascii=False)}],
        "isError": False,
    })


# ---------- Dispatch ----------

def handle(message):
    """One parsed JSON-RPC message in; the reply dict out, or None when no reply is due."""
    if not isinstance(message, dict):
        # JSON-RPC batches (arrays) were removed from MCP in 2025-06-18; refuse them.
        return _error(None, INVALID_REQUEST, "Invalid Request: expected a single JSON object")

    has_id = "id" in message
    msg_id = message.get("id")
    reply_id = msg_id if _valid_id(msg_id) else None
    method = message.get("method")

    if message.get("jsonrpc") != "2.0":
        return _error(reply_id, INVALID_REQUEST, "Invalid Request: jsonrpc must be \"2.0\"")

    if "method" not in message:
        if has_id and ("result" in message or "error" in message):
            # A response from the client. This server never sends requests, so nothing awaits it.
            log(f"ignoring a response with id {msg_id!r}: no request of ours is outstanding")
            return None
        return _error(reply_id, INVALID_REQUEST, "Invalid Request: no method")

    if not isinstance(method, str):
        return _error(reply_id, INVALID_REQUEST, "Invalid Request: method must be a string")
    if has_id and not _valid_id(msg_id):
        return _error(None, INVALID_REQUEST, "Invalid Request: id must be a string or integer")
    params = message.get("params", {})
    if not isinstance(params, dict):
        return _error(reply_id, INVALID_REQUEST, "Invalid Request: params must be an object")

    if not has_id:
        # A notification: never answered, whatever its method.
        if method not in ("notifications/initialized", "notifications/cancelled"):
            log(f"ignoring notification {method!r}")
        return None

    try:
        if method == "initialize":
            return _result(msg_id, _initialize(params))
        if method == "ping":
            return _result(msg_id, {})
        if method == "tools/list":
            return _result(msg_id, {"tools": [SCORE_POSTING_TOOL]})
        if method == "tools/call":
            return _tools_call(msg_id, params)
        return _error(msg_id, METHOD_NOT_FOUND, f"Method not found: {method}")
    except Exception as e:  # never let one bad message kill the server
        log("internal error:\n" + traceback.format_exc())
        return _error(msg_id, INTERNAL_ERROR, f"Internal error: {type(e).__name__}")


def handle_line(line):
    """One raw line in; (parsed message or raw string, reply or None)."""
    try:
        message = json.loads(line)
    except json.JSONDecodeError as e:
        return line, _error(None, PARSE_ERROR, f"Parse error: {e.msg}")
    return message, handle(message)


# ---------- Transcript and stdio loop ----------

def timestamp():
    return datetime.now().strftime("%Y-%m-%dT%H%M%S")


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class Transcript:
    """Append-only JSONL of every message; each write goes through policy.check_write."""

    def __init__(self, path, root=PROJECT_ROOT):
        self.root = root
        path = Path(path)
        self.path = path if path.is_absolute() else Path(root) / path
        make_dir(self.path.parent, root)
        write_new(self.path, "", root)  # refuse to mix into an existing transcript

    def record(self, direction, message):
        line = json.dumps({"ts": utc_now(), "direction": direction, "message": message},
                          ensure_ascii=False)
        append_line(self.path, line, self.root)


def serve(stdin, stdout, transcript):
    for raw in stdin:
        try:
            line = raw.decode("utf-8").strip()
        except UnicodeDecodeError:
            line = None
        if line == "":
            continue
        if line is None:
            transcript.record("in", raw.decode("utf-8", errors="replace").rstrip("\n"))
            reply = _error(None, PARSE_ERROR, "Parse error: input is not valid UTF-8")
        else:
            message, reply = handle_line(line)
            transcript.record("in", message)
        if reply is not None:
            stdout.write((json.dumps(reply, ensure_ascii=False) + "\n").encode("utf-8"))
            stdout.flush()
            transcript.record("out", reply)


def main(argv=None):
    ap = argparse.ArgumentParser(description="js3-job-filter MCP server (stdio)")
    ap.add_argument("--transcript", default=None,
                    help="JSONL transcript path inside out/ "
                         "(default out/transcripts/server-<timestamp>.jsonl)")
    args = ap.parse_args(argv)
    path = args.transcript or f"out/transcripts/server-{timestamp()}.jsonl"
    try:
        transcript = Transcript(path)
    except (PolicyError, OSError) as e:
        log(f"cannot open transcript {path}: {type(e).__name__}: {e}")
        return 2
    log(f"ready; protocol versions {SUPPORTED_VERSIONS}; transcript {transcript.path}")
    try:
        serve(sys.stdin.buffer, sys.stdout.buffer, transcript)
    except (KeyboardInterrupt, BrokenPipeError):
        pass
    log("stdin closed; exiting")
    return 0


if __name__ == "__main__":
    sys.exit(main())
