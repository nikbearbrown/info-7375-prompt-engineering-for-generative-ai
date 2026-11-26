"""A Model Context Protocol tool server written from scratch (JS3 brief, Step 2, Chapter 8). Standard library only.

Transport: JSON-RPC 2.0 over stdio, one JSON message per line (the MCP stdio transport). It answers initialize,
notifications/initialized, ping, tools/list and tools/call, and offers one tool, score_posting.

What it may touch: it reads the saved raw responses of the latest real watch run, the filter file and the fictional
résumé, all inside this folder, and it appends the transcript to transcripts/. It makes no network request, writes
nothing else, and has no tool that sends, applies, logs in or changes data (privacy rules in the brief).
"""
import json
import sys
from datetime import datetime, timezone

from . import collection, config, resume
from . import filter as filt
from .policy import Policy, PolicyRefused

SERVER_INFO = {"name": "js3-jobscore", "version": "1.0"}
SUPPORTED_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
FILTER_FILE = "filters/v1.1.json"  # the final filter; its version is read from the file, not written here

TOOL = {
    "name": "score_posting",
    "title": "Score one saved job posting",
    "description": ("Runs Pavithra's JS3 filter (FILTER.md, version {version}) on one posting from the latest saved "
                    "collection and returns the verdict (keep, reject or cannot tell), the gates, the score and the "
                    "reason. Read-only: it reads saved files in its own folder and makes no network request. "
                    "The verdict is a filter record, not advice on whether to apply."),
    "inputSchema": {
        "type": "object",
        "properties": {
            "board": {"type": "string", "enum": [], "description": "system:board, as in config/boards.json"},
            "job_id": {"type": "string", "minLength": 1, "maxLength": 64, "description": "the board's job id"},
        },
        "required": ["board", "job_id"],
        "additionalProperties": False,
    },
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
}

PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS, INTERNAL_ERROR = -32700, -32600, -32601, -32602, -32603


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class Server:
    def __init__(self, policy=None, transcript=None):
        self.policy = policy or Policy()
        self.transcript = transcript  # a path under transcripts/, or None for no log
        self.initialized = False
        self._data = None

    # --- the transcript: every message in both directions, as received and as sent ---
    def log(self, direction, raw):
        if self.transcript is None:
            return
        path = self.policy.check_write(self.transcript)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"at": now(), "dir": direction, "raw": raw}, ensure_ascii=False) + "\n")

    # --- the one capability ---
    def data(self):
        if self._data is None:
            run_dir = collection.latest_run(self.policy)
            postings, failed = collection.load_run(run_dir, self.policy)
            spec = filt.load_filter(self.policy.check_read(FILTER_FILE))
            persona = resume.load(self.policy.check_read(config.RESUME))
            self._data = (run_dir.name, {f"{b}:{j['id']}": (b, j) for b, j in postings}, dict(failed), spec, persona)
        return self._data

    def score_posting(self, args):
        run, jobs, failed, spec, persona = self.data()
        board, job_id = args["board"], args["job_id"]
        if board in failed:
            return self.tool_error(f"I cannot tell: board {board} failed in run {run} ({failed[board]})")
        found = jobs.get(f"{board}:{job_id}")
        if found is None:
            return self.tool_error(f"no posting {job_id} on {board} in run {run}; nothing was guessed")
        d = filt.decide(found[1], board, persona, spec).to_dict()
        d["run"] = run
        text = f"{d['verdict']} (score {d['score']}, filter v{d['filter_version']}, run {run}): {d['reason']}"
        return {"content": [{"type": "text", "text": text}], "structuredContent": d, "isError": False}

    def boards(self):
        """The configured boards, read from config/boards.json each time, so the declared list cannot drift from it."""
        return [f"{b['system']}:{b['name']}" for b in config.load("boards")]

    def declared_tool(self):
        """The tool as declared: the version of the filter it really uses (loaded once per session, together with the
        collection, so the declared version and the one used cannot differ), and the boards from config."""
        version = self.data()[3]["version"]
        schema = json.loads(json.dumps(TOOL["inputSchema"]))
        schema["properties"]["board"]["enum"] = self.boards()
        return {**TOOL, "description": TOOL["description"].format(version=version), "inputSchema": schema}

    @staticmethod
    def tool_error(message):
        return {"content": [{"type": "text", "text": message}], "isError": True}

    # --- JSON-RPC ---
    def handle(self, msg):
        """One parsed message -> the response dict, or None for a notification."""
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
            return error(msg.get("id") if isinstance(msg, dict) else None, INVALID_REQUEST, "not a JSON-RPC 2.0 request")
        method, params, mid = msg["method"], msg.get("params"), msg.get("id")
        if params is None:
            params = {}
        if not isinstance(params, dict):  # found by a review: a list here crashed the server
            return None if "id" not in msg else error(mid, INVALID_PARAMS, "params must be an object")
        if "id" not in msg:  # a notification: never answered
            if method == "notifications/initialized":
                self.initialized = True
            return None
        if method == "initialize":
            asked = params.get("protocolVersion")
            version = asked if asked in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0]
            return result(mid, {"protocolVersion": version, "capabilities": {"tools": {"listChanged": False}},
                                "serverInfo": SERVER_INFO,
                                "instructions": "One read-only tool, score_posting. It never applies, sends or changes anything."})
        if method == "ping":
            return result(mid, {})
        if method == "tools/list":
            return result(mid, {"tools": [self.declared_tool()]})
        if method == "tools/call":
            name, args = params.get("name"), params.get("arguments")
            if name != TOOL["name"]:
                return error(mid, INVALID_PARAMS, f"unknown tool: {name!r}")
            problem = check_args(args, self.boards())
            if problem:
                return error(mid, INVALID_PARAMS, problem)
            try:
                return result(mid, self.score_posting(args))
            except PolicyRefused as e:
                return result(mid, self.tool_error(str(e)))
        return error(mid, METHOD_NOT_FOUND, f"method not found: {method}")

    def serve(self, stdin=sys.stdin, stdout=sys.stdout):
        for line in stdin:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            self.log("in", line)
            try:
                msg = json.loads(line)
            except ValueError:
                reply = error(None, PARSE_ERROR, "parse error")
            else:
                try:
                    reply = self.handle(msg)
                except Exception as e:  # never crash the session: report it, keep serving
                    mid = msg.get("id") if isinstance(msg, dict) else None
                    reply = error(mid, INTERNAL_ERROR, f"internal error: {type(e).__name__}")
            if reply is not None:
                out = json.dumps(reply, ensure_ascii=False)
                self.log("out", out)
                stdout.write(out + "\n")
                stdout.flush()


def check_args(args, boards):
    """The input schema, checked by hand (no schema library): exactly board and job_id, as declared."""
    if not isinstance(args, dict):
        return "arguments must be an object"
    extra = set(args) - set(TOOL["inputSchema"]["properties"])
    if extra:
        return f"unexpected arguments: {sorted(extra)}"
    if args.get("board") not in boards:
        return f"board must be one of {boards}"
    job_id = args.get("job_id")
    if not isinstance(job_id, str) or not 1 <= len(job_id) <= 64:
        return "job_id must be a string of 1 to 64 characters"
    return None


def result(mid, value):
    return {"jsonrpc": "2.0", "id": mid, "result": value}


def error(mid, code, message):
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}


def main():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    Server(transcript=config.ROOT / "transcripts" / f"server-{stamp}.jsonl").serve()


if __name__ == "__main__":
    main()
