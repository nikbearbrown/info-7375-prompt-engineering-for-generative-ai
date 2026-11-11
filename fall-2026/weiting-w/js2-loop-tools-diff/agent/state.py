"""The watch's memory, extended from JS1 so the cross-check has a baseline.

Two things changed from JS1's `state.py`, both deliberate and both named in
`SOURCES.md`:

1. identity is now namespaced by provider (`"lever:abc"`, not `"abc"`), because
   two applicant-tracking systems can hand out the same id string;
2. a `boards` map records each board's **last observed posting count**, which
   is what `tools/crosscheck.py` compares against to catch a board that
   reported zero when it used to report many. JS1 had no reason to keep a
   count; the finished-wrong-answer check is exactly that reason.

What did **not** change: the state is written only after the run's
observations exist, and it is still append-only with respect to seen ids. JS1's
live run proved that monotonicity has a real cost — withdrawn postings stay
"seen" forever — and that is recorded in the sign-off rather than quietly fixed
here, because changing it would redefine what "seen" means.
"""

from __future__ import annotations

import json
from pathlib import Path

from .http import utc_now

STATE_VERSION = 2


def empty_state() -> dict:
    return {
        "state_version": STATE_VERSION,
        "seen_ids": [],
        "boards": {},
        "runs": 0,
        "first_seen_at": None,
        "last_run_at": None,
    }


def load(path: str | Path) -> tuple[dict, bool]:
    """Return `(state, is_first_run)`.

    `is_first_run` is true only when there was no state file at all, and it is
    the only condition under which the loop reports nothing as new.
    """
    path = Path(path)
    if not path.exists():
        return empty_state(), True
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("state_version") != STATE_VERSION:
        raise ValueError(
            f"{path} is state_version {state.get('state_version')}, "
            f"this agent writes {STATE_VERSION}"
        )
    state.setdefault("seen_ids", [])
    state.setdefault("boards", {})
    return state, False


def new_postings(postings, state: dict) -> list:
    seen = set(state.get("seen_ids", []))
    return [p for p in postings if p.identity not in seen]


def save(
    path: str | Path, state: dict, *, postings, board_counts: dict, policy=None
) -> dict:
    """Record ids as seen and per-board counts, then write.

    Only boards that were **observed successfully** may appear in
    `board_counts`; the loop never passes a failed board, because a failed
    board has no count and writing 0 for it would destroy the cross-check's
    baseline — which is exactly wrong version W1 leaking into the state file.
    """
    path = Path(path)
    # The state file is the agent's memory across runs, so it is confined like
    # every other file the agent writes (GATE.md §5.2, amendment A3).
    if policy is not None:
        policy.check_write(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    merged = sorted({*state.get("seen_ids", []), *(p.identity for p in postings)})
    boards = dict(state.get("boards", {}))
    for board, count in board_counts.items():
        boards[board] = {
            "last_count": count,
            "last_seen_at": now,
            "last_status": "ok",
        }
    state = {
        **state,
        "seen_ids": merged,
        "boards": boards,
        "runs": int(state.get("runs", 0)) + 1,
        "first_seen_at": state.get("first_seen_at") or now,
        "last_run_at": now,
    }
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state
