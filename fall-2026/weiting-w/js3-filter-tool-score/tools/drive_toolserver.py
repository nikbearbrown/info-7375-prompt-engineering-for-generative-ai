"""Drive the tool server as a client would, and keep the real transcript.

    python3 tools/drive_toolserver.py evidence/transcripts/session.txt

Starts `python3 -m toolserver` as a subprocess, speaks JSON-RPC to its stdin,
reads its stdout, and writes every line in both directions to the transcript
exactly as it went over the pipe. Nothing is retyped and nothing is
pretty-printed into the record.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SAMPLE = (
    "About the role\n"
    "You will build and operate backend services and the public API that our "
    "customers integrate with. Our stack is Python and TypeScript, backed by "
    "Postgres.\n"
    "- Design and ship microservices\n"
    "- Work on distributed systems problems with the platform team\n"
    "Requirements\n"
    "- 5+ years of experience building production software\n"
)


def main(argv) -> int:
    out_path = Path(argv[1]) if len(argv) > 1 else ROOT / "evidence" / "transcripts" / "session.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "js3-transcript-driver", "version": "1.0.0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "score_posting", "arguments": {"text": SAMPLE}}},
        # a posting with nothing to score: 0 is a real answer here
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
         "params": {"name": "score_posting",
                    "arguments": {"text": "We are looking for a friendly person."}}},
        # empty text: an error, not a 0 (W1)
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
         "params": {"name": "score_posting", "arguments": {"text": ""}}},
        # the things a compatible client is not entitled to
        {"jsonrpc": "2.0", "id": 6, "method": "tools/call",
         "params": {"name": "score_posting",
                    "arguments": {"text": "hello", "path": "../../etc/passwd"}}},
        {"jsonrpc": "2.0", "id": 7, "method": "tools/call",
         "params": {"name": "read_file", "arguments": {"path": "/etc/passwd"}}},
        {"jsonrpc": "2.0", "id": 8, "method": "resources/list"},
        {"jsonrpc": "2.0", "id": 9, "method": "tools/call",
         "params": {"name": "score_posting", "arguments": {}}},
    ]

    proc = subprocess.Popen(
        [sys.executable, "-m", "toolserver"],
        cwd=str(ROOT),
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1,
    )

    lines: list[str] = []
    for req in requests:
        wire = json.dumps(req, ensure_ascii=False)
        lines.append("--> " + wire)
        proc.stdin.write(wire + "\n")
        proc.stdin.flush()
        if "id" not in req:
            lines.append("    (notification: no reply expected)")
            continue
        reply = proc.stdout.readline().rstrip("\n")
        lines.append("<-- " + reply)

    proc.stdin.close()
    proc.wait(timeout=10)
    stderr = proc.stderr.read()

    header = [
        "Real transcript of a session with the JS3 tool server.",
        "",
        "Captured by tools/drive_toolserver.py on 2026-11-23 by running",
        "`python3 -m toolserver` as a subprocess and speaking JSON-RPC 2.0 to",
        "its stdin. Every line below went over the pipe exactly as it appears:",
        "`-->` is client to server, `<--` is server to client. Nothing retyped,",
        "nothing reformatted.",
        "",
        f"exit code: {proc.returncode}",
        f"stderr: {stderr.strip() or '(empty)'}",
        "",
        "=" * 72,
        "",
    ]
    out_path.write_text("\n".join(header + lines) + "\n", encoding="utf-8")
    print(f"wrote {out_path}  ({len(lines)} lines, exit {proc.returncode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
