"""A small scripted MCP client (stdio, JSON-RPC 2.0), written from scratch to record real transcripts.

It starts a server as a child process, sends a fixed script of messages one at a time, waits for each answer, and
logs every line in both directions, as sent and as received, to transcripts/client-<label>-<time>.jsonl.
Used on my own server and, unchanged, on the other server I evaluate (EVAL-SERVERS.md).
"""
import json
import select
import subprocess
from datetime import datetime, timezone

from . import config
from .policy import Policy


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def run_script(command, cwd, script, label, policy=None, timeout=30, answer_timeout=20):
    """script: (note, message) pairs; a message without "id" is a notification and gets no wait.

    Returns [(note, sent, received)] and the transcript path."""
    policy = policy or Policy()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = policy.check_write(config.ROOT / "transcripts" / f"client-{label}-{stamp}.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, bufsize=1)
    rows = []
    with open(path, "a", encoding="utf-8") as log:
        def write(direction, raw, note):
            log.write(json.dumps({"at": now(), "dir": direction, "note": note, "raw": raw}, ensure_ascii=False) + "\n")

        write("meta", json.dumps({"command": command, "cwd": str(cwd)}), "server started")
        for note, msg in script:
            line = msg if isinstance(msg, str) else json.dumps(msg)
            write("sent", line, note)
            proc.stdin.write(line + "\n")
            proc.stdin.flush()
            if isinstance(msg, dict) and "id" not in msg:
                rows.append((note, line, None))
                continue
            ready, _, _ = select.select([proc.stdout], [], [], answer_timeout)
            if not ready:  # a server that never answers must not hang the client
                write("no-answer", "", f"{note}: no answer within {answer_timeout} s")
                rows.append((note, line, f"(no answer within {answer_timeout} s)"))
                continue
            answer = proc.stdout.readline().rstrip("\n")
            write("received", answer, note)
            rows.append((note, line, answer))
        proc.stdin.close()
        # Wait first, with a time limit, and read stderr only after the server has exited (found in review: reading
        # stderr first could block forever on a server that ignores the end of its input).
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        err = proc.stderr.read()
        write("meta", json.dumps({"exit": proc.returncode, "stderr": err[-2000:]}), "server stopped")
    return rows, path


def request(mid, method, params=None):
    msg = {"jsonrpc": "2.0", "id": mid, "method": method}
    if params is not None:
        msg["params"] = params
    return msg


def opening(version="2025-06-18"):
    return [("initialize", request(1, "initialize", {"protocolVersion": version, "capabilities": {},
                                                     "clientInfo": {"name": "js3-scripted-client", "version": "1.0"}})),
            ("initialized notification", {"jsonrpc": "2.0", "method": "notifications/initialized"}),
            ("tools/list", request(2, "tools/list"))]
