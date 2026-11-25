"""A small Model Context Protocol tool server, written from scratch (stdio, JSON-RPC 2.0).

Implements only: initialize, notifications/initialized, ping, tools/list, tools/call.
One line in = one JSON-RPC message; one line out = one response. Nothing else is written
to stdout. Every inbound and outbound line is appended, byte-for-byte as text, to a transcript
file that must sit inside this assignment folder.

The one tool is read-only: it scores one posting from the frozen corpus with the filter.
This module imports no network, subprocess or file-writing code besides the transcript.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

SERVER_INFO = {"name": "js3-posting-scorer", "version": "1.0.0"}
SUPPORTED_VERSIONS = ["2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"]
FOLDER = Path(__file__).resolve().parent.parent

PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS = -32700, -32600, -32601, -32602


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class Transcript:
    """Appends {"utc", "dir", "line"} records. Refuses any path outside FOLDER."""

    def __init__(self, path: Optional[Path], folder: Path = FOLDER):
        self.path = None
        if path is not None:
            resolved = Path(path).resolve()
            if folder.resolve() not in resolved.parents:
                raise ValueError(f"transcript path {resolved} is outside {folder}")
            resolved.parent.mkdir(parents=True, exist_ok=True)
            self.path = resolved

    def log(self, direction: str, line: str) -> None:
        if self.path is None:
            return
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"utc": utc(), "dir": direction, "line": line}, ensure_ascii=False) + "\n")


class Tool:
    def __init__(self, name: str, description: str, input_schema: dict, handler: Callable[[dict], dict]):
        self.name, self.description, self.input_schema, self.handler = name, description, input_schema, handler

    def declaration(self) -> dict:
        return {"name": self.name, "description": self.description, "inputSchema": self.input_schema,
                "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False}}


def _validate(args, schema: dict) -> Optional[str]:
    """The small subset of JSON Schema this server declares: object, required, string, no extras."""
    if not isinstance(args, dict):
        return "arguments must be an object"
    props = schema.get("properties", {})
    for name in schema.get("required", []):
        if name not in args:
            return f"missing required argument {name!r}"
    if schema.get("additionalProperties") is False:
        extra = sorted(set(args) - set(props))
        if extra:
            return f"unexpected argument(s) {extra}"
    for name, value in args.items():
        if props.get(name, {}).get("type") == "string" and not isinstance(value, str):
            return f"argument {name!r} must be a string"
    return None


class Server:
    def __init__(self, tools: list, transcript: Transcript = None):
        self.tools = {t.name: t for t in tools}
        self.transcript = transcript or Transcript(None)
        self.initialized = False

    # -- message handling -------------------------------------------------------------
    def handle_line(self, line: str) -> Optional[str]:
        """One inbound line -> one outbound line, or None for a notification."""
        self.transcript.log("client->server", line)
        reply = self._dispatch(line)
        if reply is None:
            return None
        out = json.dumps(reply, ensure_ascii=False, separators=(",", ":"))
        self.transcript.log("server->client", out)
        return out

    def _dispatch(self, line: str) -> Optional[dict]:
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as exc:
            return _error(None, PARSE_ERROR, f"parse error: {exc}")
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
            return _error(msg.get("id") if isinstance(msg, dict) else None, INVALID_REQUEST, "not a JSON-RPC 2.0 request")
        method, params, mid = msg["method"], msg.get("params") or {}, msg.get("id")
        is_notification = "id" not in msg
        if is_notification:
            if method == "notifications/initialized":
                self.initialized = True
            return None  # notifications never get a reply, known or not
        if method == "initialize":
            return _result(mid, self._initialize(params))
        if method == "ping":
            return _result(mid, {})
        if method == "tools/list":
            return _result(mid, {"tools": [t.declaration() for t in self.tools.values()]})
        if method == "tools/call":
            return self._call(mid, params)
        return _error(mid, METHOD_NOT_FOUND, f"method {method!r} is not implemented by this server")

    def _initialize(self, params: dict) -> dict:
        asked = params.get("protocolVersion") if isinstance(params, dict) else None
        version = asked if asked in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0]
        return {"protocolVersion": version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
                "instructions": "Read-only. Scores one posting from a frozen 2026-11-09 corpus. "
                                "It cannot fetch, apply, email, message, log in, or write anything."}

    def _call(self, mid, params: dict) -> dict:
        if not isinstance(params, dict) or not isinstance(params.get("name"), str):
            return _error(mid, INVALID_PARAMS, "tools/call needs a string 'name'")
        tool = self.tools.get(params["name"])
        if tool is None:
            return _error(mid, INVALID_PARAMS, f"unknown tool {params['name']!r}")
        args = params.get("arguments", {})
        problem = _validate(args, tool.input_schema)
        if problem:
            return _error(mid, INVALID_PARAMS, problem)
        try:
            payload = tool.handler(args)
            is_error = bool(payload.pop("_is_error", False)) if isinstance(payload, dict) else False
        except Exception as exc:  # a tool failure is a tool result, not a protocol failure
            payload, is_error = {"error": f"{type(exc).__name__}: {exc}"}, True
        text = json.dumps(payload, ensure_ascii=False, indent=1)
        return _result(mid, {"content": [{"type": "text", "text": text}], "isError": is_error})

    # -- stdio loop -----------------------------------------------------------------
    def serve(self, stdin=None, stdout=None) -> None:
        stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
        for raw in stdin:
            line = raw.rstrip("\r\n")
            if not line.strip():
                continue
            out = self.handle_line(line)
            if out is not None:
                stdout.write(out + "\n")
                stdout.flush()


def _result(mid, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def _error(mid, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}
