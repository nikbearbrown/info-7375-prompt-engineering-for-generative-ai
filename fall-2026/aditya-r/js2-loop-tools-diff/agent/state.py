"""Seen-id state (CONTRACT.md §1, revision R5).

Each id is "baseline" (recorded by the first run, never judged), "completed" (both verdicts
valid), or "pending" (new, but its judgment has not yet validated; retried next run).
"""
import json
import os
from pathlib import Path

STATUSES = {"baseline", "completed", "pending"}


class StateError(ValueError):
    pass


def load_state(path):
    """None if the file is absent (first run). Malformed state is an error, never a reset."""
    path = Path(path)
    if not path.exists():
        return None
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise StateError(f"state file {path} is not valid JSON ({e.msg}); refusing to start over") from None
    if not (isinstance(state, dict) and isinstance(state.get("ids"), dict) and isinstance(state.get("runs"), list)
            and isinstance(state.get("board"), str)):
        raise StateError(f"state file {path} is malformed; refusing to start over")
    for k, v in state["ids"].items():
        if not k.isdigit() or v not in STATUSES:
            raise StateError(f"state file {path} has an invalid entry {k!r}: {v!r}")
    return state


def save_state(path, state):
    """Atomic replace, so an interrupted write cannot corrupt the previous state."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, indent=1, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def new_and_retry_ids(state, ids):
    """ids never seen, and previously pending ids still on the board."""
    known = state["ids"]
    new = [i for i in ids if str(i) not in known]
    retry = [i for i in ids if known.get(str(i)) == "pending"]
    return new, retry
