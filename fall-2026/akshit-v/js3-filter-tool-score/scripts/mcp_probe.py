"""A minimal MCP client for evaluating any stdio tool server, mine or someone else's.

    python -B scripts/mcp_probe.py <script.json> <out.jsonl> -- <server command...>

<script.json> is a list of steps. Each step is a JSON-RPC message to send (an "id" makes it a
request, which waits for its reply), or {"raw": "<text>"} to send a line that is not JSON,
or {"note": "..."} to annotate the transcript, or {"respond_to": "<method>", "result": {...}} to
answer every later server->client request with that method (for example roots/list). Every line in both directions is recorded,
with the time and direction, to <out.jsonl>. Server stderr goes to <out>.stderr.txt.
"""
import json
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sep = sys.argv.index("--")
    script_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    cmd = sys.argv[sep + 1:]
    steps = json.loads(script_path.read_text(encoding="utf-8"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    err = open(str(out_path) + ".stderr.txt", "w", encoding="utf-8")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=err,
                            text=True, encoding="utf-8", bufsize=1)
    record, replies, lock = [], {}, threading.Lock()
    responders = {}

    def send(line):
        with lock:
            record.append({"t": now(), "dir": "client->server", "msg": line})
            proc.stdin.write(line + "\n")
            proc.stdin.flush()

    def reader():
        for line in proc.stdout:
            line = line.rstrip("\n")
            with lock:
                record.append({"t": now(), "dir": "server->client", "msg": line})
                try:
                    m = json.loads(line)
                except json.JSONDecodeError:
                    continue
            if isinstance(m, dict) and "id" in m and "method" in m:      # a request from the server
                if m["method"] in responders:
                    send(json.dumps({"jsonrpc": "2.0", "id": m["id"], "result": responders[m["method"]]}))
                else:
                    send(json.dumps({"jsonrpc": "2.0", "id": m["id"],
                                     "error": {"code": -32601, "message": "Method not found"}}))
            elif isinstance(m, dict) and "id" in m:
                with lock:
                    replies[m["id"]] = m

    threading.Thread(target=reader, daemon=True).start()
    for step in steps:
        if "note" in step:
            with lock:
                record.append({"t": now(), "dir": "note", "msg": step["note"]})
            continue
        if "respond_to" in step:
            responders[step["respond_to"]] = step["result"]
            with lock:
                record.append({"t": now(), "dir": "note",
                               "msg": f"client will answer {step['respond_to']} with {json.dumps(step['result'])}"})
            continue
        line = step["raw"] if "raw" in step else json.dumps(step, ensure_ascii=False)
        send(line)
        wait_id = step.get("id") if "raw" not in step else step.get("wait_id")
        deadline = time.time() + 30
        while wait_id is not None and wait_id not in replies and time.time() < deadline and proc.poll() is None:
            time.sleep(0.02)
        if wait_id is None:
            time.sleep(0.3)   # a notification or raw line: give any reply a moment to arrive
    proc.stdin.close()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
    time.sleep(0.2)
    err.close()
    out_path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in record) + "\n", encoding="utf-8")
    for r in record:
        print(f"{r['dir']:<15} {r['msg'][:220]}")
    print(f"\n{len(record)} lines -> {out_path}; server exit {proc.returncode}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
