"""Evaluates a well-known server the same way: Claude Code's own MCP server (`claude mcp serve`, version 2.1.294).

Only Read and Write are called, and only on CONSTRUCTED files in a new temporary sandbox:
    <SANDBOX>/allowed/note.txt     inside the folder the server is started in
    <SANDBOX>/outside/secret.txt   a sibling folder, outside it
The risky tools it declares (Bash, WebFetch, Artifact, SendMessage, cron, remote triggers and others) are never
called: deciding not to call them is part of the trust decision (EVAL-SERVERS.md section 4).

    python3 scripts/probe_claude_mcp_serve.py
"""
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from agent import mcp_client as c  # noqa: E402
from agent.policy import Policy  # noqa: E402


def main():
    box = tempfile.mkdtemp(prefix="js3-sandbox-")
    allowed, outside = os.path.join(box, "allowed"), os.path.join(box, "outside")
    os.makedirs(allowed)
    os.makedirs(outside)
    with open(os.path.join(allowed, "note.txt"), "w") as f:
        f.write("CONSTRUCTED note inside the allowed folder\n")
    with open(os.path.join(outside, "secret.txt"), "w") as f:
        f.write("CONSTRUCTED secret outside the allowed folder\n")
    p = lambda *parts: os.path.join(box, *parts)
    script = c.opening() + [
        ("Read inside the folder", c.request(3, "tools/call", {"name": "Read", "arguments": {"file_path": p("allowed", "note.txt")}})),
        ("Read outside the folder (a sibling)", c.request(4, "tools/call", {"name": "Read", "arguments": {"file_path": p("outside", "secret.txt")}})),
        ("Write inside the folder", c.request(5, "tools/call", {"name": "Write", "arguments": {"file_path": p("allowed", "new.txt"), "content": "CONSTRUCTED write inside\n"}})),
        ("Write outside the folder (a sibling)", c.request(6, "tools/call", {"name": "Write", "arguments": {"file_path": p("outside", "new.txt"), "content": "CONSTRUCTED write outside\n"}})),
        ("an undeclared tool", c.request(7, "tools/call", {"name": "apply_to_job", "arguments": {}})),
        ("params as a list", '{"jsonrpc":"2.0","id":8,"method":"tools/call","params":[1,2]}'),
    ]
    try:
        rows, path = c.run_script(["claude", "mcp", "serve"], allowed, script, "claude-mcp-serve", timeout=30)
        files = sorted(os.path.relpath(os.path.join(d, f), box) for d, _, fs in os.walk(box) for f in fs)
    finally:
        shutil.rmtree(box, ignore_errors=True)
    when = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [f"Probe of `claude mcp serve` (Claude Code 2.1.294), {when}. Sandbox paths shown as <SANDBOX>.", ""]
    for note, sent, got in rows:
        if note == "tools/list":
            tools = json.loads(got)["result"]["tools"]
            lines.append(f"tools/list: {len(tools)} tools; with annotations: {sum(1 for t in tools if t.get('annotations'))}")
            lines.append("  " + ", ".join(t["name"] for t in tools))
            continue
        short = (got or "(notification: no answer)").replace(box, "<SANDBOX>")
        lines.append(f"{note}: {short[:300]}")
    lines += ["", "Files in the sandbox after the run: " + ", ".join(files), f"Client transcript: {os.path.relpath(path, HERE)}"]
    text = "\n".join(lines) + "\n"
    Policy().write_text(os.path.join(HERE, "evidence", "claude-mcp-serve-check.txt"), text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
