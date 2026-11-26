"""Claude calls through the Claude Code CLI (`claude -p`), as in JS1's agent/claude_judge.py.

Each call is a fresh conversation run from an empty temp dir (no project CLAUDE.md), with every
built-in tool disallowed and no MCP servers unless `mcp` is given (--strict-mcp-config).
Model: CLAUDE_MODEL, default claude-sonnet-5-5. Every raw reply is kept by the caller.
"""
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile

from js3.collect import HERE

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
BUILTINS = "Bash,Edit,Write,Read,Glob,Grep,WebFetch,WebSearch,NotebookEdit,Task,TodoWrite,SlashCommand,Skill,BashOutput,KillShell"
CONTENT_CHARS = 12000


def persona_view():
    with open(os.path.join(HERE, "..", "js1-contract-and-watch", "personas", "priya-nair.resume.json"), encoding="utf-8") as f:
        r = json.load(f)
    return {k: r[k] for k in ("education", "experience", "projects", "skills") if k in r}  # no contact details


def posting_view(p, context="full"):
    if context == "title_only":
        return {"title": p["title"]}
    return {"title": p["title"], "location": p.get("location"), "department": p.get("department"),
            "text": (p.get("text") or "")[:CONTENT_CHARS]}


def fill(template_path, posting, context="full"):
    with open(os.path.join(HERE, template_path), encoding="utf-8") as f:
        t = f.read()
    return (t.replace("{{PERSONA_JSON}}", json.dumps(persona_view(), indent=1, ensure_ascii=False))
             .replace("{{POSTING_JSON}}", json.dumps(posting_view(posting, context), indent=1, ensure_ascii=False)))


def call(prompt, mcp=None, allowed_tools=None, timeout=300):
    args = ["claude", "-p", prompt, "--model", MODEL, "--output-format", "json", "--disallowedTools", BUILTINS,
            "--strict-mcp-config"]
    with tempfile.TemporaryDirectory() as cwd:
        if mcp:
            path = os.path.join(cwd, "mcp.json")
            with open(path, "w") as f:
                json.dump(mcp, f)
            args += ["--mcp-config", path]
        if allowed_tools:
            args += ["--allowedTools", ",".join(allowed_tools)]
        started = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        proc = subprocess.run(args, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
    try:
        meta = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"started_utc": started, "ok": False, "raw": proc.stdout[-2000:], "stderr": proc.stderr[-2000:]}
    return {"started_utc": started, "ok": not meta.get("is_error"), "raw": meta.get("result"),
            "model": MODEL, "models_used": sorted(meta.get("modelUsage") or {}), "session_id": meta.get("session_id"),
            "num_turns": meta.get("num_turns")}


def own_server_mcp():
    return {"mcpServers": {"js3": {"type": "stdio", "command": sys.executable, "args": ["-m", "js3.mcp_server"],
                                   "env": {"PYTHONPATH": HERE}}}}


def parse_json_reply(raw):
    """Accept a bare JSON object, or one fenced in ```json; nothing else."""
    s = (raw or "").strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else ""
        s = s.rsplit("```", 1)[0]
    return json.loads(s)
