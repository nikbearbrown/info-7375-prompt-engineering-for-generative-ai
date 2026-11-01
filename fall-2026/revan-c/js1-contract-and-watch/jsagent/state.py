"""Seen-id state. Written atomically and only after the run's output is saved."""
import json
import os
import pathlib


def load_seen(path):
    """Return the set of seen ids, or None when no state exists (the next run is a baseline)."""
    path = pathlib.Path(path)
    if not path.exists():
        return None
    return set(json.loads(path.read_text())["seen_ids"])


def save_seen(path, ids, updated_at, source):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(
        {"seen_ids": sorted(ids), "updated_at": updated_at, "last_source": source}, indent=2
    ) + "\n")
    os.replace(tmp, path)
