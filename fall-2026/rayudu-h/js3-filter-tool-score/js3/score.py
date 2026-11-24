"""Rules R1-R14 of FILTER.md applied to one normalized posting.

The weights and threshold are a port of the Reallocation Engine greenhouse-watch scheme
(`scheme.default.json`, default-0.1); the words and the extra rules are Hemanth's (FILTER.md
section 7). Matching is JS1's whole-word pattern (jsagent/rule.py). Every result says which
words matched, what each contributed, which rule decided, and the filter version + hash.
"""
from __future__ import annotations

from jsagent.rule import find_words

KEPT, REJECTED, CANNOT_TELL = "kept", "rejected", "cannot tell"


def find(terms, text: str) -> list:
    """Terms that occur in text as whole words or phrases, ignoring case, in the order given."""
    return find_words(text or "", terms)


def without(phrases, text: str) -> str:
    """Text with each phrase (whole words, any case) blanked out, so words inside it do not match."""
    for ph in phrases or []:
        text = _phrase_re(ph).sub(" ", text)
    return text


def _phrase_re(ph: str):
    import re
    return re.compile(r"(?<![A-Za-z0-9])" + r"\s+".join(map(re.escape, ph.split())) + r"(?![A-Za-z0-9])", re.I)


def score(posting: dict, flt: dict) -> dict:
    w = flt["weights"]
    title = (posting.get("title") or "").strip()
    text = (posting.get("text") or "").strip()
    both = title + "\n" + text

    role = find(flt["role_words_title"], without(flt.get("role_ignore_phrases"), title))
    excluded = find(flt["exclude_title_words"], title) + find(flt["exclude_text_phrases"], text)
    skills_all = find(flt["skills"], both)
    skills = skills_all[: flt["max_skill_hits"]]
    unshipped = find(flt["skills_unshipped"], both)
    degree = find(flt["degree_terms"], text)
    seniority = find(flt["seniority_title_words"], without(flt.get("seniority_ignore_phrases"), title))
    # optional rules (absent from a filter block = off; v1.0 and v1.1 have none of them)
    topics = find(flt.get("topic_words_text", []), text)[: flt.get("topic_max", 0)]
    location = (posting.get("location") or "").strip()
    non_us = bool(flt.get("us_location_words")) and bool(location) and not find(flt["us_location_words"], location)

    parts = []                                            # (rule, points, why)
    if role:
        parts.append(("R1", w["role_word"], f"role word in title: {', '.join(role)}"))
    for s in skills:
        parts.append(("R4", w["skill"], f"skill: {s}"))
    if skills:
        parts.append(("R5", w["skill_any"], "at least one skill"))
    for s in unshipped:
        parts.append(("R6", w["skill_unshipped"], f"unshipped skill: {s}"))
    if degree:
        parts.append(("R7", w["degree"], f"degree term in text: {degree[0]}"))
    if seniority:
        parts.append(("R9", w["seniority"], f"seniority word in title: {', '.join(seniority)}"))
    for t in topics:
        parts.append(("R15", w.get("topic", 0), f"topic word in text: {t}"))
    if non_us:
        parts.append(("R16", w.get("non_us_location", 0), f"no US location: {location}"))
    total = round(sum(p for _, p, _ in parts), 4)
    skill_ok = bool(skills) or (flt.get("role_word_waives_skill") and bool(role)) \
        or (flt.get("topic_waives_skill") and bool(topics))
    threshold = flt["threshold"]

    threshold_decided = False
    if not title or len(text) < flt["min_text_chars"]:
        decision, rule, reason = CANNOT_TELL, "R13", ("empty title" if not title
                                                     else f"text shorter than {flt['min_text_chars']} characters")
    elif excluded:
        decision, rule, reason = REJECTED, "R2" if find(flt["exclude_title_words"], title) else "R3", \
            f"excluded before scoring: {', '.join(excluded)}"
    elif flt["require_skill"] and not skill_ok:
        decision, rule, reason = REJECTED, "R8", "no skill of Priya's in the posting"
    elif total >= threshold:
        decision, rule, reason, threshold_decided = KEPT, "R10", f"score {total} >= threshold {threshold}", True
    else:
        decision, rule, reason, threshold_decided = REJECTED, "R10", f"score {total} < threshold {threshold}", True

    return {
        "key": posting.get("key"), "board": posting.get("board"), "title": title,
        "location": (posting.get("location") or "").strip(), "url": posting.get("url"),
        "decision": decision, "decided_by": rule, "reason": reason,
        "score": total, "margin": round(total - threshold, 4), "threshold_decided": threshold_decided,
        "role_words": role, "skills": skills, "skills_over_cap": skills_all[flt["max_skill_hits"]:],
        "skills_unshipped": unshipped, "degree": degree, "seniority": seniority, "excluded_by": excluded,
        "topics": topics, "non_us_location": non_us,
        "contributions": [{"rule": r, "points": p, "why": why} for r, p, why in parts],
        "filter_version": flt["filter_version"], "filter_sha256": flt["filter_sha256"],
    }


def rank(results: list) -> list:
    """R14 order: score, then more distinct skills, then the posting key (arbitrary but fixed)."""
    return sorted(results, key=lambda r: (-r["score"], -len(r.get("skills") or []), r["key"]))


def shortlist(results: list, latest_keys, n: int) -> list:
    """R14: the top n KEPT postings still listed in the latest snapshot."""
    latest_keys = set(latest_keys)
    return [r for r in rank(results) if r["decision"] == KEPT and r["key"] in latest_keys][:n]
