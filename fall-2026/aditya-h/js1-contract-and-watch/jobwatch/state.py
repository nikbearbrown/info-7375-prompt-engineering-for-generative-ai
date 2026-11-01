"""State file of seen posting ids; "new" means the id is not in seen_ids (CONTRACT: Out)."""
import json
import os
import pathlib


class StateError(Exception):
    pass


def load_state(path):
    path = pathlib.Path(path)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except ValueError as e:
        raise StateError(f"state file {path} is not valid JSON") from e
    if not isinstance(data, dict) or not isinstance(data.get("seen_ids"), list) \
            or not all(isinstance(i, int) for i in data["seen_ids"]):
        raise StateError(f"state file {path} is malformed (needs a seen_ids list of integers)")
    return data


def save_state(path, board, seen_ids, last_run):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps({"board": board, "last_run": last_run, "seen_ids": sorted(seen_ids)}, indent=1) + "\n")
    os.replace(tmp, path)


def new_postings(jobs, seen_ids):
    seen = set(seen_ids)
    out = []
    for j in jobs:
        if j.get("id") not in seen:
            seen.add(j.get("id"))
            out.append(j)
    return out
