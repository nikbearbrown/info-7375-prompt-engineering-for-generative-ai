"""The rule verdict (labeled `record`). See CONTRACT.md, "The rule"."""

import html
import re

ROLE_PHRASES = [
    "software engineer", "software developer",
    "full stack engineer", "full stack developer",
    "frontend engineer", "frontend developer",
]
ROLE_WORDS = re.compile(r"\b(sde|swe)\b", re.I)
SENIORITY_WORDS = re.compile(r"\b(staff|principal|manager|director)\b", re.I)
MAX_YEARS = 3

US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY", "DC",
}
STATE_AT_END = re.compile(r"(?:^|[^a-z])([a-z]{2})$", re.I)
US_WORDS = re.compile(r"\b(united states|usa|us)\b", re.I)

SPONSOR_FAIL = [
    "unable to sponsor", "will not sponsor", "not able to sponsor",
    "do not sponsor", "does not sponsor", "without sponsorship",
]
CITIZENSHIP_FAIL = [
    "must be a U.S. citizen", "U.S. citizens only",
    "U.S. citizenship is required", "U.S. citizenship required",
    "requires U.S. citizenship", "must be a U.S. person",
]
CLEARANCE_FAIL = ["security clearance"]

YEARS = re.compile(
    r"(?<![\d.])(\d+(?:\.\d+)?)\s*\+?\s*"
    r"(?:(?:-|–|—|to)\s*(\d+(?:\.\d+)?)\s*\+?\s*)?"
    r"years?\b",
    re.I,
)
SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+|\n+")

# Fields each check reads, per CONTRACT.md "Wrong versions" 3.
FIELDS = {
    "role": (["title"], ["target.roles"]),
    "seniority": (["title"], []),
    "experience": (["content"], ["experience"]),
    "location": (["location.name"], ["target.locations"]),
    "work_authorization": (["content"], ["work_authorization"]),
}


def content_text(posting):
    """Greenhouse `content` is HTML-escaped HTML: unescape, then drop tags."""
    raw = html.unescape(posting.get("content") or "")
    return re.sub(r"<[^>]+>", "\n", raw)


def _auth_text(text):
    """Lowercase, periods removed ("U.S." == "US"), whitespace collapsed."""
    return " ".join(text.replace(".", "").lower().split())


def _auth_matches(text, phrases):
    norm = _auth_text(text)
    return [p for p in phrases if _auth_text(p) in norm]


def auth_flags(posting):
    """Work-authorization flags from the description text (text matches, not legal facts)."""
    text = content_text(posting)
    lower = _auth_text(text)
    if _auth_matches(text, SPONSOR_FAIL):
        sponsorship = "no_sponsorship"
    elif "sponsor" in lower:
        sponsorship = "mentioned"
    else:
        sponsorship = "not_mentioned"
    restricted = _auth_matches(text, CITIZENSHIP_FAIL + CLEARANCE_FAIL)
    return {
        "sponsorship": sponsorship,
        "e_verify": "mentioned" if "e-verify" in text.lower() else "not_mentioned",
        "citizenship_or_clearance_required": "yes" if restricted else "no",
    }


def _check_role(title):
    lower = title.lower()
    return any(p in lower for p in ROLE_PHRASES) or bool(ROLE_WORDS.search(title))


def _min_years_required(text):
    """Smallest years-of-experience number in any sentence that mentions experience."""
    found = []
    for sentence in SENTENCE_BREAK.split(text):
        if not re.search(r"\bexperience\b", sentence, re.I):
            continue
        for low, high in YEARS.findall(sentence):
            values = [float(low)] + ([float(high)] if high else [])
            found.append(min(values))
    return min(found) if found else None


def _check_location(name):
    for part in name.split(";"):
        part = part.replace(".", "").strip()  # "U.S." counts as "US"
        m = STATE_AT_END.search(part)
        if m and m.group(1).upper() in US_STATES:
            return True
        if US_WORDS.search(part):
            return True
    return False


def _fmt_years(n):
    return str(int(n)) if n == int(n) else str(n)


def judge(posting, resume):
    """Return {"verdict", "resume_fields", "posting_fields", "reason"}."""
    title = posting.get("title") or ""
    location = (posting.get("location") or {}).get("name") or ""
    text = content_text(posting)
    target = resume.get("target", {})
    roles = ", ".join(target.get("roles", [])) or "the target roles"
    places = ", ".join(target.get("locations", [])) or "the target locations"

    applied, passes, fails = [], [], []

    applied.append("role")
    if _check_role(title):
        passes.append(f'title "{title}" matches a target role ({roles})')
    else:
        fails.append(f'title "{title}" is not one of the target roles ({roles})')

    applied.append("seniority")
    m = SENIORITY_WORDS.search(title)
    if m:
        fails.append(f'title is "{m.group(1)}" level, above the résumé\'s mid-level target')

    lower_title = title.lower()
    if "senior" in lower_title or "lead" in lower_title:
        applied.append("experience")
        years = _min_years_required(text)
        if years is None:
            fails.append("Senior/Lead title states no years of experience to compare with the résumé's ~3 years")
        elif years <= MAX_YEARS:
            passes.append(f"asks for {_fmt_years(years)} years, within the résumé's ~3 years")
        else:
            fails.append(f"asks for {_fmt_years(years)} years, more than the résumé's ~3 years")

    applied.append("location")
    if _check_location(location):
        passes.append(f'location "{location}" is in the US ({places})')
    else:
        fails.append(f'location "{location}" is not in the US ({places})')

    applied.append("work_authorization")
    blocked = _auth_matches(text, SPONSOR_FAIL + CLEARANCE_FAIL + CITIZENSHIP_FAIL)
    if blocked:
        fails.append(f'description says "{blocked[0]}", which rules out a résumé that needs sponsorship')
    else:
        passes.append("description has no sponsorship, citizenship, or clearance restriction")

    posting_fields, resume_fields = [], []
    for check in applied:
        p_fields, r_fields = FIELDS[check]
        posting_fields += [f for f in p_fields if f not in posting_fields]
        resume_fields += [f for f in r_fields if f not in resume_fields]

    if fails:
        verdict, reason = "not_relevant", "Not relevant: " + "; ".join(fails) + "."
    else:
        verdict, reason = "relevant", "Relevant: " + "; ".join(passes) + "."
    return {
        "verdict": verdict,
        "resume_fields": resume_fields,
        "posting_fields": posting_fields,
        "reason": reason,
    }
