"""Scripted MCP client: drive a stdio server through a fixed message sequence and keep every raw line.

    python3 -I scripts/mcp_record.py --corpus <run dir>                      # transcript A (own server)
    python3 -I scripts/mcp_record.py --corpus <run dir> --expect teaching \\
        --name C-teaching-server --server-cmd "python3 -I other-server/main.py --stdio"   # transcript C

Writes transcripts/<name>-<UTC>.jsonl (one row per raw line, both directions: {"ts","dir","raw",...}),
transcripts/<name>-<UTC>.stderr.txt (the server's stderr, verbatim) and transcripts/<name>-<UTC>.md
(expected vs observed). The expected column is the STEPS table below, the same predictions written in
transcripts/EXPECTED-A.md and EXPECTED-C.md before the first run. Nothing here touches the network:
the client only reads the corpus run to pick a posting id, and talks to the server over pipes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import queue
import shlex
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from jsa3 import corpus as corpus_mod  # noqa: E402
from jsa3 import filter as filter_mod  # noqa: E402

TRANSCRIPTS = PROJECT / "transcripts"
SERVER = PROJECT / "src" / "jsa3" / "mcp_server.py"
UNKNOWN_ID = "no-such-posting-0000"
CLIENT_INFO = {"name": "jsa3-mcp-record", "version": "0.1.0"}


def utc(fmt="%Y-%m-%dT%H:%M:%S.%fZ"):
    return datetime.now(timezone.utc).strftime(fmt)


def err(code):
    return {"kind": "error", "code": code}


NONE = {"kind": "none"}


def res(**checks):
    return {"kind": "result", **checks}


def init(ident, version="2025-11-25", params=True):
    m = {"jsonrpc": "2.0", "id": ident, "method": "initialize"}
    if params:
        m["params"] = {"protocolVersion": version, "capabilities": {}, "clientInfo": CLIENT_INFO}
    return m


def call(ident, name, arguments):
    m = {"jsonrpc": "2.0"}
    if ident is not None:
        m["id"] = ident
    m.update(method="tools/call", params={"name": name, "arguments": arguments})
    return m


def req(ident, method):
    return {"jsonrpc": "2.0", "id": ident, "method": method}


NOTIFY = {"jsonrpc": "2.0", "method": "notifications/initialized"}


def steps(pid: str) -> list[dict]:
    """The sequence. `send` is a dict (sent as compact JSON) or a str (sent verbatim). expect: own / teaching."""
    S = []

    def add(session, what, send, own, teaching):
        S.append({"n": len(S) + 1, "session": session, "what": what, "send": send,
                  "expect": {"own": own, "teaching": teaching}})

    add(1, "tools/list before initialize", req(1, "tools/list"), err(-32000), err(-32000))
    add(1, "initialize (2025-11-25)", init(2), res(protocolVersion="2025-11-25"), res(protocolVersion="2025-11-25"))
    add(1, "tools/list before notifications/initialized", req(3, "tools/list"), err(-32000), err(-32000))
    add(1, "notifications/initialized", NOTIFY, NONE, NONE)
    add(1, "tools/list", req(5, "tools/list"), res(tools=["score_posting"]), res(tools=["lookup"]))
    add(1, f"tools/call score_posting real id {pid}", call(6, "score_posting", {"posting_id": pid}),
        res(isError=False, record_id=pid), err(-32602))
    add(1, "tools/call score_posting unknown id", call(7, "score_posting", {"posting_id": UNKNOWN_ID}),
        res(isError=True), err(-32602))
    add(1, "tools/call bad argument (posting_id: 5)", call(8, "score_posting", {"posting_id": 5}),
        err(-32602), err(-32602))
    add(1, "tools/call unknown tool apply_to_job", call(9, "apply_to_job", {"posting_id": pid}),
        err(-32602), err(-32602))
    add(1, "unknown method jobs/apply", req(10, "jobs/apply"), err(-32601), err(-32601))
    add(1, "unparseable line '{'", "{", err(-32700), err(-32700))
    add(1, "ping", req(12, "ping"), res(empty=True), err(-32601))
    add(1, "tools/call lookup office (teaching tool)", call(13, "lookup", {"key": "office"}),
        err(-32602), res(isError=False, text="505A Dana Hall"))
    add(1, "tools/call as a notification (no id)", call(None, "score_posting", {"posting_id": pid}), NONE, NONE)
    add(1, "second initialize (asks 2024-11-05)", init(15, "2024-11-05"), err(-32600),
        res(protocolVersion="2025-11-25"))
    add(1, "tools/list after second initialize", req(16, "tools/list"), res(tools=["score_posting"]),
        res(tools=["lookup"]))
    add(2, "initialize with no params", init(17, params=False), err(-32602), res(protocolVersion="2025-11-25"))
    add(2, "initialize asking 2024-11-05", init(18, "2024-11-05"), res(protocolVersion="2025-11-25"),
        res(protocolVersion="2025-11-25"))
    add(2, "notifications/initialized", NOTIFY, NONE, NONE)
    add(2, "tools/list", req(20, "tools/list"), res(tools=["score_posting"]), res(tools=["lookup"]))
    add(2, "raw '{}'", "{}", err(-32600), err(-32600))
    add(2, "raw '[]' (batch)", "[]", err(-32600), err(-32600))
    return S


def expected_text(e: dict) -> str:
    if e["kind"] == "none":
        return "no reply"
    if e["kind"] == "error":
        return f"error {e['code']}"
    bits = []
    if "protocolVersion" in e:
        bits.append(f"protocolVersion {e['protocolVersion']}")
    if "tools" in e:
        bits.append("tools " + ",".join(e["tools"]))
    if "isError" in e:
        bits.append(f"isError {str(e['isError']).lower()}")
    if "record_id" in e:
        bits.append(f"record.id {e['record_id']}")
    if "text" in e:
        bits.append(f"text {e['text']!r}")
    if e.get("empty"):
        bits.append("{}")
    return "result " + "; ".join(bits)


def judge(e: dict, sent, replies: list[str]) -> tuple[str, str]:
    """-> (observed summary, 'match' | 'MISMATCH')."""
    if not replies:
        return "no reply", "match" if e["kind"] == "none" else "MISMATCH"
    if len(replies) > 1:
        return f"{len(replies)} replies", "MISMATCH"
    try:
        msg = json.loads(replies[0])
    except ValueError:
        return "unparseable reply", "MISMATCH"
    want_id = sent.get("id") if isinstance(sent, dict) else None
    id_ok = msg.get("id") == want_id
    if "error" in msg:
        code = msg["error"].get("code")
        obs = f"error {code}" + ("" if id_ok else f" (id {msg.get('id')!r}, expected {want_id!r})")
        return obs, "match" if e["kind"] == "error" and code == e["code"] and id_ok else "MISMATCH"
    r = msg.get("result")
    if not isinstance(r, dict):
        return "result (not an object)", "MISMATCH"
    obs = {}
    if "protocolVersion" in r:
        obs["protocolVersion"] = r["protocolVersion"]
    if "tools" in r:
        obs["tools"] = [t.get("name") for t in r["tools"]]
    if "isError" in r:
        obs["isError"] = r["isError"]
    sc = r.get("structuredContent") or {}
    if isinstance(sc.get("record"), dict):
        obs["record_id"] = sc["record"].get("id")
    content = r.get("content") or []
    if content and isinstance(content[0], dict) and "text" in e:
        obs["text"] = content[0].get("text")
    if r == {}:
        obs["empty"] = True
    summary = expected_text(dict(obs, kind="result"))
    if not id_ok:
        summary += f" (id {msg.get('id')!r}, expected {want_id!r})"
    ok = e["kind"] == "result" and id_ok and all(obs.get(k) == v for k, v in e.items() if k != "kind")
    return summary, "match" if ok else "MISMATCH"


class Pipe:
    """One server process; stdout lines arrive on a queue, stderr is kept verbatim."""

    def __init__(self, cmd: list[str]):
        self.proc = subprocess.Popen(cmd, cwd=str(PROJECT), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        self.lines: queue.Queue = queue.Queue()
        self.stderr = bytearray()
        self._out_t = threading.Thread(target=self._out, daemon=True)
        self._out_t.start()
        self._err_t = threading.Thread(target=self._err, daemon=True)
        self._err_t.start()

    def _out(self):
        for b in self.proc.stdout:
            self.lines.put((utc(), b.decode("utf-8", errors="surrogateescape").rstrip("\r\n")))
        self.lines.put(None)

    def _err(self):
        for b in self.proc.stderr:
            self.stderr.extend(b)

    def send(self, text: str):
        self.proc.stdin.write(text.encode("utf-8") + b"\n")
        self.proc.stdin.flush()

    def collect(self, first_wait: float, settle: float) -> list[tuple[str, str]]:
        got, deadline = [], time.monotonic() + first_wait
        while True:
            left = deadline - time.monotonic()
            if left <= 0:
                return got
            try:
                item = self.lines.get(timeout=left)
            except queue.Empty:
                return got
            if item is None:
                return got
            got.append(item)
            deadline = time.monotonic() + settle

    def close(self) -> int:
        try:
            self.proc.stdin.close()
        except OSError:
            pass
        try:
            code = self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            code = self.proc.wait()
        self._err_t.join(timeout=5)
        self._out_t.join(timeout=5)
        for fh in (self.proc.stdout, self.proc.stderr):
            fh.close()
        return code


def pick_posting(corpus: dict, cfg: dict) -> tuple[str, str]:
    recs = [filter_mod.evaluate(p, cfg) for p in corpus["postings"]]
    unique = corpus_mod.by_id(corpus)
    for r in recs:
        if r["verdict"] == "keep" and r["id"] in unique:
            return r["id"], "first posting whose filter verdict is keep"
    first = next(r for r in recs if r["id"] in unique)
    return first["id"], "no posting is kept by the filter, so the first posting (unique id)"


def run(cmd: list[str], profile: str, pid: str, quiet: float = 0.8, timeout: float = 10.0, settle: float = 0.15):
    """Drive the sequence. -> (rows for the JSONL, per-step results, stderr text per session, exit codes)."""
    rows, results, stderr, codes = [], [], {}, {}
    sequence = steps(pid)
    for session in sorted({s["session"] for s in sequence}):
        pipe = Pipe(cmd)
        rows.append({"ts": utc(), "dir": "meta", "raw": None, "session": session, "note": "server started: " + shlex.join(cmd)})
        for s in (x for x in sequence if x["session"] == session):
            text = s["send"] if isinstance(s["send"], str) else json.dumps(s["send"], separators=(",", ":"))
            e = s["expect"][profile]
            rows.append({"ts": utc(), "dir": "client->server", "raw": text, "session": session, "step": s["n"]})
            pipe.send(text)
            got = pipe.collect(quiet if e["kind"] == "none" else timeout, settle)
            for ts, line in got:
                rows.append({"ts": ts, "dir": "server->client", "raw": line, "session": session, "step": s["n"]})
            observed, verdict = judge(e, s["send"], [line for _, line in got])
            results.append({"n": s["n"], "session": session, "what": s["what"], "sent": text,
                            "expected": expected_text(e), "observed": observed, "verdict": verdict,
                            "replies": [line for _, line in got]})
        codes[session] = pipe.close()
        stderr[session] = pipe.stderr.decode("utf-8", errors="replace")
        rows.append({"ts": utc(), "dir": "meta", "raw": None, "session": session,
                     "note": f"stdin closed; server exit code {codes[session]}"})
    return rows, results, stderr, codes


def run_in_process(make_server, profile: str, pid: str) -> list[dict]:
    """The same sequence and judge, fed straight to Server.handle_line (no pipes). Used by tests and by
    scripts/wrong_versions_mcp.py to show a planted wrong server fails the table."""
    results, sequence = [], steps(pid)
    for session in sorted({s["session"] for s in sequence}):
        server = make_server()
        for s in (x for x in sequence if x["session"] == session):
            text = s["send"] if isinstance(s["send"], str) else json.dumps(s["send"], separators=(",", ":"))
            reply = server.handle_line(text)
            replies = [] if reply is None else [reply]
            observed, verdict = judge(s["expect"][profile], s["send"], replies)
            results.append({"n": s["n"], "what": s["what"], "observed": observed, "verdict": verdict})
    return results


def write_md(path: Path, name: str, cmd, profile, corpus, pid, why, results, stderr, codes, recompute, started):
    mism = [r for r in results if r["verdict"] != "match"]
    out = [f"# Transcript {name}", "",
           f"Recorded {started} by `scripts/mcp_record.py` (a scripted client, not a model). Raw lines in both",
           f"directions: `{path.with_suffix('.jsonl').name}`. Server stderr: `{path.with_suffix('.stderr.txt').name}`.", "",
           f"- Server command: `{shlex.join(cmd)}` (cwd = project root; one fresh process per session)",
           f"- Expected column: profile `{profile}` (the predictions in "
           f"`transcripts/EXPECTED-{'A' if profile == 'own' else 'C'}.md`, written before the first run)",
           f"- Corpus run: `{corpus['run']}` ({len(corpus['postings'])} postings); posting id used: `{pid}` ({why})",
           f"- SHA-256 of src/jsa3/mcp_server.py at record time: `{hashlib.sha256(SERVER.read_bytes()).hexdigest()}`"
           + ("" if profile == "own" else " (not the server under test; recorded for completeness)"),
           f"- Server exit codes: " + ", ".join(f"session {k}: {v}" for k, v in codes.items()),
           f"- Result: {len(results) - len(mism)} of {len(results)} steps matched the prediction"
           + ("" if not mism else "; mismatches: " + ", ".join(str(r["n"]) for r in mism)), ""]
    if recompute is not None:
        out += [f"- Step 6 record compared with a client-side recomputation (same filter code + same corpus "
                f"files, so this checks the server used the declared corpus and config, not that the filter is "
                f"right): **{recompute}**", ""]
    out += ["| # | Session | Step | Sent (raw) | Expected | Observed | |", "|---|---|---|---|---|---|---|"]
    for r in results:
        sent = r["sent"] if len(r["sent"]) <= 90 else r["sent"][:87] + "..."
        out.append(f"| {r['n']} | {r['session']} | {r['what']} | `{sent}` | {r['expected']} | {r['observed']} | {r['verdict']} |")
    out += ["", "## Server stderr (verbatim)", ""]
    for k, v in stderr.items():
        out += [f"Session {k}:", "", "```text", v.rstrip() or "(empty)", "```", ""]
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", required=True, help="fetch run directory (report.json + raw/)")
    ap.add_argument("--config", default=str(PROJECT / "config" / "filter.json"))
    ap.add_argument("--server-cmd", help="server command line; {corpus} is replaced by --corpus. "
                                         "Default: this project's server")
    ap.add_argument("--expect", choices=["own", "teaching"], default="own")
    ap.add_argument("--name", help="output name prefix (default A-scripted / C-teaching-server)")
    ap.add_argument("--quiet", type=float, default=0.8, help="seconds to wait when no reply is expected")
    args = ap.parse_args(argv)

    corpus = corpus_mod.load(args.corpus)
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    pid, why = pick_posting(corpus, cfg)
    if args.server_cmd:
        cmd = [a.replace("{corpus}", str(args.corpus)) for a in shlex.split(args.server_cmd)]
    else:
        cmd = [sys.executable, "-I", str(SERVER), "--corpus", str(args.corpus), "--config", args.config]
    name = args.name or ("A-scripted" if args.expect == "own" else "C-teaching-server")
    started = utc("%Y-%m-%dT%H:%M:%SZ")
    stem = TRANSCRIPTS / f"{name}-{started.replace(':', '-')}"
    rows, results, stderr, codes = run(cmd, args.expect, pid, quiet=args.quiet)

    recompute = None
    if args.expect == "own":
        six = next(r for r in results if r["n"] == 6)
        try:
            got = json.loads(six["replies"][0])["result"]["structuredContent"]["record"]
            want = filter_mod.evaluate(corpus_mod.by_id(corpus)[pid], cfg)
            recompute = "identical" if got == want else "DIFFERENT"
        except (IndexError, KeyError, TypeError, ValueError):
            recompute = "not comparable (no structured record in the reply)"

    TRANSCRIPTS.mkdir(exist_ok=True)
    with open(stem.with_suffix(".jsonl"), "x", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    stem.with_suffix(".stderr.txt").write_text(
        "".join(f"--- session {k} ---\n{v}" for k, v in stderr.items()), encoding="utf-8")
    write_md(stem.with_suffix(".md"), stem.name, cmd, args.expect, corpus, pid, why, results, stderr, codes,
             recompute, started)
    mism = sum(r["verdict"] != "match" for r in results)
    print(f"wrote {stem}.jsonl/.md/.stderr.txt: {len(results) - mism}/{len(results)} steps matched")
    return 0 if mism == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
