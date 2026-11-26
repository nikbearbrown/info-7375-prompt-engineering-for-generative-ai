"""A read-only MCP-shaped tool server offering one capability: `score_posting` (FILTER.md section 7).

Usage: .venv/bin/python -m jsfilter.mcp_server [--root REPO_ROOT]

Transport: newline-delimited JSON-RPC 2.0 on stdin/stdout (the MCP stdio shape). Written from scratch, standard
library only. It is a subset, not a conformant MCP implementation: no cancellation, progress, resources, prompts,
or pagination. It reads the fictional persona and the three snapshot bodies once at start-up, through
jsfilter.filter, and never writes a file or opens a network connection. stdout is the protocol channel and the
only thing it writes to.

Lifecycle (FILTER.md 7): `initialize` -> (initialized, ready) = (T, F); then `notifications/initialized` -> (T, T).
Tool methods before ready: -32000. Codes: -32700 parse, -32600 invalid request, -32601 unknown method,
-32602 bad tool name or arguments. A well-formed call for a posting that is not in the snapshot is a tool result
with isError true, not a protocol error.

Choices FILTER.md did not make, decided here by Claude Code: `ping` is answered in any state; a second
`initialize` is refused with -32600 and changes no state; a request with no id (a notification) never gets a
response, even for tools/call; the protocol version requested by the client is echoed if it is in
SUPPORTED_VERSIONS, otherwise the newest is offered.
"""
import argparse
import json
import pathlib
import sys

from jsfilter import filter as F

SERVER_INFO = {"name": "js3-score-posting", "version": "1.0.0"}
SUPPORTED_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
BOARDS = ("klaviyo", "duolingo", "patchmypc")

TOOL = {
    "name": "score_posting",
    "description": (
        "Score one job posting from a saved, dated snapshot (2026-11-10) of three public job boards against "
        "FILTER.md v1 for a fictional persona. Returns rule results R1-R6, score components, total (0-8), the "
        "threshold (6), and the fate. Read-only: it fetches nothing and changes nothing. The score is a review "
        "order, not a judgment that the posting is worth applying to, and its matched words are not verified claims."),
    "inputSchema": {
        "type": "object",
        "properties": {
            "board": {"type": "string", "enum": list(BOARDS), "description": "Board slug in the snapshot."},
            "id": {"type": "string", "description": "Posting id as the board gives it (Greenhouse number or Lever UUID)."},
        },
        "required": ["board", "id"],
        "additionalProperties": False,
    },
}


def _error(id_, code, message):
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}}


def _result(id_, result):
    return {"jsonrpc": "2.0", "id": id_, "result": result}


class Server:
    def __init__(self, resume, boards):
        self.initialized = False
        self.ready = False
        run = F.run_filter(resume, boards)
        self.board_status = run["boards"]
        self.rows = {(r["board"], r["id"]): r for r in run["rows"]}

    # ---- transport ----
    def handle_line(self, line):
        try:
            message = json.loads(line)
        except ValueError:
            return json.dumps(_error(None, -32700, "Parse error"))
        response = self.handle(message)
        return None if response is None else json.dumps(response)

    # ---- protocol ----
    def handle(self, message):
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or not isinstance(message.get("method"), str):
            return _error(None, -32600, "Invalid Request")
        method = message["method"]
        if "id" not in message:                       # a notification: never answered
            if method == "notifications/initialized" and self.initialized:
                self.ready = True
            return None
        id_ = message["id"]
        if method == "ping":
            return _result(id_, {})
        if method == "initialize":
            if self.initialized:
                return _error(id_, -32600, "Already initialized")
            params = message.get("params") if isinstance(message.get("params"), dict) else {}
            requested = params.get("protocolVersion")
            self.initialized = True
            return _result(id_, {
                "protocolVersion": requested if requested in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0],
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO,
            })
        if not self.ready:
            return _error(id_, -32000, "Server not initialized: send initialize, then notifications/initialized")
        if method == "tools/list":
            return _result(id_, {"tools": [TOOL]})
        if method == "tools/call":
            return self._call(id_, message.get("params"))
        return _error(id_, -32601, f"Method not found: {method}")

    # ---- the one tool ----
    def _call(self, id_, params):
        if not isinstance(params, dict) or params.get("name") != TOOL["name"]:
            return _error(id_, -32602, "Unknown tool")
        args = params.get("arguments")
        if not (isinstance(args, dict) and set(args) == {"board", "id"}
                and args["board"] in BOARDS and isinstance(args["id"], str) and args["id"]):
            return _error(id_, -32602, "Expected arguments {board: one of klaviyo|duolingo|patchmypc, id: string}")
        board, pid = args["board"], args["id"]
        status = self.board_status.get(board, {})
        if status.get("status") != "ok":
            return self._tool_error(id_, f"Board {board} is unknown in this snapshot: {status.get('error')}")
        row = self.rows.get((board, pid))
        if row is None:
            return self._tool_error(id_, f"No posting {board}/{pid} in the 2026-11-10 snapshot")
        payload = {
            "filter_version": row["filter_version"], "snapshot_trace": F.SNAPSHOT_TRACE,
            "board": row["board"], "id": row["id"], "title": row["title"], "location": row["location"],
            "workplace_type": row["workplace_type"], "url": row["url"], "source_path": row["source_path"],
            "rules": {k: {"passed": v["passed"], "matched": v["matched"], "field": v["field"]}
                      for k, v in row["rules"].items()},
            "components": row["components"], "total": row["total"], "threshold": F.THRESHOLD,
            "failed_rules": row["failed_rules"], "fate": row["fate"], "evidence": row["evidence"],
            "caution": ("Word matches show where a filter word occurs in the saved text. They do not show that the "
                        "job requires the skill, that the posting is still open, or that it is worth applying to."),
        }
        return _result(id_, {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
                             "isError": False})

    @staticmethod
    def _tool_error(id_, text):
        return _result(id_, {"content": [{"type": "text", "text": text}], "isError": True})


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parent.parent))
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root)
    resume = json.loads((root / "resumes" / "aarav-patel.json").read_text())
    server = Server(resume, F.load_snapshot(root))
    for line in sys.stdin:
        if not line.strip():
            continue
        out = server.handle_line(line)
        if out is not None:
            sys.stdout.write(out + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
