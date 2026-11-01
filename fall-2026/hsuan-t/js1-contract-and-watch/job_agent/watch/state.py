"""The state file: which posting ids this board has already shown us (CONTRACT In/state).

Its own module because two things depend on its exact rules: the watch (read before fetching)
and the pipeline (write only after verdicts are saved).
"""

import json
from dataclasses import dataclass
from pathlib import Path

from ..common.errors import WatchError

KEYS = {"board", "seen_ids", "last_run_at"}


@dataclass(frozen=True)
class State:
    board: str
    seen_ids: frozenset[int]
    last_run_at: str


def load(path: Path, board: str) -> State | None:
    """None means 'first run'. A broken file is an error, never an empty state: silently starting
    over would report every posting as new, i.e. a second baseline (Wrong version 3)."""
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise WatchError(f"state file is not valid JSON: {path} ({e})") from e
    if not isinstance(raw, dict) or set(raw) != KEYS:
        raise WatchError(f"state file must have exactly the keys {sorted(KEYS)}: {path}")
    if raw["board"] != board:
        raise WatchError(f"state file is for board '{raw['board']}', not '{board}': {path}")
    ids = raw["seen_ids"]
    if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
        raise WatchError(f"state file seen_ids must be a list of integers: {path}")
    return State(board, frozenset(ids), raw["last_run_at"])


def save(path: Path, state: State) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {"board": state.board, "seen_ids": sorted(state.seen_ids), "last_run_at": state.last_run_at}
    # Write-then-rename so a crash mid-write can't leave a half file that the next run must reject.
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, indent=1) + "\n")
    tmp.replace(path)
