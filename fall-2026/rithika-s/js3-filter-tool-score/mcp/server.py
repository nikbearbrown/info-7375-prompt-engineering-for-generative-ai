"""priya-filter: an MCP tool server over stdio, written from scratch.

    python3 -m mcp.server --config config/filter-v1.1.json

Transport: newline-delimited JSON-RPC 2.0 on stdin/stdout. stdout carries
only JSON-RPC messages; every diagnostic goes to stderr.

Methods
    initialize                 protocolVersion echoed if supported, else
                               DEFAULT_PROTOCOL_VERSION
    notifications/initialized  no reply
    ping                       {}
    tools/list                 exactly one tool, score_posting
    tools/call                 score_posting {board, id} -> filter result

Errors
    -32700 parse error, -32600 invalid request (also: batch arrays, a second
    initialize), -32601 unknown method, -32602 bad params / unknown tool,
    -32603 internal error, -32002 any request before initialize.
    An unknown posting is a tool result with isError true, not a protocol
    error.

Paths are fixed at startup (--config, --root, --transcripts). Nothing a
client sends is ever used as a path: board must be one of the corpus boards
and id is only used as a dictionary key.

The only file the server writes is transcripts/server-<UTC>.jsonl: every
message in both directions, one JSON object per line, with its UTC time and
direction ("in" = client to server, "out" = server to client).

Read-only: the corpus is the frozen one in CORPUS.sha256 (hash-checked by
js3.corpus) and the filter is js3.filter. No network or process modules
are imported (tests/test_mcp_server.py checks this).
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from js3 import corpus as js3_corpus
from js3 import filter as js3_filter

ROOT = Path(__file__).resolve().parent.parent
SERVER_NAME = "priya-filter"
SERVER_VERSION = "1.0.0"
SUPPORTED_PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
DEFAULT_PROTOCOL_VERSION = SUPPORTED_PROTOCOL_VERSIONS[0]
TOOL_NAME = "score_posting"

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
NOT_INITIALIZED = -32002


class RpcError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def utc_now():
    return datetime.now(timezone.utc)


def utc_stamp(moment=None):
    return (moment or utc_now()).strftime("%Y%m%dT%H%M%SZ")


def open_transcript(folder, prefix):
    """Create <folder>/<prefix>-<UTC>.jsonl; never reuse an existing file."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    stamp = utc_stamp()
    for n in range(1, 1000):
        suffix = "" if n == 1 else f"-{n}"
        path = folder / f"{prefix}-{stamp}{suffix}.jsonl"
        try:
            return path, open(path, "x", encoding="utf-8")
        except FileExistsError:
            continue
    raise RuntimeError(f"cannot create a new transcript in {folder}")


class Transcript:
    """Append-only JSONL log of messages in both directions."""

    def __init__(self, handle):
        self.handle = handle

    def log(self, direction, message=None, raw=None):
        entry = {"time_utc": utc_now().isoformat(timespec="microseconds"),
                 "direction": direction}
        if message is not None:
            entry["message"] = message
        else:
            entry["raw"] = raw
        self.handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        self.handle.flush()

    def close(self):
        self.handle.close()


def corpus_boards(root):
    """Boards with a frozen file in CORPUS.sha256 (no hashing needed)."""
    return sorted(js3_corpus.board_from_filename(rel)
                  for rel, _ in js3_corpus.read_manifest(root))


def tool_definition(boards):
    return {
        "name": TOOL_NAME,
        "title": "Score one frozen-corpus posting",
        "description": (
            "Read-only. Scores one job posting from the frozen JS3 corpus "
            "(the files listed in CORPUS.sha256, hash-checked) with the "
            "filter config fixed when the server started. Returns the "
            "decision, score, rules fired and matched spans. Frozen corpus "
            "only: it never fetches anything, never reads a path you give "
            "it, and never changes any file."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "board": {"type": "string", "enum": list(boards),
                          "description": "Corpus board name."},
                "id": {"type": "string", "minLength": 1,
                       "description": "Posting id as it appears in the "
                                      "corpus."},
            },
            "required": ["board", "id"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False,
                        "idempotentHint": True, "openWorldHint": False},
    }


class Server:
    """Protocol state machine. handle() takes one parsed message and
    returns the reply (a dict) or None when no reply is due."""

    def __init__(self, config_path, root=ROOT, log=None):
        self.root = Path(root)
        self.config_path = Path(config_path)
        self.config = js3_filter.load_config(self.config_path)
        self.filter = js3_filter.Filter(self.config)
        self.boards = corpus_boards(self.root)
        self.tool = tool_definition(self.boards)
        self.initialized = False
        self._index = None
        self.log = log or (lambda text: None)

    # -- corpus ----------------------------------------------------------
    def posting(self, board, pid):
        if self._index is None:
            data = js3_corpus.load(self.root)
            self._index = {(p["board"], str(p["id"])): p
                           for p in data["postings"]}
            self.log(f"corpus loaded: {len(self._index)} postings")
        return self._index.get((board, pid))

    # -- dispatch --------------------------------------------------------
    def handle(self, msg):
        if isinstance(msg, list):
            return error_reply(None, INVALID_REQUEST,
                               "batch requests are not supported")
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":
            rid = msg.get("id") if isinstance(msg, dict) else None
            return error_reply(rid if valid_id(rid) else None,
                               INVALID_REQUEST, "not a JSON-RPC 2.0 message")
        method = msg.get("method")
        is_request = "id" in msg
        if not isinstance(method, str):
            if is_request and "result" not in msg and "error" not in msg:
                return error_reply(msg["id"] if valid_id(msg["id"]) else None,
                                   INVALID_REQUEST, "method missing")
            return None  # a response from the client: nothing to answer
        if is_request and not valid_id(msg["id"]):
            return error_reply(None, INVALID_REQUEST,
                               "id must be a string or integer")
        if not is_request:
            self.notification(method)
            return None
        rid = msg["id"]
        try:
            result = self.request(method, msg.get("params"))
        except RpcError as exc:
            return error_reply(rid, exc.code, exc.message)
        except Exception as exc:  # never crash the loop
            self.log(f"internal error on {method}: {exc!r}")
            return error_reply(rid, INTERNAL_ERROR, "internal error")
        return {"jsonrpc": "2.0", "id": rid, "result": result}

    def notification(self, method):
        if method == "notifications/initialized":
            if not self.initialized:
                self.log("initialized notification before initialize: "
                         "ignored")
            return
        self.log(f"notification ignored: {method}")

    def request(self, method, params):
        if params is not None and not isinstance(params, dict):
            raise RpcError(INVALID_PARAMS, "params must be an object")
        params = params or {}
        if method == "initialize":
            return self.initialize(params)
        if not self.initialized:
            raise RpcError(NOT_INITIALIZED,
                           "server not initialized: send initialize first")
        if method == "ping":
            return {}
        if method == "tools/list":
            return {"tools": [self.tool]}
        if method == "tools/call":
            return self.call(params)
        raise RpcError(METHOD_NOT_FOUND, f"method not found: {method}")

    def initialize(self, params):
        if self.initialized:
            raise RpcError(INVALID_REQUEST, "already initialized")
        asked = params.get("protocolVersion")
        if not isinstance(asked, str):
            raise RpcError(INVALID_PARAMS,
                           "initialize needs protocolVersion (string)")
        version = (asked if asked in SUPPORTED_PROTOCOL_VERSIONS
                   else DEFAULT_PROTOCOL_VERSION)
        self.initialized = True
        return {"protocolVersion": version,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME,
                               "version": SERVER_VERSION}}

    def call(self, params):
        allowed = {"name", "arguments", "_meta"}
        extra = sorted(set(params) - allowed)
        if extra:
            raise RpcError(INVALID_PARAMS, f"unexpected params: {extra}")
        name = params.get("name")
        if name != TOOL_NAME:
            raise RpcError(INVALID_PARAMS, f"unknown tool: {name!r}")
        args = params.get("arguments", {})
        if not isinstance(args, dict):
            raise RpcError(INVALID_PARAMS, "arguments must be an object")
        extra = sorted(set(args) - {"board", "id"})
        if extra:
            raise RpcError(INVALID_PARAMS,
                           f"unexpected arguments: {extra} (only board, id)")
        missing = [k for k in ("board", "id") if k not in args]
        if missing:
            raise RpcError(INVALID_PARAMS, f"missing arguments: {missing}")
        board, pid = args["board"], args["id"]
        if not isinstance(board, str) or board not in self.boards:
            raise RpcError(INVALID_PARAMS,
                           f"board must be one of {self.boards}")
        if not isinstance(pid, str) or not pid:
            raise RpcError(INVALID_PARAMS, "id must be a non-empty string")
        try:
            posting = self.posting(board, pid)
        except js3_corpus.CorpusError as exc:
            return tool_error(f"frozen corpus unusable: {exc}")
        if posting is None:
            return tool_error(f"no posting with id {pid!r} on board "
                              f"{board!r} in the frozen corpus")
        result = self.filter.evaluate(posting)
        payload = {
            "board": board,
            "id": pid,
            "title": posting["title"],
            "url": posting["url"],
            "config_version": result["config_version"],
            "decision": result["decision"],
            "reason": result["reason"],
            "score": result["score"],
            "rules_fired": result["fired"],
            "matched_spans": result["matches"],
        }
        return {"content": [{"type": "text",
                             "text": json.dumps(payload,
                                                ensure_ascii=False)}],
                "isError": False}


def valid_id(rid):
    return isinstance(rid, str) or (isinstance(rid, int)
                                    and not isinstance(rid, bool))


def error_reply(rid, code, message):
    return {"jsonrpc": "2.0", "id": rid,
            "error": {"code": code, "message": message}}


def tool_error(text):
    return {"content": [{"type": "text", "text": text}], "isError": True}


def serve(server, stdin, stdout, transcript):
    """Read newline-delimited JSON-RPC until EOF."""
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as exc:
            transcript.log("in", raw=line)
            reply = error_reply(None, PARSE_ERROR, f"parse error: {exc.msg}")
        else:
            transcript.log("in", message=msg)
            reply = server.handle(msg)
        if reply is not None:
            transcript.log("out", message=reply)
            stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            stdout.flush()


def main(argv=None, stdin=None, stdout=None, stderr=None):
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", required=True,
                        help="filter config, fixed for the server's life")
    parser.add_argument("--root", default=str(ROOT),
                        help="project folder holding CORPUS.sha256")
    parser.add_argument("--transcripts", default=None,
                        help="transcript folder (default <root>/transcripts)")
    args = parser.parse_args(argv)

    def log(text):
        print(f"[{SERVER_NAME}] {text}", file=stderr, flush=True)

    try:
        server = Server(args.config, args.root, log=log)
    except (OSError, ValueError, js3_corpus.CorpusError) as exc:
        log(f"cannot start: {exc}")
        return 2
    folder = args.transcripts or Path(args.root) / "transcripts"
    path, handle = open_transcript(folder, "server")
    transcript = Transcript(handle)
    log(f"config {args.config} (v{server.config['version']}); boards "
        f"{server.boards}; transcript {path}")
    try:
        serve(server, stdin, stdout, transcript)
    finally:
        transcript.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
