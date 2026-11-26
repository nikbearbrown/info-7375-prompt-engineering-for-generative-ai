"""Offer score_posting to Claude (Chapter 8). Runs the Claude Code CLI, `claude -p`, with ONLY this
folder's MCP server: from an empty temporary folder, with no settings files (so no plugins, hooks or
CLAUDE.md), no built-in tools, and no saved session. Claude Code is the MCP client; it starts
`python3 -m js3 serve`, which writes its own transcript of every line in both directions.

Saved for each session:
  transcripts/server/server-<UTC>-<pid>.jsonl   the server's transcript (as sent, both directions)
  transcripts/claude/<name>.jsonl               Claude Code's stream-json output: what Claude saw and said
  transcripts/claude/<name>.meta.json           the exact command, prompt, date, model and cost

  python3 -m js3.offer <name> "<prompt>" [--model opus]
"""
import datetime
import json
import os
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent


INIT_KEEP = ("type", "subtype", "cwd", "session_id", "tools", "mcp_servers", "model", "permissionMode",
             "apiKeySource", "claude_code_version", "output_style", "plugins", "skills", "agents")


def redact(stdout):
    """What is committed: the stream unchanged except local paths (home folder -> ~), the init event cut to
    the fields that say what Claude had, rate-limit details and the credential expiry time removed."""
    out = []
    for line in stdout.splitlines():
        if not line.strip().startswith("{"):
            continue
        e = json.loads(line.replace(str(pathlib.Path.home()), "~"))
        if e.get("type") == "system" and e.get("subtype") == "init":
            dropped = sorted(k for k in e if k not in INIT_KEEP)
            e = {k: e[k] for k in INIT_KEEP if k in e}
            e["redacted_keys"] = dropped
        elif e.get("type") == "rate_limit_event":
            e = {"type": e["type"], "redacted": "rate-limit details removed"}
        elif e.get("type") == "result":
            e.pop("credential_expires_at", None)
        out.append(json.dumps(e, ensure_ascii=False))
    return "\n".join(out) + "\n"


def config():
    return {"mcpServers": {"js3": {"type": "stdio", "command": sys.executable, "args": ["-m", "js3", "serve"],
                                   "env": {"PYTHONPATH": str(HERE)}}}}


def offer(name, prompt, model="opus", allowed=("mcp__js3__score_posting",), extra=()):
    out_dir = HERE / "transcripts" / "claude"
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="js3-offer-") as empty:
        cfg_path = pathlib.Path(empty) / "mcp-config.json"
        cfg_path.write_text(json.dumps(config()))
        cmd = ["claude", "-p", "--model", model, "--mcp-config", str(cfg_path), "--strict-mcp-config",
               "--setting-sources", "", "--tools", "", "--allowedTools", ",".join(allowed),
               "--no-session-persistence", "--output-format", "stream-json", "--verbose", *extra, prompt]
        started = datetime.datetime.now().astimezone()
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=empty, timeout=600)
    (out_dir / f"{name}.jsonl").write_text(redact(proc.stdout))
    events = [json.loads(l) for l in proc.stdout.splitlines() if l.strip().startswith("{")]
    final = next((e for e in reversed(events) if e.get("type") == "result"), {})
    shown_cmd = [("<empty temp folder>/mcp-config.json" if c == str(cfg_path) else c) for c in cmd]
    meta = {"name": name, "started": started.isoformat(timespec="seconds"), "returncode": proc.returncode,
            "command": shown_cmd, "cwd": "<an empty temporary folder>",
            "mcp_config": json.loads(json.dumps(config()).replace(str(HERE), "<FOLDER>").replace(sys.executable, "python3")),
            "prompt": prompt, "result": final.get("result"), "is_error": final.get("is_error"),
            "models": sorted((final.get("modelUsage") or {}).keys()), "cost_usd": final.get("total_cost_usd"),
            "stderr_tail": proc.stderr[-800:]}
    (out_dir / f"{name}.meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    return meta, events


if __name__ == "__main__":
    args = sys.argv[1:]
    model = "opus"
    if "--model" in args:
        i = args.index("--model")
        model = args[i + 1]
        del args[i:i + 2]
    meta, _ = offer(args[0], args[1], model=model)
    print(json.dumps({k: meta[k] for k in ("name", "started", "returncode", "models", "cost_usd", "result")},
                     indent=1, ensure_ascii=False))
