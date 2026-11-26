"""A Model Context Protocol tool server, written from scratch (stdlib only).

Transport: stdio, one JSON-RPC 2.0 message per line (MCP "stdio" transport). Methods:
``initialize``, ``notifications/initialized``, ``ping``, ``tools/list``, ``tools/call``.
One tool, ``score_posting``: read-only, no network, scores a posting the agent already
collected with FILTER.md and returns the C1–C5 claims (FILTER.md §2).

What it can touch: it reads the saved raw responses, FILTER.md and the persona; it
writes only the optional transcript, which must be a ``.jsonl`` file under
``data/js3/mcp/``. It opens no socket and starts no process.

Run: ``uv run python -m job_search_agent.js3 serve``, optionally with
``--transcript data/js3/mcp/x.jsonl``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import IO, Any

from job_search_agent.js3.claims import justify
from job_search_agent.js3.corpus import EXPECTED_BOARDS, Entry, load_corpus, load_inputs
from job_search_agent.js3.filter import load_filter, score
from job_search_agent.resume import default_project_root

PROTOCOL_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
"""Supported MCP revisions, newest first. The tool shape is the same in all four."""

SERVER_INFO = {
    "name": "jsa-js3",
    "title": "Job-Search Agent 3 (read-only)",
    "version": "0.3",
}
MAX_LINE_BYTES = 1_000_000
_ID = re.compile(
    r"[0-9]{1,12}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
)

TOOL: dict[str, Any] = {
    "name": "score_posting",
    "title": "Score one collected job posting",
    "description": (
        "Read-only. Scores one job posting that the agent already collected (no "
        "network access) with the filter in FILTER.md, for the fictional job seeker "
        "Kiran Joshi. Returns the score and each rule's points, whether the filter "
        "keeps it, and the claims C1-C5 with a supported/contradicted/insufficient "
        "label and the quoted span of the posting each label rests on. It is not a "
        "recommendation: whether a posting is worth applying to is the user's "
        "decision. It never applies, contacts anyone, logs in, or changes any file."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "board": {
                "type": "string",
                "enum": list(EXPECTED_BOARDS),
                "description": "Board as provider/token.",
            },
            "posting_id": {
                "type": "string",
                "description": "Greenhouse numeric ID or Ashby UUID.",
                "pattern": "^([0-9]{1,12}|"
                "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$",
            },
        },
        "required": ["board", "posting_id"],
        "additionalProperties": False,
    },
    "annotations": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
}

PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS = (
    -32700,
    -32600,
    -32601,
    -32602,
)


def _error(msg_id: object, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def _result(msg_id: object, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


class Server:
    """The protocol state machine; ``handle`` takes one parsed message."""

    def __init__(self, root: Path) -> None:
        self._root = root
        self._initialized = False
        self._entries: dict[str, Entry] | None = None

    def _corpus(self) -> dict[str, Entry]:
        # loaded on the first call, so initialize answers fast
        if self._entries is None:
            self._entries = load_corpus(self._root).by_key()
        return self._entries

    def score_posting(self, args: object) -> dict[str, Any]:
        """Runs the tool; returns an MCP ``CallToolResult``."""
        if not isinstance(args, dict) or set(args) != {"board", "posting_id"}:
            return _tool_error("arguments must be exactly {board, posting_id}")
        board, pid = args["board"], args["posting_id"]
        if board not in EXPECTED_BOARDS:
            return _tool_error(f"board must be one of {list(EXPECTED_BOARDS)}")
        if not isinstance(pid, str) or not _ID.fullmatch(pid):
            return _tool_error(
                "posting_id must be a Greenhouse numeric ID or an Ashby UUID"
            )
        entry = self._corpus().get(f"{board}/{pid}")
        if entry is None:
            return _tool_error(
                f"no collected posting {board}/{pid}; the tool only sees saved raws"
            )
        spec = load_filter(self._root / "FILTER.md")
        s = score(entry.posting, entry.key, entry.board, spec, load_inputs(self._root))
        j = justify(s)
        out = {
            "key": entry.key,
            "title": entry.posting.title.strip(),
            "url": entry.url,
            "filter_version": spec.version,
            "kept": s.kept,
            "score": s.total,
            "threshold": spec.threshold,
            "points": s.points,
            "answer": j.answer,
            "claims": [c for c in j.to_dict()["claims"]],
            "source": entry.raw_rel,
        }
        return {
            "content": [{"type": "text", "text": json.dumps(out, ensure_ascii=False)}],
            "structuredContent": out,
            "isError": False,
        }

    def handle(self, msg: object) -> dict[str, Any] | None:
        """Answers one message; returns None for notifications."""
        if (
            not isinstance(msg, dict)
            or msg.get("jsonrpc") != "2.0"
            or not isinstance(msg.get("method"), str)
        ):
            msg_id = msg.get("id") if isinstance(msg, dict) else None
            return _error(
                msg_id,
                INVALID_REQUEST,
                "not a JSON-RPC 2.0 request (batches are not supported)",
            )
        method, params = msg["method"], msg.get("params") or {}
        if "id" not in msg:  # a notification never gets a reply
            if method == "notifications/initialized":
                self._initialized = True
            return None
        msg_id = msg["id"]
        if isinstance(msg_id, bool) or not isinstance(msg_id, str | int):
            return _error(None, INVALID_REQUEST, "id must be a string or an integer")
        if method == "ping":
            return _result(msg_id, {})
        if method == "initialize":
            asked = params.get("protocolVersion") if isinstance(params, dict) else None
            version = asked if asked in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0]
            return _result(
                msg_id,
                {
                    "protocolVersion": version,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": SERVER_INFO,
                    "instructions": (
                        "One read-only tool over postings already collected. "
                        "It scores; it does not decide."
                    ),
                },
            )
        if not self._initialized:
            return _error(
                msg_id,
                INVALID_REQUEST,
                "send initialize and notifications/initialized first",
            )
        if method == "tools/list":
            return _result(msg_id, {"tools": [TOOL]})
        if method == "tools/call":
            if not isinstance(params, dict) or params.get("name") != TOOL["name"]:
                return _error(
                    msg_id,
                    INVALID_PARAMS,
                    f"unknown tool; the only tool is {TOOL['name']}",
                )
            return _result(msg_id, self.score_posting(params.get("arguments")))
        return _error(msg_id, METHOD_NOT_FOUND, f"method not supported: {method}")


def _tool_error(text: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "isError": True}


def serve(
    server: Server, stdin: IO[bytes], stdout: IO[bytes], log: Callable[[str, str], None]
) -> None:
    """Reads lines until EOF and writes one reply line per request."""
    for raw in stdin:
        if len(raw) > MAX_LINE_BYTES:
            reply: dict[str, Any] | None = _error(
                None, INVALID_REQUEST, "message too large"
            )
            log("client->server", f"<{len(raw)} bytes, dropped>")
        else:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            log("client->server", line)
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                reply = _error(None, PARSE_ERROR, "invalid JSON")
            else:
                try:
                    reply = server.handle(msg)
                except Exception as exc:  # noqa: BLE001 - a crash must not kill the session
                    is_request = isinstance(msg, dict) and "id" in msg
                    msg_id = msg.get("id") if isinstance(msg, dict) else None
                    reply = (  # a notification never gets a reply, even on a crash
                        _error(msg_id, -32603, f"internal error: {type(exc).__name__}")
                        if is_request
                        else None
                    )
        if reply is not None:
            out = json.dumps(reply, ensure_ascii=False)
            log("server->client", out)
            stdout.write(out.encode("utf-8") + b"\n")
            stdout.flush()


def transcript_logger(root: Path, rel: str | None) -> Callable[[str, str], None]:
    """Appends each line, both directions, with a UTC time, to a transcript file.

    The file must be a ``.jsonl`` file under data/js3/mcp/.
    """
    if rel is None:
        return lambda direction, line: None
    path = (root / rel).resolve()
    allowed = (root / "data" / "js3" / "mcp").resolve()
    if not path.is_relative_to(allowed) or path.suffix != ".jsonl":
        raise SystemExit("--transcript must be a .jsonl file under data/js3/mcp/")
    path.parent.mkdir(parents=True, exist_ok=True)

    def log(direction: str, line: str) -> None:
        stamp = datetime.now(UTC).isoformat(timespec="milliseconds")
        with path.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {"utc": stamp, "dir": direction, "line": line}, ensure_ascii=False
                )
                + "\n"
            )

    return log


def main(argv: list[str] | None = None) -> int:
    """Entry point for ``python -m job_search_agent.js3 serve``."""
    parser = argparse.ArgumentParser(prog="serve")
    parser.add_argument("--transcript", default=None, help="data/js3/mcp/<name>.jsonl")
    args = parser.parse_args(argv)
    root = default_project_root()
    serve(
        Server(root),
        sys.stdin.buffer,
        sys.stdout.buffer,
        transcript_logger(root, args.transcript),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
