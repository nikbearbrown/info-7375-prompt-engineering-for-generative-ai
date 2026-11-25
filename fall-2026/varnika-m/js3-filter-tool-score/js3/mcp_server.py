"""A Model Context Protocol tool server, from scratch: JSON-RPC 2.0, one JSON message per line on stdin/stdout.

    python3 -m js3.mcp_server            # from this folder; a client starts it and talks over stdin/stdout

It offers one capability, `score_posting`: the filter, the evidence labels and the answer for one saved
posting. It is read-only. It reads the saved responses in data/ and nothing else; the only file it writes
is its own transcript in transcripts/ (every message in both directions). It makes no network request.
"""

import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from js3.claims import answer, label_claims  # noqa: E402
from js3.filter import run_filter  # noqa: E402
from js3.load import load, load_persona  # noqa: E402

SUPPORTED_VERSIONS = ["2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"]
SERVER_INFO = {"name": "js3-job-filter", "version": "1.0.0"}
TOOL = {
    "name": "score_posting",
    "title": "Score a saved job posting",
    "description": ("Run Varnika's JS3 filter (FILTER.md v1) on one posting saved from the 2026-11-10 run: its score "
                    "out of 5, which rules failed, each claim labeled supported / contradicted / insufficient with "
                    "the quote that decides it, and the answer ('fits', 'does not fit' or 'I cannot tell'). "
                    "Read-only. The posting_id is 'system/board/id', e.g. 'lever/palantir/<uuid>', or the bare id."),
    "inputSchema": {"type": "object", "additionalProperties": False, "required": ["posting_id"],
                    "properties": {"posting_id": {"type": "string", "maxLength": 200,
                                                  "description": "the posting's id, alone or as system/board/id"}}},
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
}


class Server:
    def __init__(self, transcript=None):
        self.transcript = Path(transcript) if transcript else None
        self.postings = self.results = None
        self.version = None

    def log(self, direction, line):
        if self.transcript:
            self.transcript.parent.mkdir(parents=True, exist_ok=True)
            with open(self.transcript, "a", encoding="utf-8") as handle:
                handle.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "dir": direction,
                                         "message": line}, ensure_ascii=False) + "\n")

    def data(self):
        if self.postings is None:
            postings, _ = load(HERE)
            self.results, _ = run_filter(postings, load_persona())
            self.postings = {p["key"]: p for p in postings}
        return self.postings, self.results

    def find(self, posting_id):
        postings, _ = self.data()
        if posting_id in postings:
            return postings[posting_id]
        matches = [p for p in postings.values() if p["id"] == posting_id]
        return matches[0] if len(matches) == 1 else None

    def score(self, posting_id):
        posting = self.find(posting_id)
        if posting is None:
            return {"content": [{"type": "text", "text": "No saved posting has the id %r." % posting_id}],
                    "isError": True}
        result = self.data()[1][posting["key"]]
        claims = label_claims(posting, result) if result["outcome"] != "cannot_tell" else []
        body = {"posting_id": posting["key"], "company": posting["company_name"], "title": posting["title"],
                "location": (posting.get("location") or {}).get("name"), "url": posting["absolute_url"],
                "filter": "FILTER.md v1", "score": result["score"], "outcome": result["outcome"],
                "failed_rules": result.get("failed", []), "skills_matched": result["skills"],
                "claims": claims, "answer": answer(claims) if claims else
                {"answer": "I cannot tell", "because": ["missing: " + ", ".join(result["missing"])]}}
        return {"content": [{"type": "text", "text": json.dumps(body, ensure_ascii=False, indent=1)}],
                "isError": False}

    def handle(self, message):
        """One request or notification in; a response, or None for a notification."""
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or "method" not in message:
            return error(message.get("id") if isinstance(message, dict) else None, -32600, "Invalid Request")
        method, mid, params = message["method"], message.get("id"), message.get("params") or {}
        if mid is None:  # a notification, e.g. notifications/initialized: no answer
            return None
        if method == "initialize":
            asked = params.get("protocolVersion")
            self.version = asked if asked in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0]
            return ok(mid, {"protocolVersion": self.version, "capabilities": {"tools": {"listChanged": False}},
                            "serverInfo": SERVER_INFO,
                            "instructions": "One read-only tool over saved postings. It never applies, emails, "
                                            "messages, logs in or fetches anything."})
        if method == "ping":
            return ok(mid, {})
        if method == "tools/list":
            return ok(mid, {"tools": [TOOL]})
        if method == "tools/call":
            if params.get("name") != TOOL["name"]:
                return error(mid, -32602, "Unknown tool: %r" % params.get("name"))
            arguments = params.get("arguments") or {}
            posting_id = arguments.get("posting_id")
            if set(arguments) - {"posting_id"} or not isinstance(posting_id, str) or not 0 < len(posting_id) <= 200:
                return error(mid, -32602, "arguments must be exactly {posting_id: string of 1-200 characters}")
            return ok(mid, self.score(posting_id))
        return error(mid, -32601, "Method not found: %s" % method)

    def serve(self, stdin=sys.stdin, stdout=sys.stdout):
        for line in stdin:
            line = line.strip()
            if not line:
                continue
            self.log("client->server", line)
            try:
                message = json.loads(line)
            except ValueError:
                reply = error(None, -32700, "Parse error")
            else:
                reply = self.handle(message)
            if reply is not None:
                text = json.dumps(reply, ensure_ascii=False)
                self.log("server->client", text)
                stdout.write(text + "\n")
                stdout.flush()


def ok(mid, result):
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def error(mid, code, message):
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}


def main():
    transcript = os.environ.get("JS3_TRANSCRIPT") or HERE / "transcripts" / ("server-%s.jsonl" %
                                                                            time.strftime("%Y%m%dT%H%M%S"))
    Server(transcript).serve()
    return 0


if __name__ == "__main__":
    sys.exit(main())
