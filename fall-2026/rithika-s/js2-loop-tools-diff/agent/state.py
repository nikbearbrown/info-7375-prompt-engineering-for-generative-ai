"""Load and save the set of posting ids seen on earlier runs."""

import json
import os
from pathlib import Path


class StateInvalid(Exception):
    """Raised when an existing state file cannot be read as seen ids."""


def load_seen(path):
    """Return the set of seen ids, or None if no state file exists (baseline)."""
    path = Path(path)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        ids = data["seen_ids"]
        if not all(isinstance(i, int) and not isinstance(i, bool) for i in ids):
            raise TypeError
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise StateInvalid(f"{path}: not a valid state file ({exc!r})") from None
    return set(ids)


def save_seen(path, ids, timestamp):
    """Write ids atomically so a crash never leaves a half-written state."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(
        {"updated": timestamp, "seen_ids": sorted(ids)}, indent=2) + "\n",
        encoding="utf-8")
    os.replace(tmp, path)


def split_new(posting_ids, seen):
    """Return (new_ids, run_is_baseline) for the current posting ids."""
    if seen is None:
        return [], True
    return [i for i in posting_ids if i not in seen], False
