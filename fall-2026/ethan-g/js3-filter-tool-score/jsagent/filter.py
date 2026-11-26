"""The JS3 filter, exactly as FILTER.md v1.3 section 1 states it. Every result carries the evidence it was decided on.

Buckets: kept (every hard rule passes and T3 is met), rejected (a rule fails on evidence in the posting's own text),
cannot_tell (no rule fails on evidence, but a field a rule needs is missing or names no country). A reject on evidence wins
over a missing field: a Staff title is rejected even if the description is empty.
"""
import json
import re
from pathlib import Path

from . import fetch, rule

FILTER_VERSION = "FILTER.md v1.3"
ROOT = Path(__file__).resolve().parent.parent
PERSONA = json.loads((ROOT / "persona" / "evan-gordon.resume.json").read_text())

# F1: Evan's target titles plus the two BI phrases (v1.1). Whole phrase, case-insensitive.
ROLE_PHRASES = list(PERSONA["search"]["target_titles"]) + ["business intelligence", "BI engineer"]
# F1, v1.3 (change A, measured on held-out): also an Engineer/Developer title with the whole word Data or Pipeline.
F1_ENGINEER_DATA = True
# F2: excluded whole words, case-insensitive. "Senior" is allowed. v1.3 adds "internship" (found on held-out, not measured).
EXCLUDED = list(PERSONA["search"]["excluded_title_terms"]) + ["internship"]
MAX_YEARS = 5          # F4 gate, inherited from the persona
PREFERRED_YEARS = 3    # score bonus cut-off, v1.2
# T1/T2: Evan's shipped skills; "familiar_with_not_shipped" (Flink, Kubernetes) never counts.
TOPIC_WORDS = [w for g in ("languages", "data_tools", "database_cloud", "devops_cicd", "bi_tools") for w in PERSONA["skills"][g]]
THRESHOLD = 2          # T3, inherited from JS1 R4
POINTS = {"per_topic": 8, "topic_cap": 8, "years": 16, "boston": 10, "remote_us": 5, "visa": 10}

US_MARKERS = list(PERSONA["search"]["us_location_markers"])
# A location part names a country outside the US only if it contains one of these (whole word). A bare city ("London",
# "Tokyo") names no country, so F3 says cannot tell for it (FILTER.md section 3).
NON_US_COUNTRIES = [
    "Australia", "AU", "Austria", "Belgium", "Brazil", "Canada", "Chile", "China", "Colombia", "Costa Rica", "Croatia",
    "Denmark", "England", "Finland", "France", "Germany", "India", "Indonesia", "Ireland", "IE", "Israel", "Italy", "Japan",
    "Lithuania", "Mexico", "Netherlands", "New Zealand", "Norway", "Poland", "Portugal", "Saudi Arabia", "Scotland", "Serbia",
    "Singapore", "South Korea", "Spain", "Sweden", "Switzerland", "Taiwan", "UK", "United Arab Emirates", "United Kingdom",
]

_word = rule._word
_ROLE = [(p, _word(p, re.I)) for p in ROLE_PHRASES]
_EXCL = [(w, _word(w, re.I)) for w in EXCLUDED]
_TOPIC = [(w, _word(w)) for w in TOPIC_WORDS]
_US = [(m, _word(m)) for m in US_MARKERS]
_NON_US = [(c, _word(c)) for c in NON_US_COUNTRIES]
_BOSTON = _word("Boston")
_SENT = re.compile(r"(?<=[.!?])\s+")
_SPONSOR = re.compile(r"sponsor", re.I)
_VISA = re.compile(r"\b(visas?|immigration|H-?1B|work permits?|green cards?)\b", re.I)
_NEG = re.compile(r"\b(no|not|unable|cannot|can't|won't|without|unavailable|ineligible|neither|nor|never)\b|n't\b", re.I)


def sentences(text):
    return [s.strip() for s in _SENT.split(text) if s.strip()]


def _rule(result, field, span, why):
    return {"result": result, "field": field, "span": span, "why": why}


_ENGINEER = re.compile(r"(?<![A-Za-z0-9])(engineer|developer)(?![A-Za-z0-9])", re.I)
_DATA_WORD = re.compile(r"(?<![A-Za-z0-9])(data|pipeline)(?![A-Za-z0-9])", re.I)


def check_f1(title):
    for phrase, rx in _ROLE:
        m = rx.search(title)
        if m:
            return _rule("pass", "title", m.group(0), f"title contains the role phrase '{phrase}'")
    if F1_ENGINEER_DATA and _ENGINEER.search(title) and _DATA_WORD.search(title):
        return _rule("pass", "title", title, "an Engineer/Developer title with the whole word Data or Pipeline (v1.3)")
    return _rule("fail", "title", title, "title contains none of the role phrases")


def check_f2(title):
    hits = [w for w, rx in _EXCL if rx.search(title)]
    if hits:
        return _rule("fail", "title", title, "excluded seniority word(s): " + ", ".join(hits))
    return _rule("pass", "title", title, "no excluded seniority word")


def _location_part(part):
    us = [m for m, rx in _US if rx.search(part)]
    if us:
        if _BOSTON.search(part):
            return "boston"
        return "remote_us" if "remote" in part.lower() else "us"
    if any(rx.search(part) for _, rx in _NON_US):
        return "non_us"
    return "unknown"


def check_f3(loc):
    """Returns (rule, kind). kind: boston > remote_us > us, or None."""
    if not loc.strip():
        return _rule("cannot_tell", "location", loc, "no location"), None
    kinds = [_location_part(p) for p in loc.split(";") if p.strip()]
    for best in ("boston", "remote_us", "us"):
        if best in kinds:
            return _rule("pass", "location", loc, f"a US location ({best})"), best
    if "unknown" in kinds:
        return _rule("cannot_tell", "location", loc, "the location names no country"), None
    return _rule("fail", "location", loc, "every listed location is outside the US"), None


def check_f4(content):
    """Returns (rule, years, phrase)."""
    if not content:
        return _rule("cannot_tell", "description", "", "no description"), None, ""
    phrase, n = rule.first_years_phrase(content)
    if n is None:
        return _rule("pass", "description", "", "no years-of-experience phrase (seniority fit: I cannot tell)"), None, ""
    if n > MAX_YEARS:
        return _rule("fail", "description", phrase, f"first years phrase asks for {n}, above {MAX_YEARS}"), n, phrase
    return _rule("pass", "description", phrase, f"first years phrase asks for {n}, at most {MAX_YEARS}"), n, phrase


def topic_words(content):
    return sorted(w for w, rx in _TOPIC if rx.search(content))


def visa(content):
    """('offered' | 'negative' | 'silent', span). V1: a sentence with sponsor + a visa word and no negation."""
    negative = None
    for s in sentences(content):
        if _SPONSOR.search(s) and _VISA.search(s):
            if _NEG.search(s):
                negative = negative or s
            else:
                return "offered", s
    return ("negative", negative) if negative else ("silent", "")


def evaluate(p):
    title = (p.get("title") or "").strip()
    loc = ((p.get("location") or {}).get("name") or "").strip()
    content = fetch.html_to_text(p.get("content") or "")  # X1; X2: the whole text, never truncated
    rules, missing = {}, []
    if title:
        rules["F1"], rules["F2"] = check_f1(title), check_f2(title)
    else:
        missing.append("title")
        rules["F1"] = rules["F2"] = _rule("cannot_tell", "title", "", "no title")
    rules["F3"], kind = check_f3(loc)
    if not loc:
        missing.append("location")
    rules["F4"], years, phrase = check_f4(content)
    if not content:
        missing.append("description")
        words = []
        rules["T3"] = _rule("cannot_tell", "description", "", "no description")
    else:
        words = topic_words(content)
        ok = len(words) >= THRESHOLD
        rules["T3"] = _rule("pass" if ok else "fail", "description", ", ".join(words),
                            f"{len(words)} distinct topic word(s), threshold {THRESHOLD}")
    results = [r["result"] for r in rules.values()]
    bucket = "rejected" if "fail" in results else ("cannot_tell" if "cannot_tell" in results else "kept")

    v, vspan = visa(content) if content else ("silent", "")
    parts = score = None
    if content:
        parts = {"topics": POINTS["per_topic"] * min(len(words), POINTS["topic_cap"]),
                 "years": POINTS["years"] if years is not None and years <= PREFERRED_YEARS else 0,
                 "location": POINTS["boston"] if kind == "boston" else (POINTS["remote_us"] if kind == "remote_us" else 0),
                 "visa": POINTS["visa"] if v == "offered" else 0}
        score = sum(parts.values())
    pre = all(rules[k]["result"] == "pass" for k in ("F1", "F2", "F3"))
    closest = pre and ((rules["F4"]["result"] == "pass" and len(words) in (1, 2)) or years in (5, 6))
    return {"board": p.get("board"), "id": p.get("id"), "title": title, "location": loc, "url": p.get("absolute_url", ""),
            "filter_version": FILTER_VERSION, "bucket": bucket, "rules": rules, "missing": missing,
            "topic_words": words, "years": years, "years_phrase": phrase, "location_kind": kind,
            "visa": v, "visa_span": vspan, "score": score, "score_parts": parts, "closest_call": bool(closest),
            "content": content}
