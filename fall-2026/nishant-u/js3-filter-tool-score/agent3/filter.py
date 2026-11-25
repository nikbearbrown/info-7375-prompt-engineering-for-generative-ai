"""FILTER.md v1: relevance rules F1-F4 and the abstention rule.

A verdict is accept, reject (with the first failing rule and the field it read), or
abstain ("abstain: cannot tell"). A missing or empty field fails the rule that needs it
as "missing: <field>"; nothing is ever accepted on a default.

Interpretations of FILTER.md v1 that the text leaves open, fixed here so they are visible:
- "location part" is a ;-separated part of the location field (the JS1 contract's reading).
- "ends in a US state code" uses the inherited JS1 marker list in data/requirements.json
  (", CA", ", NY", ...): the part must end in comma, space, two-letter code.
- "says Remote with US" means the part contains the whole word "remote" (any case) and a
  US marker: "US" or "USA" (exact case, so the pronoun "us" does not count), "U.S." or
  "United States".
- Abstention is checked first and overrides F1-F4. A text field that is absent or empty is
  not "shorter than 300 characters": it fails F4 as "missing: <field>".
- Ashby: location is the `location` field only (secondaryLocations is not read in v1);
  text is descriptionHtml, or descriptionPlain when descriptionHtml is empty.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ROLE_WORDS = ("data", "analytics", "analyst", "scientist", "machine learning", "ML")
EXCLUDE_WORDS = ("manager", "director", "head", "lead", "intern")
MIN_TEXT_CHARS = 300
MIN_SKILLS = 1
SHIPPED_SKILL_LISTS = ("languages", "data_bi", "backend_automation", "database_cloud")
US_MARKER = re.compile(r"(?<!\w)(US|USA|U\.S\.|United States)(?!\w)")
REMOTE = re.compile(r"(?<!\w)remote(?!\w)", re.IGNORECASE)
ABSTAIN = "abstain: cannot tell"


def _state_codes():
    req = json.loads((ROOT / "data" / "requirements.json").read_text(encoding="utf-8"))
    return tuple(m for m in req["us_location_markers"] if m.startswith(", "))


STATE_ENDINGS = _state_codes()


def strip_html(content):
    """Greenhouse sends escaped HTML: unescape, drop tags, unescape what was inside, collapse space."""
    text = re.sub(r"<[^>]+>", " ", html.unescape(content or ""))
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def find_term(text, term):
    """The text matching term as a whole word, ignoring case, or None. Spaces in term match any space."""
    pattern = r"\s+".join(re.escape(w) for w in term.split())
    match = re.search(r"(?<!\w)" + pattern + r"(?!\w)", text or "", re.IGNORECASE)
    return match.group(0) if match else None


def shipped_skills(resume):
    """Every skill in the shipped lists, in résumé order (not familiar_with_not_shipped)."""
    found = []
    for name in SHIPPED_SKILL_LISTS:
        value = resume["skills"].get(name)
        if not isinstance(value, list) or not all(isinstance(s, str) for s in value):
            raise ValueError(f"skills.{name} must be a list of strings")
        found.extend(value)
    return found


def _clean(value):
    return value.strip() if isinstance(value, str) and value.strip() else None


def read_title(system, job):
    return "title", _clean(job.get("title"))


def read_location(system, job):
    if system == "greenhouse":
        loc = job.get("location")
        return "location.name", _clean(loc.get("name") if isinstance(loc, dict) else None)
    return "location", _clean(job.get("location"))


def read_text(system, job):
    if system == "greenhouse":
        return "content", _clean(strip_html(job.get("content")))
    text = _clean(strip_html(job.get("descriptionHtml"))) or _clean(strip_html(job.get("descriptionPlain")))
    return "descriptionHtml/descriptionPlain", text


def make_posting(system, board, job, board_status="ok", source=None):
    title_field, title = read_title(system, job)
    location_field, location = read_location(system, job)
    text_field, text = read_text(system, job)
    return {
        "posting_id": f"{system}:{board}:{job.get('id')}",
        "system": system,
        "board": board,
        "board_status": board_status,
        "title": title, "title_field": title_field,
        "location": location, "location_field": location_field,
        "text": text, "text_field": text_field,
        "url": job.get("absolute_url") or job.get("jobUrl"),
        "source": source,
    }


def location_parts(location):
    return [p.strip() for p in (location or "").split(";") if p.strip()]


def is_us_part(part):
    if any(part.endswith(code) for code in STATE_ENDINGS):
        return True
    return bool(REMOTE.search(part) and US_MARKER.search(part))


def us_part(location):
    return next((p for p in location_parts(location) if is_us_part(p)), None)


def skills_in(text, skills):
    return [s for s in skills if find_term(text, s)]


def evaluate(posting, skills):
    text = posting["text"]
    result = {"posting_id": posting["posting_id"], "verdict": None, "abstain": False, "rule": None,
              "field": None, "reason": None, "skills_found": [], "text_chars": len(text or "")}

    def done(verdict, rule=None, field=None, reason=None):
        result.update(verdict=verdict, rule=rule, field=field, reason=reason, abstain=verdict == "abstain")
        return result

    if posting["board_status"] == "unverified-empty":
        return done("abstain", "ABSTAIN", None,
                    f"{ABSTAIN} (board {posting['system']}:{posting['board']} is unverified-empty)")
    if text is not None and len(text) < MIN_TEXT_CHARS:
        return done("abstain", "ABSTAIN", posting["text_field"],
                    f"{ABSTAIN} (text is {len(text)} characters after removing HTML, under {MIN_TEXT_CHARS})")

    tf, title = posting["title_field"], posting["title"]
    if title is None:
        return done("reject", "F1", tf, f"F1 [{tf}]: missing: {tf}")
    role = next((hit for hit in (find_term(title, w) for w in ROLE_WORDS) if hit), None)
    if not role:
        return done("reject", "F1", tf, f"F1 [{tf}]: no role word in {title!r}")
    excluded = next((hit for hit in (find_term(title, w) for w in EXCLUDE_WORDS) if hit), None)
    if excluded:
        return done("reject", "F2", tf, f"F2 [{tf}]: excluded word {excluded!r} in {title!r}")

    lf, location = posting["location_field"], posting["location"]
    if location is None:
        return done("reject", "F3", lf, f"F3 [{lf}]: missing: {lf}")
    if not us_part(location):
        return done("reject", "F3", lf, f"F3 [{lf}]: no US part in {location!r}")

    xf = posting["text_field"]
    if text is None:
        return done("reject", "F4", xf, f"F4 [{xf}]: missing: {xf}")
    found = skills_in(text, skills)
    result["skills_found"] = found
    if len(found) < MIN_SKILLS:
        return done("reject", "F4", xf, f"F4 [{xf}]: none of the {len(skills)} shipped skills named")
    return done("accept", None, None,
                f"accept: role word {role!r}, no excluded word, US part {us_part(location)!r}, "
                f"skills {', '.join(found)}")
