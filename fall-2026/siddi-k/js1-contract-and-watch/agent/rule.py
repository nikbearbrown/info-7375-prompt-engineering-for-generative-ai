"""The rule (CONTRACT.md, The rule): four checks, all must pass. A record anyone can recompute; no model involved."""
from __future__ import annotations

import re

from .textprep import requirements_text, whole_word

SENIORITY_RE = re.compile(r"\b(senior|sr|staff|principal|lead|manager|director|head|vp)\b")
YEARS_RE = re.compile(r"(?<!\d)(\d{1,2})\s*(?:\+|(?:-|–|to)\s*\d{1,2}\+?)?\s*years?(?![a-z0-9])")
DEGREE_RE = re.compile(r"(?<![a-z0-9])(?:ms|m\.s\.|master's|masters|phd|ph\.d\.?|doctorate)(?![a-z0-9])")
REMOTE_REGION_RE = re.compile(r"(?<![a-z0-9])(?:us|usa|united states|north america)(?![a-z0-9])")
LOCATION_SPLIT_RE = re.compile(r";|\||/|(?<![a-z0-9])or(?![a-z0-9])")
EXPERIENCE_RE = whole_word("experience")


def first_whole_word(phrases, text: str):
    return next((ph for ph in phrases if whole_word(ph).search(text)), None)


def title_check(title: str, persona: dict) -> dict:
    t = title.lower()
    keyword = first_whole_word(persona["target_title_keywords"], t)
    exclusion = first_whole_word(persona["title_exclusions"], t)
    return {"passed": keyword is not None and exclusion is None, "matched_keyword": keyword, "exclusion_hit": exclusion}


def years_required(sentences: list[str]):
    """Smallest first-group capture over sentences that whole-word contain "experience", skipping degree-tied numbers."""
    found = []
    for s in sentences:
        if not EXPERIENCE_RE.search(s):
            continue
        for m in YEARS_RE.finditer(s):
            if DEGREE_RE.search(s[max(0, m.start() - 25):m.start()]):
                continue
            found.append(int(m.group(1)))
    return min(found) if found else None


def seniority_check(title: str, sentences: list[str], persona: dict) -> dict:
    token = SENIORITY_RE.search(title.lower())
    years = years_required(sentences)
    ok_years = years is None or years <= persona["years_experience"] + 2
    return {"passed": token is None and ok_years, "seniority_token": token.group(1) if token else None,
            "years_required": years}


def location_check(location_name: str, persona: dict) -> dict:
    for segment in (s.strip() for s in LOCATION_SPLIT_RE.split(location_name.lower())):
        if not segment:
            continue
        if "remote" in segment:
            if persona["remote_ok"] and (segment == "remote" or REMOTE_REGION_RE.search(segment)):
                return {"passed": True, "matched": segment}
            continue
        city = first_whole_word(persona["preferred_cities"], segment)
        if city:
            return {"passed": True, "matched": city}
    return {"passed": False, "matched": None}


def posting_skills(sentences: list[str], vocab: dict) -> list[str]:
    text = requirements_text(sentences)
    return [skill for skill, aliases in vocab.items()
            if any(whole_word(a).search(text) for a in {skill, *aliases})]


def skill_check(sentences: list[str], persona: dict, vocab: dict) -> dict:
    found = posting_skills(sentences, vocab)
    matched = [s for s in found if s in persona["skills"]]
    ratio = len(matched) / len(found) if found else 0.0
    return {"passed": bool(found) and len(matched) >= 3 and ratio >= 0.40, "posting_skills": found,
            "matched": matched, "matched_count": len(matched), "ratio": round(ratio, 4)}


def justify(checks: dict, posting: dict, persona: dict) -> str:
    t, s, loc, sk = (checks[k] for k in ("title_match", "seniority_ok", "location_ok", "skill_overlap"))
    parts = []
    if t["matched_keyword"] and not t["exclusion_hit"]:
        parts.append(f"title contains target_title_keywords '{t['matched_keyword']}' with no title_exclusions hit")
    elif t["exclusion_hit"]:
        parts.append(f"title hits title_exclusions '{t['exclusion_hit']}'")
    else:
        parts.append("title contains no target_title_keywords phrase")
    parts.append(f"title has seniority token '{s['seniority_token']}'" if s["seniority_token"]
                 else "title has no seniority token")
    yx = persona["years_experience"]
    if s["years_required"] is None:
        parts.append("content states no years-of-experience figure")
    else:
        op = "≤" if s["years_required"] <= yx + 2 else ">"
        parts.append(f"content years_required {s['years_required']} {op} years_experience {yx} + 2")
    parts.append(f"location '{posting['location']}' matches preferred_cities/remote_ok as '{loc['matched']}'"
                 if loc["passed"] else f"location '{posting['location']}' matches no preferred_cities or allowed remote")
    n = len(sk["posting_skills"])
    parts.append(f"{sk['matched_count']} of {n} content skills are in skills ({sk['ratio']:.2f})" if n
                 else "content names no vocab skills")
    return "; ".join(parts) + "."


def judge(posting: dict, sentences: list[str], persona: dict, vocab: dict) -> dict:
    """posting = {"id", "title", "location"}; sentences = the requirements text from textprep."""
    checks = {"title_match": title_check(posting["title"], persona),
              "seniority_ok": seniority_check(posting["title"], sentences, persona),
              "location_ok": location_check(posting["location"], persona),
              "skill_overlap": skill_check(sentences, persona, vocab)}
    verdict = "relevant" if all(c["passed"] for c in checks.values()) else "not_relevant"
    return {"rule_verdict": verdict, "rule_label": "record", "rule_checks": checks,
            "rule_justification": justify(checks, posting, persona)}
