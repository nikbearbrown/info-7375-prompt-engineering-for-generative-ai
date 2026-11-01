"""The seen-ID state file (CONTRACT.md, In 3 and Out 4)."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Optional

SCHEMA_VERSION = 1
KEYS = {"board", "schema_version", "seen_ids", "last_successful_run"}


class StateError(RuntimeError):
    """The state file exists but is unusable. Stop; never restart the baseline silently."""


def load_state(path: Path, board: str) -> Optional[dict]:
    """None means no state file: this run is the baseline."""
    path = Path(path)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StateError(f"state file {path} is not valid JSON: {exc}") from None
    if not isinstance(data, dict) or set(data) != KEYS:
        raise StateError(f"state file {path} must have exactly the keys {sorted(KEYS)}")
    if data["schema_version"] != SCHEMA_VERSION:
        raise StateError(f"unsupported state schema_version {data['schema_version']!r}")
    if data["board"] != board:
        raise StateError(f"state file is for board {data['board']!r}, not {board!r}")
    ids = data["seen_ids"]
    if not isinstance(ids, list) or not all(isinstance(i, str) and i.isdigit() for i in ids):
        raise StateError("seen_ids must be a list of numeric strings")
    if ids != sorted(set(ids)):
        raise StateError("seen_ids must be sorted and unique")
    return data


def save_state(path: Path, board: str, seen_ids: set, run_timestamp: str) -> dict:
    """Write atomically: a temp file in the same folder, then os.replace."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"board": board, "schema_version": SCHEMA_VERSION,
            "seen_ids": sorted(seen_ids), "last_successful_run": run_timestamp}
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".seen_ids.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
    return data
