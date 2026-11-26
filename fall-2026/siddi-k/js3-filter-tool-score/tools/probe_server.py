"""Probe a stdio MCP server the same way, whoever wrote it (brief Step 2.3): send fixed messages, record every
line both ways, and print what came back. Used on js3.mcp_server and on the course's Chapter 8 lesson server.

Usage: python tools/probe_server.py --name NAME --tool TOOL --good-args JSON --log evidence/... -- CMD ARGS..."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from js3 import policy  # noqa: E402


def probes(tool: str, good: dict) -> list[tuple[str, str | None]]:
    """(what it checks, raw line). None = close stdin after this point."""
    j = lambda o: json.dumps(o, ensure_ascii=False)  # noqa: E731
    init = {"jsonrpc": "2.0", "id": 3, "method": "initialize",
            "params": {"protocolVersion": "2099-01-01", "capabilities": {}, "clientInfo": {"name": "probe", "version": "1"}}}
    call = lambda i, args, name=tool: {"jsonrpc": "2.0", "id": i, "method": "tools/call",  # noqa: E731
                                       "params": {"name": name, "arguments": args}}
    return [
        ("P1 tools/list before initialize", j({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})),
        ("P2 2026-07-28 discovery probe before initialize", j({"jsonrpc": "2.0", "id": 2, "method": "server/discover"})),
        ("P3 initialize asking for an unknown protocol version", j(init)),
        ("P4 ping (allowed at any time by the spec)", j({"jsonrpc": "2.0", "id": 4, "method": "ping"})),
        ("P5 notifications/initialized (no reply expected)", j({"jsonrpc": "2.0", "method": "notifications/initialized"})),
        ("P6 tools/list", j({"jsonrpc": "2.0", "id": 6, "method": "tools/list"})),
        ("P7 tools/call with valid arguments", j(call(7, good))),
        ("P8 tools/call with an extra argument", j(call(8, {**good, "path": "/etc/passwd"}))),
        ("P9 tools/call with a path-like value", j(call(9, {k: "../../.env" for k in good}))),
        ("P10 tools/call of a tool that was never listed", j(call(10, {}, name="write_file"))),
        ("P11 non-ASCII argument value", j(call(11, {k: "Zürich–café" for k in good}))),
        ("P12 a method the server does not offer", j({"jsonrpc": "2.0", "id": 12, "method": "resources/list"})),
        ("P13 malformed JSON", "{"),
        ("P14 a JSON-RPC batch", j([{"jsonrpc": "2.0", "id": 14, "method": "ping"}])),
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--good-args", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    plan = probes(a.tool, json.loads(a.good_args))
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines, report = [], []
    for what, raw in plan:
        t = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        lines.append({"t": t, "dir": "client->server", "probe": what, "raw": raw})
        proc.stdin.write(raw.encode("utf-8") + b"\n")
        proc.stdin.flush()
        expect_reply = '"method": "notifications/' not in raw
        reply = proc.stdout.readline().decode("utf-8", "replace").rstrip("\r\n") if expect_reply else None
        if reply is not None:
            lines.append({"t": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                          "dir": "server->client", "probe": what, "raw": reply})
        report.append(f"{what}\n  -> {reply if reply is not None else '(no reply, as expected for a notification)'}")
    proc.stdin.close()
    proc.wait(timeout=10)
    err = proc.stderr.read().decode("utf-8", "replace")
    policy.write_bytes(a.log, "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in lines).encode("utf-8"))
    text = f"# probe of {a.name}\n# command: {' '.join(cmd)}\n# exit code {proc.returncode}; stderr: {err.strip()[:300]!r}\n\n" \
           + "\n".join(report) + "\n"
    policy.write_bytes(a.log.replace(".jsonl", ".txt"), text.encode("utf-8"))
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
