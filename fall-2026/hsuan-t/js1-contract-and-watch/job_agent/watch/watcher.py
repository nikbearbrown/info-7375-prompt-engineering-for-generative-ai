"""The watch: get one board's postings (live or replayed), keep the raw response as evidence, and pick out the new ones.

Without this, every run would re-judge all ~700 Stripe postings and nobody could tell what changed
between two runs (CONTRACT: In/state, Out/raw response, Wrong version 3). Fetching, parsing and
state rules live in net.py, boards/ and state.py; this module only puts them in order.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ..common import net
from . import state as state_file
from ..common.posting import Posting
from .boards import greenhouse
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


def save_raw(folder: Path, board: str, body: bytes, headers: str) -> Path:
    """Write the bytes exactly as received; re-serialising would make the evidence differ from what the board sent."""
    folder.mkdir(parents=True, exist_ok=False)
    path = folder / f"{board}_content.json"
    path.write_bytes(body)
    (folder / f"{board}_content.headers.txt").write_text(headers)
    return path


def find_new(postings: list[Posting], previous: State | None) -> list[Posting]:
    """Baseline (no state) reports 0 by definition: with nothing seen yet, 'new' has no meaning (R13)."""
    if previous is None:
        return []
    return [p for p in postings if p.id not in previous.seen_ids]


def watch(board: str, state_path: Path, raw_folder: Path, now: datetime,
          from_raw: Path | None = None, fetcher=net.http_get, adapter=greenhouse) -> WatchResult:
    """State is read first, so a broken file stops the run before any fetch.

    from_raw replays a saved response instead of fetching: that run is 'seeded', and no new raw
    folder is written because the evidence already exists. fetcher/adapter are parameters so
    tests can fake the network and another board type can plug in.
    """
    previous = state_file.load(state_path, board)
    run_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    if from_raw is not None:
        postings = adapter.parse(from_raw.read_bytes())
        raw_path, source = from_raw, "seeded"
    else:
        body, headers = fetcher(adapter.board_url(board))
        postings = adapter.parse(body)  # validated before anything is written
        raw_path, source = save_raw(raw_folder, board, body, headers), "live"

    seen_before = previous.seen_ids if previous else frozenset()
    return WatchResult(
        board=board, run_at=run_at, source=source, baseline=previous is None,
        raw_path=raw_path, fetched=len(postings), new=find_new(postings, previous),
        # Union, not replace: a posting that drops off and comes back is not new again.
        next_state=State(board, seen_before | {p.id for p in postings}, run_at),
    )
