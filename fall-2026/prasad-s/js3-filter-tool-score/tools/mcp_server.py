"""JS3 MCP tool server: FILTER v2 offered to Claude as one tool, score_posting (JS3 brief, Chapter 8).

Written from scratch: JSON-RPC 2.0 over stdio, one JSON message per line on
stdin and on stdout, standard library only, no MCP SDK. A client starts it
from the JS3 folder and talks to it until it closes stdin:

    python3.13 tools/mcp_server.py

Protocol versions (decision 2026-11-19, from modelcontextprotocol.io as read
that day). Implemented: 2025-11-25, 2025-06-18 and 2024-11-05. For what this
server does (stdio; initialize, notifications/initialized, ping, tools/list,
and tools/call answered with one text block and isError) the three agree on
the wire: the same initialize exchange, the same tool result, no JSON-RPC
batches. initialize answers the client's requested version when it is one of
the three, and otherwise 2025-11-25, the newest: the lifecycle rule is that
the server answers with another version it supports and the client decides
whether to go on. Not implemented: 2025-03-26, which requires accepting
JSON-RPC batches (2025-06-18 removed them); and 2026-07-28, the current
version, which removes initialize and ping and adds server/discover,
resultType, ttlMs and cacheScope. Bad tool arguments are a tool result with
isError true, as 2025-11-25 clarified; an unknown tool or a malformed request
is a JSON-RPC error (-32602).

The tool judges one posting from the frozen corpus (FILTER.md §3), loaded
once per server start, at the first call, through tools/filter_run.py's
checked loading: the SHA-256 check against vault/corpus_manifest.tsv,
agent/adapters.py, the latest copy per posting. It judges with FILTER v2
(agent/filter.py, V2_OPTIONS) and returns, as JSON in one text block, the
verdict, C1-C4 with their status and reason, the score, the missing fields
and, for a kept posting only, the agent's claims (tools/filter_run.py's
claims: the sentences of justifications.tsv). Never the posting's text: the
only words from a posting that can appear are the seniority word or the years
phrase that failed C4, as in C4_reason. A posting in
vault/final_heldout_ids.tsv or vault/js3_heldout_ids_v2.tsv is refused
before anything is looked up (SEAL.md). No refusal or error message repeats
anything the client sent.

It reads only the corpus files, the manifest, the two sealed id files and
resume_persona.json; it writes only its transcript; it makes no network
request. Every line received and every line sent, unaltered (without its line
break), is appended to transcripts/mcp_server_<UTC of start>.jsonl as
{"utc", "direction", "line"}; each start gets a new file, never an old one.
Nothing but protocol messages ever goes to stdout: while the server runs,
sys.stdout points at stderr, and the messages go to the saved stdout.
"""

import argparse
import itertools
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

_JS3 = Path(__file__).resolve().parent.parent
if str(_JS3) not in sys.path:
    sys.path.insert(0, str(_JS3))

from agent import filter as filter_v1  # noqa: E402
from tools import filter_run, seal_draw  # noqa: E402

SUPPORTED_VERSIONS = ("2025-11-25", "2025-06-18", "2024-11-05")  # newest first; why: the module docstring
SERVER_INFO = {"name": "js3-filter-tool-score", "version": "1.0.0"}
TOOL_NAME = "score_posting"
OPTIONS = filter_v1.V2_OPTIONS  # FILTER.md v2: F6 (v2), F9, F10
TRANSCRIPT_DIR = "transcripts"
CONDITIONS = ("C1", "C2", "C3", "C4")

# JSON-RPC 2.0 error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


class ToolRefusal(Exception):
    """Answered as a tool result with isError true. Its message never repeats an id or anything the client sent."""


class ProtocolError(Exception):
    """Answered as a JSON-RPC error. Its message never repeats anything the client sent."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def tool_definition(boards):
    """The one tool. boards: the corpus's board keys (the four of FILTER.md §3 in the real corpus)."""
    return {
        "name": TOOL_NAME,
        "description": ("Judge one job posting from the frozen JS3 corpus (FILTER.md §3) with FILTER v2: C1 title, "
                        "C2 location, C3 text present, C4 level. Returns the verdict (relevant, not_relevant or "
                        "cannot_tell), each condition's status and reason, the skills score, the missing fields, "
                        "and, for a posting the filter keeps, the claims the agent makes about it. Never returns "
                        "the posting's text. Postings in the sealed sets (SEAL.md) are refused."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "board_key": {"type": "string", "enum": list(boards),
                              "description": "The posting's board, as ATS:name."},
                "posting_id": {"type": "string",
                               "description": "The posting's id on that board, as a string."},
            },
            "required": ["board_key", "posting_id"],
            "additionalProperties": False,
        },
    }


def reasons(record):
    """C1-C4's reason for one FILTER v2 record, from the terms rule.py matched and C4_reason."""
    def terms(key):
        return ", ".join(record[key])

    skills = f"skills found: {terms('skills_found')}" if record["skills_found"] else "no persona skill found"
    by_status = {
        "C1": {filter_v1.PASS: f"the title contains a target title: {terms('title_match')}",
               filter_v1.FAIL: "the title contains no target title",
               filter_v1.MISSING: "the title is missing (F7)"},
        "C2": {filter_v1.PASS: f"the location is workable: {terms('location_match')}",
               filter_v1.FAIL: "the location matches none of the workable locations",
               filter_v1.MISSING: "the location is missing (F7)"},
        "C3": {filter_v1.PASS: f"the text is present (FILTER v2's C3 asks only that); {skills}",
               filter_v1.FAIL: f"the score is under {OPTIONS['skills_needed']}; {skills}",
               filter_v1.MISSING: "the text is missing (F7)"},
        "C4": {filter_v1.PASS: f"no seniority word in the title, and no stated minimum above {OPTIONS['max_years']} "
                               f"years in the text",
               filter_v1.FAIL: record.get("C4_reason", ""),
               filter_v1.MISSING: "the title or the text is missing (F7), so the level could not be read in full"},
    }
    return {condition: by_status[condition][record[condition]] for condition in CONDITIONS}


def result_of(record):
    """score_posting's answer for one judged posting. No posting text, no id."""
    why = reasons(record)
    kept = record["verdict"] == filter_v1.RELEVANT
    return {
        "filter": "FILTER.md v2",
        "verdict": record["verdict"],
        "conditions": {condition: {"status": record[condition], "reason": why[condition]} for condition in CONDITIONS},
        "score": record["score"],
        "missing": record["missing"],
        # Claims only for a posting the filter keeps (decision 2026-11-19), as in justifications.tsv.
        "claims": [{"claim": claim, "field": field} for claim, field in filter_run.claims(record, OPTIONS["max_years"])]
                  if kept else [],
    }


class Scorer:
    """FILTER v2 over the frozen corpus. The sealed sets and the corpus are each read once, when first needed."""

    def __init__(self, root, corpus):
        self.root = Path(root)
        self.corpus = corpus
        self.boards = sorted({board for board, _, _ in corpus})
        self._sealed = None
        self._loaded = None

    def sealed(self):
        if self._sealed is None:
            self._sealed = filter_run.read_sealed(self.root)  # every rank recomputed (label_view)
        return self._sealed

    def loaded(self):
        """(persona, {(board, id): posting}). A failed check is not kept: the next call checks again."""
        if self._loaded is None:
            persona = filter_run.load_checked_persona(self.root)
            latest = filter_run.latest_postings(filter_run.read_checked_corpus(self.root, self.corpus))
            if not self.sealed() <= set(latest):
                raise filter_run.FilterRunError("a sealed posting is not in the corpus; nothing judged")
            self._loaded = (persona, latest)
        return self._loaded

    def validated(self, arguments):
        """(board_key, posting_id) from arguments that match the inputSchema; otherwise a refusal."""
        if set(arguments) - {"board_key", "posting_id"}:
            raise ToolRefusal("bad arguments: only board_key and posting_id are accepted")
        if "board_key" not in arguments or "posting_id" not in arguments:
            raise ToolRefusal("bad arguments: board_key and posting_id are both required")
        board, posting_id = arguments["board_key"], arguments["posting_id"]
        if not isinstance(board, str) or not isinstance(posting_id, str):
            raise ToolRefusal("bad arguments: board_key and posting_id must both be strings")
        if board not in self.boards:
            raise ToolRefusal("unknown board key: it must be one of " + ", ".join(self.boards))
        return board, posting_id

    def score(self, arguments):
        board, posting_id = self.validated(arguments)
        try:
            if (board, posting_id) in self.sealed():  # before the corpus is even loaded
                raise ToolRefusal("refused: this posting is in a sealed set (SEAL.md: the final's set or JS3's "
                                  "held-out set), which this server never judges or returns")
            persona, latest = self.loaded()
        except filter_run.FilterRunError as exc:
            raise ToolRefusal(f"cannot use the frozen corpus: {exc}") from exc
        posting = latest.get((board, posting_id))
        if posting is None:
            raise ToolRefusal("no posting with this board key and id in the frozen corpus (FILTER.md §3)")
        return result_of(filter_v1.judge(posting, persona, OPTIONS))


def _error(request_id, code, message):
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _valid_id(value):
    """MCP request ids: a string or a number, never null (and never a bool)."""
    return isinstance(value, str) or (isinstance(value, (int, float)) and not isinstance(value, bool))


class Server:
    """The JSON-RPC side: one received line in, the responses to send out (none, or one)."""

    def __init__(self, root, corpus):
        self.scorer = Scorer(root, corpus)
        self.initialized = False  # notifications/initialized seen; informational, requests are not held back

    def handle(self, line):
        if not line.strip():
            return []  # a blank line is not a message
        try:
            message = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            return [_error(None, PARSE_ERROR, "Parse error: the line is not a UTF-8 JSON text")]
        if isinstance(message, list):
            return [_error(None, INVALID_REQUEST, "Invalid Request: JSON-RPC batches are not supported "
                                                  "(the implemented MCP versions have none)")]
        if not isinstance(message, dict):
            return [_error(None, INVALID_REQUEST, "Invalid Request: not a JSON-RPC message object")]
        if "method" not in message:
            if "id" in message and ("result" in message or "error" in message):
                return []  # a response; this server sends no requests, so there is nothing to match it to
            return [_error(message["id"] if _valid_id(message.get("id")) else None, INVALID_REQUEST,
                           "Invalid Request: no method")]
        is_request = "id" in message
        if is_request and not _valid_id(message["id"]):
            return [_error(None, INVALID_REQUEST, "Invalid Request: the id must be a string or a number")]
        request_id = message.get("id")
        if message.get("jsonrpc") != "2.0" or not isinstance(message["method"], str):
            return [_error(request_id, INVALID_REQUEST, "Invalid Request: jsonrpc must be \"2.0\" and method a string")]
        params = message.get("params", {})
        if not is_request:
            self.notification(message["method"])
            return []  # a notification never gets a reply, not even an error
        if not isinstance(params, dict):
            return [_error(request_id, INVALID_PARAMS, "Invalid params: params must be an object")]
        try:
            result = self.request(message["method"], params)
        except ProtocolError as exc:
            return [_error(request_id, exc.code, exc.message)]
        except Exception:  # keep running; the details go to stderr, never into the reply
            traceback.print_exc(file=sys.stderr)
            return [_error(request_id, INTERNAL_ERROR, "Internal error")]
        return [{"jsonrpc": "2.0", "id": request_id, "result": result}]

    def notification(self, method):
        if method == "notifications/initialized":
            self.initialized = True
        # Any other notification (notifications/cancelled, unknown ones) is ignored.

    def request(self, method, params):
        if method == "initialize":
            requested = params.get("protocolVersion")
            if not isinstance(requested, str):
                raise ProtocolError(INVALID_PARAMS, "Invalid params: initialize needs a protocolVersion string")
            version = requested if requested in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0]
            return {"protocolVersion": version, "capabilities": {"tools": {}}, "serverInfo": dict(SERVER_INFO)}
        if method == "ping":
            return {}
        if method == "tools/list":
            return {"tools": [tool_definition(self.scorer.boards)]}
        if method == "tools/call":
            name = params.get("name")
            if not isinstance(name, str):
                raise ProtocolError(INVALID_PARAMS, "Invalid params: tools/call needs a tool name")
            if name != TOOL_NAME:
                raise ProtocolError(INVALID_PARAMS, f"Unknown tool: this server has one tool, {TOOL_NAME}")
            arguments = params.get("arguments", {})
            if not isinstance(arguments, dict):
                raise ProtocolError(INVALID_PARAMS, "Invalid params: tools/call arguments must be an object")
            try:
                answer = self.scorer.score(arguments)
            except ToolRefusal as refusal:
                return {"content": [{"type": "text", "text": str(refusal)}], "isError": True}
            return {"content": [{"type": "text", "text": json.dumps(answer, ensure_ascii=False)}], "isError": False}
        raise ProtocolError(METHOD_NOT_FOUND, "Method not found")


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


class Transcript:
    """transcripts/mcp_server_<UTC of start>.jsonl, opened new ("x"); a second start in the same second adds _2, _3."""

    def __init__(self, root, started):
        folder = Path(root) / TRANSCRIPT_DIR
        folder.mkdir(exist_ok=True)
        stamp = started.astimezone(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
        for n in itertools.count(1):
            self.path = folder / (f"mcp_server_{stamp}.jsonl" if n == 1 else f"mcp_server_{stamp}_{n}.jsonl")
            try:
                self.handle = open(self.path, "x", encoding="utf-8")
                break
            except FileExistsError:
                continue

    def record(self, direction, line):
        # json.dumps escapes everything outside ASCII, so even invalid UTF-8 (kept as surrogate escapes) is lossless.
        self.handle.write(json.dumps({"utc": utc_now(), "direction": direction, "line": line}) + "\n")
        self.handle.flush()

    def close(self):
        self.handle.close()


def serve(server, transcript, stdin, stdout):
    """Read lines until EOF; record each, answer it, record and send each answer."""
    while True:
        raw = stdin.readline()
        if not raw:
            return
        line = raw[:-1] if raw.endswith(b"\n") else raw
        transcript.record("client->server", line.decode("utf-8", "surrogateescape"))
        for response in server.handle(line):
            text = json.dumps(response, separators=(",", ":"))  # ASCII only: one line, always encodable
            transcript.record("server->client", text)
            try:
                stdout.write(text.encode("ascii") + b"\n")
                stdout.flush()
            except BrokenPipeError:
                return  # the client has gone


def main(argv=None, root=_JS3, corpus=seal_draw.CORPUS, stdin=None, stdout=None, stderr=None, now=None):
    stderr = stderr or sys.stderr
    protocol_out = stdout or sys.stdout.buffer
    saved = sys.stdout
    sys.stdout = stderr  # nothing but protocol ever reaches the real stdout, not even a stray print or --help
    try:
        argparse.ArgumentParser(prog="mcp_server.py",
                                description="FILTER v2 as an MCP tool over stdio (JS3).").parse_args(argv)
        transcript = Transcript(root, now or datetime.now(timezone.utc))
        stderr.write(f"js3 MCP server: tool {TOOL_NAME} (FILTER v2); transcript {transcript.path}\n")
        try:
            serve(Server(root, corpus), transcript, stdin or sys.stdin.buffer, protocol_out)
        finally:
            transcript.close()
    finally:
        sys.stdout = saved
    return 0


if __name__ == "__main__":
    sys.exit(main())
