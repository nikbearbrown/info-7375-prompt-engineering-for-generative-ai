"""A Model Context Protocol tool server, written from scratch on the standard library.

    python3 mcp_server.py                  serve on stdio; log every message to state/mcp/transcript_<UTC>.jsonl
    python3 mcp_server.py --log none       serve without a log (tests)

Transport: stdio. One JSON-RPC 2.0 message per line on stdin, one per line on stdout. Nothing else is ever
written to stdout; diagnostics go to stderr.

Methods: initialize, notifications/initialized, ping, tools/list, tools/call. Anything else is a JSON-RPC
"method not found" error. A message without an id is a notification and gets no reply.

One tool, score_posting. It takes a posting key from the frozen corpus and returns the current filter's verdict
with the words behind every rule and point. It is read-only by construction:
- the corpus is loaded once, at start, from the saved raw responses (corpus.load), never fetched;
- no code path in a request handler writes, sends, or fetches anything;
- the only file the server writes is its own transcript log, in state/mcp/, opened at start.
The verdict is the filter's, not a judgment of the posting's worth: whether Riley should apply stays with me.
"""
import datetime as dt
import json
import os
import re
import sys

import filter as F

SERVER = {"name": "js3-job-filter", "version": "1.0.0"}
PROTOCOL_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")  # newest first
KEY = re.compile(r"^(greenhouse|ashby|lever)/[a-z0-9-]+/[A-Za-z0-9-]+$")

TOOL = {
    "name": "score_posting",
    "title": "Score one job posting with the JS3 filter",
    "description": (
        "Return the JS3 filter's verdict (keep or reject) for one posting in the frozen corpus, by its key "
        "(\"system/board/id\", for example \"greenhouse/fanduel/8055746\"). The result lists which reject rule "
        "fired and the exact words that fired it, the score, the threshold, and the skill words found. "
        "Read-only: it reads postings saved on disk and never fetches, writes, or sends anything. The verdict is "
        "the filter's rule output, not advice on whether to apply."),
    "inputSchema": {
        "type": "object",
        "properties": {"key": {"type": "string", "description": "Posting key: system/board/id",
                               "pattern": KEY.pattern}},
        "required": ["key"],
        "additionalProperties": False,
    },
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True,
                    "openWorldHint": False},
}


class Server:
    def __init__(self, postings, log=None):
        self.postings = {p["key"]: p for p in postings}
        self.log = log or (lambda direction, message: None)
        self.initialized = False

    # --- one line in, at most one line out ---

    def handle_line(self, line):
        try:
            message = json.loads(line)
        except json.JSONDecodeError as e:
            self.log("in", {"unparseable": line[:500]})
            return self._send(error(None, -32700, f"Parse error: {e.msg}"))
        self.log("in", message)
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or not isinstance(
                message.get("method"), str):
            if isinstance(message, dict) and "method" not in message and ("result" in message or "error" in message):
                return None  # a response to a request we never send; ignore it
            return self._send(error(message.get("id") if isinstance(message, dict) else None, -32600,
                                    "Invalid Request"))
        if "id" not in message:
            self._notify(message)
            return None
        return self._send(self._request(message))

    def _send(self, reply):
        self.log("out", reply)
        return json.dumps(reply, separators=(",", ":"))

    def _notify(self, message):
        if message["method"] == "notifications/initialized":
            self.initialized = True

    def _request(self, message):
        mid, method, params = message["id"], message["method"], message.get("params") or {}
        if method == "initialize":
            asked = params.get("protocolVersion")
            version = asked if asked in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0]
            return result(mid, {"protocolVersion": version, "capabilities": {"tools": {"listChanged": False}},
                                "serverInfo": SERVER,
                                "instructions": "One read-only tool, score_posting, over a frozen job-posting "
                                                "corpus. Its verdicts are rule outputs, not advice."})
        if method == "ping":
            return result(mid, {})
        if method == "tools/list":
            return result(mid, {"tools": [TOOL]})
        if method == "tools/call":
            if params.get("name") != TOOL["name"]:
                return error(mid, -32602, f"Unknown tool: {params.get('name')!r}")
            return result(mid, self._score(params.get("arguments") or {}))
        return error(mid, -32601, f"Method not found: {method}")

    def _score(self, args):
        key = args.get("key")
        if set(args) != {"key"} or not isinstance(key, str) or not KEY.match(key):
            return tool_error("Give exactly one argument, key, as system/board/id "
                              "(for example greenhouse/fanduel/8055746).")
        p = self.postings.get(key)
        if p is None:
            return tool_error(f"No posting with key {key} in the frozen corpus.")
        v = F.evaluate(p)
        out = {"key": key, "title": p["title"], "locations": list(dict.fromkeys(p["locations"])), "url": p["url"],
               "corpus": p["corpus"], "filter_version": F.VERSION, "verdict": v["verdict"], "score": v["score"],
               "threshold": v["threshold"], "rejected_by": v["rejected_by"], "title_signal": v["title_signal"],
               "skills": v["skills"],
               "note": f"A rule output from FILTER.md v{F.VERSION}, not a judgment of whether to apply."}
        return {"content": [{"type": "text", "text": json.dumps(out, indent=1)}], "structuredContent": out,
                "isError": False}


def result(mid, value):
    return {"jsonrpc": "2.0", "id": mid, "result": value}


def error(mid, code, text):
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": text}}


def tool_error(text):
    return {"content": [{"type": "text", "text": text}], "isError": True}


def open_log(here):
    folder = os.path.join(here, "state", "mcp")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"transcript_{dt.datetime.now(dt.timezone.utc):%Y-%m-%dT%H%M%SZ}.jsonl")
    handle = open(path, "x", encoding="utf-8")  # "x": never overwrite an earlier transcript

    def log(direction, message):
        handle.write(json.dumps({"t": dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds"),
                                 "dir": direction, "msg": message}) + "\n")
        handle.flush()
    return log, path


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)  # the corpus and the policy are relative to this folder, whatever the client's cwd
    import corpus
    from policy import Policy
    from tools import Tools
    _, postings = corpus.load(Tools(Policy()))
    log, path = (None, None) if argv[1:] == ["--log", "none"] else open_log(here)
    print(f"{SERVER['name']}: {len(postings)} postings loaded; log: {path or 'off'}", file=sys.stderr)
    server = Server(postings, log)
    for line in sys.stdin:
        if not line.strip():
            continue
        reply = server.handle_line(line)
        if reply is not None:
            sys.stdout.write(reply + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
