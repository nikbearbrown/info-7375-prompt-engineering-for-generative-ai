#!/usr/bin/env python3
"""capture.py: run one command and keep its exact terminal output, line by line, with timing.

Usage:
    python3 tools/capture.py --out evidence/terminal/<name> --cwd <dir> -- <command...>

Writes <name>.txt (the prompt line, then the output exactly as printed) and <name>.json
({"command", "cwd_shown", "started_utc", "ended_utc", "exit_code", "python", "path_substitutions",
"lines": [{"t", "text"}]}). Stdout and stderr are merged in the order they arrive. The only change
made to the text is replacing the home folder with "~", which is recorded in "path_substitutions".
Written by Claude Code for the Final Project Film, 2026-11-21.
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="output path without extension")
    ap.add_argument("--cwd", required=True, help="folder the command runs in")
    ap.add_argument("--shown-cwd", default=None, help="folder name to show in the prompt line")
    ap.add_argument("command", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.command[1:] if a.command[:1] == ["--"] else a.command
    if not cmd:
        ap.error("no command given")

    home = str(Path.home())
    cwd = str(Path(a.cwd).resolve())
    shown = a.shown_cwd or Path(cwd).name

    def scrub(s):
        return s.replace(home, "~")

    started = dt.datetime.now(dt.timezone.utc)
    t0 = time.monotonic()
    lines = []
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, bufsize=1, env={**os.environ, "PYTHONUNBUFFERED": "1"})
    for raw in proc.stdout:
        lines.append({"t": round(time.monotonic() - t0, 3), "text": scrub(raw.rstrip("\n"))})
    code = proc.wait()
    ended = dt.datetime.now(dt.timezone.utc)

    shown_cmd = " ".join(cmd)
    record = {
        "command": shown_cmd,
        "cwd_shown": shown,
        "started_utc": started.isoformat(timespec="seconds"),
        "ended_utc": ended.isoformat(timespec="seconds"),
        "exit_code": code,
        "python": sys.version.split()[0],
        "path_substitutions": [{"from": "<home folder>", "to": "~"}],
        "lines": lines,
    }
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    text = [f"{shown} % {shown_cmd}"] + [ln["text"] for ln in lines] + [f"[exit {code}]"]
    out.with_suffix(".txt").write_text("\n".join(text) + "\n")
    print(f"[capture] {out.name}: exit {code}, {len(lines)} lines, {lines[-1]['t'] if lines else 0:.2f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
