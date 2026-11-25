"""Remember posting ids between runs and work out which ones are new."""

import json
import os


def load(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def new_ids(previous_state, current_ids):
    """Ids in current_ids that were not seen before.

    With no previous state this is the baseline run: nothing is new."""
    if previous_state is None:
        return []
    seen = set(previous_state["seen_ids"])
    return sorted(i for i in set(current_ids) if i not in seen)


def updated(previous_state, board, current_ids, run_record):
    """The state to save after this run: every id ever seen, plus a log of
    runs."""
    seen = set(previous_state["seen_ids"]) if previous_state else set()
    runs = list(previous_state["runs"]) if previous_state else []
    return {
        "board": board,
        "seen_ids": sorted(seen | set(current_ids)),
        "runs": runs + [run_record],
    }


def save(path, state):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
    os.replace(tmp, path)
