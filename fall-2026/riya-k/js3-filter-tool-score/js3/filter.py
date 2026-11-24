"""FILTER.md as code. One function, `apply(posting, flt)`, returns a decision record anyone can recompute by hand.

Order (FILTER.md §1 and §3): abstain A1/A2 -> gates G1-G5 -> score -> threshold -> abstain A3 on would-be keeps.
`flt` is a filter file (filters/filter-v1.json). Nothing here reads the network or writes anywhere.
"""

import json
from pathlib import Path

from .text import find_word, plain_text, names_us_place, names_non_us_place, is_us_location

HERE = Path(__file__).resolve().parent.parent


def load_filter(path=None):
    return json.loads(Path(path or HERE / "filters" / "filter-v1.json").read_text())


def _hits(words, text):
    return [w for w in words if find_word(w, text)]


def score_parts(posting, flt):
    title = posting.get("title", "")
    body = title + " " + plain_text(posting.get("content", ""))
    parts = {}
    for name, spec in flt["score"].items():
        where = title if spec["where"] == "title" else body
        hits = _hits(spec["words"], where)
        counted = hits[: spec["max_hits"]]
        parts[name] = {"hits": hits, "counted": counted, "points": len(counted) * spec["points"]}
    return parts


def location_state(location):
    """'us', 'non_us', or 'bare_remote' (Remote with no country: FILTER.md A2), or 'unknown'."""
    if names_us_place(location):
        return "us"
    if names_non_us_place(location):
        return "non_us"
    if find_word("Remote", location) or find_word("Remote-Friendly", location):
        return "bare_remote"
    return "unknown"


def gate_failures(posting, flt):
    g = flt["gates"]
    title = posting.get("title", "")
    location = (posting.get("location") or {}).get("name", "")
    fails = []
    if not is_us_location(location):
        fails.append(f"G1 location '{location}' is not US/Remote-US")
    if _hits(g["seniority_words"], title):
        fails.append(f"G2 seniority word(s) {_hits(g['seniority_words'], title)}")
    if _hits(g["intern_words"], title):
        fails.append(f"G3 intern word(s) {_hits(g['intern_words'], title)}")
    nft = _hits(g["not_full_time_words"], title)
    emp = posting.get("employment")
    if nft:
        fails.append(f"G4 not-full-time title word(s) {nft}")
    if emp is not None and emp != "FullTime":
        fails.append(f"G4 employmentType '{emp}'")
    if g.get("require_role_word_in_title") and not _hits(flt["score"]["role"]["words"], title):
        fails.append("G5 no ROLE word in title")
    return fails


def apply(posting, flt, claims_fn=None):
    """Decision record. `claims_fn(posting, flt)` -> list of claims (js3.evidence.claims); needed only for A3."""
    location = (posting.get("location") or {}).get("name", "")
    text = plain_text(posting.get("content", ""))
    parts = score_parts(posting, flt)
    score = sum(p["points"] for p in parts.values())
    rec = {"id": posting["id"], "board": posting.get("board", ""), "title": posting.get("title", ""),
           "location": location, "url": posting.get("absolute_url", ""), "filter": flt["version"],
           "score": score, "parts": {k: v["counted"] for k, v in parts.items()}, "gates_failed": [],
           "abstain": None, "decision": None}

    if len(text) < flt["abstain"]["min_text_chars"]:
        rec.update(abstain=f"A1 text is {len(text)} chars (< {flt['abstain']['min_text_chars']})", decision="cannot_tell")
        return rec
    if location_state(location) == "bare_remote":
        rec.update(abstain=f"A2 location '{location}' is Remote with no country", decision="cannot_tell")
        return rec

    rec["gates_failed"] = gate_failures(posting, flt)
    if rec["gates_failed"]:
        rec["decision"] = "rejected"
        return rec
    if score < flt["threshold"]:
        rec["decision"] = "rejected"
        return rec
    if score == flt["threshold"] and claims_fn is not None:
        weak = [c["claim"] for c in claims_fn(posting, flt) if c["label"] == "insufficient"]
        if weak:
            rec.update(abstain=f"A3 score at threshold {score} with insufficient claim(s): {weak}", decision="cannot_tell")
            return rec
    rec["decision"] = "kept"
    return rec
