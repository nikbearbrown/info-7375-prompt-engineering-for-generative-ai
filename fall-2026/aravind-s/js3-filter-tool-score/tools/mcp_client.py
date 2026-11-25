"""Our own MCP client (JS3, step 2 item 3): the normal requests, then requests a client is not entitled to.

It starts a server as a child process, speaks newline-delimited JSON-RPC 2.0 over the child's stdin and stdout, and
keeps a dated transcript of every line in both directions. Each step carries the answer it expects, written here
before any run: for our server, the contract in job_agent/mcp_server.py; for the other server, what the copied
source says it will do. A step whose answer differs is recorded as a mismatch, never hidden.

Sessions (each on a fresh server process, so that a call before initialize meets a server that has seen nothing):
  early      a tool call before initialize, then initialize, then tools/list before notifications/initialized
  main       the handshake, tools/list, a kept posting, a rejected posting, an unknown posting; then the requests a
             client is not entitled to: an unknown tool (update_state), an extra argument, a path-traversal id,
             arguments that are not an object, resources/read, and a malformed line; then tools/list again
  lifecycle  initialize sent twice, and a tool call sent as a notification (no id): choices chapter 8 says the
             reference never made
  bytes      a line that is not UTF-8 (a client MUST NOT send one; this checks what the server does if one comes)
  deep       a line of 20,000 nested brackets (valid-looking JSON that Python's parser cannot hold)
The last three go beyond the brief's list; they are labeled so in the record.

Usage (from the repo root):
  python3 tools/mcp_client.py own     our server, python3 -B -m job_agent.mcp_server, started with --transcript so
                                      the server keeps its own record of the same lines; the two records are compared
  python3 tools/mcp_client.py other   the course's lesson 8 reference server, js3/mcp/other-server/main.py --stdio

Writes js3/mcp/transcripts/<UTC time>-<target>-client.jsonl (every line, both directions, with times) and
<UTC time>-<target>-client.md (the same, readable, with each expectation). Exit 0 when every answer was the expected
one (and, for our server, its own record matches the client's), 1 when one was not, 2 when nothing could be run.
"""

from __future__ import annotations

import argparse
import json
import queue
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
TRANSCRIPTS = REPO / "js3" / "mcp" / "transcripts"
OTHER_SERVER = Path("js3") / "mcp" / "other-server" / "main.py"
SERVER_ENV = {"PATH": "/usr/bin:/bin", "LANG": "en_US.UTF-8", "LC_ALL": "en_US.UTF-8"}
WAIT_SECONDS = 15
CLIENT_INFO = {"name": "js3-mcp-client", "version": "1.0.0"}
DEEP = 20_000

# Our server's postings (FILTER.md v1.0 on the saved answers of run 2026-11-20T114036Z). Chosen outside the audit's
# and the held-out set's cards and outside the shortlist, so no blind card's verdict shows up here.
KEPT = ("ashby-openai", "f3ddd41c-541f-485e-90d6-86c26e018e9f")      # Software Engineer, GPT Infrastructure
REJECTED = ("greenhouse-verkada", "5283655007")                       # Software Engineer, Cloud Infrastructure
UNKNOWN = ("ashby-openai", "00000000-0000-4000-8000-000000000000")   # well formed, in no saved answer


# The plans: what is sent and what each answer is expected to be.

def step(label, send, expect, entitled=True, why=""):
    return {"label": label, "send": send, "expect": expect, "entitled": entitled, "why": why}


def request(rid, method, params=None):
    message = {"jsonrpc": "2.0", "id": rid, "method": method}
    if params is not None:
        message["params"] = params
    return message


def notification(method, params=None):
    message = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        message["params"] = params
    return message


INITIALIZE_PARAMS = {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": CLIENT_INFO}


def handshake(rid=1):
    return [step("initialize", request(rid, "initialize", INITIALIZE_PARAMS), "result"),
            step("notifications/initialized", notification("notifications/initialized"), "none",
                 why="a notification is never answered")]


def own_plan(kept=KEPT, rejected=REJECTED, unknown=UNKNOWN) -> list:
    """Our server: the expected answers are its contract (job_agent/mcp_server.py, the lifecycle table)."""
    def call(rid, arguments, name="score_posting"):
        return request(rid, "tools/call", {"name": name, "arguments": arguments})

    def args(pair):
        return {"board": pair[0], "posting_id": pair[1]}

    return [
        {"name": "early", "about": "a fresh server: calls before the handshake is finished", "steps": [
            step("tools/call before initialize", call(1, args(kept)), "error -32000", entitled=False),
            step("initialize", request(2, "initialize", INITIALIZE_PARAMS), "result"),
            step("tools/list before notifications/initialized", request(3, "tools/list"), "error -32000",
                 entitled=False, why="initialized but not ready: chapter 8's missing lifecycle test"),
        ]},
        {"name": "main", "about": "the normal requests, then requests a client is not entitled to", "steps": [
            *handshake(1),
            step("tools/list", request(2, "tools/list"), "result"),
            step(f"score_posting, a kept posting ({kept[0]} {kept[1]})", call(3, args(kept)), "result isError=false"),
            step(f"score_posting, a rejected posting ({rejected[0]} {rejected[1]})", call(4, args(rejected)),
                 "result isError=false", why="a rejection is the tool's answer, not a failure"),
            step(f"score_posting, an unknown posting ({unknown[1]})", call(5, args(unknown)), "result isError=true",
                 why="the tool ran and found nothing: a tool result, not a protocol error"),
            step("an unknown tool, update_state", call(6, {"board": kept[0]}, name="update_state"), "error -32602",
                 entitled=False),
            step("an extra argument (profile)", call(7, {**args(kept), "profile": "private/real-resume.json"}),
                 "result isError=true", entitled=False,
                 why="input validation is a tool execution error in MCP 2025-11-25"),
            step("a path-traversal posting_id", call(8, {"board": kept[0], "posting_id": "../../../../etc/passwd"}),
                 "result isError=true", entitled=False, why="the id fails the pattern; it is never used as a path"),
            step("arguments that are not an object", call(9, [kept[0], kept[1]]), "error -32602", entitled=False,
                 why="fails the CallToolRequest schema: a protocol error"),
            step("resources/read", request(10, "resources/read", {"uri": "file:///etc/passwd"}), "error -32601",
                 entitled=False, why="the server declares no resources"),
            step("a malformed line", b'{"jsonrpc": "2.0", "id": 11, "method": "tools/list"', "error -32700",
                 entitled=False, why="answered with id null: a parse error cannot know the id"),
            step("tools/list again", request(12, "tools/list"), "result", why="the server still answers"),
        ]},
        {"name": "lifecycle", "about": "beyond the brief's list: two choices the lesson 8 reference leaves unmade",
         "steps": [
             *handshake(1),
             step("initialize again", request(2, "initialize", INITIALIZE_PARAMS), "error -32000", entitled=False),
             step("tools/call sent as a notification (no id)",
                  notification("tools/call", {"name": "score_posting", "arguments": args(kept)}), "none",
                  entitled=False, why="never answered and never run"),
             step("tools/list", request(3, "tools/list"), "result"),
         ]},
        {"name": "bytes", "about": "beyond the brief's list: a line that is not UTF-8", "steps": [
            *handshake(1),
            step("tools/list", request(2, "tools/list"), "result"),
            step("a line that is not UTF-8", b"\xff\xfe not UTF-8", "error -32700", entitled=False),
            step("tools/list", request(3, "tools/list"), "result", why="the server still answers"),
        ]},
        {"name": "deep", "about": f"beyond the brief's list: {DEEP:,} nested brackets on one line", "steps": [
            *handshake(1),
            step("tools/list", request(2, "tools/list"), "result"),
            step(f"{DEEP:,} nested brackets", b"[" * DEEP, "error -32700", entitled=False),
            step("tools/list", request(3, "tools/list"), "result", why="the server still answers"),
        ]},
    ]


def other_plan() -> list:
    """The lesson 8 reference server: each expected answer is what its source (main.py) says it will do."""
    def call(rid, arguments, name="lookup"):
        return request(rid, "tools/call", {"name": name, "arguments": arguments})

    return [
        {"name": "early", "about": "a fresh server: calls before the handshake is finished", "steps": [
            step("tools/call before initialize", call(1, {"key": "office"}), "error -32000", entitled=False,
                 why="main.py line 29: not ready"),
            step("initialize", request(2, "initialize", INITIALIZE_PARAMS), "result"),
            step("tools/list before notifications/initialized", request(3, "tools/list"), "error -32000",
                 entitled=False, why="main.py line 29: initialized but not ready"),
        ]},
        {"name": "main", "about": "the normal requests, then requests a client is not entitled to", "steps": [
            *handshake(1),
            step("tools/list", request(2, "tools/list"), "result"),
            step("lookup, a known key (office)", call(3, {"key": "office"}), "result isError=false",
                 why="main.py line 42: the literal mapping"),
            step("lookup, an unknown key (missing)", call(4, {"key": "missing"}), "result isError=true",
                 why="main.py lines 42 to 44"),
            step("an unknown tool, update_state", call(5, {"key": "office"}, name="update_state"), "error -32602",
                 entitled=False, why="main.py lines 37 to 38"),
            step("an extra argument (profile)", call(6, {"key": "office", "profile": "private/real-resume.json"}),
                 "error -32602", entitled=False, why="main.py lines 40 to 41: exactly the key 'key'"),
            step("a path-traversal key", call(7, {"key": "../../../../etc/passwd"}), "result isError=true",
                 entitled=False, why="any string is looked up in the mapping, never opened"),
            step("arguments that are not an object", call(8, ["office"]), "error -32602", entitled=False,
                 why="main.py lines 40 to 41"),
            step("resources/read", request(9, "resources/read", {"uri": "file:///etc/passwd"}), "error -32601",
                 entitled=False, why="main.py lines 45 to 46"),
            step("a malformed line", b'{"jsonrpc": "2.0", "id": 10, "method": "tools/list"', "error -32700",
                 entitled=False, why="main.py lines 64 to 67"),
            step("tools/list again", request(11, "tools/list"), "result"),
        ]},
        {"name": "lifecycle", "about": "beyond the brief's list: two choices the lesson 8 reference leaves unmade",
         "steps": [
             *handshake(1),
             step("initialize again", request(2, "initialize", INITIALIZE_PARAMS), "result", entitled=False,
                  why="main.py lines 25 to 28 run again; ready stays true"),
             step("tools/call sent as a notification (no id)",
                  notification("tools/call", {"name": "lookup", "arguments": {"key": "office"}}), "none",
                  entitled=False, why="main.py lines 18 to 21: dropped"),
             step("tools/list", request(3, "tools/list"), "result"),
         ]},
        {"name": "bytes", "about": "beyond the brief's list: a line that is not UTF-8", "steps": [
            *handshake(1),
            step("tools/list", request(2, "tools/list"), "result"),
            step("a line that is not UTF-8", b"\xff\xfe not UTF-8", "ends", entitled=False,
                 why="main.py line 63 decodes stdin outside the try: UnicodeDecodeError is not caught"),
            step("tools/list", request(3, "tools/list"), "not sent", why="the process has ended"),
        ]},
        {"name": "deep", "about": f"beyond the brief's list: {DEEP:,} nested brackets on one line", "steps": [
            *handshake(1),
            step("tools/list", request(2, "tools/list"), "result"),
            step(f"{DEEP:,} nested brackets", b"[" * DEEP, "ends", entitled=False,
                 why="main.py line 66 catches ValueError only; json raises RecursionError"),
            step("tools/list", request(3, "tools/list"), "not sent", why="the process has ended"),
        ]},
    ]


# One server process.

class Session:
    """A server child process, with a thread reading its stdout line by line and another collecting its stderr."""

    def __init__(self, command: list, cwd: Path, env: dict):
        self.proc = subprocess.Popen(command, cwd=str(cwd), env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        self.lines = queue.Queue()
        self.ended = False
        self.stderr = b""
        self._out = threading.Thread(target=self._read_stdout, daemon=True)
        self._err = threading.Thread(target=self._read_stderr, daemon=True)
        self._out.start()
        self._err.start()

    def _read_stdout(self):
        for raw in iter(self.proc.stdout.readline, b""):
            self.lines.put((now(), raw))
        self.lines.put((now(), None))

    def _read_stderr(self):
        self.stderr = self.proc.stderr.read()

    def send(self, data: bytes) -> bool:
        try:
            self.proc.stdin.write(data + b"\n")
            self.proc.stdin.flush()
            return True
        except (BrokenPipeError, OSError):
            return False

    def next_line(self, timeout: float = WAIT_SECONDS):
        """(time, raw line), (time, None) once stdout has ended, or None when nothing came in time."""
        if self.ended:
            return None
        try:
            at, raw = self.lines.get(timeout=timeout)
        except queue.Empty:
            return None
        if raw is None:
            self.ended = True
        return at, raw

    def close(self) -> list:
        """Close stdin (MCP's stdio shutdown), read what is left, and wait for the process. Returns late lines."""
        late = []
        try:
            self.proc.stdin.close()
        except OSError:
            pass
        while not self.ended:
            got = self.next_line(timeout=10)
            if got is None:
                break
            if got[1] is not None:
                late.append(got)
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()
        self._out.join(timeout=5)
        self._err.join(timeout=5)
        for stream in (self.proc.stdout, self.proc.stderr):
            stream.close()
        return late


def run_session(session_plan: dict, command: list, cwd: Path, env: dict, log: list) -> list:
    """Run one session's steps on a fresh process; append every line and every step's outcome to log."""
    name = session_plan["name"]
    log.append({"type": "session", "session": name, "about": session_plan["about"], "at": now()})
    proc = Session(command, cwd, env)
    outcomes, pending = [], None  # pending: a notification whose silence is confirmed by the next answer
    for number, item in enumerate(session_plan["steps"], 1):
        data = item["send"] if isinstance(item["send"], bytes) else json.dumps(item["send"]).encode("utf-8")
        outcome = {"type": "step", "session": name, "step": number, "label": item["label"],
                   "entitled": item["entitled"], "why": item["why"], "expected": item["expect"], "unexpected": []}
        if proc.ended:
            outcome["actual"] = "not sent"
            outcomes.append(outcome)
            continue
        sent_at = now()
        if not proc.send(data):
            outcome["actual"] = "not sent"
            outcomes.append(outcome)
            continue
        log.append(_line(name, number, "client->server", data, sent_at))
        wanted = item["send"].get("id") if isinstance(item["send"], dict) else None
        if isinstance(item["send"], dict) and "id" not in item["send"]:
            outcome["actual"] = "none"  # confirmed or overturned by the next answer
            pending = outcome
            outcomes.append(outcome)
            continue
        while True:
            got = proc.next_line()
            if got is None:
                outcome["actual"] = f"no answer within {WAIT_SECONDS} s"
                break
            at, raw = got
            if raw is None:
                outcome["actual"] = "ends"
                break
            log.append(_line(name, number, "server->client", raw, at))
            message = _parse(raw)
            if isinstance(item["send"], bytes) or (isinstance(message, dict) and message.get("id") == wanted):
                outcome["actual"] = describe(message)
                outcome["envelope"] = envelope_problems(message, None if isinstance(item["send"], bytes) else wanted)
                break
            (pending or outcome)["unexpected"].append(raw.decode("utf-8", "replace").rstrip("\n"))
        if pending is not None:
            if pending["unexpected"]:
                pending["actual"] = "answered"
            pending = None
        outcomes.append(outcome)
    for at, raw in proc.close():
        log.append(_line(name, None, "server->client", raw, at))
        target = pending or (outcomes[-1] if outcomes else None)
        if target is not None:
            target["unexpected"].append(raw.decode("utf-8", "replace").rstrip("\n"))
            if target is pending:
                pending["actual"] = "answered"
    for outcome in outcomes:
        outcome["match"] = outcome["actual"] == outcome["expected"] and not outcome["unexpected"] \
            and not outcome.get("envelope")
        log.append(outcome)
    log.append({"type": "session_end", "session": name, "at": now(), "exit_code": proc.proc.returncode,
                "stderr": scrub(proc.stderr.decode("utf-8", "replace"), cwd)[-4000:]})
    return outcomes


def describe(message) -> str:
    """An answer as the plans write it: "result", "result isError=true/false" or "error <code>"."""
    if not isinstance(message, dict):
        return "not JSON-RPC"
    if "error" in message:
        error = message["error"]
        return f"error {error.get('code')}" if isinstance(error, dict) else "error"
    if "result" in message:
        result = message["result"]
        if isinstance(result, dict) and "isError" in result:
            return f"result isError={'true' if result['isError'] is True else 'false'}"
        return "result"
    return "not JSON-RPC"


def envelope_problems(message, wanted_id) -> list:
    """JSON-RPC 2.0's response shape: version, the request's id (null for a parse error), one of result or error."""
    if not isinstance(message, dict):
        return ["the line is not a JSON object"]
    problems = []
    if message.get("jsonrpc") != "2.0":
        problems.append('jsonrpc is not "2.0"')
    if message.get("id") != wanted_id or "id" not in message:
        problems.append(f"id is {message.get('id')!r}, not {wanted_id!r}")
    if ("result" in message) == ("error" in message):
        problems.append("not exactly one of result and error")
    error = message.get("error")
    if "error" in message and not (isinstance(error, dict) and isinstance(error.get("code"), int)
                                   and isinstance(error.get("message"), str)):
        problems.append("the error has no integer code and string message")
    return problems


# A run: the sessions, the files, the comparison.

def run(target: str, *, repo: Path = REPO, out: Path = None, plan: list = None, stamp: str = None,
        command: list = None) -> dict:
    """Run every session of the target's plan; write <stamp>-<target>-client.jsonl and .md into out.

    command replaces the target's server command (the tests use it for a constructed server).
    """
    repo = Path(repo)
    out = Path(out) if out is not None else repo / "js3" / "mcp" / "transcripts"
    stamp = stamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    base = out / f"{stamp}-{target}-client"
    server_log = None
    if target == "own":
        server_log = repo / "js3" / "mcp" / "transcripts" / f"{stamp}-own-server.jsonl"
        default_command = [sys.executable, "-B", "-m", "job_agent.mcp_server", "--transcript",
                           str(server_log.relative_to(repo))]
        plan = plan if plan is not None else own_plan()
    elif target == "other":
        default_command = [sys.executable, "-B", "-I", str(OTHER_SERVER), "--stdio"]
        plan = plan if plan is not None else other_plan()
    else:
        raise ValueError(f"unknown target {target!r}")
    command = command or default_command
    for path in (base.with_suffix(".jsonl"), base.with_suffix(".md"), server_log):
        if path is not None and path.exists():
            raise FileExistsError(f"{path} already exists; a transcript is never overwritten")
    log = [{"type": "run", "target": target, "started_at": now(), "command": ["python3", *command[1:]],
            "python": sys.version.split()[0], "cwd": "the repo root", "env": SERVER_ENV,
            "server_transcript": str(server_log.relative_to(repo)) if server_log else None,
            "client": "tools/mcp_client.py"}]
    outcomes = []
    for session_plan in plan:
        outcomes += run_session(session_plan, command, repo, dict(SERVER_ENV), log)
    comparison = compare_with_server_log(log, server_log) if server_log else None
    evidence = evidence_checks(log, repo) if target == "own" else []
    matched = sum(1 for o in outcomes if o["match"])
    summary = {"type": "summary", "steps": len(outcomes), "matched": matched,
               "server_record_matches": comparison["match"] if comparison else None, "finished_at": now()}
    if comparison:
        log.append({"type": "comparison", **comparison})
    log += [{"type": "evidence", **e} for e in evidence]
    log.append(summary)
    out.mkdir(parents=True, exist_ok=True)
    with open(base.with_suffix(".jsonl"), "x", encoding="utf-8") as handle:
        for entry in log:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    with open(base.with_suffix(".md"), "x", encoding="utf-8") as handle:
        handle.write(render(log, target, base.name))
    ok = matched == len(outcomes) and (comparison is None or comparison["match"])
    return {"ok": ok, "summary": summary, "files": [base.with_suffix(".jsonl"), base.with_suffix(".md")]
            + ([server_log] if server_log else []), "outcomes": outcomes, "comparison": comparison,
            "evidence": evidence}


def compare_with_server_log(log: list, server_log: Path) -> dict:
    """The server's own record (--transcript) against the client's, session by session, line by line."""
    if not server_log.exists():
        return {"match": False, "details": [f"{server_log.name} was not written"]}
    sessions, current = [], None
    for entry in (json.loads(line) for line in server_log.read_text(encoding="utf-8").splitlines() if line):
        if entry.get("event") == "start":
            current = {"lines": [], "end": None}
            sessions.append(current)
        elif entry.get("event") == "end" and current is not None:
            current["end"] = entry.get("reason")
        elif "dir" in entry and current is not None:
            current["lines"].append(({"in": "client->server", "out": "server->client"}[entry["dir"]], entry["text"],
                                     entry.get("utf8", True)))
    names = [e["session"] for e in log if e["type"] == "session"]
    client = {name: [(e["dir"], e["text"], e.get("utf8", True)) for e in log
                     if e["type"] == "line" and e["session"] == name] for name in names}
    details = []
    if len(sessions) != len(names):
        details.append(f"the server recorded {len(sessions)} sessions, the client {len(names)}")
    for name, server in zip(names, sessions):
        if server["lines"] != client[name]:
            details.append(f"session {name}: the two records differ")
        if server["end"] != "stdin closed":
            details.append(f"session {name}: the server's record ends with {server['end']!r}")
    counted = sum(len(s["lines"]) for s in sessions)
    return {"match": not details, "server_transcript": server_log.name, "sessions": len(sessions),
            "lines": counted, "details": details}


def evidence_checks(log: list, repo: Path) -> list:
    """Each successful score_posting result against the committed filter run of the same FILTER.md version.

    FILTER.md keeps every version, and the server names the one it scored with; the newest committed run of that
    version is the one to compare with (comparing with a run of another version would test the wrong rules).
    """
    base = repo / "js3" / "filter-run"
    runs = sorted(p for p in base.glob("*") if (p / "verdicts.json").exists()) if base.exists() else []
    if not runs:
        return []
    by_version = {}
    for run in runs:  # oldest first, so the newest run of each version is the one kept
        data = json.loads((run / "verdicts.json").read_text(encoding="utf-8"))
        by_version[data["meta"].get("filter_version", "1.0")] = (run, data)
    checks = []
    for entry in log:
        if entry["type"] != "line" or entry["dir"] != "server->client":
            continue
        message = _parse(entry["text"].encode("utf-8"))
        result = message.get("result") if isinstance(message, dict) else None
        if not (isinstance(result, dict) and result.get("isError") is False and result.get("content")):
            continue
        try:
            payload = json.loads(result["content"][0]["text"])
        except (ValueError, KeyError, TypeError):
            continue
        if not isinstance(payload, dict) or payload.get("tool") != "score_posting":
            continue
        key = (payload["board"], payload["posting_id"])
        version = (payload.get("filter") or {}).get("version")
        run, verdicts = by_version.get(version, (None, None))
        if verdicts is None:
            checks.append({"session": entry["session"], "board": key[0], "posting_id": key[1],
                           "fate": payload["record"]["fate"], "filter_run": None, "filter_version": version,
                           "same_saved_answer": False, "same_filter_md": False, "record_equal": False})
            continue
        records = {(r["board"], r["id"]): r for r in verdicts["records"]}
        shas = {s["key"]: s["sha256"] for s in verdicts["meta"]["sources"]}
        committed = records.get(key)
        checks.append({"session": entry["session"], "board": key[0], "posting_id": key[1],
                       "fate": payload["record"]["fate"], "filter_run": run.name, "filter_version": version,
                       "same_saved_answer": shas.get(key[0]) == payload["source"]["sha256"],
                       "same_filter_md": verdicts["meta"]["filter_md_sha256"] == payload["filter"]["sha256"],
                       "record_equal": committed is not None and committed == payload["record"]})
    return checks


# The readable copy.

def render(log: list, target: str, name: str) -> str:
    run_entry = log[0]
    summary = log[-1]
    title = "our server (job_agent/mcp_server.py)" if target == "own" else \
        "the course's lesson 8 reference server (js3/mcp/other-server/main.py)"
    lines = [f"# MCP client run: {title}", "",
             f"Recorded by `tools/mcp_client.py` (`python3 tools/mcp_client.py {target}`), started "
             f"{run_entry['started_at']} (UTC), Python {run_entry['python']}. Every line below comes from "
             f"`{name}.jsonl`, which holds the exact text of each line in both directions and the time it was sent "
             "or read. Here each line is laid out for reading; where a tool result's text is itself JSON, it is "
             "shown parsed under the message instead of as one escaped string.", "",
             f"- Server command: `{' '.join(run_entry['command'])}`, run in {run_entry['cwd']}, one fresh process "
             "per session.",
             f"- Environment given to the server: {', '.join(f'{k}={v}' for k, v in run_entry['env'].items())} "
             "(nothing else).",
             f"- The server's own record of the same lines: `{run_entry['server_transcript']}`." if
             run_entry["server_transcript"] else "- The server keeps no record of its own; this file is the only one.",
             "", "## Summary", "",
             f"**{summary['matched']} of {summary['steps']} answers were the expected ones.** \"Not entitled\" marks "
             "a request a compatible client has no right to make.", "",
             "| Session | # | Step | Entitled | Expected | Actual | Match |", "|---|---:|---|---|---|---|---|"]
    steps = [e for e in log if e["type"] == "step"]
    for o in steps:
        lines.append(f"| {o['session']} | {o['step']} | {o['label']} | {'yes' if o['entitled'] else 'not entitled'} "
                     f"| {o['expected']} | {o['actual']} | {'yes' if o['match'] else '**NO**'} |")
    comparison = next((e for e in log if e["type"] == "comparison"), None)
    if comparison:
        lines += ["", "## The server's own record", "",
                  f"`{comparison['server_transcript']}`: {comparison['sessions']} sessions, {comparison['lines']} "
                  f"lines. **{'It matches this record line for line.' if comparison['match'] else 'It differs.'}**"]
        lines += [f"- {d}" for d in comparison["details"]]
    evidence = [e for e in log if e["type"] == "evidence"]
    if evidence:
        lines += ["", "## Evidence checks, after the run", "",
                  "Each successful score_posting record against the record the committed filter run made of the "
                  "same posting (`python3 -m job_agent filter`, an earlier commit).", "",
                  "| Session | Board | Posting | Fate | Filter run | Same saved answer | Same FILTER.md | "
                  "Record equal |", "|---|---|---|---|---|---|---|---|"]
        for e in evidence:
            lines.append(f"| {e['session']} | {e['board']} | `{e['posting_id']}` | {e['fate']} | {e['filter_run']} | "
                         f"{_yes(e['same_saved_answer'])} | {_yes(e['same_filter_md'])} | {_yes(e['record_equal'])} |")
    for entry in log:
        if entry["type"] == "session":
            lines += ["", f"## Session: {entry['session']}", "", f"{entry['about']}. Started {entry['at']}."]
            for o in (s for s in steps if s["session"] == entry["session"]):
                lines += ["", f"### {o['step']}. {o['label']}" + ("" if o["entitled"] else " (not entitled)"), "",
                          f"Expected: {o['expected']}" + (f" ({o['why']})" if o["why"] else "") +
                          f". Actual: {o['actual']}. " + ("Match." if o["match"] else "**Mismatch.**")]
                for problem in o.get("envelope") or []:
                    lines.append(f"- Envelope problem: {problem}")
                for extra in o["unexpected"]:
                    lines.append(f"- Unexpected line: `{extra[:300]}`")
                for line in (e for e in log if e["type"] == "line" and e["session"] == o["session"]
                             and e["step"] == o["step"]):
                    lines += _shown_line(line)
        elif entry["type"] == "session_end":
            lines += ["", f"Session {entry['session']} ended {entry['at']}: exit code {entry['exit_code']}."]
            if entry["stderr"].strip():
                lines += ["", "The server's stderr:", "", "```text", entry["stderr"].rstrip(), "```"]
            else:
                lines.append("The server wrote nothing to stderr.")
    return "\n".join(lines) + "\n"


def render_server_transcript(path: Path) -> str:
    """A readable copy of a server transcript (.jsonl written by job_agent.mcp_server --transcript)."""
    entries = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]
    lines = [f"# Server transcript: {Path(path).name}", "",
             f"Written by `job_agent/mcp_server.py` itself (`--transcript`), one entry per line received (in) and "
             f"sent (out), with the UTC time. Copied from `{Path(path).name}`; nothing is left out.", ""]
    for entry in entries:
        if "event" in entry:
            details = ", ".join(f"{k} {json.dumps(v)}" for k, v in entry.items() if k not in ("at", "event"))
            lines += [f"**{entry['event']}** at {entry['at']}" + (f": {details}" if details else ""), ""]
            continue
        arrow = "-> in (client to server)" if entry["dir"] == "in" else "<- out (server to client)"
        lines += _block(f"{arrow}, {entry['at']}" + ("" if entry.get("utf8", True) else ", not UTF-8"),
                        entry["text"])
    return "\n".join(lines) + "\n"


def _shown_line(entry: dict) -> list:
    arrow = "-> client to server" if entry["dir"] == "client->server" else "<- server to client"
    return _block(f"{arrow}, {entry['at']}" + ("" if entry.get("utf8", True) else ", not UTF-8"), entry["text"])


def _block(head: str, text: str) -> list:
    if len(text) > 2000 and text.strip("[") == "":
        return ["", head + f" ({len(text):,} characters, all of them `[`; the full line is in the .jsonl):", "",
                "```text", text[:60] + "...", "```"]
    message = _parse(text.encode("utf-8"))
    if message is None:
        return ["", head + " (not JSON):", "", "```text", text, "```"]
    result = message.get("result") if isinstance(message, dict) else None
    parsed = None
    if isinstance(result, dict) and isinstance(result.get("content"), list) and result["content"]:
        inner = result["content"][0].get("text") if isinstance(result["content"][0], dict) else None
        parsed = _parse(inner.encode("utf-8")) if isinstance(inner, str) else None
        if isinstance(parsed, dict):
            message = json.loads(json.dumps(message))
            message["result"]["content"][0]["text"] = f"({len(inner):,} characters of JSON, shown parsed below)"
    out = ["", head + ":", "", "```json", json.dumps(message, indent=1, ensure_ascii=False), "```"]
    if isinstance(parsed, dict):
        out += ["", "The text content, parsed:", "", "```json", json.dumps(parsed, indent=1, ensure_ascii=False),
                "```"]
    return out


def _line(session, number, direction, raw: bytes, at: str) -> dict:
    try:
        text, utf8 = raw.decode("utf-8"), True
    except UnicodeDecodeError:
        text, utf8 = raw.decode("utf-8", "backslashreplace"), False
    entry = {"type": "line", "session": session, "step": number, "dir": direction, "at": at,
             "text": text[:-1] if text.endswith("\n") else text}
    if not utf8:
        entry["utf8"] = False
    return entry


def _parse(raw: bytes):
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError, RecursionError):
        return None


def _yes(value) -> str:
    return "yes" if value else "**no**"


def scrub(text: str, repo: Path) -> str:
    """The repo folder written as <repo> and the home folder as ~, so no record names this Mac's account."""
    for path in sorted({str(Path(repo)), str(Path(repo).resolve())}, key=len, reverse=True):
        text = text.replace(path, "<repo>")
    home = str(Path.home())
    return text.replace(home, "~") if len(home) > 1 else text


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python3 tools/mcp_client.py", description=__doc__.split("\n")[0])
    parser.add_argument("target", choices=("own", "other"), help="our server, or the lesson 8 reference server")
    args = parser.parse_args(argv)
    try:
        result = run(args.target)
    except (OSError, ValueError) as exc:
        print(f"stopped: {exc}", file=sys.stderr)
        return 2
    s = result["summary"]
    print(f"{s['matched']} of {s['steps']} answers were the expected ones"
          + ("" if s["server_record_matches"] is None else
             f"; the server's own record {'matches' if s['server_record_matches'] else 'DIFFERS FROM'} the client's"))
    for o in result["outcomes"]:
        if not o["match"]:
            print(f"  MISMATCH {o['session']} {o['step']}. {o['label']}: expected {o['expected']}, got {o['actual']}")
    for e in result["evidence"]:
        print(f"  evidence: {e['board']} {e['posting_id']} {e['fate']}: record equal to filter run "
              f"{e['filter_run']}: {e['record_equal']}")
    for path in result["files"]:
        print(f"wrote {path.relative_to(REPO) if REPO in path.parents else path}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
