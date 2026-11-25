"""A minimal Model Context Protocol server, written from scratch (stdio, newline-delimited JSON-RPC 2.0).

One read-only capability: score_posting(posting_id[, filter_version]) against the saved corpus.

  .venv/bin/python js3/mcp_server.py [--filter v1.0] [--log PATH]

What it can touch:
- It reads raw/, filters/ and resume/ in this folder, and builds the corpus in memory. It never writes build/.
- It writes only the wire log named by --log (default: none). The log is appended locally, line by line, in both directions.
- It has no network code and no subprocess use, and it exposes no write, delete, fetch or exec tool.
  tests/test_mcp_server.py checks the source for these.
Methods: initialize, notifications/initialized, ping, tools/list, tools/call. Anything else gets -32601.
"""
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from js3.corpus import build  # noqa: E402
from js3.filter import load_filter, score_posting  # noqa: E402

SERVER_INFO = {"name": "js3-score-posting", "version": "1.0.0"}
SUPPORTED_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
FILTER_VERSIONS = sorted(p.stem for p in (ROOT / "filters").glob("v*.json"))

TOOL = {
    "name": "score_posting",
    "title": "Score one saved job posting with the JS3 filter",
    "description": (
        "Read-only. Returns the FILTER.md score breakdown (R+S+T+E+Y, threshold, verdict, the matched phrases "
        "with the field and a verbatim quote) for ONE posting in the saved corpus "
        "(JS1/JS2 captures of 2026-10-30 and 2026-11-10; nothing is fetched). posting_id is a full key "
        "'provider:board:id' or a bare id. The verdict is a filter score, not a judgment that the job is worth "
        "applying to."),
    "inputSchema": {
        "type": "object",
        "properties": {
            "posting_id": {"type": "string", "minLength": 1, "maxLength": 200,
                           "description": "e.g. 'greenhouse:databricks:8091041002' or '8091041002'"},
            "filter_version": {"type": "string", "enum": FILTER_VERSIONS,
                               "description": "Filter file to apply; default is the server's configured version"},
        },
        "required": ["posting_id"],
        "additionalProperties": False,
    },
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
}


class Server:
    def __init__(self, default_filter="v1.0", log_path=None):
        self.default_filter = default_filter
        self.log_path = Path(log_path) if log_path else None
        self.corpus, _ = build(write=False)
        self.by_bare_id = {}
        for key, p in self.corpus.items():
            self.by_bare_id.setdefault(str(p["id"]), []).append(key)

    # ---- wire log -----------------------------------------------------------------------------
    def log(self, direction, line):
        if self.log_path:
            rec = {"t": dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds"),
                   "dir": direction, "line": line}
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # ---- protocol -----------------------------------------------------------------------------
    def handle(self, msg):
        """Return a response dict, or None for notifications."""
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
            return _err(msg.get("id") if isinstance(msg, dict) else None, -32600, "Invalid Request")
        method, mid, params = msg["method"], msg.get("id"), msg.get("params") or {}
        if not isinstance(params, dict):
            return None if "id" not in msg else _err(mid, -32602, "Invalid params: must be an object")
        is_notification = "id" not in msg
        if method.startswith("notifications/"):
            return None  # notifications/initialized, notifications/cancelled: no response
        if is_notification:
            return None
        if method == "initialize":
            requested = params.get("protocolVersion")
            version = requested if requested in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0]
            return _ok(mid, {"protocolVersion": version, "capabilities": {"tools": {"listChanged": False}},
                             "serverInfo": SERVER_INFO,
                             "instructions": ("One read-only tool over a saved corpus; no network. Tools write "
                                              "nothing; the operator may enable a local wire log (--log).")})
        if method == "ping":
            return _ok(mid, {})
        if method == "tools/list":
            return _ok(mid, {"tools": [TOOL]})
        if method == "tools/call":
            return self.call(mid, params)
        return _err(mid, -32601, f"Method not found: {method}")

    def call(self, mid, params):
        if params.get("name") != TOOL["name"]:
            return _err(mid, -32602, f"Unknown tool: {params.get('name')!r}")
        args = params.get("arguments") or {}
        if not isinstance(args, dict) or set(args) - {"posting_id", "filter_version"}:
            return _err(mid, -32602, "Invalid arguments: only posting_id and filter_version are accepted")
        pid, fv = args.get("posting_id"), args.get("filter_version", self.default_filter)
        if not isinstance(pid, str) or not pid.strip() or len(pid) > 200:
            return _err(mid, -32602, "Invalid arguments: posting_id must be a non-empty string (max 200)")
        if fv not in FILTER_VERSIONS:
            return _err(mid, -32602, f"Invalid arguments: filter_version must be one of {FILTER_VERSIONS}")
        key = pid.strip()
        if key not in self.corpus:
            matches = self.by_bare_id.get(key, [])
            if len(matches) != 1:
                why = "matches several boards" if matches else "is not in the saved corpus"
                return _ok(mid, {"isError": True, "content": [{"type": "text", "text": (
                    f"I cannot tell: posting {key!r} {why} ({len(self.corpus)} postings from the 2026-10-30 and "
                    f"2026-11-10 captures). Nothing was fetched or guessed.")}]})
            key = matches[0]
        r = score_posting(self.corpus[key], load_filter(fv))
        p = self.corpus[key]
        summary = {"key": key, "title": p["title"], "location": p["location"], "url": p["url"],
                   "captured_utc": p["last_seen"], **{k: r[k] for k in ("filter_version", "threshold", "score",
                                                                         "verdict", "missing")},
                   "arithmetic": r.get("arithmetic"), "parts": r["parts"]}
        text = (f"{key} — {p['title']}\nfilter {fv}: {r.get('arithmetic', r.get('reason'))}; "
                f"threshold {r['threshold']} -> {r['verdict']}\n\n" + json.dumps(summary, ensure_ascii=False, indent=1))
        return _ok(mid, {"content": [{"type": "text", "text": text}], "isError": False})

    def serve(self, stdin=sys.stdin, stdout=sys.stdout):
        for line in stdin:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            self.log("client->server", line)
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                resp = _err(None, -32700, "Parse error")
            else:
                resp = self.handle(msg)
            if resp is not None:
                out = json.dumps(resp, ensure_ascii=False)
                self.log("server->client", out)
                stdout.write(out + "\n")
                stdout.flush()


def _ok(mid, result):
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def _err(mid, code, message):
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--filter", default="v1.0", choices=FILTER_VERSIONS)
    ap.add_argument("--log")
    a = ap.parse_args(argv)
    Server(a.filter, a.log).serve()


if __name__ == "__main__":
    main()
