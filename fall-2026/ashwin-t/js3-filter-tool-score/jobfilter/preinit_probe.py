"""Probe: does a server answer requests sent BEFORE `initialize`?

The MCP lifecycle says a client sends `initialize` first and the server should not answer other requests (ping
aside) until then. This probe skips the handshake on purpose. It sends `tools/list` as the very first message and,
optionally, one `tools/call`, then closes stdin. It records both directions like `mcp_client.py`.

    python3 -m jobfilter.preinit_probe OUT.jsonl [CALLS.json|-] [--cwd DIR] -- <server command...>

CALLS.json is a list of tools/call params, as for mcp_client; pass `-` for none (tools/list only).
"""
import json
import os
import sys
from pathlib import Path

from .mcp_client import Probe


def run(command: list, calls: list, cwd: str = None, timeout: float = 30.0) -> tuple:
    """Send tools/list (and each call) with no initialize. Returns (replies, records, exit code)."""
    probe = Probe(command, cwd=cwd, env=dict(os.environ), timeout=timeout)
    replies = []
    try:
        for method, params in [("tools/list", {})] + [("tools/call", c) for c in calls]:
            try:
                replies.append(probe.request(method, params))
            except TimeoutError as exc:
                replies.append({"timeout": str(exc)})
    finally:
        code = probe.close()
    return replies, probe.records, code


def answered_before_initialize(reply: dict) -> bool:
    """True when the server returned a normal result instead of an error or silence."""
    return isinstance(reply, dict) and "result" in reply


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    cwd = None
    if "--cwd" in argv:
        i = argv.index("--cwd")
        cwd, argv = argv[i + 1], argv[:i] + argv[i + 2:]
    if "--" not in argv or argv.index("--") != 2:
        print(__doc__, file=sys.stderr)
        return 2
    out, calls_arg, command = Path(argv[0]), argv[1], argv[3:]
    calls = [] if calls_arg == "-" else json.loads(Path(calls_arg).read_text())
    replies, records, code = run(command, calls, cwd=cwd)
    for reply in replies:
        if "result" in reply and "tools" in reply["result"]:
            summary = f"result: {len(reply['result']['tools'])} tools"
        else:
            summary = json.dumps(reply)[:300]
        print(f"answered={answered_before_initialize(reply)} {summary}")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"server exit {code}; {len(records)} lines -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
