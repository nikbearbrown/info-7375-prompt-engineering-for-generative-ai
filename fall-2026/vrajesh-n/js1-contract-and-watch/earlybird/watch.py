"""Remember posting ids already seen and report only the new ones. The first run is a baseline."""
import json
from pathlib import Path


def load_state(path):
    path = Path(path)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path, state):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def watch(postings, state_path, board, day, label):
    """Return the postings whose id was not in the saved state, then save every id as seen."""
    state = load_state(state_path)
    if state is None:
        new = []  # baseline: nothing counts as new on the very first run
        state = {"board": board, "seen": [], "runs": []}
    else:
        seen = set(state["seen"])
        new = [p for p in postings if p["id"] not in seen]
    state["seen"] = sorted(set(state["seen"]) | {p["id"] for p in postings})
    state["runs"].append({"date": day, "label": label, "postings": len(postings), "new": len(new)})
    save_state(state_path, state)
    return new
