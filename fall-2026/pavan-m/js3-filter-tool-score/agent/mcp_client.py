"""A minimal MCP client, written from scratch, that drives agent/mcp_server.py. No network.

    .venv/bin/python -m agent.mcp_client --run out/runs/2026-11-23T153111 \\
        --postings greenhouse:gleanwork:4742953005 lever:palantir:<uuid> ...

Each --postings value is <system>:<board>:<posting id>. Title, location and content come
from that run's raw file for the board (found through <run>/summary.json), parsed with
agent/adapters.py, the same text agent/run_filter.py scores. All postings are looked up
before the server starts; an unknown one stops the client with exit code 2.

The client starts the server as a subprocess with its own --transcript, then sends
initialize, notifications/initialized, tools/list, one tools/call score_posting per
posting, and one tools/call apply_to_job, a tool the server does not offer and must refuse.
It saves its own transcript (same line shape as the server's, directions from the client's
side) and prints a short summary. Both transcripts share one timestamp:
    out/transcripts/client-<timestamp>.jsonl
    out/transcripts/server-<timestamp>.jsonl
Exit code 0 when every check passed, 1 when any did, 2 for bad arguments.
"""

import argparse
import json
import queue
import subprocess
import sys
import threading
from pathlib import Path

from agent import adapters
from agent.mcp_server import Transcript, timestamp
from agent.policy import PolicyError, check_read

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLIENT_INFO = {"name": "js3-minimal-client", "version": "1.0"}
PROTOCOL_VERSION = "2025-06-18"
REPLY_TIMEOUT_SECONDS = 10
REFUSED_TOOL = "apply_to_job"


def _resolve(path, root=PROJECT_ROOT):
    path = Path(path)
    return path if path.is_absolute() else Path(root) / path


def _read_json(path, root=PROJECT_ROOT):
    with open(check_read(path, root), encoding="utf-8") as f:
        return json.load(f)


def load_postings(run_dir, keys, root=PROJECT_ROOT):
    """Return [(key, {"title", "location", "content"}, notes)] or raise ValueError."""
    run_dir = _resolve(run_dir, root)
    boards = _read_json(run_dir / "summary.json", root).get("boards", {})
    parsed, found, problems = {}, [], []
    for key in keys:
        parts = key.split(":", 2)
        if len(parts) != 3 or not all(parts):
            problems.append(f"{key!r}: expected <system>:<board>:<posting id>")
            continue
        system, board_name, pid = parts
        board = f"{system}:{board_name}"
        info = boards.get(board)
        if not info or info.get("status") != "ok" or not info.get("raw_file"):
            problems.append(f"{key!r}: board {board} has no usable raw file in this run")
            continue
        if board not in parsed:
            parsed[board] = adapters.parse(system, _read_json(run_dir / info["raw_file"], root))
        match = [p for p in parsed[board] if str(p.get("id")) == pid]
        if not match:
            problems.append(f"{key!r}: no posting with id {pid} on {board}")
            continue
        posting, notes = {}, []
        for field in ("title", "location", "content"):
            value = match[0].get(field)
            if value is None:
                notes.append(f"{field} missing in the raw file; sent as an empty string")
                value = ""
            elif not isinstance(value, str):
                problems.append(f"{key!r}: {field} is {type(value).__name__}, not text")
            posting[field] = value
        found.append((key, posting, notes))
    if problems:
        raise ValueError("; ".join(problems))
    return found


class Connection:
    """The server subprocess plus a reader thread, so a silent server cannot hang us."""

    def __init__(self, server_transcript, transcript):
        self.transcript = transcript
        self.next_id = 1
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "agent.mcp_server", "--transcript", str(server_transcript)],
            cwd=PROJECT_ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None)
        self.lines = queue.Queue()
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        for raw in self.proc.stdout:
            self.lines.put(raw)
        self.lines.put(None)

    def send(self, message):
        self.proc.stdin.write((json.dumps(message, ensure_ascii=False) + "\n").encode("utf-8"))
        self.proc.stdin.flush()
        self.transcript.record("out", message)

    def notify(self, method, params=None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        self.send(msg)

    def request(self, method, params=None):
        msg_id, self.next_id = self.next_id, self.next_id + 1
        msg = {"jsonrpc": "2.0", "id": msg_id, "method": method}
        if params is not None:
            msg["params"] = params
        self.send(msg)
        while True:
            try:
                raw = self.lines.get(timeout=REPLY_TIMEOUT_SECONDS)
            except queue.Empty:
                raise RuntimeError(f"no reply to {method} (id {msg_id}) "
                                   f"within {REPLY_TIMEOUT_SECONDS}s") from None
            if raw is None:
                raise RuntimeError(f"server closed stdout before answering {method}")
            try:
                reply = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self.transcript.record("in", raw.decode("utf-8", errors="replace").rstrip("\n"))
                raise RuntimeError(f"server wrote a non-JSON line to stdout: {raw[:120]!r}")
            self.transcript.record("in", reply)
            if reply.get("id") == msg_id:
                return reply
            print(f"  note: skipped a message not answering id {msg_id}: {reply}",
                  file=sys.stderr)

    def close(self):
        try:
            self.proc.stdin.close()
            return self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            return self.proc.wait()


def run(run_dir, keys):
    try:
        postings = load_postings(run_dir, keys)
    except (ValueError, OSError, PolicyError, adapters.BadResponse) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    stamp = timestamp()
    client_path = Path("out/transcripts") / f"client-{stamp}.jsonl"
    server_path = Path("out/transcripts") / f"server-{stamp}.jsonl"
    transcript = Transcript(client_path)
    conn = Connection(server_path, transcript)
    checks = []  # (ok, description)

    def check(ok, text):
        checks.append((bool(ok), text))

    try:
        r = conn.request("initialize", {"protocolVersion": PROTOCOL_VERSION,
                                        "capabilities": {}, "clientInfo": CLIENT_INFO})
        res = r.get("result", {})
        check(res.get("protocolVersion") == PROTOCOL_VERSION,
              f"initialize: protocolVersion {res.get('protocolVersion')!r}, "
              f"server {res.get('serverInfo')}")
        check("tools" in res.get("capabilities", {}), "initialize: server declares tools")
        conn.notify("notifications/initialized")

        r = conn.request("tools/list")
        tools = r.get("result", {}).get("tools", [])
        names = [t.get("name") for t in tools]
        check(names == ["score_posting"], f"tools/list: {names}")
        if tools:
            check(tools[0].get("annotations", {}).get("readOnlyHint") is True,
                  f"tools/list: annotations {tools[0].get('annotations')}")

        print("scores:")
        for key, posting, notes in postings:
            r = conn.request("tools/call", {"name": "score_posting", "arguments": posting})
            res = r.get("result")
            if res is None or res.get("isError"):
                why = r.get("error") or res["content"][0]["text"]
                check(False, f"score_posting {key}: {why}")
                continue
            body = json.loads(res["content"][0]["text"])
            title = " ".join(posting["title"].split())
            print(f"  {key}\n    {title[:60]} | {posting['location'] or '(no location)'}\n"
                  f"    -> {body['decision']}, score {body['score']}; {body['reasons'][-1]}")
            for n in notes:
                print(f"    note: {n}")
            check(True, f"score_posting {key}: {body['decision']}")

        r = conn.request("tools/call", {"name": REFUSED_TOOL,
                                        "arguments": {"posting": postings[0][0] if postings else ""}})
        refused = "error" in r or r.get("result", {}).get("isError") is True
        how = (f"error {r['error']['code']} {r['error']['message']!r}" if "error" in r
               else f"result {r.get('result')}")
        check(refused, f"{REFUSED_TOOL}: {'refused' if refused else 'NOT refused'} ({how})")
    except RuntimeError as e:
        check(False, f"protocol failure: {e}")
    finally:
        exit_code = conn.close()
    check(exit_code == 0, f"server exited with code {exit_code}")

    print("checks:")
    for ok, text in checks:
        print(f"  [{'ok' if ok else 'FAIL'}] {text}")
    print(f"client transcript: {client_path}\nserver transcript: {server_path}")
    return 0 if all(ok for ok, _ in checks) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="Minimal MCP client for js3-job-filter")
    ap.add_argument("--run", required=True, help="saved run folder, e.g. out/runs/2026-11-23T153111")
    ap.add_argument("--postings", required=True, nargs="+", metavar="SYSTEM:BOARD:ID")
    args = ap.parse_args(argv)
    return run(args.run, args.postings)


if __name__ == "__main__":
    sys.exit(main())
