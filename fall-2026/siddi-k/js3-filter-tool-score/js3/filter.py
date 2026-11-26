"""The filter (FILTER.md A): four gates, a capped score, a keep line, and "cannot tell" when a missing field
could change the outcome. Every result records which words matched and where, so it can be redone by hand."""
from __future__ import annotations

import re

from .location import posting_place
from .textprep import posting_sentences, whole_word

# JS1's years rule, unchanged (CONTRACT.md "The rule" 2).
YEARS_RE = re.compile(r"(?<!\d)(\d{1,2})\s*(?:\+|(?:-|–|to)\s*\d{1,2}\+?)?\s*years?(?![a-z0-9])")
DEGREE_RE = re.compile(r"(?<![a-z0-9])(?:ms|m\.s\.|master's|masters|phd|ph\.d\.?|doctorate)(?![a-z0-9])")
EXPERIENCE_RE = whole_word("experience")


def years_required(sentences: list[str]):
    found = []
    for s in sentences:
        if not EXPERIENCE_RE.search(s):
            continue
        for m in YEARS_RE.finditer(s):
            if DEGREE_RE.search(s[max(0, m.start() - 25):m.start()]):
                continue
            found.append((int(m.group(1)), s))
    return min(found, key=lambda x: x[0]) if found else (None, None)


def first_hit(words, text: str):
    return next((w for w in words if whole_word(w).search(text)), None)


def find_in(words, sentences: list[str]) -> list[dict]:
    """Every word found, with the first sentence it was found in (for the audit and the false-friend hunt)."""
    hits = []
    for w in words:
        pat = whole_word(w)
        for i, s in enumerate(sentences):
            if pat.search(s):
                hits.append({"word": w, "sentence": i, "text": s[:240]})
                break
    return hits


def skills_in(cfg: dict, sentences: list[str]) -> list[dict]:
    out = []
    for skill, aliases in cfg["skills"].items():
        for alias in dict.fromkeys([skill, *aliases]):
            hit = find_in([alias], sentences)
            if hit:
                out.append({"skill": skill, **hit[0]})
                break
    return out


def score_parts(cfg: dict, title: str, sentences: list[str]) -> dict:
    t = title.lower()
    role = first_hit(cfg["role_words"], t)
    skills = skills_in(cfg, sentences)
    topics = find_in(cfg["topic_words"], sentences)
    r1 = cfg["role_points"] if role else 0
    r2 = min(len(skills) * cfg["skill_points_each"], cfg["skill_cap"])
    r3 = cfg["topic_points"] if topics else 0
    return {"R1": r1, "R2": r2, "R3": r3, "score": r1 + r2 + r3, "role_word": role,
            "skills": skills, "topics": topics}


def evaluate(cfg: dict, posting: dict) -> dict:
    """One posting -> {verdict: keep | reject | cannot_tell, reasons, gates, score, ...}."""
    title = posting["title"]
    t = title.lower()
    sentences = posting_sentences(posting, cfg["boilerplate"])
    has_text = bool(sentences)
    excl = first_hit(cfg["title_exclusions"], t)
    senior = re.search(cfg["seniority_regex"], t)
    years, years_sentence = years_required(sentences)
    place = posting_place(posting["location"], cfg.get("us_place_names", ()))
    gates = {
        "G1_title_exclusion": {"passed": excl is None, "hit": excl},
        "G2_seniority": {"passed": senior is None, "hit": senior.group(1) if senior else None},
        "G3_years": {"passed": (years is None or years <= cfg["years_cap"]) if has_text else None,
                     "years_required": years, "sentence": years_sentence},
        "G4_location": {"passed": {"us": True, "not_us": False, "unknown": None}[place["place"]], **place},
    }
    rec = {"board": posting["board"], "id": posting["id"], "title": title,
           "location": posting["location"].get("name") or "", "filter_version": cfg["version"],
           "has_text": has_text, "text_missing": posting.get("text_missing"), "gates": gates,
           "score": None, "parts": None}

    failed = [g for g, v in gates.items() if v["passed"] is False]
    if failed:
        rec.update(verdict="reject", reasons=failed)
        return rec
    if not has_text:
        # FILTER.md "Cannot tell": the text could change the outcome (G3, R2 and R3 all read it).
        rec.update(verdict="cannot_tell", reasons=["text_missing"])
        return rec
    parts = score_parts(cfg, title, sentences)
    rec.update(score=parts["score"], parts=parts)
    if parts["score"] < cfg["keep_threshold"]:
        rec.update(verdict="reject", reasons=["below_threshold"])
    elif gates["G4_location"]["passed"] is None:
        rec.update(verdict="cannot_tell", reasons=["location_unknown"])    # it would be kept if the place were US
    else:
        rec.update(verdict="keep", reasons=[])
    return rec


def rank_key(cfg: dict, rec: dict):
    order = {b: i for i, b in enumerate(cfg["board_order"])}
    return (-rec["score"], -len(rec["parts"]["skills"]), order.get(rec["board"], 99), rec["id"])


def shortlist(cfg: dict, results: list[dict]) -> list[dict]:
    kept = [r for r in results if r["verdict"] == "keep"]
    return sorted(kept, key=lambda r: rank_key(cfg, r))[: cfg["shortlist_size"]]
