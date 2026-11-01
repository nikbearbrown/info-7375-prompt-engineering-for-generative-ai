"""Remember seen posting ids and report only new ones (assignment Step 2)."""
import json
from pathlib import Path


def load_state(path: Path) -> dict | None:
    path = Path(path)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def find_new(state: dict | None, board: str, postings: list[dict]) -> list[int] | None:
    """None means this is the baseline run (no state yet): nothing is reported as new."""
    if state is None:
        return None
    if state["board"] != board:
        raise ValueError(f"state file is for board {state['board']!r}, not {board!r}")
    seen = set(state["seen_ids"])
    return [p["id"] for p in postings if p["id"] not in seen]


def next_state(state: dict | None, board: str, postings: list[dict], run_record: dict) -> dict:
    # Union, not replacement: a posting that disappears and comes back is not "new".
    seen = set(state["seen_ids"]) if state else set()
    seen |= {p["id"] for p in postings}
    runs = (state["runs"] if state else []) + [run_record]
    return {"board": board, "seen_ids": sorted(seen), "runs": runs}


def save_state(path: Path, state: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
