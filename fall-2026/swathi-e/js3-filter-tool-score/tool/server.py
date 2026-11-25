"""The JS3 score_posting tool server: MCP (revision 2025-11-25) over stdio, standard library only.

    python3 tool/server.py

Implements tool/TOOL-SERVER.md (commit f1c24dd) and its amendment (ff32302).
One read-only tool, score_posting(board, posting_id), returns filter v1.1's
saved record for one posting from the 2026-11-17 results file; it retrieves a
previously computed judgment and never rescores. JSON-RPC 2.0, one message per
line on stdin/stdout; diagnostics go to stderr only.

Boundaries (declared in the contract, not enforced by the operating system):
- reads one data file, a constant path checked against a pinned SHA-256 at
  startup; no path is ever built from client input;
- no network, no subprocesses;
- writes only its own transcript, tool/transcripts/<UTC time>-<pid>.jsonl,
  created new ("x") for each session: every line received and sent, with a
  timestamp and direction.
Written by Claude Code.
"""
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import traceback

PROTOCOL_VERSION = "2025-11-25"
SERVER_INFO = {"name": "js3-score-posting", "version": "1.0.0"}
TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
RESULTS_REL = "runs/filter-v1.1-2026-11-17T21-47-06-167440-0500/results.json"
RESULTS_SHA256 = "a7f90a74cfd3c82324e55502439684f0234599cde74789fd0736808e2e5edeff"
FILTER_VERSION = "v1.1"
TRANSCRIPTS = TOOL_DIR / "transcripts"
MAX_LINE = 64 * 1024  # bytes per message, newline excluded
TRUNCATED_CHARS = 1024
RATE_LIMIT, RATE_WINDOW = 20, 1.0  # tools/call per second per session (amendment 2026-11-20)

# JSON-RPC 2.0 error codes
PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS, INTERNAL_ERROR = -32700, -32600, -32601, -32602, -32603

TOOL_NAME = "score_posting"
_DIGITS = re.compile(r"[0-9]{1,20}")
_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
ID_FORMATS = {"databricks": _DIGITS, "stripe": _DIGITS, "plaid": _UUID}
ID_FORMAT_TEXT = {"databricks": "1-20 digits", "stripe": "1-20 digits", "plaid": "a lowercase UUID"}
TOOL = {
    "name": TOOL_NAME,
    "title": "Score posting (saved filter v1.1 result)",
    "description": ("Returns filter v1.1's saved verdict, score, per-rule results (R1-R7) and exact recorded "
                    "quotes for one posting of the saved 2026-11-17 collection. It retrieves a previously "
                    "computed judgment; it does not fetch or rescore postings. A verdict is the filter's rule "
                    "output, not confirmed fit, employment eligibility, sponsorship or F-1 OPT eligibility."),
    "inputSchema": {
        "type": "object",
        "properties": {
            "board": {"type": "string", "enum": sorted(ID_FORMATS),
                      "description": "The job board: databricks, stripe or plaid."},
            "posting_id": {"type": "string",
                           "pattern": "^(?:[0-9]{1,20}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$",
                           "description": "The posting id: 1-20 digits for databricks and stripe, a lowercase "
                                          "UUID for plaid."},
        },
        "required": ["board", "posting_id"],
        "additionalProperties": False,
    },
}
SOURCE_NOTE = ("Retrieved from filter v1.1's saved results for the LIVE collection of 2026-11-17; not rescored "
               "and not current. Not confirmed fit, employment eligibility, sponsorship or OPT eligibility "
               "(see audit/AUDIT-REPORT.md and shortlist/SHORTLIST.md).")


class StartupError(Exception):
    pass


def load_results():
    """{(board, posting id): record} from the one data file, after checking its SHA-256."""
    path = ROOT / RESULTS_REL
    try:
        with open(str(path), "rb") as f:
            raw = f.read()
    except OSError as e:
        raise StartupError(f"cannot read {RESULTS_REL}: {e.strerror}") from None
    digest = hashlib.sha256(raw).hexdigest()
    if digest != RESULTS_SHA256:
        raise StartupError(f"{RESULTS_REL}: sha256 {digest} does not match the pinned sha256 {RESULTS_SHA256}")
    data = json.loads(raw.decode("utf-8"))
    index = {(r["board"], str(r["posting_id"])): r for r in data["results"]}
    return index, data["source_run"]["run_id"]


class Transcript:
    """One new file per session; one JSON object per line received or sent."""

    def __init__(self):
        try:
            os.mkdir(str(TRANSCRIPTS))
        except FileExistsError:
            pass
        name = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S-%fZ") + f"-{os.getpid()}.jsonl"
        self.rel = f"tool/transcripts/{name}"
        self.file = open(str(TRANSCRIPTS / name), "x", encoding="utf-8")  # never overwrites

    def write(self, direction, line, **extra):
        entry = {"t": datetime.now(timezone.utc).isoformat(timespec="microseconds"), "dir": direction,
                 "line": line, **extra}
        self.file.write(json.dumps(entry, ensure_ascii=True) + "\n")
        self.file.flush()

    def close(self):
        self.file.close()


def error(id_, code, message):
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}}


def result(id_, value):
    return {"jsonrpc": "2.0", "id": id_, "result": value}


def tool_error(text):
    return {"content": [{"type": "text", "text": text}], "isError": True}


class Session:
    def __init__(self, index, run_id):
        self.index = index
        self.run_id = run_id
        self.initialized = False
        self.calls = deque()  # monotonic times of accepted tools/call requests

    def handle(self, msg):
        """The response to one parsed message, or None for a notification."""
        if not isinstance(msg, dict):
            return error(None, INVALID_REQUEST, "Invalid Request: expected one JSON-RPC object (batches are not supported)")
        id_ = msg.get("id")
        id_ok = isinstance(id_, (str, int)) and not isinstance(id_, bool)
        reply_id = id_ if id_ok else None
        if msg.get("jsonrpc") != "2.0":
            return error(reply_id, INVALID_REQUEST, 'Invalid Request: "jsonrpc" must be "2.0"')
        method = msg.get("method")
        if not isinstance(method, str):
            return error(reply_id, INVALID_REQUEST, 'Invalid Request: "method" must be a string')
        if "id" not in msg:  # notification: never answered
            return None
        if not id_ok:
            return error(None, INVALID_REQUEST, "Invalid Request: id must be a string or an integer, not null")
        params = msg.get("params")

        if method == "initialize":
            if self.initialized:
                return error(id_, INVALID_REQUEST, "already initialized")
            self.initialized = True
            return result(id_, {"protocolVersion": PROTOCOL_VERSION, "capabilities": {"tools": {"listChanged": False}},
                                "serverInfo": SERVER_INFO})
        if method == "ping":
            return result(id_, {})
        if method not in ("tools/list", "tools/call"):
            return error(id_, METHOD_NOT_FOUND, f"Method not found: {method}")
        if not self.initialized:
            return error(id_, INVALID_REQUEST, "not initialized: send initialize first")
        if method == "tools/list":
            return result(id_, {"tools": [TOOL]})
        return self.tools_call(id_, params)

    def tools_call(self, id_, params):
        if not isinstance(params, dict):
            return error(id_, INVALID_PARAMS, "Invalid params: params must be an object")
        name = params.get("name")
        if not isinstance(name, str):
            return error(id_, INVALID_PARAMS, 'Invalid params: "name" must be a string')
        if name != TOOL_NAME:
            return error(id_, INVALID_PARAMS, f"Unknown tool: {name}")
        arguments = params.get("arguments", {})
        if not isinstance(arguments, dict):
            return error(id_, INVALID_PARAMS, 'Invalid params: "arguments" must be an object')
        if not self.admit():
            return result(id_, tool_error(f"rate limit exceeded: at most {RATE_LIMIT} tools/call requests per "
                                          "second per session; retry after the one-second window"))
        problem = validate(arguments)
        if problem:
            return result(id_, tool_error(f"invalid arguments: {problem}"))
        board, posting_id = arguments["board"], arguments["posting_id"]
        record = self.index.get((board, posting_id))
        if record is None:
            return result(id_, tool_error(f"unknown posting: {board} {posting_id} is not in the saved 2026-11-17 "
                                          "results (it may be newer, removed, or on another board)"))
        content = {"record": record,
                   "source": {"file": RESULTS_REL, "sha256": RESULTS_SHA256, "run_id": self.run_id,
                              "filter_version": FILTER_VERSION, "note": SOURCE_NOTE}}
        return result(id_, {"content": [{"type": "text", "text": json.dumps(content, ensure_ascii=False)}],
                            "structuredContent": content, "isError": False})

    def admit(self):
        """Sliding one-second window over accepted calls; refused calls are not counted."""
        now = time.monotonic()
        while self.calls and now - self.calls[0] >= RATE_WINDOW:
            self.calls.popleft()
        if len(self.calls) >= RATE_LIMIT:
            return False
        self.calls.append(now)
        return True


def validate(arguments):
    """None if the arguments are valid, else a short reason that never echoes the input."""
    keys = set(arguments)
    if keys != {"board", "posting_id"}:
        missing, extra = {"board", "posting_id"} - keys, keys - {"board", "posting_id"}
        parts = ([f"missing {', '.join(sorted(missing))}"] if missing else []) + (
            [f"{len(extra)} unexpected argument(s); only board and posting_id are accepted"] if extra else [])
        return "; ".join(parts)
    board, posting_id = arguments["board"], arguments["posting_id"]
    if not isinstance(board, str) or board not in ID_FORMATS:
        return "board must be exactly one of databricks, stripe, plaid"
    if not isinstance(posting_id, str) or not ID_FORMATS[board].fullmatch(posting_id):
        return f"posting_id for {board} must be a string of {ID_FORMAT_TEXT[board]}"
    return None


def read_line(stream):
    """(text, raw length, sha256 or None, truncated) for one line, or None at end of input."""
    raw = stream.readline(MAX_LINE + 1)
    if not raw:
        return None
    if raw.endswith(b"\n") or len(raw) <= MAX_LINE:
        body = raw[:-1] if raw.endswith(b"\n") else raw
        return body.decode("utf-8", "surrogateescape"), len(body), None, False
    # longer than MAX_LINE: consume the rest of the line, keep only its length, hash and start
    digest, length, head = hashlib.sha256(), 0, b""
    chunk = raw
    while True:
        done = chunk.endswith(b"\n")
        part = chunk[:-1] if done else chunk
        digest.update(part)
        length += len(part)
        if len(head) < 4 * TRUNCATED_CHARS:
            head += part[:4 * TRUNCATED_CHARS - len(head)]
        if done:
            break
        chunk = stream.readline(MAX_LINE + 1)
        if not chunk:
            break
    text = head.decode("utf-8", "replace")[:TRUNCATED_CHARS]
    return text, length, digest.hexdigest(), True


def main():
    try:
        index, run_id = load_results()
    except StartupError as e:
        print(f"refusing to start: {e}", file=sys.stderr, flush=True)
        return 1
    transcript = Transcript()
    print(f"transcript: {transcript.rel}", file=sys.stderr, flush=True)
    session = Session(index, run_id)
    stdin, stdout = sys.stdin.buffer, sys.stdout.buffer

    def send(response):
        line = json.dumps(response, ensure_ascii=False)
        transcript.write("out", line)
        stdout.write(line.encode("utf-8") + b"\n")
        stdout.flush()

    try:
        while True:
            got = read_line(stdin)
            if got is None:
                break
            text, length, digest, truncated = got
            if truncated:
                transcript.write("in", text, truncated=True, length=length, sha256=digest)
                send(error(None, INVALID_REQUEST, f"Invalid Request: message longer than {MAX_LINE} bytes"))
                continue
            transcript.write("in", text)
            if not text.strip():
                continue  # blank line: not a message
            try:
                msg = json.loads(text)
            except ValueError:
                send(error(None, PARSE_ERROR, "Parse error: not valid JSON"))
                continue
            try:
                response = session.handle(msg)
            except Exception:
                traceback.print_exc(file=sys.stderr)
                reply_id = msg.get("id") if isinstance(msg, dict) else None
                response = error(reply_id if isinstance(reply_id, (str, int)) else None, INTERNAL_ERROR,
                                 "Internal error")
            if response is not None:
                send(response)
    finally:
        transcript.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
