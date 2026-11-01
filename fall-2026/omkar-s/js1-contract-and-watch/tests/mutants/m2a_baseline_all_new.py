"""WRONG VERSION 2a (CONTRACT.md): with no state file, every posting is reported as new."""
from jsagent import watch


def apply():
    def diff_new(postings, state):
        seen = set(state["seen_ids"]) if state else set()
        return [p for p in postings if p["id"] not in seen]
    watch.diff_new = diff_new
