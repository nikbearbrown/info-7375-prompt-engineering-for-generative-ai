"""The watch: read a board's state, keep what the board sent as evidence, and pick out the new postings.

Without this, every run would re-judge all ~700 Stripe postings and nobody could tell what changed
between two runs (CONTRACT: In/state, Out/raw response, Wrong version 3). Since JS2 Step 5 the
fetching itself (attempts, retries, budgets) lives in loop/runner.py; this module keeps the parts
that are about one board's data, so the loop decides *when* and this module decides *what*.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ..common.policy import Policy
from ..common.posting import Posting
from . import state as state_file
from .state import State


@dataclass(frozen=True)
class WatchResult:
    board: str
    run_at: str
    source: str            # "live" or "seeded" (replayed saved response, brief R14)
    baseline: bool
    raw_path: Path
    fetched: int
    new: list[Posting]
    next_state: State      # NOT saved here: the pipeline saves it after verdicts are on disk


def load_previous(state_path: Path, board: str, id_type: type, policy: Policy) -> State | None:
    """Read before any request, so a broken file stops this board before it is fetched."""
    if state_path.exists():
        policy.check_read(state_path)
    return state_file.load(state_path, board, id_type)


def save_raw(folder: Path, board: str, body: bytes, headers: str, policy: Policy) -> Path:
    """Write the bytes exactly as received; re-serialising would make the evidence differ from what the board sent."""
    # exist_ok: an existing folder only gets here after the policy got an explicit yes (JS2 D15).
    policy.check_write(folder).mkdir(parents=True, exist_ok=True)
    path = folder / f"{board}_content.json"
    policy.check_write(path).write_bytes(body)
    policy.check_write(folder / f"{board}_content.headers.txt").write_text(headers)
    return path


def save_failed_attempt(folder: Path, board: str, attempt: int, body: bytes, policy: Policy) -> Path:
    """What a board sent with an HTTP error (the 404 page, a 503 note), kept so the trace's code can
    be checked against what really came back (S11 saved raw responses, including the failure)."""
    policy.check_write(folder).mkdir(parents=True, exist_ok=True)
    path = folder / f"{board}_attempt{attempt}_error.txt"
    policy.check_write(path).write_bytes(body)
    return path


def find_new(postings: list[Posting], previous: State | None) -> list[Posting]:
    """Baseline (no state) reports 0 by definition: with nothing seen yet, 'new' has no meaning (R13)."""
    if previous is None:
        return []
    return [p for p in postings if p.id not in previous.seen_ids]


def observe(board: str, postings: list[Posting], previous: State | None, raw_path: Path,
            source: str, now: datetime) -> WatchResult:
    """One board's postings compared with what it showed before."""
    run_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    seen_before = previous.seen_ids if previous else frozenset()
    return WatchResult(
        board=board, run_at=run_at, source=source, baseline=previous is None,
        raw_path=raw_path, fetched=len(postings), new=find_new(postings, previous),
        # Union, not replace: a posting that drops off and comes back is not new again.
        next_state=State(board, seen_before | {p.id for p in postings}, run_at),
    )
