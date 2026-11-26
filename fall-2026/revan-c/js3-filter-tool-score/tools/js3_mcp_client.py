"""Scripted client: drive a stdio MCP server through the tap and save the real transcript.

Usage:
  .venv/bin/python tools/js3_mcp_client.py --label own -- .venv/bin/python -m jsfilter.mcp_server
  .venv/bin/python tools/js3_mcp_client.py --label teaching --script teaching -- python3 -I PATH/main.py --stdio

Sends the messages of the chosen script one line at a time, waits for a response only when the message has an id,
and writes runs/js3/transcripts/<UTC time>_<label>.jsonl (via tools/mcp_tap.py). This is a constructed client,
not Claude; the Claude session is recorded separately through .mcp.json.
"""
import argparse
import datetime
import json
import pathlib
import queue
import subprocess
import sys
import threading

ROOT = pathlib.Path(__file__).resolve().parent.parent

INIT = {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "js3-scripted-client", "version": "1"}}


def _req(id_, method, params=None):
    m = {"jsonrpc": "2.0", "id": id_, "method": method}
    if params is not None:
        m["params"] = params
    return m


NOTE = {"jsonrpc": "2.0", "method": "notifications/initialized"}

SCRIPTS = {
    # FILTER.md section 7 rows 1-6 in order, then the other codes, then real calls.
    "own": [
        _req(1, "tools/list"),
        _req(2, "initialize", INIT),
        _req(3, "tools/list"),
        NOTE,
        _req(5, "tools/call", {"name": "score_posting", "arguments": {"board": "klaviyo"}}),
        _req(6, "tools/call", {"name": "score_posting", "arguments": {"board": "klaviyo", "id": "999"}}),
        "{",
        {"id": 8},
        _req(9, "resources/list"),
        _req(10, "tools/call", {"name": "delete_posting", "arguments": {"board": "klaviyo", "id": "8041054003"}}),
        _req(11, "tools/list"),
        _req(12, "tools/call", {"name": "score_posting", "arguments": {"board": "klaviyo", "id": "8041054003"}}),
        _req(13, "tools/call", {"name": "score_posting", "arguments": {"board": "duolingo", "id": "8628658002"}}),
        _req(14, "initialize", INIT),
    ],
    # The Chapter 8 teaching server: same lifecycle probes, its own tool and fixture key.
    "teaching": [
        _req(1, "tools/list"),
        _req(2, "initialize", {**INIT, "protocolVersion": "unsupported-fixture"}),
        _req(3, "tools/list"),
        NOTE,
        _req(4, "tools/list"),
        _req(5, "tools/call", {"name": "lookup", "arguments": {"key": "office"}}),
        _req(6, "tools/call", {"name": "lookup", "arguments": {"key": "missing"}}),
        _req(7, "tools/call", {"name": "lookup", "arguments": ["office"]}),
        _req(8, "tools/call", {"name": "lookup", "arguments": {"key": "office", "extra": 1}}),
        _req(9, "tools/call", {"name": "score_posting", "arguments": {"key": "office"}}),
        "{",
        {"id": 11},
        _req(12, "bad"),
        _req(13, "initialize", INIT),
        {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "lookup", "arguments": {"key": "office"}}},
    ],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--script", default="own", choices=sorted(SCRIPTS))
    ap.add_argument("command", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    cmd = args.command[1:] if args.command[:1] == ["--"] else args.command
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    log = ROOT / "runs" / "js3" / "transcripts" / f"{stamp}_{args.label}.jsonl"
    tap = [sys.executable, str(ROOT / "tools" / "mcp_tap.py"), "--log", str(log), "--"] + cmd
    proc = subprocess.Popen(tap, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1, cwd=ROOT)
    out = queue.Queue()
    threading.Thread(target=lambda: [out.put(l) for l in proc.stdout], daemon=True).start()

    for msg in SCRIPTS[args.script]:
        line = msg if isinstance(msg, str) else json.dumps(msg)
        proc.stdin.write(line + "\n")
        proc.stdin.flush()
        expects = isinstance(msg, str) or "id" in msg
        try:
            reply = out.get(timeout=10) if expects else out.get(timeout=1)
            print(f">> {line}\n<< {reply.rstrip()}")
        except queue.Empty:
            print(f">> {line}\n<< (no response)")
    proc.stdin.close()
    proc.wait(timeout=10)
    print(f"transcript: {log.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
