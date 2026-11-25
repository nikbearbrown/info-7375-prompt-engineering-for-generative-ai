"""The written rule from CONTRACT.md > The rule. Its output is a record:
anyone can recompute it by hand from the posting and the résumé."""
import html
import re

from agent import resume as resume_mod

TITLE_WORDS = ["engineer", "developer"]
SENIORITY_WORDS = ["senior", "staff", "principal", "lead", "manager", "director"]
SKILLS_NEEDED = 3

# A place counts as US if it contains one of these as a whole word (any case).
# This list is how "anywhere in the US" is applied; anything else is not US.
US_STATE_CODES = """AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO
MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC""".split()
US_STATE_NAMES = """Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|
Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|
Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|
New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|
Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|
West Virginia|Wisconsin|Wyoming""".replace("\n", "").split("|")
US_CITIES = ["Seattle", "SEA", "San Francisco", "South San Francisco", "SF", "New York City",
             "NYC", "Chicago", "Atlanta", "Boston", "Austin", "Denver", "Los Angeles", "Miami",
             "Portland", "San Jose", "Palo Alto", "Mountain View", "Menlo Park", "Sunnyvale",
             "Oakland", "Redmond", "Bellevue", "Dallas", "Houston", "Phoenix", "Pittsburgh",
             "Philadelphia", "Minneapolis", "Detroit", "Raleigh", "Salt Lake City"]
NA_VALUES = {"n/a", "na", ""}


def _word(token, any_case=True):
    flags = re.IGNORECASE if any_case else 0
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(token) + r"(?![A-Za-z0-9])", flags)


# Codes match in capitals only, so "Remote in Canada" is not Indiana ("IN").
_US_PATTERNS = ([(t, _word(t, any_case=False)) for t in ["US", "USA", "U.S."] + US_STATE_CODES]
                + [(t, _word(t)) for t in ["United States"] + US_STATE_NAMES + US_CITIES])


def split_places(name):
    parts = re.split(r"[;,/]| or ", name or "")
    out = []
    for p in parts:
        p = re.sub(r"^or\s+", "", p.strip(), flags=re.IGNORECASE).strip()
        if p:
            out.append(p)
    return out


def place_is_us(place):
    if place.strip().lower() == "remote":  # plain Remote counts as US (contract)
        return True, "plain Remote"
    for token, pat in _US_PATTERNS:
        if pat.search(place):
            return True, token
    return False, None


def check_title(title):
    t = (title or "").lower()
    matched = next((w for w in TITLE_WORDS if w in t), None)
    blocked = [w for w in SENIORITY_WORDS if w in t]
    return {"passed": matched is not None and not blocked, "matched_word": matched, "blocked_by": blocked}


def check_location(name):
    name = name or ""
    if name.strip().lower() in NA_VALUES:
        return {"passed": False, "places": [], "reason": f"location is {name!r} (N/A fails)"}
    places = []
    for p in split_places(name):
        us, why = place_is_us(p)
        places.append({"place": p, "us": us, "matched_token": why})
    passed = bool(places) and all(p["us"] for p in places)
    non_us = [p["place"] for p in places if not p["us"]]
    reason = "all places are US" if passed else f"not US: {', '.join(non_us) or 'no places'}"
    return {"passed": passed, "places": places, "reason": reason}


def posting_text(p):
    body = html.unescape(p.get("content") or "")
    body = re.sub(r"<[^>]+>", " ", body)
    return f"{p.get('title') or ''} {html.unescape(body)}"


def check_skills(p, resume_data):
    skills = resume_mod.counted_skills(resume_data)
    if not skills:
        return {"passed": False, "matched": [], "count": 0, "needed": SKILLS_NEEDED,
                "reason": "resume.skills is missing or empty"}
    text = posting_text(p)
    matched, sources, seen = [], {}, set()
    for list_name, skill in skills:
        if skill.lower() in seen:
            continue
        if _word(skill).search(text):
            seen.add(skill.lower())
            matched.append(skill)
            sources[skill] = f"resume.skills.{list_name}"
    return {"passed": len(matched) >= SKILLS_NEEDED, "matched": matched, "sources": sources,
            "count": len(matched), "needed": SKILLS_NEEDED}


def judge(p, resume_data):
    loc_name = (p.get("location") or {}).get("name", "")
    title = check_title(p.get("title"))
    location = check_location(loc_name)
    skills = check_skills(p, resume_data)
    checks = {"title": title, "location": location, "skills": skills}
    failed = [k for k, c in checks.items() if not c["passed"]]
    verdict = "relevant" if not failed else "not relevant"

    if title["passed"]:
        t_why = f"posting.title {p.get('title')!r} contains {title['matched_word']!r}, no seniority word"
    elif title["blocked_by"]:
        t_why = f"posting.title {p.get('title')!r} contains seniority word(s) {title['blocked_by']}"
    else:
        t_why = f"posting.title {p.get('title')!r} contains neither 'engineer' nor 'developer'"
    l_why = f"posting.location.name {loc_name!r}: {location['reason']}"
    if skills.get("reason"):
        s_why = skills["reason"]
    else:
        found = ", ".join(f"{s} ({skills['sources'][s]})" for s in skills["matched"]) or "none"
        s_why = (f"{skills['count']} of {SKILLS_NEEDED} needed resume.skills found as whole words "
                 f"in posting.title/content: {found}")
    head = verdict if not failed else f"{verdict} (failed: {', '.join(failed)})"
    justification = f"{head}. Title: {t_why}. Location: {l_why}. Skills: {s_why}."

    return {"posting_id": p.get("id"), "posting_title": p.get("title"), "posting_url": p.get("absolute_url"),
            "judge": "rule", "label": "record", "verdict": verdict, "failed_checks": failed,
            "checks": checks, "justification": justification}


def judge_all(postings, resume_data):
    return [judge(p, resume_data) for p in postings]
