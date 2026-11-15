"""The filter from FILTER.md, as code. Each rule cites the posting text that decided it.

judge(posting, skills) -> {"verdict": keep|reject|cannot_tell, "rule", "reason", "evidence",
                           "skills", "score", "filter_version"}

A posting is a dict with board, id, title, location, country (or None), text (plain text).
Standard library only.
"""
import html
import re

FILTER_VERSION = "1.0"

ROLE_WORDS = ["software engineer", "software developer", "backend engineer", "back-end engineer",
              "back end engineer", "full stack engineer", "full-stack engineer",
              "fullstack engineer", "cloud engineer", "platform engineer"]
SENIORITY_WORDS = ["senior", "sr", "staff", "principal", "lead", "manager", "director", "head"]
TITLE_BONUS_WORDS = ["software engineer", "software developer"]
MIN_SKILLS = 2
MAX_YEARS = 4          # 4 or more years -> reject
TITLE_BONUS = 2
POINTS_PER_SKILL = 1
EXCLUDED_SKILL_GROUPS = {"familiar_with_not_shipped"}

US_STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
             "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
             "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
             "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
             "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
             "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
             "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
             "Washington", "West Virginia", "Wisconsin", "Wyoming", "District of Columbia"]
US_CODES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN",
            "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV",
            "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN",
            "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"]
US_PHRASES = ["United States", "USA", "U.S.A.", "U.S."]
US_COUNTRY_VALUES = {"US", "USA", "UNITED STATES", "UNITED STATES OF AMERICA"}
WORK_MODE_WORDS = r"remote|hybrid|anywhere|flexible|onsite|on-site|in-office|office|or"

_YEARS = re.compile(
    r"(?<![A-Za-z0-9])(\d{1,2})\s*(\+|plus)?\s*(?:(?:-|–|—|to)\s*(\d{1,2})\s*\+?\s*)?"
    r"(or more\s+)?(?:years?|yrs?)(?![A-Za-z])", re.IGNORECASE)
_YEARS_NO_NUMBER = re.compile(r"\byears?\s+of\s+(?:\w+\s+){0,3}experience\b|\byears'?\s+experience\b",
                              re.IGNORECASE)
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?;])\s+|\n+|\s*[•·]\s*")


def plain_text(raw):
    """HTML (possibly entity-escaped twice, as Greenhouse sends it) -> plain text."""
    if not raw:
        return ""
    text = html.unescape(html.unescape(raw))
    text = re.sub(r"<(br|/p|/li|/div|/h\d)[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<li[^>]*>", "\n• ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\s*\n\s*", "\n", text).strip()


def _pattern(term):
    body = re.escape(term).replace(r"\ ", r"\s+")
    return r"(?<![A-Za-z0-9])" + body + r"(?![A-Za-z0-9])"


def find_whole(term, text, case_sensitive=False):
    if not text:
        return None
    return re.search(_pattern(term), text, 0 if case_sensitive else re.IGNORECASE)


def resume_skills(resume):
    out = []
    for group, values in resume.get("skills", {}).items():
        if group in EXCLUDED_SKILL_GROUPS or not isinstance(values, list):
            continue
        out.extend(v for v in values if isinstance(v, str))
    return out


def sentence_around(text, start, end):
    """The sentence (or bullet) of `text` that contains text[start:end]."""
    left = max(text.rfind(c, 0, start) for c in ".!?;\n•")
    rights = [i for i in (text.find(c, end) for c in ".!?;\n•") if i != -1]
    right = min(rights) + 1 if rights else len(text)
    return text[left + 1:right].strip()


def location_is_us(location, country):
    """True / False / None (cannot tell), plus the quote that decided it."""
    if country:
        return str(country).strip().upper() in US_COUNTRY_VALUES, ("country", str(country))
    if not location or not location.strip():
        return None, ("location", location or "")
    for phrase in US_PHRASES:
        if find_whole(phrase, location, case_sensitive=True):
            return True, ("location", location)
    if find_whole("US", location, case_sensitive=True):
        return True, ("location", location)
    for state in US_STATES:
        if find_whole(state, location):
            return True, ("location", location)
    if re.search(r",\s*(" + "|".join(US_CODES) + r")(?![A-Za-z])", location):
        return True, ("location", location)
    rest = re.sub(r"(?<![A-Za-z])(" + WORK_MODE_WORDS + r")(?![A-Za-z])", " ", location, flags=re.IGNORECASE)
    if re.search(r"[A-Za-zÀ-ÿ]", rest):
        return False, ("location", location)
    return None, ("location", location)


def years_requirement(text):
    """("ok"|"too_many"|"unclear"|"not_stated", quote or None)."""
    reqs, unnumbered = [], None
    for sentence in _SENTENCE_SPLIT.split(text or ""):
        if not find_whole("experience", sentence):
            continue
        found = False
        for m in _YEARS.finditer(sentence):
            lower = int(m.group(1))
            upper = int(m.group(3)) if m.group(3) else None
            reqs.append((lower, upper, m.group(0).strip(), sentence.strip()))
            found = True
        if not found and unnumbered is None and _YEARS_NO_NUMBER.search(sentence):
            unnumbered = sentence.strip()
    if reqs:
        lower, upper, quote, sentence = min(reqs, key=lambda r: r[0])
        if lower >= MAX_YEARS:
            return "too_many", quote, sentence
        if upper is not None and upper >= MAX_YEARS:
            return "unclear", quote, sentence
        return "ok", quote, sentence
    if unnumbered:
        return "unclear", unnumbered, unnumbered
    return "not_stated", None, None


def judge(posting, skills):
    title = posting.get("title") or ""
    text = posting.get("text") or ""
    evidence = []

    def out(verdict, rule, reason, found=()):
        score = None
        if verdict == "keep":
            bonus = TITLE_BONUS if any(find_whole(w, title) for w in TITLE_BONUS_WORDS) else 0
            score = POINTS_PER_SKILL * len(found) + bonus
        return {"posting_id": posting.get("id"), "board": posting.get("board"), "title": title,
                "verdict": verdict, "rule": rule, "reason": reason, "evidence": evidence,
                "skills": list(found), "score": score, "filter_version": FILTER_VERSION}

    found, both = [], title + "\n" + text
    for s in skills:
        m = find_whole(s, both)
        if m:
            found.append(s)
            evidence.append({"check": "skill", "field": "title" if m.start() < len(title) else "text",
                             "quote": m.group(0), "context": sentence_around(both, m.start(), m.end())})

    role = next((m for m in (find_whole(w, title) for w in ROLE_WORDS) if m), None)
    if not role:
        return out("reject", "R1", "title has no role word", found)
    evidence.insert(0, {"check": "role", "field": "title", "quote": role.group(0)})

    senior = next((m for m in (find_whole(w, title) for w in SENIORITY_WORDS) if m), None)
    if senior:
        evidence.insert(1, {"check": "seniority", "field": "title", "quote": senior.group(0)})
        return out("reject", "R2", f"title contains seniority word «{senior.group(0)}»", found)

    if not text.strip():
        return out("cannot_tell", "R3", "I cannot tell: the posting has no description", found)

    us, (field, quote) = location_is_us(posting.get("location"), posting.get("country"))
    evidence.insert(1, {"check": "location", "field": field, "quote": quote})
    if us is None:
        return out("cannot_tell", "R4", "I cannot tell: no country in the location", found)
    if us is False:
        return out("reject", "R4", f"location is not in the US: «{quote}»", found)

    status, yq, ysent = years_requirement(text)
    if yq:
        evidence.insert(2, {"check": "years", "field": "text", "quote": yq, "context": ysent})
    if status == "too_many":
        return out("reject", "R5", f"asks for {MAX_YEARS}+ years: «{yq}»", found)
    if status == "unclear":
        return out("cannot_tell", "R5", f"I cannot tell how many years are required: «{yq}»", found)

    if len(found) < MIN_SKILLS:
        return out("reject", "R6", f"{len(found)} résumé skill(s) found, {MIN_SKILLS} needed", found)
    return out("keep", "R6", f"{len(found)} résumé skills found", found)
