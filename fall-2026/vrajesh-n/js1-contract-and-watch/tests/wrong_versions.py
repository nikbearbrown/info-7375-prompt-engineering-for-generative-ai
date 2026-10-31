"""The two plausible-but-wrong implementations named in CONTRACT.md. Tests must catch both."""
from earlybird.watch import load_state, save_state


def watch_baseline_reports_all(postings, state_path, board, day, label):
    """Wrong version 1: treats 'no state yet' as 'everything is new'."""
    state = load_state(state_path) or {"board": board, "seen": [], "runs": []}
    seen = set(state["seen"])
    new = [p for p in postings if p["id"] not in seen]
    state["seen"] = sorted(seen | {p["id"] for p in postings})
    save_state(state_path, state)
    return new


def watch_never_saves(postings, state_path, board, day, label):
    """Wrong version 2: computes new ids correctly but forgets to write the state file."""
    state = load_state(state_path)
    if state is None:
        return []
    seen = set(state["seen"])
    return [p for p in postings if p["id"] not in seen]
