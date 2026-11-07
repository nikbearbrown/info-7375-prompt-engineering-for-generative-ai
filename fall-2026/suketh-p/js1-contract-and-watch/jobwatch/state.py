"""The state file: every posting id the agent has ever seen (CONTRACT.md 'The watch').

No file means the first run. A file that exists but does not parse into exactly this
shape is damaged, and the agent stops instead of starting another baseline."""

import json
import os
import tempfile
from pathlib import Path

from jobwatch import net
from jobwatch.errors import StateError

SCHEMA = "jobwatch-state/1"
BOARD = "anthropic"
FIELDS = {"schema", "board", "endpoint", "seen_ids", "runs"}


def new_state(seen_ids, runs=()):
    return {"schema": SCHEMA, "board": BOARD, "endpoint": net.BOARD_URL,
            "seen_ids": sorted(set(seen_ids)), "runs": list(runs)}


def load_state(path):
    path = Path(path)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as error:
        raise StateError(f"state file {path} is damaged: {error}") from None
    problem = _problem(data)
    if problem:
        raise StateError(f"state file {path} is damaged: {problem}")
    return data


def _problem(data):
    if not isinstance(data, dict) or set(data) != FIELDS:
        return f"expected exactly the fields {sorted(FIELDS)}"
    if data["schema"] != SCHEMA or data["board"] != BOARD or data["endpoint"] != net.BOARD_URL:
        return "schema, board, or endpoint does not match this agent"
    ids = data["seen_ids"]
    if not isinstance(ids, list) or any(type(i) is not int or i <= 0 for i in ids):
        return "seen_ids must be a list of positive integers"
    if len(set(ids)) != len(ids):
        return "seen_ids contains duplicates"
    if not isinstance(data["runs"], list):
        return "runs must be a list"
    return None


def save_state(path, data):
    """Write to a temporary file in the same directory, then rename over the old file,
    so a reader sees either the old state or the new one, never half of one."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def new_ids(current_ids, seen_ids):
    return sorted(set(current_ids) - set(seen_ids))
