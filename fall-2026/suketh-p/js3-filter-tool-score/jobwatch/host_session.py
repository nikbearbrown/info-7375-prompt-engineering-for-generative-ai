"""One real session with Claude Code as the host of the score_posting server (Chapter 8, "Use It").

  python3 -m jobwatch.host_session --name 2026-11-24-claude-code-session

Claude Code (`claude -p`) starts the server through jobwatch/mcp_tap.py, so the server side of
the session is recorded line by line in transcripts/NAME.jsonl. Claude Code's own stream
(its tool_use requests and the tool_result content it received) goes to transcripts/NAME-host.jsonl.
Built-in tools are off (--tools ""), only this server is loaded (--strict-mcp-config), only its
one tool is allowed, no settings are read, no session is saved, and it runs from an empty folder.
The home folder is shown as ~ in everything saved here; secrets are never involved."""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = PROJECT_ROOT / "transcripts"
HOME = str(Path.home())
MODEL = "claude-opus-5-5"


def redact(text):
    return text.replace(HOME, "~")


def config(log_path):
    return {"mcpServers": {"jobwatch": {
        "type": "stdio", "command": "python3",
        "args": ["-B", "-m", "jobwatch.mcp_tap", "--log", str(log_path), "--", "python3", "-B", "-m", "jobwatch.mcp_server"],
        "env": {"PYTHONPATH": str(PROJECT_ROOT)}}}}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m jobwatch.host_session")
    parser.add_argument("--name", required=True)
    parser.add_argument("--prompt-file", required=True)
    args = parser.parse_args(argv)
    log_path = TRANSCRIPTS / f"{args.name}.jsonl"
    host_path = TRANSCRIPTS / f"{args.name}-host.jsonl"
    for path in (log_path, host_path):
        if path.exists():
            raise SystemExit(f"refused: {path.name} already exists")
    prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="jobwatch-host-") as empty_dir:
        config_path = Path(empty_dir) / "mcp-config.json"
        config_path.write_text(json.dumps(config(log_path), indent=1), encoding="utf-8")
        command = ["claude", "-p", "--model", MODEL, "--mcp-config", str(config_path), "--strict-mcp-config",
                   "--allowedTools", "mcp__jobwatch__score_posting", "--tools", "", "--setting-sources", "",
                   "--disable-slash-commands", "--no-session-persistence", "--output-format", "stream-json", "--verbose"]
        env = dict(os.environ, CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1")
        done = subprocess.run(command, input=prompt, capture_output=True, text=True, cwd=empty_dir, env=env, timeout=600)
    host_path.write_text(redact(done.stdout), encoding="utf-8")
    if log_path.exists():
        log_path.write_text(redact(log_path.read_text(encoding="utf-8")), encoding="utf-8")
    shown = [c if c != str(config_path) else "<temporary folder>/mcp-config.json" for c in command]
    (TRANSCRIPTS / f"{args.name}-command.json").write_text(json.dumps({
        "command": shown, "cwd": "<an empty temporary folder>", "stdin": args.prompt_file,
        "env_added": {"CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"},
        "mcp_config": json.loads(redact(json.dumps(config(log_path)))),
        "returncode": done.returncode, "stderr": redact(done.stderr)[-2000:]}, indent=1) + "\n", encoding="utf-8")
    print(f"claude exited {done.returncode}; host stream {len(done.stdout.splitlines())} lines; "
          f"server log {'written' if log_path.exists() else 'MISSING'}")
    return done.returncode


if __name__ == "__main__":
    sys.exit(main())
