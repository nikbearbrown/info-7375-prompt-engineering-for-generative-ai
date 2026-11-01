"""The deterministic rule: title, seniority, location, skills (CONTRACT.md, The rule).

The verdict this module returns is the RULE RECORD. Claude never changes it.
"""
from __future__ import annotations

from typing import Callable, Iterable

from .text import find_phrase, normalize, snippet

TITLE_PHRASES = [
    "software engineer",
    "backend engineer",
    "back-end engineer",
    "backend developer",
    "back-end developer",
]
SENIORITY_EXCLUDED = [
    "senior", "sr", "staff", "principal", "lead", "manager", "director", "architect",
    "intern", "internship", "engineer iii", "engineer iv", "engineer v",
]
BOSTON = "boston"
REMOTE_US = ["remote, us", "remote - us", "remote us", "us remote", "united states - remote"]
SKILL_THRESHOLD = 2

RELEVANT = "RELEVANT"
NOT_RELEVANT = "NOT_RELEVANT"


def posting_id(posting: dict) -> str:
    return str(posting["id"])


def location_fields(posting: dict) -> list:
    """(field name, raw value) for every structured location the rule reads."""
    fields = []
    name = (posting.get("location") or {}).get("name")
    if name:
        fields.append(("posting.location.name", name))
    for office in posting.get("offices") or []:
        if office.get("name"):
            fields.append(("posting.offices[].name", office["name"]))
    return fields


def _preferred_index(resume: dict, wanted: str) -> str:
    for i, value in enumerate(resume["preferred_locations"]):
        if normalize(value) == wanted:
            return f'resume.preferred_locations[{i}]="{value}"'
    return "the contract's accepted-location list"


def check_title(posting: dict, find: Callable = find_phrase) -> dict:
    title = posting["title"]
    t = normalize(title)
    for phrase in TITLE_PHRASES:
        if find(phrase, t):
            return {"pass": True, "matched": phrase,
                    "line": f'posting.title="{title}" contains "{phrase}" (title_check PASS)'}
    return {"pass": False, "matched": None,
            "line": f'posting.title="{title}" contains none of the target title phrases (title_check FAIL)'}


def check_seniority(posting: dict, find: Callable = find_phrase) -> dict:
    title = posting["title"]
    t = normalize(title)
    hits = [term for term in SENIORITY_EXCLUDED if find(term, t)]
    if hits:
        return {"pass": False, "excluded_terms": hits,
                "line": f'posting.title="{title}" failed seniority_check because "{hits[0]}" is excluded.'}
    return {"pass": True, "excluded_terms": [],
            "line": f'posting.title="{title}" contains no excluded seniority term (seniority_check PASS)'}


def check_location(posting: dict, resume: dict, find: Callable = find_phrase) -> dict:
    fields = location_fields(posting)
    for field, value in fields:
        v = normalize(value)
        if find(BOSTON, v):
            return {"pass": True, "field": field, "value": value, "matched": BOSTON,
                    "line": f'{field}="{value}" contains "boston", meeting '
                            f'{_preferred_index(resume, "boston")} (location_check PASS)'}
        for pattern in REMOTE_US:
            if find(pattern, v):
                return {"pass": True, "field": field, "value": value, "matched": pattern,
                        "line": f'{field}="{value}" contains "{pattern}", meeting '
                                f'{_preferred_index(resume, "remote us")} (location_check PASS)'}
    shown = "; ".join(f'{f}="{v}"' for f, v in fields) or "no structured location fields"
    return {"pass": False, "field": None, "value": None, "matched": None,
            "line": f"{shown}: none contains Boston or an accepted US-remote pattern (location_check FAIL)"}


def check_skills(posting: dict, resume: dict, find: Callable = find_phrase) -> dict:
    content = normalize(posting.get("content"))
    matched = []
    for i, skill in enumerate(resume["skills"]):
        m = find(skill, content)
        if m:
            matched.append({"resume_field": f"skills[{i}]", "skill": skill,
                            "posting_field": "content", "snippet": snippet(content, m)})
    passed = len(matched) >= SKILL_THRESHOLD
    lines = [f'resume.{m["resume_field"]}="{m["skill"]}" matched posting.content="{m["snippet"]}"'
             for m in matched]
    lines.append(f"{len(matched)} distinct résumé skill(s) found in posting.content; "
                 f"{SKILL_THRESHOLD} required (skills_check {'PASS' if passed else 'FAIL'})")
    return {"pass": passed, "count": len(matched), "threshold": SKILL_THRESHOLD,
            "matched": matched, "lines": lines}


def classify(posting: dict, resume: dict, find: Callable = find_phrase) -> dict:
    """Apply all four checks independently and combine them. Every check is reported."""
    checks = {
        "title": check_title(posting, find),
        "seniority": check_seniority(posting, find),
        "location": check_location(posting, resume, find),
        "skills": check_skills(posting, resume, find),
    }
    relevant = all(c["pass"] for c in checks.values())
    justification = [checks["title"]["line"], checks["seniority"]["line"], checks["location"]["line"]]
    justification += checks["skills"]["lines"]
    return {
        "label": "RULE RECORD",
        "posting_id": posting_id(posting),
        "title": posting["title"],
        "verdict": RELEVANT if relevant else NOT_RELEVANT,
        "checks": {name: c["pass"] for name, c in checks.items()},
        "details": checks,
        "justification": justification,
    }


def classify_all(postings: Iterable[dict], resume: dict) -> dict:
    """Classify each posting and key the result by its own Greenhouse id (never by position)."""
    return {posting_id(p): classify(p, resume) for p in postings}
