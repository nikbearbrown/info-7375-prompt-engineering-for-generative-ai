"""Scripted MCP client: spawns mcp.server and runs a fixed script.

    python3 -m mcp.client [--config config/filter-v1.1.json]
                          [--decisions out/filter/v1.1/decisions.jsonl]

Steps (each prints one line: step, what was sent, what came back, and
whether that is the expected outcome):

    1 initialize                      -> result with serverInfo
    2 notifications/initialized       -> no reply
    3 tools/list                      -> exactly one tool, score_posting
    4 tools/call valid                -> the first kept posting in the
                                         decisions file, isError false
    5 tools/call unknown id           -> isError true
    6 tools/call extra "path"         -> error -32602
    7 tools/call delete_posting       -> error -32602
    8 unknown method                  -> error -32601

Every message in both directions is appended to
transcripts/client-<UTC>.jsonl. Exit status 0 only if every step behaved
as expected. The server's stderr is passed through to this stderr.
"""

import argparse
import json
import queue
import subprocess
import sys
import threading
from pathlib import Path

from mcp.server import (DEFAULT_PROTOCOL_VERSION, INVALID_PARAMS,
                        METHOD_NOT_FOUND, TOOL_NAME, Transcript,
                        open_transcript)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = "config/filter-v1.1.json"
DEFAULT_DECISIONS = "out/filter/v1.1/decisions.jsonl"
REPLY_TIMEOUT_SECONDS = 120
UNKNOWN_ID = "no-such-posting-0000"


def first_kept(decisions_path):
    with open(decisions_path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                row = json.loads(line)
                if row.get("decision") == "kept":
                    return row["board"], str(row["id"])
    raise ValueError(f"no kept posting in {decisions_path}")


class Connection:
    """Newline-delimited JSON-RPC over a child process's pipes."""

    def __init__(self, proc, transcript, timeout=REPLY_TIMEOUT_SECONDS):
        self.proc = proc
        self.transcript = transcript
        self.timeout = timeout
        self.lines = queue.Queue()
        self.next_id = 1
        reader = threading.Thread(target=self._read, daemon=True)
        reader.start()

    def _read(self):
        for line in self.proc.stdout:
            self.lines.put(line)
        self.lines.put(None)

    def send(self, message):
        """Send one message; False if the server has gone away."""
        self.transcript.log("out", message=message)
        try:
            self.proc.stdin.write(json.dumps(message) + "\n")
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError, ValueError):
            return False
        return True

    def request(self, method, params=None):
        rid = self.next_id
        self.next_id += 1
        message = {"jsonrpc": "2.0", "id": rid, "method": method}
        if params is not None:
            message["params"] = params
        if not self.send(message):
            return None
        return self.receive()

    def notify(self, method):
        self.send({"jsonrpc": "2.0", "method": method})

    def receive(self, timeout=None):
        try:
            line = self.lines.get(timeout=timeout or self.timeout)
        except queue.Empty:
            return None
        if line is None:
            return None
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            self.transcript.log("in", raw=line.rstrip("\n"))
            return {"_not_json": line}
        self.transcript.log("in", message=message)
        return message

    def close(self):
        try:
            self.proc.stdin.close()
        except OSError:
            pass
        try:
            code = self.proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            code = self.proc.wait()
        self.proc.stdout.close()
        return code


def spawn_server(config, root, transcripts, stderr=None):
    """Start `python3 -m mcp.server` from this code's folder. config, root
    and transcripts are absolute paths fixed here, before the server runs."""
    command = [sys.executable, "-m", "mcp.server", "--config", str(config),
               "--root", str(root)]
    if transcripts:
        command += ["--transcripts", str(transcripts)]
    return subprocess.Popen(command, cwd=str(ROOT), stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=stderr, text=True,
                            encoding="utf-8")


def error_code(reply):
    return (reply or {}).get("error", {}).get("code")


def tool_text(reply):
    try:
        return reply["result"]["content"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return None


def run_script(conn, board, pid):
    """Run the eight steps; return [(step, label, ok, detail)]."""
    steps = []

    def record(label, ok, detail):
        steps.append((len(steps) + 1, label, bool(ok), detail))

    reply = conn.request("initialize", {
        "protocolVersion": DEFAULT_PROTOCOL_VERSION,
        "capabilities": {},
        "clientInfo": {"name": "js3-scripted-client", "version": "1.0.0"}})
    result = (reply or {}).get("result", {})
    record("initialize", result.get("serverInfo", {}).get("name")
           == "priya-filter",
           f"protocolVersion={result.get('protocolVersion')} "
           f"server={result.get('serverInfo')}")

    conn.notify("notifications/initialized")
    record("notifications/initialized", True, "sent, no reply expected")

    reply = conn.request("tools/list")
    tools = (reply or {}).get("result", {}).get("tools", [])
    names = [t.get("name") for t in tools]
    record("tools/list", names == [TOOL_NAME], f"tools={names}")

    reply = conn.request("tools/call", {
        "name": TOOL_NAME, "arguments": {"board": board, "id": pid}})
    text = tool_text(reply)
    try:
        payload = json.loads(text) if text else {}
    except json.JSONDecodeError:
        payload = {}
    ok = (reply or {}).get("result", {}).get("isError") is False and \
        payload.get("id") == pid
    record(f"tools/call {board}/{pid}", ok,
           f"decision={payload.get('decision')} score={payload.get('score')}"
           f" fired={payload.get('rules_fired')}")

    reply = conn.request("tools/call", {
        "name": TOOL_NAME, "arguments": {"board": board, "id": UNKNOWN_ID}})
    record(f"tools/call unknown id {UNKNOWN_ID}",
           (reply or {}).get("result", {}).get("isError") is True,
           f"isError={(reply or {}).get('result', {}).get('isError')} "
           f"text={tool_text(reply)!r}")

    reply = conn.request("tools/call", {
        "name": TOOL_NAME,
        "arguments": {"board": board, "id": pid,
                      "path": "../../etc/passwd"}})
    record("tools/call extra argument path", error_code(reply)
           == INVALID_PARAMS, f"error={(reply or {}).get('error')}")

    reply = conn.request("tools/call", {
        "name": "delete_posting", "arguments": {"board": board, "id": pid}})
    record("tools/call delete_posting", error_code(reply) == INVALID_PARAMS,
           f"error={(reply or {}).get('error')}")

    reply = conn.request("resources/delete_everything")
    record("unknown method resources/delete_everything",
           error_code(reply) == METHOD_NOT_FOUND,
           f"error={(reply or {}).get('error')}")
    return steps


def main(argv=None, spawn=spawn_server, out=None):
    out = out or sys.stdout
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--decisions", default=DEFAULT_DECISIONS)
    parser.add_argument("--transcripts", default=None,
                        help="transcript folder (default <root>/transcripts)")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    decisions, config = (p if p.is_absolute() else root / p
                         for p in (Path(args.decisions), Path(args.config)))
    board, pid = first_kept(decisions)
    folder = (Path(args.transcripts).resolve() if args.transcripts
              else root / "transcripts")
    path, handle = open_transcript(folder, "client")
    transcript = Transcript(handle)
    conn = Connection(spawn(config, root, folder), transcript)
    try:
        steps = run_script(conn, board, pid)
    finally:
        code = conn.close()
        transcript.close()
    for number, label, ok, detail in steps:
        print(f"step {number} {label}: {'OK' if ok else 'UNEXPECTED'} "
              f"({detail})", file=out)
    print(f"server exit {code}; transcript {path}", file=out)
    return 0 if all(ok for _, _, ok, _ in steps) and code == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
