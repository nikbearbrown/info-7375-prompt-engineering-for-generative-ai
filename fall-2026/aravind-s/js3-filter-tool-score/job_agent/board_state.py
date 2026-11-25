"""One state file per board (GATE.md, Error policy and Permission policy): state/<system>-<name>.json.

A posting is new if its id was not seen in any earlier run of that board; gone means it was in the
board's last answer and is missing from this one. Seen ids are never removed, so a normal run only
adds to a board's state. Postings still waiting for Claude's judgment are kept in order under
"pending_claude" and judged first next run. Layer 1's single state file (state/seen.json, OpenAI)
is read here so the loop can move it into this format, which needs --approve.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from .errors import BrokenInput

SCHEMA = 2
JS1_FILE = "seen.json"
JS1_BOARD = ("ashby", "openai")


@dataclass
class Diff:
    baseline: bool
    new: list = field(default_factory=list)  # postings, in the answer's order
    gone: list = field(default_factory=list)  # (id, title) pairs, in the last answer's order


def path_for(state_root: Path, system: str, name: str) -> Path:
    return Path(state_root) / f"{system}-{name}.json"


def load(path: Path, system: str, name: str):
    """The board's state, or None when it has none yet (its first run is a baseline)."""
    path = Path(path)
    if not path.exists():
        return None
    data = _read(path)
    problem = _shape_problem(data)
    if not problem and (data.get("system"), data.get("name")) != (system, name):
        problem = f"it belongs to {data.get('system')}/{data.get('name')}, not {system}/{name}"
    if problem:
        raise BrokenInput(f"the state file {path.name} is unreadable: {problem}")
    return data


def load_js1(path: Path):
    """Layer 1's state of the OpenAI board, converted to this format (in memory only), or None."""
    path = Path(path)
    if not path.exists():
        return None
    data = _read(path)
    if (not isinstance(data, dict) or data.get("schema") != 1 or not isinstance(data.get("seen_ids"), list)
            or not isinstance(data.get("last_run"), dict) or not isinstance(data.get("runs"), list)):
        raise BrokenInput(f"the state file {path.name} is not layer 1's schema 1 state")
    last = data["last_run"]
    return {
        "schema": SCHEMA, "system": JS1_BOARD[0], "name": JS1_BOARD[1], "url": data.get("board"),
        "seen_ids": sorted(set(data["seen_ids"])),
        "last_run": {**last, "posting_ids": list(last.get("posting_ids") or []), "titles": dict(last.get("titles") or {})},
        "runs": list(data["runs"]),
        "pending_claude": [],
        "moved_from": f"state/{JS1_FILE} (layer 1, schema 1)",
    }


def diff(previous, postings: list) -> Diff:
    if previous is None:
        return Diff(baseline=True)
    seen = set(previous["seen_ids"])
    new, listed = [], set()
    for posting in postings:
        if posting["id"] not in seen and posting["id"] not in listed:
            new.append(posting)
            listed.add(posting["id"])
    current = {posting["id"] for posting in postings}
    titles = previous["last_run"]["titles"]
    gone = [(i, titles.get(i, "")) for i in previous["last_run"]["posting_ids"] if i not in current]
    return Diff(baseline=False, new=new, gone=gone)


def next_state(previous, system: str, name: str, url: str, postings: list, run: dict, pending: list) -> dict:
    """The board's state after a run that read it: every id ever seen, and this run as the last one."""
    seen = set(previous["seen_ids"]) if previous else set()
    order, listed = [], set()
    for posting in postings:
        if posting["id"] not in listed:
            order.append(posting["id"])
            listed.add(posting["id"])
    seen.update(order)
    runs = list(previous["runs"]) if previous else []
    runs.append(dict(run))
    state = {
        "schema": SCHEMA, "system": system, "name": name, "url": url,
        "seen_ids": sorted(seen),
        "last_run": {**run, "posting_ids": order, "titles": {p["id"]: p["title"] for p in postings}},
        "runs": runs,
        "pending_claude": list(pending),
    }
    if previous and previous.get("moved_from"):
        state["moved_from"] = previous["moved_from"]
    return state


def dumps(data: dict) -> str:
    return json.dumps(data, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def save(path: Path, data: dict) -> None:
    """Write the whole file to a temporary name beside it, then rename it over the old one in one step."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(dumps(data))
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def _read(path: Path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise BrokenInput(f"the state file {Path(path).name} is unreadable ({type(exc).__name__})") from None


def _shape_problem(data) -> str:
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        return f"not a schema {SCHEMA} state file"
    if not isinstance(data.get("seen_ids"), list) or not all(isinstance(i, str) for i in data["seen_ids"]):
        return "seen_ids is not a list of ids"
    last = data.get("last_run")
    if not isinstance(last, dict) or not isinstance(last.get("posting_ids"), list) or not isinstance(last.get("titles"), dict):
        return "last_run is missing its posting ids or titles"
    if not isinstance(data.get("runs"), list):
        return "runs is not a list"
    if not isinstance(data.get("pending_claude"), list):
        return "pending_claude is not a list"
    return ""
