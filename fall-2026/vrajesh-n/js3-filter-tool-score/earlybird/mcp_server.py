"""A from-scratch Model Context Protocol server (stdio, JSON-RPC 2.0, one JSON object per line).

It offers ONE capability to Claude: score_posting - run FILTER.md v2 and the claim labels on one posting from the
LOCAL snapshot (data/snapshot-2026-11-01). Run: python -m earlybird.mcp_server

What it does NOT do (declared here, checked in review/ by tests and by the evaluation):
- no network: connect() and connect_ex() are disabled at start-up (a guard, not a sandbox) and no network library is
  imported;
- no writes except an optional message log, and only to the path in EARLYBIRD_MCP_LOG (both directions, JSON lines);
- no tools other than score_posting; it cannot apply, email, message, log in, or change data.

Implements: initialize (version negotiation), notifications/initialized, ping, tools/list, tools/call.
Everything else is JSON-RPC error -32601."""
import json
import os
import re
import socket
import sys
from pathlib import Path

from . import boards, claims, rule
from .resume import load_resume

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "data" / "snapshot-2026-11-01"
SUPPORTED = ["2025-06-18", "2025-03-26", "2024-11-05"]
ID_OK = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
BOARD_OK = re.compile(r"^(?:ashby|greenhouse|lever)_[A-Za-z0-9-]{1,40}$")

TOOL = {
    "name": "score_posting",
    "title": "Score one job posting",
    "description": ("Run the Early Bird filter (FILTER.md v2: rules R1-R5 and cannot_tell) and label each claim "
                    "(supported / contradicted / insufficient) for ONE posting from the local 2026-11-01 snapshot. "
                    "Read-only, no network. The persona is fictional (Rohan Desai, new grad, needs sponsorship)."),
    "inputSchema": {
        "type": "object",
        "properties": {
            "posting_id": {"type": "string", "description": "Posting id as it appears in the snapshot board file."},
            "board": {"type": "string", "description": "Snapshot board, e.g. greenhouse_stripe. Needed if the id is ambiguous."},
        },
        "required": ["posting_id"],
        "additionalProperties": False,
    },
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
}


def _no_network(*_a, **_k):
    raise OSError("network disabled in earlybird mcp_server")


def disable_network():
    """Belt and braces, not a sandbox: the real guarantee is that no module here opens a socket (scripts/eval_own_server.py
    checks the imports). Patches connect() AND connect_ex() - the first version patched connect() only, and
    connect_ex() got past it (found by evaluating this server, review/14-network-guard-red.txt)."""
    socket.socket.connect = _no_network
    socket.socket.connect_ex = _no_network


class Server:
    def __init__(self, log_path=None):
        self.log = open(log_path, "a", encoding="utf-8") if log_path else None
        self.index = None
        self.resume = load_resume(ROOT / "data/resume/rohan-desai.example.json")

    # --- message log (both directions) --------------------------------
    def record(self, direction, raw):
        if self.log:
            self.log.write(json.dumps({"dir": direction, "msg": raw}, ensure_ascii=False) + "\n")
            self.log.flush()

    # --- data ------------------------------------------------------------
    def load_index(self):
        if self.index is None:
            self.index = {}
            for f in sorted(SNAPSHOT.glob("*.json")):
                for p in boards.parse(f.stem.split("_")[0], f.read_text(encoding="utf-8")):
                    self.index.setdefault(p["id"], {})[f.stem] = p
        return self.index

    # --- the tool --------------------------------------------------------
    def score_posting(self, args):
        extra = set(args) - {"posting_id", "board"}
        if extra:
            return "unexpected argument(s): " + ", ".join(sorted(extra)), True
        pid, board = args.get("posting_id"), args.get("board")
        if not isinstance(pid, str) or not ID_OK.match(pid):
            return "posting_id must be a string of letters, digits, '-' or '_' (max 64)", True
        if board is not None and (not isinstance(board, str) or not BOARD_OK.match(board)):
            return "board must look like greenhouse_stripe", True
        found = self.load_index().get(pid, {})
        if board is not None:
            found = {b: p for b, p in found.items() if b == board}
        if not found:
            return f"posting {pid!r} not found in the 2026-11-01 snapshot" + (f" (board {board})" if board else ""), True
        if len(found) > 1:
            return f"posting id {pid!r} is on several boards ({', '.join(sorted(found))}); pass board", True
        (b, p), = found.items()
        v = rule.judge(p, self.resume)
        body = {"posting_id": p["id"], "board": b, "title": p["title"], "location": p["location"], "url": p["url"],
                "verdict": v["verdict"], "failed_check": v["failed_check"], "justification": v["justification"],
                "claims": [{k: c[k] for k in ("claim", "label", "quote", "why")} for c in claims.label_claims(p, self.resume)],
                "filter_version": "v2", "persona": "rohan-desai (fictional)", "source": "local snapshot 2026-11-01"}
        return json.dumps(body, ensure_ascii=False), False

    # --- JSON-RPC --------------------------------------------------------
    def handle(self, msg):
        """Return a response dict, or None for a notification."""
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
            return {"jsonrpc": "2.0", "id": msg.get("id") if isinstance(msg, dict) else None,
                    "error": {"code": -32600, "message": "Invalid Request"}}
        method, mid, params = msg["method"], msg.get("id"), msg.get("params") or {}
        is_notification = "id" not in msg

        def ok(result):
            return None if is_notification else {"jsonrpc": "2.0", "id": mid, "result": result}

        def err(code, text):
            return None if is_notification else {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": text}}

        if method == "initialize":
            asked = params.get("protocolVersion")
            return ok({"protocolVersion": asked if asked in SUPPORTED else SUPPORTED[0],
                       "capabilities": {"tools": {"listChanged": False}},
                       "serverInfo": {"name": "earlybird-score", "title": "Early Bird score_posting", "version": "0.3.0"}})
        if method.startswith("notifications/"):
            return None
        if method == "ping":
            return ok({})
        if method == "tools/list":
            return ok({"tools": [TOOL]})
        if method == "tools/call":
            if params.get("name") != TOOL["name"]:
                return err(-32602, f"Unknown tool: {params.get('name')!r}")
            args = params.get("arguments")
            if args is None:
                args = {}
            if not isinstance(args, dict):
                return ok({"content": [{"type": "text", "text": "arguments must be an object"}], "isError": True})
            text, is_error = self.score_posting(args)
            return ok({"content": [{"type": "text", "text": text}], "isError": is_error})
        return err(-32601, f"Method not found: {method}")

    def serve(self, stdin, stdout):
        for raw in stdin:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            self.record("client->server", line)
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
            else:
                reply = self.handle(msg)
            if reply is not None:
                out = json.dumps(reply, ensure_ascii=True)
                self.record("server->client", out)
                stdout.write(out.encode("ascii") + b"\n")
                stdout.flush()


def main():
    disable_network()  # declared: this server never touches the network
    Server(os.environ.get("EARLYBIRD_MCP_LOG")).serve(sys.stdin.buffer, sys.stdout.buffer)


if __name__ == "__main__":
    main()
