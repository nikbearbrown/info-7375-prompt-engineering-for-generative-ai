"""Redacts local machine details from the transcripts in transcripts/, in place. Run once before publishing.

What it changes, and nothing else:
* absolute local paths: the home folder becomes <HOME>, the probe's throwaway sandbox becomes <SANDBOX> (so its
  allowed/ and outside/ folders stay visible), other temporary and scratch folders become <TMP>;
* in Claude Code's own first message ("system", "init"): it drops the lists and paths that describe my machine and
  my Claude Code setup (memory_paths, scratchpad_path, messaging_socket_path, plugins, skills, slash_commands,
  terminal_slash_commands, agents, capabilities, startup_timing);
* Claude Code's "rate_limit_event" lines (account status, not part of the exchange);
* in the transcripts of `claude mcp serve`, the long text descriptions in its tools/list answer (about 90,000
  characters of Claude Code's own tool instructions, some listing my setup). Each tool's name, input schema and
  every other field stay; only "description" becomes "<redacted: N characters>".

Apart from those changes (paths inside messages included), every JSON-RPC message, tool call, tool result and reply
from Claude is left as recorded. EVAL-SERVERS.md lists the same changes.

    python3 scripts/redact_transcripts.py
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
HOME = os.path.expanduser("~")
DROP_INIT = ("memory_paths", "scratchpad_path", "messaging_socket_path", "plugins", "skills", "slash_commands",
             "terminal_slash_commands", "agents", "capabilities", "startup_timing")
SANDBOX = re.compile(r"(/private)?/(tmp|var/folders)/[^\"'\s\\]*?/js3-sandbox-[^/\"'\s\\]+")
TMP = re.compile(r"(/private)?/(tmp|var/folders)/[^\"'\s\\]*")


def scrub(text):
    text = SANDBOX.sub("<SANDBOX>", text)  # keeps .../allowed/... and .../outside/... visible
    text = TMP.sub("<TMP>", text)
    return text.replace(HOME, "<HOME>")


def redact_tool_list(raw):
    try:
        answer = json.loads(raw)
        tools = answer["result"]["tools"]
    except (ValueError, KeyError, TypeError):
        return raw
    for tool in tools:
        if isinstance(tool.get("description"), str) and not tool["description"].startswith("<redacted"):
            tool["description"] = f"<redacted: {len(tool['description'])} characters>"
    return json.dumps(answer, ensure_ascii=False)


def redact_line(line, path_name=""):
    try:
        msg = json.loads(line)
    except ValueError:
        return scrub(line)
    if "claude-mcp-serve" in path_name and msg.get("dir") == "received" and msg.get("note") == "tools/list":
        msg["raw"] = redact_tool_list(msg["raw"])
    if msg.get("type") == "rate_limit_event":
        return None
    if msg.get("type") == "system" and msg.get("subtype") == "init":
        for key in DROP_INIT:
            msg.pop(key, None)
        msg["redacted"] = "local paths and Claude Code setup lists removed by scripts/redact_transcripts.py"
    return scrub(json.dumps(msg, ensure_ascii=False))


def main():
    changed = 0
    for path in sorted((HERE / "transcripts").glob("*.jsonl")):
        old = path.read_text(encoding="utf-8").splitlines()
        new = [r for r in (redact_line(line, path.name) for line in old) if r is not None]
        if new != old:
            path.write_text("\n".join(new) + "\n", encoding="utf-8")
            changed += 1
            print(f"redacted {path.name}: {len(old)} lines -> {len(new)}")
    print(f"{changed} files changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
