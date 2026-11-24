"""A small MCP client from scratch (stdio, one JSON message per line), used to evaluate a tool server I did not write.

    python3 tools/mcp_client.py --script evals/<probe>.json --out transcripts/<name>.jsonl -- <server command...>

The script is a list of steps: {"send": {...JSON-RPC...}} or {"sleep": seconds}. If the server sends the client a
request (for example roots/list), the client answers it from the script's "answers" table, and records that too.
Every line in both directions is written to --out, with UTC time and direction. Standard library only.
"""

import argparse
import json
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--redact", action="append", default=[], help="OLD=NEW text replacement in the saved transcript")
    ap.add_argument("--sub", action="append", default=[], help="KEY=VALUE substituted into the script before running")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    text = Path(a.script).read_text()
    for kv in a.sub:
        k, v = kv.split("=", 1)
        text = text.replace(k, v)
    script = json.loads(text)
    answers = script.get("answers", {})
    reps = [r.split("=", 1) for r in a.redact]
    log = []

    def rec(direction, line):
        for old, new in reps:
            line = line.replace(old, new)
        log.append({"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "dir": direction, "msg": line})

    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    inbox = queue.Queue()

    def reader():
        for line in p.stdout:
            inbox.put(line.strip())

    threading.Thread(target=reader, daemon=True).start()

    def send(obj):
        line = json.dumps(obj)
        rec("client->server", line)
        p.stdin.write(line + "\n")
        p.stdin.flush()

    def drain(wait):
        end = time.time() + wait
        while time.time() < end:
            try:
                line = inbox.get(timeout=max(0.01, end - time.time()))
            except queue.Empty:
                break
            if not line:
                continue
            rec("server->client", line)
            try:
                m = json.loads(line)
            except ValueError:
                continue
            if "method" in m and "id" in m:  # a request from the server to the client
                ans = answers.get(m["method"])
                send({"jsonrpc": "2.0", "id": m["id"], **({"result": ans} if ans is not None else
                      {"error": {"code": -32601, "message": "client does not support " + m["method"]}})})

    for step in script["steps"]:
        if "send" in step:
            send(step["send"])
            drain(step.get("wait", 1.5))
        elif "sleep" in step:
            drain(step["sleep"])
    p.stdin.close()
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        p.kill()
    err = p.stderr.read()
    for old, new in reps:
        err = err.replace(old, new)
    log.append({"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "dir": "server-stderr", "msg": err})
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in log))
    for x in log:
        print(x["dir"], x["msg"][:300])


if __name__ == "__main__":
    sys.exit(main())
