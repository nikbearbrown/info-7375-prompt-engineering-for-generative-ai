"""Minimal MCP test client: starts the REAL server (python3 -m js3.mcp_server)
as a subprocess and talks to it over a real stdin/stdout pipe.

Sequence: initialize -> notifications/initialized -> tools/list ->
tools/call x2 (one filter-relevant posting, which calls Claude if a key is
set; one filter-rejected posting, which never does) -> four malformed probes
(unknown tool, invalid arguments, unparseable line, batch array) -> close
stdin (the server exits on EOF).

The client keeps ITS OWN verbatim record of every line it sent and received
(logs/mcp/client_<stamp>.jsonl), then cross-checks it against the server's
own wire log: both sides must have seen exactly the same bytes per line.

    python3 tools/mcp_client.py            # [key] for the judged call
    python3 tools/mcp_client.py --audit    # same, server run under tools/mcp_audit.py
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs" / "mcp"


def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    client_log = LOG_DIR / f"client_{stamp}.jsonl"
    audit = "--audit" in sys.argv[1:]
    cmd = [sys.executable, "tools/mcp_audit.py"] if audit else [sys.executable, "-m", "js3.mcp_server"]
    proc = subprocess.Popen(cmd, cwd=ROOT, text=True, encoding="utf-8",
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)
    record = []

    def log(direction, raw):
        record.append((direction, raw))
        with open(client_log, "a", encoding="utf-8") as f:
            f.write(json.dumps({"at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                                "dir": direction, "raw": raw}, ensure_ascii=False) + "\n")
        arrow = ">>>" if direction == "client->server" else "<<<"
        print(f"{arrow} {raw}", flush=True)

    def send(obj_or_raw, expect_reply=True):
        raw = obj_or_raw if isinstance(obj_or_raw, str) else json.dumps(obj_or_raw)
        log("client->server", raw)
        proc.stdin.write(raw + "\n")
        proc.stdin.flush()
        if expect_reply:
            line = proc.stdout.readline().rstrip("\n")
            log("server->client", line)
            return json.loads(line)

    n = iter(range(1, 100))
    r = lambda method, params=None: {"jsonrpc": "2.0", "id": next(n), "method": method,
                                     **({"params": params} if params is not None else {})}

    init = send(r("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                 "clientInfo": {"name": "js3-test-client", "version": "0.1.0"}}))
    assert init["result"]["protocolVersion"] == "2025-06-18", init
    send({"jsonrpc": "2.0", "method": "notifications/initialized"}, expect_reply=False)
    tools = send(r("tools/list"))["result"]["tools"]
    assert [t["name"] for t in tools] == ["score_posting"], tools
    send(r("tools/call", {"name": "score_posting", "arguments": {"board": "gitlab", "id": 8704363002}}))
    send(r("tools/call", {"name": "score_posting", "arguments": {"board": "gitlab", "id": 8396674002}}))
    # malformed probes
    send(r("tools/call", {"name": "delete_everything", "arguments": {}}))
    send(r("tools/call", {"name": "score_posting", "arguments": {"board": "gitlab", "id": 1, "title": "x",
                                                                 "content": "y"}}))
    send("{this is not json")
    send("[" + json.dumps(r("ping")) + "]")

    proc.stdin.close()
    proc.wait(timeout=30)
    stderr = proc.stderr.read()
    print("--- server stderr ---\n" + stderr.strip())

    # cross-check against the server's own wire log
    wire = next(l.split("wire log: ", 1)[1].strip() for l in stderr.splitlines() if "wire log: " in l)
    server_side = [(e["dir"], e["raw"]) for e in map(json.loads, Path(wire).read_text().splitlines())]
    print(f"--- cross-check: client record ({len(record)} lines) vs server wire log ({len(server_side)} lines) ---")
    print("IDENTICAL" if server_side == record else "MISMATCH")
    print(f"client log: {client_log.relative_to(ROOT)}\nserver log: {Path(wire).relative_to(ROOT)}")
    print(f"server exit code: {proc.returncode}")
    if audit:
        events = [json.loads(l[6:]) for l in stderr.splitlines() if l.startswith("AUDIT ")]
        allowed = (LOG_DIR.resolve(),)
        writes = sorted({e["path"] for e in events if e["kind"] == "write_open"})
        print(f"--- audit: {len(events)} events ---")
        for w in writes:
            inside = Path(w).resolve().is_relative_to(allowed[0])
            print(f"  write {'INSIDE logs/mcp' if inside else 'OUTSIDE logs/mcp'}: {w}")
        for e in events:
            if e["kind"] != "write_open":
                print(f"  {e['kind']}: {e.get('event')} {e.get('args')}")
    return 0 if server_side == record else 1


if __name__ == "__main__":
    sys.exit(main())
