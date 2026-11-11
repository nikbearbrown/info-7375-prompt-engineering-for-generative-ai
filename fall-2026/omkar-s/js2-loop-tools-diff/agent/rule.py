"""The written rule from CONTRACT.md ("The rule"), as code. Its output is a RECORD:
anyone can recompute it by hand from the posting and the résumé.

  A. posting.title contains "Software Engineer"
  B. (v2, 2026-10-26) posting is in the US: Boston, or a "City, ST" US location backed by a
     United States office in posting.offices[], or a US remote location
  C. >= 2 distinct shipped skills appear as whole words in posting.content
relevant iff A and B and C.
"""
import html
import re

from .persona import shipped_skills

ROLE_PHRASE = "software engineer"
MIN_SKILLS = 2
_US = re.compile(r"(?<![A-Za-z])(US|USA|United States)(?![A-Za-z])", re.I)
US_STATES = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH "
                "NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())
_STATE_SUFFIX = re.compile(r",\s*([A-Z]{2})\s*$")


def clean_content(raw):
    """Greenhouse double-escapes HTML: unescape, strip tags, unescape again."""
    text = html.unescape(raw or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _skill_regex(skill):
    # Whole-word: no letter or digit may touch either end, so Java != JavaScript, SQL != PostgreSQL.
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(skill) + r"(?![A-Za-z0-9])", re.I)


def location_ok(location_name, offices=()):
    """Contract v2: any US location. A two-letter suffix is ambiguous ("Munich, DE" is Germany,
    not Delaware), so "City, ST" counts only when an office in posting.offices[] is in the
    United States. Boston and "Remote ... US" pass on location.name alone."""
    us_office = any(str((o or {}).get("location") or "").strip().endswith("United States") for o in offices or ())
    for part in (location_name or "").split(";"):
        p = part.strip()
        if "boston" in p.lower():
            return True, "Boston"
        if "remote" in p.lower() and _US.search(p):
            return True, "US remote"
        m = _STATE_SUFFIX.search(p)
        if m and m.group(1) in US_STATES and us_office:
            return True, f"US city ({p}; posting.offices[] has a United States office)"
    if any(_STATE_SUFFIX.search(p.strip()) for p in (location_name or "").split(";")) and not us_office:
        return False, "state-like suffix but no United States office in posting.offices[]"
    return False, "not a US location"


def judge(posting, resume):
    title = posting.get("title") or ""
    loc = (posting.get("location") or {}).get("name") or ""
    text = clean_content(posting.get("content"))

    a = ROLE_PHRASE in title.lower()
    b, b_why = location_ok(loc, posting.get("offices"))
    found = [(g, s) for g, s in shipped_skills(resume) if _skill_regex(s).search(text)]
    c = len({s.lower() for _, s in found}) >= MIN_SKILLS
    relevant = a and b and c

    exp_titles = "; ".join(e.get("title", "") for e in resume.get("experience", []))
    by_group = {}
    for g, s in found:
        by_group.setdefault(g, []).append(s)
    found_txt = " + ".join(f"resume.skills.{g}[{', '.join(v)}]" for g, v in by_group.items()) or "none"
    n_shipped = len(shipped_skills(resume))

    lines = [
        f'A role: posting.title="{title}" {"contains" if a else "does not contain"} "Software Engineer"'
        f" (resume.experience[].title: {exp_titles}) -> {'PASS' if a else 'FAIL'}",
        f'B location (US): posting.location.name="{loc}" vs resume.personal.location="{resume["personal"]["location"]}"'
        f" -> {'PASS' if b else 'FAIL'} ({b_why})",
        f"C skills: {found_txt} found in posting.content -> {len(found)} of {n_shipped}, need {MIN_SKILLS}"
        f" -> {'PASS' if c else 'FAIL'}",
        f"verdict: {'relevant' if relevant else 'not_relevant'}"
        f" (A {'PASS' if a else 'FAIL'}, B {'PASS' if b else 'FAIL'}, C {'PASS' if c else 'FAIL'})",
    ]
    return {
        "kind": "record",
        "verdict": "relevant" if relevant else "not_relevant",
        "clauses": {
            "A": {"pass": a, "posting_field": "title", "value": title},
            "B": {"pass": b, "posting_field": "location.name", "value": loc,
                  "resume_field": "personal.location"},
            "C": {"pass": c, "posting_field": "content", "found": [s for _, s in found],
                  "resume_fields": sorted({f"skills.{g}" for g, _ in found})},
        },
        "justification": lines,
    }
