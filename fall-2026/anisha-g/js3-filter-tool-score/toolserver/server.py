"""js3-job-filter: a small tool server written from scratch (Python standard library only) that speaks the Model Context
Protocol message shape over stdio: one JSON-RPC 2.0 message per line. Methods: initialize, notifications/initialized,
ping, tools/list, tools/call. It offers ONE capability, score_posting, which runs my filter (FILTER.md) and evidence
rules on a posting from the local corpus or on a title + text given by the caller.

Boundaries (assignment "Privacy and boundaries"): read-only. It has no network code, sends nothing, applies to nothing,
and the only file it writes is its own transcript under --transcripts (default: transcripts/ in this folder).
Every message in and out is appended to that transcript.

Run:  python3 -m toolserver.server [--corpus data/corpus.jsonl.gz] [--filter filters/filter_v1.0.json] [--transcripts transcripts]"""
import argparse, json, os, re, sys, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from js3 import filter as F, evidence as E

SUPPORTED_VERSIONS = ["2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"]
SERVER_INFO = {"name": "js3-job-filter", "version": "1.0.0"}
TOOL = {
    "name": "score_posting",
    "title": "Score a job posting with Anisha's JS3 filter",
    "description": ("Scores ONE job posting for the fictional persona Nadia Okafor (entry-level data analyst, at most 3 years) "
                    "with the rules in FILTER.md v1.0. Give either `id` (a posting id from the local corpus, e.g. "
                    "'greenhouse:stripe:123') or `title` + `text`. Returns the filter verdict (kept / rejected / cannot_tell), "
                    "the score, the failed rules, and every justification claim labelled SUPPORTED / CONTRADICTED / "
                    "INSUFFICIENT with a quote from the posting. Read-only: it does not fetch, apply or email; it appends every message "
                    "to its own transcript file. Rules: R1 analyst title word, R1b no engineer title (v1.1), R2 no seniority word, "
                    "R3 at least 2 of the persona's skills, R4 at most 3 years stated."),
    "inputSchema": {"type": "object", "additionalProperties": False,
                    "properties": {"id": {"type": "string", "description": "posting id from the local corpus"},
                                   "title": {"type": "string", "description": "posting title (use with text)"},
                                   "text": {"type": "string", "description": "full posting text (use with title)"},
                                   "location": {"type": "string", "description": "optional; does not affect the verdict"}}},
    "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
}

class Transcript:
    def __init__(self, folder):
        folder = Path(folder).resolve(); folder.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        self.path = folder / f"server-{stamp}-{os.getpid()}.jsonl"
    def log(self, direction, msg=None, raw=None):
        row = {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"), "dir": direction}
        if msg is not None: row["msg"] = msg
        if raw is not None: row["raw"] = raw
        with open(self.path, "a", encoding="utf-8") as f: f.write(json.dumps(row, ensure_ascii=False) + "\n")

class Server:
    def __init__(self, corpus_path, filter_path, transcript):
        self.cfg = F.load_filter(filter_path)
        self.corpus = {p["id"]: p for p in F.load_corpus(corpus_path)} if corpus_path and Path(corpus_path).exists() else {}
        self.t = transcript; self.initialized = False

    def handle(self, msg):
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
            return self.err(msg.get("id") if isinstance(msg, dict) else None, -32600, "Invalid Request")
        mid, method, params = msg.get("id"), msg["method"], msg.get("params") or {}
        is_note = "id" not in msg
        if method == "initialize":
            want = params.get("protocolVersion")
            self.initialized = True
            return self.ok(mid, {"protocolVersion": want if want in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0],
                                 "capabilities": {"tools": {"listChanged": False}}, "serverInfo": SERVER_INFO,
                                 "instructions": "One read-only tool: score_posting. Verdicts follow FILTER.md v1.0; "
                                                 "INSUFFICIENT claims mean 'I cannot tell'."})
        if is_note: return None                                   # notifications/initialized and any other notification
        if method == "ping": return self.ok(mid, {})
        if method == "tools/list": return self.ok(mid, {"tools": [TOOL]})
        if method == "tools/call":
            if params.get("name") != TOOL["name"]:
                return self.err(mid, -32602, f"Unknown tool: {params.get('name')!r}. This server offers only score_posting.")
            return self.ok(mid, self.score(params.get("arguments")))
        return self.err(mid, -32601, f"Method not found: {method}")

    def score(self, args):
        def bad(m): return {"content": [{"type": "text", "text": m}], "isError": True}
        if not isinstance(args, dict): return bad("arguments must be an object")
        extra = set(args) - set(TOOL["inputSchema"]["properties"])
        if extra: return bad(f"unknown argument(s): {sorted(extra)}")
        if any(not isinstance(v, str) for v in args.values()): return bad("every argument must be a string")
        if "id" in args:
            if set(args) - {"id"}: return bad("give either id, or title + text, not both")
            p = self.corpus.get(args["id"])
            if p is None: return bad(f"posting {args['id']!r} not found in the local corpus ({len(self.corpus)} postings). "
                                     f"Nothing was invented.")
        elif "title" in args and "text" in args:
            p = {"id": "caller-supplied", "title": args["title"], "text": args["text"], "location": args.get("location"), "url": None}
        else:
            return bad("give either id, or title + text")
        d = F.evaluate(p, self.cfg); j = E.justify(p, self.cfg)
        out = {"id": p["id"], "title": p.get("title"), "url": p.get("url"), "filter_version": d["filter_version"],
               "status": d["status"], "score": d["score"], "failed": d["failed"], "skills_matched": d["skills"],
               "years_max": d["years_max"], "shortlist": j["shortlist"], "why_not": j["why_not"],
               "claims": [{"claim": c["claim"], "label": c["label"], "quote": c["quote"], "say": c["say"]} for c in j["claims"]]}
        return {"content": [{"type": "text", "text": json.dumps(out, ensure_ascii=False)}], "structuredContent": out, "isError": False}

    @staticmethod
    def ok(mid, result): return {"jsonrpc": "2.0", "id": mid, "result": result}
    @staticmethod
    def err(mid, code, message): return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(HERE / "data" / "corpus.jsonl.gz"))
    ap.add_argument("--filter", default=str(HERE / "filters" / "filter_v1.0.json"))
    ap.add_argument("--transcripts", default=str(HERE / "transcripts"))
    a = ap.parse_args()
    t = Transcript(a.transcripts); srv = Server(a.corpus, a.filter, t)
    print(f"js3-job-filter ready: {len(srv.corpus)} postings, filter v{srv.cfg['version']}, transcript {t.path}", file=sys.stderr)
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            t.log("in", raw=line); reply = Server.err(None, -32700, "Parse error")
        else:
            t.log("in", msg=msg); reply = srv.handle(msg)
        if reply is not None:
            t.log("out", msg=reply); sys.stdout.write(json.dumps(reply, ensure_ascii=False) + "\n"); sys.stdout.flush()

if __name__ == "__main__": main()
