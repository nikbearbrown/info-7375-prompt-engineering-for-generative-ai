"""JS3 step 2.3: the filter as one MCP tool, written from scratch (stdlib only, no MCP SDK).

Usage (from js3-filter-tool-score/):
    .venv/bin/python tools/mcp_server.py [--log-dir evidence/mcp]

Transport: JSON-RPC 2.0 over stdio, one JSON message per line (stdin in, stdout out).
Methods answered:
    initialize                -> protocolVersion, capabilities {"tools": {}}, serverInfo
    notifications/initialized -> no reply (no notification ever gets a reply)
    ping                      -> {} (MCP base protocol; either side may ping)
    tools/list                -> exactly one tool, score_posting
    tools/call score_posting  -> content [{type: "text", text: <JSON>}]; bad input -> isError
    anything else             -> -32601; malformed JSON -> -32700; not a request object -> -32600

What it touches (assignment rule: nothing that can send or change data outside my folder):
    reads   evidence/runs/live-text-1 (summary.json + raw/), FILTER.md, and the persona file
            that agent.filter reads (../js1-contract-and-watch/persona/cole-palmer.example.json),
            plus the Python source it imports
    writes  only evidence/mcp/transcript-<run>.jsonl (or a --log-dir inside evidence/mcp/)
    network none: this module imports no network code, and agent.filter imports none either
The transcript holds every message in both directions with a UTC timestamp and direction,
plus a start and an end record. Environment variables are never read into the log.

Scoring is agent.filter.evaluate with the v0.2 rule mode, unchanged. Before scoring, FILTER.md
is hashed as a git blob and must equal the blob frozen at commit f3edf99; otherwise the call
is refused with isError, so the tool can't silently score under rules that have moved.
"""

import sys

if __name__ == "__main__":
    sys.dont_write_bytecode = True  # no import may write __pycache__ outside evidence/mcp/

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import secrets  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
from pathlib import Path  # noqa: E402

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from agent import filter as flt  # noqa: E402
from agent.postings import RunError, load_run  # noqa: E402

SERVER_INFO = {"name": "js3-filter", "version": "0.1.0"}
# Newest first. A client's version from this list is echoed; any other gets the newest.
PROTOCOL_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")

RUN_DIR = PROJECT_DIR / "evidence" / "runs" / "live-text-1"
FILTER_MD = PROJECT_DIR / "FILTER.md"
PERSONA = flt.DEFAULT_PERSONA
LOG_ROOT = PROJECT_DIR / "evidence" / "mcp"
RULE_MODE = "v0.2"
FROZEN_COMMIT = "f3edf99"
# `git rev-parse f3edf99:fall-2026/tushar-p/js3-filter-tool-score/FILTER.md`, run 2026-11-24.
FROZEN_FILTER_BLOB = "aa49e255b311a028bd214ad995cbda99b0cf5f83"

BOARDS = ("greenhouse/stripe", "ashby/notion", "ashby/linear")
TOOL_NAME = "score_posting"
TOOL = {
    "name": TOOL_NAME,
    "description": ("Score one saved posting against FILTER.md v0.2. Read-only; uses the committed "
                    "corpus evidence/runs/live-text-1; no network. "
                    "Also reads the fictional persona file ../js1-contract-and-watch/persona/cole-palmer.example.json. "
                    "Every call's arguments and results are logged to evidence/mcp/."),
    "inputSchema": {
        "type": "object",
        "properties": {
            "board": {"type": "string", "enum": list(BOARDS)},
            "posting_id": {"type": "string"},
        },
        "required": ["board", "posting_id"],
        "additionalProperties": False,
    },
    # Hints only (MCP schema 2025-11-25). Read as the tool's effect on the corpus and the user's files:
    # a call changes neither. The server process does append each message to its transcript in
    # evidence/mcp/ (said in the description); under a reading that counts that log, readOnlyHint
    # and idempotentHint would be false. destructiveHint/idempotentHint only carry meaning when
    # readOnlyHint is false.
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True,
                    "openWorldHint": False},
}

PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS, INTERNAL_ERROR = (
    -32700, -32600, -32601, -32602, -32603)


class ToolInputError(Exception):
    """A tools/call the tool can't answer: reported as isError, never as a crash."""


class InvalidParams(Exception):
    """A request whose params break the protocol (JSON-RPC -32602)."""


# ---------- the tool ----------

def git_blob_sha1(data: bytes) -> str:
    """The hash git gives a file's contents (`git hash-object`), computed without running git."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def rules_version(filter_md: Path = FILTER_MD) -> dict:
    """The rules this tool scores under; raises ToolInputError if FILTER.md isn't the frozen v0.2."""
    try:
        blob = git_blob_sha1(filter_md.read_bytes())
    except OSError as err:
        raise ToolInputError(f"cannot read FILTER.md: {err.strerror}") from None
    if blob != FROZEN_FILTER_BLOB:
        raise ToolInputError(f"FILTER.md (git blob {blob}) is not the v0.2 frozen at {FROZEN_COMMIT} "
                             f"(blob {FROZEN_FILTER_BLOB}); refusing to score under changed rules")
    return {"mode": RULE_MODE, "changes": sorted(flt.RULE_MODES[RULE_MODE]), "contract": flt.CONTRACT_V02,
            "filter_md_git_blob": blob, "frozen_commit": FROZEN_COMMIT}


class Corpus:
    """The saved postings and persona, loaded on the first tools/call and kept for the session."""

    def __init__(self, run_dir: Path = RUN_DIR, persona_path: Path = PERSONA):
        self.run_dir, self.persona_path = run_dir, persona_path
        self._postings = None
        self._persona = None
        self.run_id = None

    def _load(self) -> None:
        try:
            persona = flt.load_persona(self.persona_path)
            postings, _failures = load_run(self.run_dir, with_blocks=True)
            run_id = json.loads((self.run_dir / "summary.json").read_text())["run_id"]
        except (flt.PersonaError, RunError, OSError, KeyError, ValueError) as err:
            raise ToolInputError(f"cannot load the saved corpus: {err}") from None
        self._postings = {(p["board"], str(p["id"])): p for p in postings}
        self._persona, self.run_id = persona, run_id

    def score(self, board: str, posting_id: str) -> dict:
        rules = rules_version()
        if self._postings is None:
            self._load()
        posting = self._postings.get((board, posting_id))
        if posting is None:
            raise ToolInputError(f"no posting with id {posting_id!r} on board {board!r} in "
                                 f"evidence/runs/live-text-1")
        result = flt.evaluate(posting, self._persona, flt.RULE_MODES[RULE_MODE])
        return {
            "board": result["board"], "posting_id": posting_id, "title": result["title"],
            "verdict": result["verdict"],
            "gates": result["gates"],
            "first_failing_gate": result["first_failing_gate"],
            "first_unknown_gate": result["first_unknown_gate"],
            "score": result["score"], "keep_threshold": flt.KEEP_THRESHOLD,
            "near_threshold": result["near_threshold"],
            "text_status": result["text_status"], "text_chars": result["text_chars"],
            "rules": rules,
            "corpus": {"path": "evidence/runs/live-text-1", "run_id": self.run_id},
            "note": ("Output of the FILTER.md v0.2 rules on saved posting text; not a fact about the job, "
                     "and not checked by a person."),
        }


def check_arguments(arguments) -> tuple[str, str]:
    if not isinstance(arguments, dict):
        raise ToolInputError("arguments must be an object with board and posting_id")
    extra = sorted(set(arguments) - {"board", "posting_id"})
    if extra:
        raise ToolInputError(f"unexpected argument(s): {', '.join(extra)}")
    board, posting_id = arguments.get("board"), arguments.get("posting_id")
    if not isinstance(board, str) or board not in BOARDS:
        raise ToolInputError(f"unknown board {board!r}; choose one of {', '.join(BOARDS)}")
    if not isinstance(posting_id, str) or not posting_id.strip():
        raise ToolInputError("posting_id must be a non-empty string")
    return board, posting_id.strip()


# ---------- JSON-RPC ----------

def _error(id_, code: int, message: str, data=None) -> dict:
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": id_, "error": err}


def _valid_id(id_) -> bool:
    return isinstance(id_, str) or (isinstance(id_, int) and not isinstance(id_, bool))


class Server:
    def __init__(self, corpus: Corpus | None = None):
        self.corpus = corpus or Corpus()
        self.methods = {"initialize": self.initialize, "ping": self.ping,
                        "tools/list": self.tools_list, "tools/call": self.tools_call}

    def initialize(self, params: dict) -> dict:
        asked = params.get("protocolVersion")
        version = asked if asked in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0]
        return {"protocolVersion": version, "capabilities": {"tools": {}}, "serverInfo": SERVER_INFO}

    def ping(self, params: dict) -> dict:
        return {}

    def tools_list(self, params: dict) -> dict:
        return {"tools": [TOOL]}

    def tools_call(self, params: dict) -> dict:
        name = params.get("name")
        if name != TOOL_NAME:
            raise InvalidParams(f"unknown tool {name!r}")
        try:
            board, posting_id = check_arguments(params.get("arguments", {}))
            text = json.dumps(self.corpus.score(board, posting_id), ensure_ascii=False)
            return {"content": [{"type": "text", "text": text}], "isError": False}
        except ToolInputError as err:
            return {"content": [{"type": "text", "text": str(err)}], "isError": True}

    def handle(self, raw: bytes) -> dict | None:
        """One inbound line -> one reply, or None for a notification or a client's response."""
        try:
            msg = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as err:
            return _error(None, PARSE_ERROR, "Parse error", str(err))
        if not isinstance(msg, dict):
            return _error(None, INVALID_REQUEST, "Invalid Request", "expected one JSON object per line (no batches)")
        if "method" not in msg and ("result" in msg or "error" in msg):
            return None  # a response to a request this server never sends; nothing to answer
        id_ = msg.get("id")
        if msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str) or ("id" in msg and not _valid_id(id_)):
            return _error(id_ if _valid_id(id_) else None, INVALID_REQUEST, "Invalid Request")
        if "id" not in msg:
            return None  # notifications (notifications/initialized, cancelled, unknown ones) get no reply
        handler = self.methods.get(msg["method"])
        if handler is None:
            return _error(id_, METHOD_NOT_FOUND, "Method not found", msg["method"])
        params = msg.get("params", {})
        if not isinstance(params, dict):
            return _error(id_, INVALID_PARAMS, "Invalid params", "params must be an object")
        try:
            return {"jsonrpc": "2.0", "id": id_, "result": handler(params)}
        except InvalidParams as err:
            return _error(id_, INVALID_PARAMS, "Invalid params", str(err))
        except Exception as err:  # never crash the session; never send a traceback to the client
            return _error(id_, INTERNAL_ERROR, "Internal error", type(err).__name__)


# ---------- transcript ----------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class Transcript:
    """Append-only JSONL: one record per message, flushed as it is written."""

    def __init__(self, log_dir: Path, run: str):
        self.path = log_dir / f"transcript-{run}.jsonl"
        self._fh = open(self.path, "x", encoding="utf-8")  # "x": never overwrite an earlier run

    def write(self, record: dict) -> None:
        self._fh.write(json.dumps({"ts": _now(), **record}, ensure_ascii=False) + "\n")
        self._fh.flush()

    def inbound(self, raw: bytes) -> None:
        try:
            message = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            message = None
        self.write({"direction": "client->server", "raw": raw.decode("utf-8", errors="replace"),
                    "message": message})

    def outbound(self, message: dict) -> None:
        self.write({"direction": "server->client", "message": message})

    def close(self) -> None:
        self._fh.close()


def resolve_log_dir(value) -> Path:
    path = (PROJECT_DIR / value).resolve() if not Path(value).is_absolute() else Path(value).resolve()
    if not path.is_relative_to(LOG_ROOT.resolve()):
        raise ValueError(f"--log-dir must be inside {LOG_ROOT}, got {path}")
    return path


def serve(stdin, stdout, transcript: Transcript, server: Server) -> None:
    for raw in stdin:
        raw = raw.rstrip(b"\r\n")
        if not raw.strip():
            continue
        transcript.inbound(raw)
        reply = server.handle(raw)
        if reply is not None:
            transcript.outbound(reply)
            stdout.write(json.dumps(reply, ensure_ascii=False).encode("utf-8") + b"\n")
            stdout.flush()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="tools/mcp_server.py", description="JS3 filter as one MCP tool (stdio).")
    parser.add_argument("--log-dir", default="evidence/mcp", help="transcript folder; must be inside evidence/mcp/")
    args = parser.parse_args(argv)
    try:
        log_dir = resolve_log_dir(args.log_dir)
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    log_dir.mkdir(parents=True, exist_ok=True)
    run = f"run-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{secrets.token_hex(3)}"
    transcript = Transcript(log_dir, run)
    transcript.write({"direction": "meta", "event": "start", "run": run, "server": SERVER_INFO,
                      "protocol_versions": list(PROTOCOL_VERSIONS)})
    end = "stdin closed"
    try:
        serve(sys.stdin.buffer, sys.stdout.buffer, transcript, Server())
    except (BrokenPipeError, KeyboardInterrupt) as err:
        end = type(err).__name__
    finally:
        transcript.write({"direction": "meta", "event": "end", "reason": end})
        transcript.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
