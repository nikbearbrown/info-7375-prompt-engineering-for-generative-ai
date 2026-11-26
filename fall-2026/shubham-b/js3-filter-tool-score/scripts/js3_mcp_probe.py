"""A minimal MCP client (stdlib): initialize, list tools, optionally call one tool.

Used to evaluate a tool server the way a client sees it, ours or someone else's. Every
line, both directions, is written with a UTC time to data/js3/mcp/<name>.jsonl.

Usage:
  python scripts/js3_mcp_probe.py <name>
      [--call TOOL JSON_ARGS] [--raw JSON_LINE ...] -- CMD...
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Runs the probe and returns 0 when every request got a reply."""
    argv = sys.argv[1:]
    cut = argv.index("--")
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument(
        "--call", nargs=2, action="append", default=[], metavar=("TOOL", "ARGS")
    )
    parser.add_argument(
        "--raw",
        action="append",
        default=[],
        help="extra raw line, sent after the calls",
    )
    args = parser.parse_args(argv[:cut])
    out = ROOT / "data" / "js3" / "mcp" / f"{args.name}.jsonl"
    if out.exists():
        print(f"{out.relative_to(ROOT)} exists", file=sys.stderr)
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(  # noqa: S603 - runs the command the user typed after --
        argv[cut + 1 :],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    assert proc.stdin and proc.stdout  # noqa: S101 - narrows types; PIPE sets both

    def log(direction: str, line: str) -> None:
        with out.open("a", encoding="utf-8") as fh:
            stamp = datetime.now(UTC).isoformat(timespec="milliseconds")
            fh.write(
                json.dumps(
                    {"utc": stamp, "dir": direction, "line": line}, ensure_ascii=False
                )
                + "\n"
            )

    def send(line: str, expect_reply: bool) -> None:
        log("client->server", line)
        proc.stdin.write(line.encode() + b"\n")
        proc.stdin.flush()
        while expect_reply:
            reply = proc.stdout.readline().decode().strip()
            if not reply:
                raise SystemExit("server closed the stream")
            log("server->client", reply)
            if '"id"' in reply:  # skip server notifications such as logging
                return

    msg_id = 0

    def request(method: str, params: dict[str, object] | None = None) -> None:
        nonlocal msg_id
        msg_id += 1
        body: dict[str, object] = {"jsonrpc": "2.0", "id": msg_id, "method": method}
        if params is not None:
            body["params"] = params
        send(json.dumps(body), True)

    request(
        "initialize",
        {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "js3-probe", "version": "0.1"},
        },
    )
    send(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}), False)
    request("tools/list")
    for tool, raw_args in args.call:
        request("tools/call", {"name": tool, "arguments": json.loads(raw_args)})
    for line in args.raw:
        send(line, '"id"' in line)
    proc.stdin.close()
    proc.wait(timeout=30)
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
