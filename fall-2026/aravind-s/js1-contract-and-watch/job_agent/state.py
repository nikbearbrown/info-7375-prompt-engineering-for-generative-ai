"""The seen-ids state (CONTRACT.md, In: State; Out: new, gone, ids never removed).

A posting is new if its id was not seen in ANY earlier run, so a posting that disappears and comes
back is not new again. Gone means: in the last run's response, missing from this one.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from .allowlist import BOARD_URL
from .errors import BrokenInput

SCHEMA = 1


@dataclass
class Diff:
    baseline: bool
    new: list = field(default_factory=list)  # jobs, in the response's order
    gone: list = field(default_factory=list)  # (id, title) pairs, in the last run's order


def load(path: Path):
    """The last run's state, or None when there is none yet (the next run is the baseline)."""
    path = Path(path)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise BrokenInput(f"the state file {path} is unreadable ({type(exc).__name__})") from None
    problem = _shape_problem(data)
    if problem:
        raise BrokenInput(f"the state file {path} is unreadable: {problem}")
    return data


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
    return ""


def diff(previous, jobs: list) -> Diff:
    if previous is None:
        return Diff(baseline=True)
    seen = set(previous["seen_ids"])
    new, listed = [], set()
    for job in jobs:
        if job["id"] not in seen and job["id"] not in listed:
            new.append(job)
            listed.add(job["id"])
    current = {job["id"] for job in jobs}
    titles = previous["last_run"]["titles"]
    gone = [(i, titles.get(i, "")) for i in previous["last_run"]["posting_ids"] if i not in current]
    return Diff(baseline=False, new=new, gone=gone)


def next_state(previous, jobs: list, run: dict) -> dict:
    """The state after this run: every id ever seen, plus this run as the last one."""
    seen = set(previous["seen_ids"]) if previous else set()
    order, listed = [], set()
    for job in jobs:
        if job["id"] not in listed:
            order.append(job["id"])
            listed.add(job["id"])
    seen.update(order)
    runs = list(previous["runs"]) if previous else []
    runs.append(dict(run))
    return {
        "schema": SCHEMA,
        "board": BOARD_URL,
        "seen_ids": sorted(seen),
        "last_run": {
            **run,
            "posting_ids": order,
            "titles": {job["id"]: job["title"] for job in jobs},
        },
        "runs": runs,
    }


def save(path: Path, data: dict) -> None:
    """Write the whole file to a temporary name, then rename it over the old one in one step."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=1, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)
