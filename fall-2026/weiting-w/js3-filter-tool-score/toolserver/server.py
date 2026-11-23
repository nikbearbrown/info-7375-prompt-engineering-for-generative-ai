"""A Model Context Protocol server, written from scratch. No SDK, no deps.

    python3 -m toolserver                 # speaks JSON-RPC 2.0 over stdio

It offers Claude exactly one capability — `score_posting` — and the choice of
*one* is deliberate. FILTER.md and the assignment both say a tool server I
write must not expose anything that can send or change data outside my own
folder, and the narrowest useful surface is the easiest to say true things
about.

**What this server does.** Takes posting text, runs F-v2's scorer S-v2 over it,
and returns the total, the per-signal breakdown, and for every point awarded
the word that matched and the sentence it sat in. It is arithmetic over a word
list, so a caller can check the answer without trusting the server.

**What it cannot do, structurally rather than by promise.**

- No network. The module imports no socket, no http client, no urllib. The
  evaluation in `reports/tool-evaluation.md` checks that by reading the import
  graph rather than taking this paragraph's word for it.
- No filesystem writes. Nothing here opens a file for writing.
- No filesystem reads driven by the caller. `score_posting` takes *text*, not a
  path, so there is no argument a caller can set to make the server read
  something. The corpus is never touched by this server at all.
- No model call, no API key, no environment variable.

**The protocol.** Three methods over newline-delimited JSON-RPC 2.0 on stdin
and stdout: `initialize`, `tools/list`, `tools/call`, plus the
`notifications/initialized` notification, which carries no `id` and so gets no
reply. Anything else returns JSON-RPC error −32601. The wire format is the
message shape MCP uses; this is a hand-written implementation of it, not a
binding to anyone's library.

Every byte in and out is logged to stderr when `--log` is given, which is how
`evidence/transcripts/` was produced: a real transcript in both directions, not
a retyped one.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jobfilter import score as scorer  # noqa: E402

SERVER_NAME = "js3-score-posting"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"

MAX_TEXT = 200_000

TOOLS = [
    {
        "name": "score_posting",
        "description": (
            "Score the text of a job posting against the filter in FILTER.md "
            "(F-v2 / S-v2) for a fictional new-graduate software engineering "
            "persona. Returns the total, the per-signal breakdown, and for "
            "every point awarded the word that matched and the sentence it "
            "appeared in. Pure arithmetic over a published word list: it reads "
            "no file, makes no network request, and calls no model. Text with "
            "no scoreable content returns 0; empty text is an error, not a 0, "
            "because 'nothing to read' and 'read it and found nothing' are "
            "different answers."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The posting's plain-text body. Not a path, "
                                   "not a URL -- this server fetches nothing.",
                },
            },
            "required": ["text"],
            "additionalProperties": False,
        },
    }
]


class RpcError(Exception):
    def __init__(self, code: int, message: str, data=None):
        super().__init__(message)
        self.code, self.message, self.data = code, message, data


def call_score_posting(arguments: dict) -> dict:
    if not isinstance(arguments, dict):
        raise RpcError(-32602, "arguments must be an object")

    unexpected = set(arguments) - {"text"}
    if unexpected:
        # additionalProperties: false, enforced rather than declared
        raise RpcError(-32602, f"unexpected argument(s): {sorted(unexpected)}")

    text = arguments.get("text")
    if not isinstance(text, str):
        raise RpcError(-32602, "`text` is required and must be a string")
    if len(text) > MAX_TEXT:
        raise RpcError(-32602, f"`text` is longer than {MAX_TEXT} characters")

    result = scorer.score(text)
    if result is None:
        raise RpcError(
            -32602,
            "`text` is empty. An empty body is not a score of 0: see FILTER.md "
            "section 3 and wrong version W1.",
        )

    return {
        "scorer_version": scorer.SCORER_VERSION,
        "total": result.total,
        "threshold": scorer.THRESHOLD,
        "shortlisted": result.shortlisted,
        "per_signal": result.per_signal,
        "evidence": [
            {
                "signal": h.signal,
                "word": h.word,
                "points": h.points,
                "sentence": h.sentence,
            }
            for h in result.hits
        ],
    }


def handle(message: dict) -> dict | None:
    """One request in, one response out, or None for a notification."""
    if message.get("jsonrpc") != "2.0":
        raise RpcError(-32600, "jsonrpc must be '2.0'")

    method = message.get("method")
    msg_id = message.get("id")

    if msg_id is None:
        # A notification. `notifications/initialized` is the expected one.
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": msg_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        params = message.get("params") or {}
        name = params.get("name")
        if name != "score_posting":
            raise RpcError(-32602, f"no such tool: {name!r}")
        try:
            payload = call_score_posting(params.get("arguments") or {})
        except RpcError as exc:
            # A tool-level failure is reported in the result with isError,
            # not as a protocol error: the call was well formed, the work was
            # not possible.
            return {
                "jsonrpc": "2.0", "id": msg_id,
                "result": {
                    "isError": True,
                    "content": [{"type": "text", "text": exc.message}],
                },
            }
        return {
            "jsonrpc": "2.0", "id": msg_id,
            "result": {
                "isError": False,
                "content": [
                    {"type": "text", "text": json.dumps(payload, ensure_ascii=False)}
                ],
            },
        }

    raise RpcError(-32601, f"method not found: {method!r}")


def serve(stdin=None, stdout=None, log=None) -> int:
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout

    for line in stdin:
        line = line.strip()
        if not line:
            continue
        if log:
            log.write(f">> {line}\n")
            log.flush()

        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            response = {
                "jsonrpc": "2.0", "id": None,
                "error": {"code": -32700, "message": f"parse error: {exc}"},
            }
        else:
            try:
                response = handle(message)
            except RpcError as exc:
                response = {
                    "jsonrpc": "2.0", "id": message.get("id"),
                    "error": {"code": exc.code, "message": exc.message},
                }
            except Exception as exc:                      # noqa: BLE001
                response = {
                    "jsonrpc": "2.0", "id": message.get("id"),
                    "error": {"code": -32603, "message": f"internal error: {exc}"},
                }

        if response is None:
            continue
        out = json.dumps(response, ensure_ascii=False)
        stdout.write(out + "\n")
        stdout.flush()
        if log:
            log.write(f"<< {out}\n")
            log.flush()
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    log = sys.stderr if "--log" in argv else None
    return serve(log=log)


if __name__ == "__main__":
    raise SystemExit(main())
