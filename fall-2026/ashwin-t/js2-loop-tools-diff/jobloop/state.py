"""Seen ids per board, keyed "provider/board" (GATE.md section 1).

Adapted from JS1 jobwatch/state.py (commit d95f05e): same strict validation and atomic
replace, now one entry per board, and every write goes through policy.replace_state.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from . import policy

SCHEMA_VERSION = 1
STATE_PATH = "state/seen.json"
TOP_KEYS = {"schema_version", "boards", "last_finished_run"}
BOARD_KEYS = {"seen_ids", "last_observed"}


class StateError(RuntimeError):
    """The state file exists but is unusable. Stop with `error`; never restart the baseline silently."""


def board_key(provider: str, board: str) -> str:
    return f"{provider}/{board}"


def validate(data) -> dict:
    if not isinstance(data, dict) or set(data) != TOP_KEYS:
        raise StateError(f"state must have exactly the keys {sorted(TOP_KEYS)}")
    if data["schema_version"] != SCHEMA_VERSION:
        raise StateError(f"unsupported state schema_version {data['schema_version']!r}")
    if not isinstance(data["boards"], dict):
        raise StateError("state 'boards' must be an object")
    for key, entry in data["boards"].items():
        if not isinstance(key, str) or key.count("/") != 1:
            raise StateError(f"state board key {key!r} must be 'provider/board'")
        if not isinstance(entry, dict) or set(entry) != BOARD_KEYS:
            raise StateError(f"state entry {key!r} must have exactly {sorted(BOARD_KEYS)}")
        ids = entry["seen_ids"]
        if not isinstance(ids, list) or not all(isinstance(i, str) and i for i in ids):
            raise StateError(f"state entry {key!r}: seen_ids must be a list of nonempty strings")
        if ids != sorted(set(ids)):
            raise StateError(f"state entry {key!r}: seen_ids must be sorted and unique")
        if not ids:
            raise StateError(f"state entry {key!r}: an empty seen_ids list is not a valid baseline")
    return data


def load(path: str = STATE_PATH, root: Path = policy.PROJECT_ROOT) -> Optional[dict]:
    """None means no state file yet: every observed board is a baseline."""
    if not policy.exists(path, root=root):
        return None
    try:
        data = json.loads(policy.read_bytes(path, root=root).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StateError(f"state file {path} is not valid JSON: {exc}") from None
    return validate(data)


def merged(previous: Optional[dict], observed: dict, run_ts: str) -> dict:
    """New state: previous boards kept, observed boards' ids added. `observed` maps key -> set of ids."""
    boards = {k: dict(v) for k, v in (previous or {}).get("boards", {}).items()}
    for key, ids in observed.items():
        old = set(boards.get(key, {}).get("seen_ids", []))
        boards[key] = {"seen_ids": sorted(old | set(ids)), "last_observed": run_ts}
    return validate({"schema_version": SCHEMA_VERSION, "boards": boards, "last_finished_run": run_ts})


def save(data: dict, *, approve_state_write: bool, run_status: str,
         root: Path = policy.PROJECT_ROOT) -> None:
    blob = (json.dumps(validate(data), indent=2, sort_keys=True) + "\n").encode("utf-8")
    policy.replace_state(blob, approve_state_write=approve_state_write, run_status=run_status, root=root)
