"""Seen-id state: baseline on first run, then new = current ids - seen ids.
v3: boards seen for the first time are baselined too (CONTRACT: per-board baseline)."""
import json
from pathlib import Path


def load_state(path):
    path = Path(path)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def save_state(path, st):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(st, indent=2) + "\n")


def _board(p):
    return p.get("board", "")


def _seen_boards(prev_state, postings):
    # States written before v3 have no seen_boards: every board in them counts as seen.
    if "seen_boards" not in prev_state:
        return {_board(p) for p in postings}
    return set(prev_state["seen_boards"])


def check_unique_ids(postings):
    first = {}
    for p in postings:
        if p["id"] in first and first[p["id"]] != _board(p):
            raise ValueError(f"posting id {p['id']} appears on boards {first[p['id']]!r} and {_board(p)!r}")
        first.setdefault(p["id"], _board(p))


def diff_new(prev_state, postings):
    """Return (is_baseline, new_postings). The baseline, and any board seen for the first time, report nothing as new."""
    if prev_state is None:
        return True, []
    seen = set(prev_state["seen_ids"])
    boards = _seen_boards(prev_state, postings)
    return False, [p for p in postings if p["id"] not in seen and _board(p) in boards]


def new_boards(prev_state, postings):
    if prev_state is None:
        return []
    boards = _seen_boards(prev_state, postings)
    return sorted({_board(p) for p in postings} - boards)


def update_state(prev_state, postings, run_meta, fetched_boards=()):
    """fetched_boards: every board fetched OK this run, including empty ones (v3 fix: they count as seen too)."""
    seen = set() if prev_state is None else set(prev_state["seen_ids"])
    seen.update(p["id"] for p in postings)
    runs = [] if prev_state is None else list(prev_state["runs"])
    runs.append(run_meta)
    boards = set(prev_state.get("seen_boards", [])) if prev_state else set()
    boards.update(_board(p) for p in postings)
    boards.update(fetched_boards)
    return {"seen_ids": sorted(seen), "seen_boards": sorted(boards), "runs": runs}
