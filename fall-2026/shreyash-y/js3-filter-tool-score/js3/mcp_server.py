"""A Model Context Protocol tool server, written from scratch: JSON-RPC 2.0 over stdio, one JSON
message per line. It offers ONE tool, score_posting (FILTER.md answer 13): score one posting this
agent already collected against FILTER.md v1, with the evidence quotes and the claim labels.

What it can touch (TOOLSERVER.md evaluates this as if someone else had written it):
- reads data/corpus.jsonl, filter-v1.json and persona/alex_morgan.json in this folder, once, at start;
- writes one transcript file per session under transcripts/ (every line in and out, as sent);
- imports no network module, starts no process, and has no tool that writes, sends or fetches.

Run:  python3 -m js3 serve            (Claude Code starts it from an --mcp-config file)
"""
import datetime
import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
SERVER_INFO = {"name": "js3-score-posting", "version": "1.0.0"}
SUPPORTED = ("2025-06-18", "2025-03-26", "2024-11-05")
KEY_RE = re.compile(r"^[a-z0-9-]{1,64}:[A-Za-z0-9-]{1,64}$")

TOOL = {
    "name": "score_posting",
    "title": "Score a saved job posting against FILTER.md v1",
    "description": (
        "Scores ONE job posting that this job-search agent already collected (it is in the agent's saved "
        "corpus) against the agent's written filter, FILTER.md v1, for the fictional applicant Alex Morgan. "
        "Returns the filter's verdict (Relevant, Not Relevant, or I cannot tell), the outcome of each of its "
        "six rules with exact quotes from the posting, and, for a kept posting, every claim of its "
        "justification labeled supported, contradicted or insufficient. It reads only saved data: it does "
        "not fetch pages, contact any site, apply, or change anything. A verdict is the filter's record, "
        "not a judgment that the job is good."),
    "inputSchema": {
        "type": "object",
        "properties": {"posting_key": {
            "type": "string", "pattern": KEY_RE.pattern,
            "description": "board:id of a saved posting, for example klaviyo:7792539003"}},
        "required": ["posting_key"],
        "additionalProperties": False},
    "annotations": {"title": "Score a saved job posting", "readOnlyHint": True, "destructiveHint": False,
                    "idempotentHint": True, "openWorldHint": False},
}


class Server:
    def __init__(self, log_dir=None):
        from js3 import corpus, filtering, claims
        self.filtering, self.claims = filtering, claims
        self.cfg = filtering.load_config(HERE / "filter-v1.json")
        self.persona = json.loads((HERE / "persona" / "alex_morgan.json").read_text())
        self.postings = {p["key"]: p for p in corpus.load(HERE / "data" / "corpus.jsonl")}
        self.log = None
        if log_dir is not None:
            log_dir = pathlib.Path(log_dir).resolve()
            if not str(log_dir).startswith(str((HERE / "transcripts").resolve())):
                raise SystemExit("the transcript folder must be inside transcripts/")
            log_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            self.log = open(log_dir / f"server-{stamp}-{os.getpid()}.jsonl", "a", encoding="utf-8")

    def record(self, direction, raw):
        if self.log:
            self.log.write(json.dumps({"at": datetime.datetime.now().astimezone().isoformat(timespec="milliseconds"),
                                       "dir": direction, "raw": raw}, ensure_ascii=False) + "\n")
            self.log.flush()

    # -- the protocol ---------------------------------------------------------------------------
    def handle(self, msg):
        """One parsed message in; a response dict out, or None for a notification."""
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
            return error(msg.get("id") if isinstance(msg, dict) else None, -32600, "Invalid Request")
        mid, method, params = msg.get("id"), msg["method"], msg.get("params") or {}
        if "id" not in msg:  # a notification: never answered
            return None
        if method == "initialize":
            asked = params.get("protocolVersion")
            return result(mid, {"protocolVersion": asked if asked in SUPPORTED else SUPPORTED[0],
                                "capabilities": {"tools": {"listChanged": False}},
                                "serverInfo": SERVER_INFO,
                                "instructions": "One read-only tool over this job-search agent's saved postings. "
                                                "Its verdicts are a written filter's record, not facts about the job."})
        if method == "ping":
            return result(mid, {})
        if method == "tools/list":
            return result(mid, {"tools": [TOOL]})
        if method == "tools/call":
            if params.get("name") != TOOL["name"]:
                return error(mid, -32602, f"Unknown tool: {params.get('name')!r}")
            return result(mid, self.call(params.get("arguments") or {}))
        return error(mid, -32601, f"Method not found: {method}")

    def call(self, args):
        if set(args) != {"posting_key"} or not isinstance(args.get("posting_key"), str):
            return tool_error("score_posting takes exactly one argument, posting_key (a string like klaviyo:7792539003).")
        key = args["posting_key"].strip()
        if not KEY_RE.match(key):
            return tool_error(f"{key!r} is not a posting key (board:id).")
        p = self.postings.get(key)
        if p is None:
            return tool_error(f"{key} is not in this agent's saved corpus. This tool does not fetch postings; "
                              "it can only score ones the agent already collected.")
        rec = self.filtering.evaluate(p, self.persona, self.cfg)
        out = {"posting_key": key, "title": p["title"], "board": p["board"], "url": p.get("url"),
               "open_in_latest_run": p["open_in_latest_run"], "filter_version": rec["filter_version"],
               "verdict": rec["verdict"], "failed_rules": rec["failed"], "cannot_tell_rules": rec["unsure"],
               "closest_call": rec["closest_call"],
               "rules": [{"rule": l["n"], "name": l["rule"], "outcome": l["outcome"], "detail": l["detail"],
                          "quotes": l["evidence"]} for l in rec["rules"]],
               "note": "The verdict is FILTER.md v1 applied by code: a record of the rules, not a judgment of the job."}
        if rec["verdict"] == "Relevant":
            out["justification"] = self.claims.justify(p, rec, self.persona, self.cfg)
        return {"content": [{"type": "text", "text": json.dumps(out, ensure_ascii=False, indent=1)}],
                "structuredContent": out, "isError": False}

    def serve(self, stdin=sys.stdin, stdout=sys.stdout):
        for raw in stdin:
            raw = raw.rstrip("\n")
            if not raw.strip():
                continue
            self.record("client->server", raw)
            try:
                msg = json.loads(raw)
            except ValueError:
                reply = error(None, -32700, "Parse error")
            else:
                if isinstance(msg, list):
                    reply = error(None, -32600, "Batches are not supported")
                else:
                    reply = self.handle(msg)
            if reply is not None:
                line = json.dumps(reply, ensure_ascii=False)
                self.record("server->client", line)
                stdout.write(line + "\n")
                stdout.flush()


def result(mid, value):
    return {"jsonrpc": "2.0", "id": mid, "result": value}


def error(mid, code, message):
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}


def tool_error(text):
    return {"content": [{"type": "text", "text": text}], "isError": True}


def main(argv=()):
    log_dir = HERE / "transcripts" / "server"
    if "--no-log" in argv:
        log_dir = None
    Server(log_dir).serve()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
