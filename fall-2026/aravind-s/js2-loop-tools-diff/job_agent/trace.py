"""The agent trace (GATE.md, The trace): one JSON line per observation, then the same as a table.

Every line has a step number, a UTC time and a kind. Paths in the trace are relative to the repo,
so a trace never names this machine's home folder.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

KINDS = ("run_start", "board_list", "approval", "permission", "request", "answer", "no_answer", "decision",
         "parse", "diff", "budget_stop", "judge_rule", "claude_call", "report", "state_write", "exit")


class Trace:
    def __init__(self, path: Path, now=None):
        self.path = Path(path)
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.entries = []

    def add(self, kind: str, **fields) -> dict:
        if kind not in KINDS:
            raise ValueError(f"unknown trace kind {kind!r}")
        entry = {"step": len(self.entries) + 1, "at": _iso(self.now()), "kind": kind, **fields}
        self.entries.append(entry)
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def markdown(self, title: str) -> str:
        out = [f"# {title}", "", "| Step | Time (UTC) | Kind | What happened |", "|---:|---|---|---|"]
        for entry in self.entries:
            what = "; ".join(f"{k}: {_short(v)}" for k, v in entry.items() if k not in ("step", "at", "kind"))
            out.append(f"| {entry['step']} | {entry['at'][11:19]} | {entry['kind']} | {_cell(what)} |")
        return "\n".join(out) + "\n"


def _iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _short(value) -> str:
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = str(value)
    return text if len(text) <= 160 else text[:157] + "..."


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")
