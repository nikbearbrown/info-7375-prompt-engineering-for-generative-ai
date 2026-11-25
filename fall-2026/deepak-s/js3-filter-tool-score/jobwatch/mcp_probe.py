"""Phase 5 probe: a stdio stub that only records what a client sends when it connects.

    python -m jobwatch mcp-probe

Reads stdin line by line and appends each line, verbatim, with the UTC time and direction "in",
to evidence/mcp/probe/<UTC start>.jsonl through tools.write_file. It never writes to stdout, so
it never answers; the client gives up on it. It exits at end of input. It opens no network and
reads no file. Used once, to choose the protocol revision the real server targets.
"""
import json
import sys
from datetime import datetime, timezone

from jobwatch.policy import Policy
from jobwatch.tools import Tools


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def main(root, stdin=sys.stdin):
    start = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = f"evidence/mcp/probe/{start}.jsonl"
    tools = Tools(Policy(root, read_dirs=(), write_dirs=("evidence/mcp/probe",)), append_names=(f"{start}.jsonl",))
    tools.write_file(path, (json.dumps({"t": _now(), "dir": "note", "line": "probe started; it never replies"}) + "\n").encode())
    for raw in stdin:
        tools.write_file(path, (json.dumps({"t": _now(), "dir": "in", "line": raw.rstrip("\n")}, ensure_ascii=False) + "\n").encode("utf-8"),
                         mode="append")
    tools.write_file(path, (json.dumps({"t": _now(), "dir": "note", "line": "end of input"}) + "\n").encode(), mode="append")
    return 0
