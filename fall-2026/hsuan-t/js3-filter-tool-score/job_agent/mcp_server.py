"""A dependency-free stdio MCP server with one read-only tool, score_posting (see MCP.md, ADR 0003).

Run: .venv/bin/python -m job_agent.mcp_server

JSON-RPC 2.0, one message per line on stdin/stdout. stdout carries only JSON-RPC messages; logs go
to stderr. Every message in and out is appended to transcripts/mcp-<UTC date>.jsonl (or the folder
named by JSA_MCP_TRANSCRIPT_DIR). The tool only reads saved raw files under evidence/raw: it never
fetches, so this module imports no networking or subprocess modules.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import inputs
from .common.paths import Paths
from .judges import rule
from .watch import board_list

SUPPORTED_VERSIONS = ("2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25")
FALLBACK_VERSION = "2025-06-18"
SERVER_INFO = {"name": "job-search-agent", "version": "js3"}
TOOL_NAME = "score_posting"
TRANSCRIPT_ENV = "JSA_MCP_TRANSCRIPT_DIR"

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


def log(text: str) -> None:
    print(f"mcp_server: {text}", file=sys.stderr, flush=True)


class Transcript:
    """Appends {ts, dir, msg} lines; the file name follows the UTC date of each message."""

    def __init__(self, folder: Path):
        self.folder = folder

    def write(self, direction: str, msg) -> None:
        now = datetime.now(timezone.utc)
        entry = {"ts": now.isoformat().replace("+00:00", "Z"), "dir": direction, "msg": msg}
        try:
            self.folder.mkdir(parents=True, exist_ok=True)
            path = self.folder / f"mcp-{now.strftime('%Y-%m-%d')}.jsonl"
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as e:  # a transcript problem must not take the server down
            log(f"transcript write failed: {e}")


class Server:
    def __init__(self, paths: Paths | None = None):
        self.paths = paths or Paths()
        self._criteria = None
        try:
            self.boards = {b.name: b for b in board_list.load(self.paths.boards)}
        except Exception as e:  # noqa: BLE001 - a bad board list leaves an empty enum, not a crash
            log(f"board list not loaded: {e}")
            self.boards = {}
        self.board_names = sorted(n for n in self.boards if self._newest_raw(n) is not None)

    # --- data ---------------------------------------------------------------------------------

    def _newest_raw(self, board: str) -> Path | None:
        root = self.paths.out / "evidence" / "raw"
        files = sorted(root.glob(f"*/{board}_content.json"), key=lambda p: p.parent.name)
        return files[-1] if files else None

    def criteria(self):
        if self._criteria is None:
            p = self.paths
            self._criteria = inputs.load_criteria(p.default_resume, p.default_profile, p)
        return self._criteria

    # --- tool ---------------------------------------------------------------------------------

    def tool(self) -> dict:
        return {
            "name": TOOL_NAME,
            "title": "Score a saved job posting",
            "description": (
                "Read-only. Finds a posting in the newest saved raw file of a board and judges it "
                "with the rule judge and the default criteria. Never fetches or writes postings."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "board": {"type": "string", "enum": list(self.board_names)},
                    "posting_id": {"type": "string"},
                },
                "required": ["board", "posting_id"],
                "additionalProperties": False,
            },
            "annotations": {"readOnlyHint": True, "openWorldHint": False},
        }

    def check_arguments(self, args) -> str | None:
        """Returns a message when args break the input schema, else None."""
        if not isinstance(args, dict):
            return "arguments must be an object"
        extra = sorted(set(args) - {"board", "posting_id"})
        if extra:
            return f"unexpected arguments: {', '.join(extra)}"
        for key in ("board", "posting_id"):
            if key not in args:
                return f"missing argument: {key}"
            if not isinstance(args[key], str):
                return f"{key} must be a string"
        if args["board"] not in self.board_names:
            return f"board must be one of: {', '.join(self.board_names)}"
        return None

    def score_posting(self, board: str, posting_id: str) -> dict:
        raw = self._newest_raw(board)
        if raw is None:
            return _tool_error(f"no saved raw file for board {board}")
        try:
            postings = self.boards[board].adapter.parse(raw.read_bytes())
        except Exception as e:  # noqa: BLE001
            return _tool_error(f"could not read {self.paths.show(raw)}: {e}")
        posting = next((p for p in postings if str(p.id) == posting_id), None)
        if posting is None:
            return _tool_error(f"posting {posting_id} not found in {self.paths.show(raw)}")
        verdict = json.loads(json.dumps(rule.judge(posting, self.criteria()).verdict))
        lines = [f"{posting.title} ({board} #{posting.id})", f"verdict: {verdict['verdict']}"]
        if verdict.get("error_message"):
            lines.append(f"error: {verdict['error_message']}")
        for j in verdict["justification"]:
            lines.append(f"- {j['posting_field']} vs {j['compared_to']}: {j['result']}")
        lines.append(f"source: {self.paths.show(raw)}")
        return {"content": [{"type": "text", "text": "\n".join(lines)}],
                "structuredContent": verdict, "isError": False}

    # --- JSON-RPC -----------------------------------------------------------------------------

    def handle(self, msg) -> dict | None:
        """One parsed message -> the response, or None for a notification."""
        if not isinstance(msg, dict):
            return _error(None, INVALID_REQUEST, "request must be a JSON object")
        has_id = "id" in msg
        msg_id = msg.get("id")
        if has_id and not (msg_id is None or isinstance(msg_id, (str, int)) and not isinstance(msg_id, bool)):
            return _error(None, INVALID_REQUEST, "id must be a string or a number")
        method = msg.get("method")
        if msg.get("jsonrpc") != "2.0" or not isinstance(method, str):
            if not has_id:
                return None  # a response or junk without an id: nothing to answer
            return _error(msg_id, INVALID_REQUEST, "not a JSON-RPC 2.0 request")
        if not has_id:
            return None  # notifications (initialized, cancelled, ...) get no reply
        params = msg.get("params", {})
        if params is None:
            params = {}
        if not isinstance(params, dict):
            return _error(msg_id, INVALID_PARAMS, "params must be an object")
        try:
            return self._dispatch(msg_id, method, params)
        except Exception as e:  # noqa: BLE001 - never crash on one request
            log(f"internal error on {method}: {e!r}")
            return _error(msg_id, INTERNAL_ERROR, f"internal error: {e}")

    def _dispatch(self, msg_id, method: str, params: dict) -> dict:
        if method == "initialize":
            asked = params.get("protocolVersion")
            version = asked if asked in SUPPORTED_VERSIONS else FALLBACK_VERSION
            return _result(msg_id, {"protocolVersion": version,
                                    "capabilities": {"tools": {"listChanged": False}},
                                    "serverInfo": dict(SERVER_INFO)})
        if method == "ping":
            return _result(msg_id, {})
        if method == "tools/list":
            return _result(msg_id, {"tools": [self.tool()]})
        if method == "tools/call":
            name = params.get("name")
            if name != TOOL_NAME:
                return _error(msg_id, INVALID_PARAMS, f"unknown tool: {name}")
            args = params.get("arguments", {})
            problem = self.check_arguments(args)
            if problem:
                return _error(msg_id, INVALID_PARAMS, problem)
            return _result(msg_id, self.score_posting(args["board"], args["posting_id"]))
        return _error(msg_id, METHOD_NOT_FOUND, f"method not found: {method}")


def _result(msg_id, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _error(msg_id, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def _tool_error(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}], "isError": True}


def serve(stdin, stdout, server: Server, transcript: Transcript) -> None:
    for raw in stdin:
        line = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except (json.JSONDecodeError, ValueError) as e:
            transcript.write("in", line)
            response = _error(None, PARSE_ERROR, f"parse error: {e}")
        else:
            transcript.write("in", msg)
            response = server.handle(msg)
        if response is not None:
            transcript.write("out", response)
            stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            stdout.flush()


def main() -> int:
    paths = Paths()
    folder = os.environ.get(TRANSCRIPT_ENV) or str(paths.out / "transcripts")
    transcript = Transcript(Path(folder))
    server = Server(paths)
    log(f"ready; boards: {', '.join(server.board_names) or '(none)'}; transcript: {folder}")
    out = open(sys.stdout.fileno(), "w", encoding="utf-8", closefd=False)
    try:
        serve(sys.stdin.buffer, out, server, transcript)
    except KeyboardInterrupt:
        pass
    except BrokenPipeError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
