"""New-since-last-run by posting id. CONTRACT.md Final, Out: D5§1."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class WatchResult:
    baseline: bool
    new_postings: list
    seen_after: set


def load_seen(state_path):
    """Return the set of seen ids, or None when no state exists yet."""
    path = Path(state_path)
    if not path.exists():
        return None
    return set(json.loads(path.read_text(encoding="utf-8"))["seen_ids"])


def save_seen(state_path, seen, last_fetched=None, last_run=None):
    """Write state atomically. last_fetched and last_run let the next run count removals."""
    path = Path(state_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"seen_ids": sorted(seen)}
    if last_fetched is not None:
        data["last_fetched_ids"] = sorted(last_fetched)
    if last_run is not None:
        data["last_run"] = last_run
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_state(state_path):
    """Full state dict, or None. Older files have only seen_ids."""
    path = Path(state_path)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "seen_ids": set(data["seen_ids"]),
        "last_fetched_ids": set(data["last_fetched_ids"]) if "last_fetched_ids" in data else None,
        "last_run": data.get("last_run"),
    }


def diff(board, seen):
    """Baseline when seen is None: record every id, report none as new."""
    jobs = board["jobs"]
    ids = {job["id"] for job in jobs}
    if seen is None:
        return WatchResult(baseline=True, new_postings=[], seen_after=ids)
    new = [job for job in jobs if job["id"] not in seen]
    return WatchResult(baseline=False, new_postings=new, seen_after=seen | ids)
