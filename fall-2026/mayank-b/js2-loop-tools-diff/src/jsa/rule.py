"""The JS1 relevance rule (CONTRACT.md), ported from js1-contract-and-watch/src/rule.js.

A record anyone can recompute from the posting and the persona's `search` block:
title matches a target term (whole word, case-insensitive), matches no exclude term,
and some location piece matches the persona's location, a relocate city, or remote United States.
"""
from __future__ import annotations

import re


def _collapse(s) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


def matches_term(text: str, term: str) -> bool:
    pattern = " ".join(re.escape(p) for p in _collapse(term).split(" "))
    return re.search(rf"(?<![^\W_]){pattern}(?![^\W_])", _collapse(text), re.IGNORECASE) is not None


def split_locations(name: str) -> list[str]:
    return [p.strip() for p in re.split(r"[|;]", str(name or "")) if p.strip()]


def judge(posting: dict, persona: dict) -> dict:
    s, home = persona["search"], persona["personal"]["location"]
    title = _collapse(posting.get("title"))
    inc = next((t for t in s["target_titles"] if matches_term(title, t)), None)
    exc = next((t for t in s["exclude_titles"] if matches_term(title, t)), None)
    loc = None
    for piece in split_locations(posting.get("location")):
        if piece.lower() == home.lower() or any(piece.lower() == c.lower() for c in s["open_to_relocate"]) \
                or (s.get("open_to_remote") and matches_term(piece, "Remote") and matches_term(piece, "United States")):
            loc = piece
            break
    return {"kind": "record", "verdict": "relevant" if inc and not exc and loc else "not_relevant",
            "include_matched": inc, "exclude_matched": exc, "location_passed": loc}
