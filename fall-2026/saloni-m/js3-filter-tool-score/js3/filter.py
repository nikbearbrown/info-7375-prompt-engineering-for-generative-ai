"""The filter in FILTER.md, applied. The rules live in the document; this file only reads them.

score(posting, flt) returns a record anyone can recompute: every rule that fired, the words
that made it fire, and where (title or text). Nothing here calls a model.
"""
import json
import os
import re

from js3.text import has_phrase, sentences, words

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DOC = os.path.join(HERE, "FILTER.md")

_BLOCK = re.compile(r"```json filter\n(.*?)\n```", re.S)
# R4: a number of years within 60 characters before "experience".
_YEARS = re.compile(r"(\d{1,2})\s*\+?\s*(?:-|–|to)?\s*(?:\d{1,2})?\s*\+?\s*years?\b[^.\n]{0,60}?\bexperience", re.I)
_PHD = re.compile(r"\bph\.?\s?d\.?(?![a-z])", re.I)
_REQUIRED = re.compile(r"\b(required|require|requires|must)\b", re.I)
_SOFT = re.compile(r"\b(preferred|or equivalent|nice to have|a plus|bonus)\b", re.I)


def load_filter(doc_path=DEFAULT_DOC, override_json=None):
    """Read the one ```json filter block from a filter document (or a JSON override file)."""
    if override_json:
        with open(override_json, encoding="utf-8") as f:
            return json.load(f)
    with open(doc_path, encoding="utf-8") as f:
        blocks = _BLOCK.findall(f.read())
    if len(blocks) != 1:
        raise ValueError(f"{doc_path}: expected exactly one ```json filter block, found {len(blocks)}")
    return json.loads(blocks[0])


def years_required(text):
    """Largest minimum number of years asked for next to 'experience', or None."""
    found = [int(m.group(1)) for m in _YEARS.finditer(text or "")]
    found = [y for y in found if 0 < y < 30]
    return (max(found), [m.group(0) for m in _YEARS.finditer(text or "")]) if found else (None, [])


def phd_required(text):
    hits = [s for s in sentences(text) if _PHD.search(s) and _REQUIRED.search(s) and not _SOFT.search(s)]
    return bool(hits), hits


def score(posting, flt):
    title = posting.get("title") or ""
    text = posting.get("text") or ""
    fired = []
    total = 0

    role = [p for p in flt["role_title"]["phrases"] if has_phrase(title, p)]
    if role:
        total += flt["role_title"]["weight"]
        fired.append({"rule": "R1", "where": "title", "matched": role, "points": flt["role_title"]["weight"]})

    veto = [p for p in flt["seniority_veto_title"] if has_phrase(title, p)]
    if veto:
        fired.append({"rule": "R2", "where": "title", "matched": veto, "points": "veto"})

    text_missing = len(text) < flt["text_min_chars"]
    if text_missing:
        fired.append({"rule": "R7", "where": "text", "matched": [], "points": 0,
                      "note": f"text is {len(text)} chars (< {flt['text_min_chars']}); R3-R5 not applied"})
    else:
        tw = words(text)
        topic = [p for p in flt["topic_text"]["phrases"] if _in_words(tw, p)]
        if topic:
            pts = min(len(topic) * flt["topic_text"]["weight_each"], flt["topic_text"]["cap"])
            total += pts
            fired.append({"rule": "R3", "where": "text", "matched": topic, "points": pts})
        yrs, spans = years_required(text)
        if yrs is not None and yrs >= flt["years_penalty"]["min_years"]:
            total += flt["years_penalty"]["weight"]
            fired.append({"rule": "R4", "where": "text", "matched": spans[:3], "points": flt["years_penalty"]["weight"],
                          "years": yrs})
        phd, phd_spans = phd_required(text)
        if phd:
            total += flt["phd_penalty"]["weight"]
            fired.append({"rule": "R5", "where": "text", "matched": phd_spans[:2], "points": flt["phd_penalty"]["weight"]})

    keep = total >= flt["threshold"] and not veto
    return {
        "uid": posting.get("uid"),
        "title": title,
        "filter_version": flt["filter_version"],
        "score": total,
        "threshold": flt["threshold"],
        "vetoed": bool(veto),
        "text_missing": text_missing,
        "decision": "keep" if keep else "reject",
        "margin": total - flt["threshold"],
        "fired": fired,
    }


def _in_words(tw, phrase):
    target = words(phrase)
    n = len(target)
    return any(tw[i:i + n] == target for i in range(len(tw) - n + 1))


def rank(results):
    """Kept postings first, then by score, then by title so the order is reproducible."""
    return sorted(results, key=lambda r: (r["decision"] != "keep", -r["score"], r["title"], r["uid"] or ""))
