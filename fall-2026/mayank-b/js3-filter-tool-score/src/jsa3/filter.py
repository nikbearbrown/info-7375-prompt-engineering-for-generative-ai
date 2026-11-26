"""The filter (FILTER.md v0.1), as pure functions: (posting, filter config) -> one record.

No network, no files, no clock: the same posting and the same config always give the same record,
and every number in it can be recomputed by hand from the posting text (FILTER.md section 1).

Order (FILTER.md section 1.4):
  1. hard gates from fields that exist: an exclude word in the title -> reject; a location Priya
     won't take -> reject.
  2. missing evidence: no location, or no posting text -> "cannot tell" (never a silent reject, WF4).
  3. keep if a role word is in the title, OR at least T distinct topic words are in the text.
     The score is the number of DISTINCT topic words (WF2: never the raw count of repeats).

The small functions below are the rules; scripts/wrong_versions.py swaps them to plant WF1-WF4.
"""
from __future__ import annotations

import re

WORD_EDGE_L = r"(?<![^\W_])"   # not preceded by a letter or digit
WORD_EDGE_R = r"(?![^\W_])"    # not followed by a letter or digit


def collapse(s) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


def _pattern(form: str) -> re.Pattern:
    words = collapse(form).split(" ")
    return re.compile(WORD_EDGE_L + r"\s+".join(re.escape(w) for w in words) + WORD_EDGE_R, re.IGNORECASE)


def find_term(text: str, form: str) -> list[int]:
    """Start offsets of `form` in `text`: whole words, case-insensitive (WF1 swaps in a substring search)."""
    return [m.start() for m in _pattern(form).finditer(text or "")]


def first_term(text: str, terms: list[str]) -> str | None:
    return next((t for t in terms if find_term(collapse(text), t)), None)


def snippet(text: str, at: int, width: int = 240) -> str:
    lo = max(0, at - width // 2)
    return ("…" if lo else "") + text[lo:lo + width].strip() + ("…" if lo + width < len(text) else "")


def topic_hits(text: str, topic_words: dict, ignore: list[str]) -> list[dict]:
    """One entry per topic word found (a word counts once however often it repeats)."""
    hits = []
    for word, forms in topic_words.items():
        if word in ignore:
            continue
        found = sorted((at, f) for f in forms for at in find_term(text, f))
        if found:
            at, form = found[0]
            hits.append({"word": word, "form": form, "where": "text", "count": len(found),
                         "first_at": at, "snippet": snippet(text, at)})
    return hits


def score(hits: list[dict]) -> int:
    """Distinct topic words (WF2 swaps in the sum of every repeat)."""
    return len(hits)


def split_locations(name: str) -> list[str]:
    return [p.strip() for p in re.split(r"[|;]", str(name or "")) if p.strip()]


def location_check(location: str, loc_cfg: dict) -> tuple[str, str | None]:
    """-> ("pass", piece) | ("fail", None) | ("missing", None). JS1 rule + the Remote-USA fix (FILTER.md 1.3)."""
    pieces = split_locations(location)
    if not pieces:
        return "missing", None
    exact = [loc_cfg["home"], *loc_cfg["relocate"]] + (loc_cfg["remote_us_pieces"] if loc_cfg.get("open_to_remote") else [])
    same_place = {k.casefold(): v for k, v in loc_cfg.get("same_place", {}).items()}   # optional (absent in v0.1)
    pieces = [same_place.get(p.casefold(), p) for p in pieces]
    for piece in pieces:
        if any(piece.casefold() == e.casefold() for e in exact):
            return "pass", piece
        if loc_cfg.get("open_to_remote") and find_term(piece, "Remote") and find_term(piece, "United States"):
            return "pass", piece
    return "fail", None


def no_text_verdict() -> str:
    """A posting with no text cannot be judged on its text (WF4 swaps in "reject")."""
    return "cannot_tell"


def evaluate(posting: dict, cfg: dict) -> dict:
    title = collapse(posting.get("title"))
    text = collapse(posting.get("text")) if posting.get("text") else ""
    board = posting.get("board", "")
    rec = {"board": board, "id": str(posting.get("id")), "title": title, "location": posting.get("location", ""),
           "url": posting.get("url", ""), "filter_version": cfg["version"], "text_chars": len(text),
           "role_match": None, "exclude_match": None, "location_status": None, "location_piece": None,
           "topic_hits": [], "score": None, "verdict": None, "reason": None, "cannot_tell": []}

    rec["exclude_match"] = first_term(title, cfg["exclude_words_title"])
    rec["role_match"] = first_term(title, cfg["role_words_title"])
    rec["location_status"], rec["location_piece"] = location_check(posting.get("location", ""), cfg["location"])
    if text:
        rec["topic_hits"] = topic_hits(text, cfg["topic_words_text"], cfg.get("ignore_words_by_board", {}).get(board, []))
        rec["score"] = score(rec["topic_hits"])

    # 1. hard gates, decided from fields that exist
    if rec["exclude_match"]:
        rec["verdict"], rec["reason"] = "reject", f"exclude word in title: {rec['exclude_match']!r}"
        return rec
    if rec["location_status"] == "fail":
        rec["verdict"], rec["reason"] = "reject", "location is not one Priya accepts"
        return rec
    # 2. missing evidence -> cannot tell
    if rec["location_status"] == "missing":
        rec["cannot_tell"].append("no location")
    if not text:
        rec["cannot_tell"].append("no posting text")
    if rec["cannot_tell"]:
        rec["verdict"] = no_text_verdict() if "no posting text" in rec["cannot_tell"] else "cannot_tell"
        rec["reason"] = "cannot tell: " + ", ".join(rec["cannot_tell"])
        return rec
    # 3. keep rule
    if rec["role_match"]:
        rec["verdict"], rec["reason"] = "keep", f"role word in title: {rec['role_match']!r}"
    elif rec["score"] >= cfg["threshold_T"]:
        rec["verdict"], rec["reason"] = "keep", f"{rec['score']} distinct topic words in text (T={cfg['threshold_T']})"
    else:
        rec["verdict"], rec["reason"] = "reject", f"no role word in title and {rec['score']} topic words < T={cfg['threshold_T']}"
    return rec


def is_close_call(rec: dict, cfg: dict) -> bool:
    """A reject decided by the score alone, one topic word short of T (FILTER.md 1.5)."""
    return rec["verdict"] == "reject" and rec["score"] == cfg["threshold_T"] - 1 and not rec["exclude_match"] \
        and rec["location_status"] == "pass" and not rec["role_match"]
