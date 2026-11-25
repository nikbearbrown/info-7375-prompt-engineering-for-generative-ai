"""Seen posting ids per board. A board's first successful run is its baseline: nothing counts as new."""
import json


def empty_state():
    return {"boards": {}}


def loads(text):
    state = json.loads(text)
    if not isinstance(state, dict) or not isinstance(state.get("boards"), dict):
        raise ValueError("state file is not {'boards': {...}}")
    return state


def dumps(state):
    return json.dumps(state, indent=2)


def update(state, key, postings, day, label):
    """Return the postings whose id this board has not seen, then mark every id as seen."""
    board = state["boards"].get(key)
    if board is None:
        new = []
        board = {"seen": [], "runs": []}
    else:
        seen = set(board["seen"])
        new = [p for p in postings if p["id"] not in seen]
    board["seen"] = sorted(set(board["seen"]) | {p["id"] for p in postings})
    board["runs"].append({"date": day, "label": label, "postings": len(postings), "new": len(new),
                          "baseline": key not in state["boards"]})
    state["boards"][key] = board
    return new
