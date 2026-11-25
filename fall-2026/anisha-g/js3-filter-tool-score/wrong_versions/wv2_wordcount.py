"""WRONG VERSION 2 (FILTER.md 4.2): rank by word count. score = number of skill words found, no cap, no rules."""
import re, sys
from wrong_versions._mutate import clone
_real = clone(__name__ + "_real")
def evaluate(posting, cfg):
    d = _real.evaluate(posting, cfg)
    text = posting.get("text") or ""
    n = sum(len(re.findall(r"(?<!\w)" + re.escape(s) + r"(?!\w)", text, re.I)) for s in cfg["skills"])
    d["score"] = n
    if d["status"] != "cannot_tell":
        d["status"] = "kept" if n >= cfg["min_skills"] else "rejected"
        d["failed"] = [] if d["status"] == "kept" else ["R3"]
    return d
def rank(decisions):
    return sorted([d for d in decisions if d["status"] == "kept"], key=lambda d: (-d["score"], d["id"]))
sys.modules[__name__] = clone(__name__, evaluate=evaluate, rank=rank)
