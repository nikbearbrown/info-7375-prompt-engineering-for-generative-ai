"""The written rule (CONTRACT.md section 4, Rules 1-5 = R1-R5). Output is a record: anyone can recompute it."""
import re

from .resume import skill_groups

RULE_VERSION = "R1-R5 v2.4 (CONTRACT.md 2026-10-31 18:26 ET)"
YEARS_RE = re.compile(r"(?<![\d.])(\d{1,2})\s*(?:\+|plus)?\s*(?:(?:-|–|to)\s*\d{1,2})?\s*\+?\s*years?\b", re.I)
WINDOW = 60


def _cite(r, *paths):
    out = []
    for path in paths:
        cur = r
        for part in path.split("."):
            cur = cur[part]
        out.append({"field": path, "value": cur})
    return out


def _word(term, flags=0):
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])", flags)


def check_r1(p, r):
    title = p["title"]
    hits = [t for t in r["search"]["target_titles"] if t.lower() in title.lower()]
    if hits:
        i = title.lower().index(hits[0].lower())
        value = title[i:i + len(hits[0])]
    else:
        value = title
    return {"check": "R1", "resume": _cite(r, "search.target_titles"),
            "posting": {"field": "title", "value": value}, "matched": hits, "passed": bool(hits)}


def check_r2(p, r):
    title = p["title"]
    hits = [t for t in r["search"]["excluded_title_terms"] if _word(t, re.I).search(title)]
    return {"check": "R2", "resume": _cite(r, "search.excluded_title_terms"),
            "posting": {"field": "title", "value": title}, "matched": hits, "passed": not hits}


def check_r3(p, r):
    """Boston (preferred), or a listed US marker that is remote (if open_to_remote) or on-site/hybrid (if open_to_relocate)."""
    loc = p["location"]["name"]
    s = r["search"]
    home = [c for c in (x.split(",")[0].strip() for x in s["locations"]) if c.lower() in loc.lower()]
    us = [m for m in s["us_location_markers"] if _word(m).search(loc)]
    remote = "remote" in loc.lower()
    hits = list(home)
    if us and remote and s["open_to_remote"]:
        hits.append("remote in US: " + ", ".join(us))
    if us and not remote and s["open_to_relocate"]:
        hits.append("relocate within US: " + ", ".join(us))
    return {"check": "R3",
            "resume": _cite(r, "search.locations", "search.open_to_remote", "search.open_to_relocate", "search.us_location_markers"),
            "posting": {"field": "location.name", "value": loc}, "matched": hits, "passed": bool(hits),
            "preferred": bool(home)}


def check_r4(p, r):
    groups = skill_groups(r)
    hits = []
    for g in groups:
        for skill in r["skills"][g]:
            if skill not in hits and _word(skill).search(p["content"]):
                hits.append(skill)
    return {"check": "R4", "resume": _cite(r, *[f"skills.{g}" for g in groups]),
            "posting": {"field": "content", "value": hits}, "matched": hits, "passed": len(hits) >= 2}


def first_years_phrase(content):
    """First 'N years' / 'N+ years' / 'N-M years' with 'experience' within WINDOW chars. Returns (phrase, N) or ("", None)."""
    for m in YEARS_RE.finditer(content):
        around = (content[max(0, m.start() - WINDOW):m.start()] + " " + content[m.end():m.end() + WINDOW]).lower()
        if "experience" in around:
            return m.group(0).strip(), int(m.group(1))
    return "", None


def check_r5(p, r):
    phrase, n = first_years_phrase(p["content"])
    s = r["search"]
    return {"check": "R5", "resume": _cite(r, "search.max_required_years", "search.preferred_max_years"),
            "posting": {"field": "content", "value": phrase}, "matched": [] if n is None else [n],
            "passed": n is None or n <= s["max_required_years"],
            "preferred": n is not None and n <= s["preferred_max_years"]}


CHECKS = [check_r1, check_r2, check_r3, check_r4, check_r5]


def judge(p, r):
    checks = [c(p, r) for c in CHECKS]
    return {
        "posting_id": p["id"],
        "kind": "record",
        "rule": RULE_VERSION,
        "verdict": "relevant" if all(c["passed"] for c in checks) else "not_relevant",
        "preferred_location": checks[2]["preferred"],  # reported, never changes the verdict (CONTRACT.md sections 2 and 6)
        "preferred_years": checks[4]["preferred"],     # reported, never changes the verdict (CONTRACT.md sections 2 and 6)
        "checks": checks,
    }
