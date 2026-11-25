"""Chapter 8, "Use It": ask Claude for discrepancies between a transcript, a server's source and its
advertised tool description, not for a verdict. The instruction text is the chapter's, word for word.

  python3 evaluations/ask_for_discrepancies.py jobwatch
  python3 evaluations/ask_for_discrepancies.py course-reference

Live: one `claude -p` call per server through the student's Claude Code login (no tools, no settings,
no MCP servers, empty folder). The reply is saved unread in evaluations/claude-leads/."""

import datetime
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FORK = ROOT.parent.parent.parent
CHAPTER_8_INSTRUCTION = """Here are three things about one MCP server: a transcript of an
initialize, a tools/list, and two tools/call exchanges; the server's
source file; and the tool description it advertises.
List every place where they disagree, or where one claims more than
another supports. For each, quote the line you relied on.
Do not tell me whether to connect this server, and do not call any
behavior safe."""

SERVERS = {
    "jobwatch": {"transcript": ROOT / "transcripts" / "2026-11-24-claude-code-session.jsonl",
                 "sources": [ROOT / "jobwatch" / "mcp_server.py"]},
    "course-reference": {"transcript": ROOT / "transcripts" / "2026-11-24-course-reference-harness.jsonl",
                         "sources": [FORK / "lessons" / "08-mcp-from-scratch" / "code" / "main.py"]},
}


def protocol_lines(path):
    """The transcript's protocol messages only (the audit-hook lines are left out)."""
    keep = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["direction"] in ("host->server", "server->host", "client->server", "server->client"):
            keep.append(f'{row["at"]} {row["direction"]}: {row["line"]}')
    return "\n".join(keep)


def advertised(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["direction"] in ("server->host", "server->client"):
            message = json.loads(row["line"])
            tools = (message.get("result") or {}).get("tools")
            if tools:
                return json.dumps(tools, indent=1)
    return "(no tools/list result in the transcript)"


def main(name):
    spec = SERVERS[name]
    sources = "\n\n".join(f"--- {p.name} ---\n{p.read_text(encoding='utf-8')}" for p in spec["sources"])
    user = (f"{CHAPTER_8_INSTRUCTION}\n\n=== TRANSCRIPT ===\n{protocol_lines(spec['transcript'])}\n\n"
            f"=== SOURCE ===\n{sources}\n\n=== ADVERTISED TOOL DESCRIPTION ===\n{advertised(spec['transcript'])}\n")
    command = ["claude", "-p", "--model", "claude-opus-5-5", "--tools", "", "--setting-sources", "",
               "--strict-mcp-config", "--disable-slash-commands", "--no-session-persistence", "--output-format", "json"]
    started = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    with tempfile.TemporaryDirectory(prefix="jobwatch-leads-") as empty:
        done = subprocess.run(command, input=user, capture_output=True, text=True, cwd=empty, timeout=600,
                              env=dict(os.environ, CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"))
    out = HERE / "claude-leads"
    out.mkdir(exist_ok=True)
    home = str(Path.home())
    (out / f"{name}-prompt.txt").write_text(user.replace(home, "~"), encoding="utf-8")
    (out / f"{name}-reply.json").write_text(json.dumps({
        "started": started, "command": command, "returncode": done.returncode,
        "stdout": done.stdout.replace(home, "~"), "stderr": done.stderr.replace(home, "~")[-2000:]},
        indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{name}: claude exited {done.returncode}")
    return done.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
