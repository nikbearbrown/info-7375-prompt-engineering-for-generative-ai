"""Seen posting IDs across runs (GATE "Loop, budgets, and exits"; F4, F5, F17, F20).

<root>/state.json maps "provider/token" to a sorted list of seen IDs, typed per provider
(Greenhouse integers, Ashby strings). Tokens cannot contain "/" (F7), so the key is
unambiguous. A missing file means no board has a baseline yet.

Each run: load through the FileGate, write runs/<run_id>/pre-run-state.json (the exact bytes
loaded, or JSON null), stage successful boards in memory, and replace state.json once at the
end of a finished, incomplete or budget-exhausted run. On error, state.json is left alone.
IDs are only ever added; failed and unattempted boards keep their prior entries.
"""

import json
import os
from dataclasses import dataclass, field

from . import providers
from .errors import ConfigError, PermissionDenied, ReadDenied, StateError, EvidenceError
from .providers import Board

SNAPSHOT_NAME = "pre-run-state.json"


@dataclass(frozen=True)
class LoadedState:
    entries: dict | None   # key -> frozenset of IDs; None if there was no state file
    raw: bytes | None      # the exact bytes read, for the pre-run snapshot


def _validate(data) -> dict:
    if not isinstance(data, dict):
        raise StateError("state.json must hold a JSON object")
    entries = {}
    for key, ids in data.items():
        provider, sep, token = key.partition("/")
        try:
            if not sep:
                raise ConfigError("missing '/'")
            Board(provider, token)
        except ConfigError as err:
            raise StateError(f"state.json key {key!r} is not a valid provider/token: {err}") from None
        if not isinstance(ids, list) or not all(providers.valid_id(provider, i) for i in ids):
            kind = "non-bool integers" if provider == "greenhouse" else "non-empty strings"
            raise StateError(f"state.json entry {key!r} must be a list of {kind}")
        entries[key] = frozenset(ids)
    return entries


def load_state(gate) -> LoadedState:
    """The saved state, or LoadedState(None, None) if <root>/state.json does not exist."""
    if not os.path.lexists(gate.state_path):  # a stat, not an open
        return LoadedState(None, None)
    try:
        raw = gate.read(gate.state_path)
    except ReadDenied as err:
        raise StateError(f"state.json is unusable: {err}") from None
    try:
        data = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as err:
        raise StateError(f"state.json is not valid JSON: {err}") from None
    return LoadedState(_validate(data), raw)


def write_snapshot(gate, run_dir, loaded: LoadedState) -> str:
    """F17: write runs/<run_id>/pre-run-state.json before any update is staged."""
    data = loaded.raw if loaded.raw is not None else b"null\n"
    path = run_dir / SNAPSHOT_NAME
    try:
        gate.write(path, data)
    except (PermissionDenied, OSError) as err:
        raise EvidenceError(f"cannot write the pre-run state snapshot: {err}") from None
    return str(path.relative_to(gate.root))


def new_ids(seen, ids) -> list:
    """IDs not seen before, in response order. No entry yet (seen is None) is a baseline: none."""
    if seen is None:
        return []
    return [i for i in ids if i not in seen]


@dataclass
class StateStore:
    loaded: LoadedState
    staged: dict = field(default_factory=dict)

    def seen(self, board: Board):
        """The board's seen IDs, or None if it has no entry (F4)."""
        return (self.loaded.entries or {}).get(board.key)

    def stage(self, board: Board, ids) -> None:
        """Stage seen ∪ ids in memory. Only call after the raw response is saved and valid."""
        self.staged[board.key] = frozenset(self.seen(board) or ()) | frozenset(ids)

    def merged(self) -> dict:
        entries = dict(self.loaded.entries or {})
        entries.update(self.staged)
        return {key: sorted(ids) for key, ids in sorted(entries.items())}


def serialize(entries: dict) -> bytes:
    return (json.dumps(entries, indent=2, sort_keys=True) + "\n").encode("utf-8")


def commit(gate, store: StateStore) -> None:
    """F5: one atomic replace of state.json (FileGate writes a temp file, then os.replace)."""
    try:
        gate.write(gate.state_path, serialize(store.merged()))
    except (PermissionDenied, OSError) as err:
        raise EvidenceError(f"cannot write state.json: {err}") from None
