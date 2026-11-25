"""The written rule from CONTRACT.md, as code. Its verdicts are records:
anyone can recompute them from the posting and the résumé.

The five checks are always all computed (no short-circuit), so every
justification lists every check, whether it passed, and what it matched.
"""

import html
import re

GOOD_TITLE_WORDS = ["AI", "Machine Learning", "ML", "Software Engineer",
                    "Intern", "New Grad", "Early Career"]
BAD_TITLE_WORDS = ["Senior", "Sr", "Staff", "Principal", "Distinguished",
                   "Manager", "Director", "Lead", "Sales", "PhD",
                   "Research Scientist"]
US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
    "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
    "Washington", "West Virginia", "Wisconsin", "Wyoming"]
# Rule v2 (2026-10-30): Databricks writes "San Francisco, California" with no
# "USA", so a US state name or D.C. also marks a location part as US.
US_MARKERS = ["USA", "United States", "D.C."] + US_STATES
SKILL_FIELDS = ["skills.languages", "skills.data_bi",
                "skills.backend_automation", "skills.database_cloud"]
MIN_SKILLS = 2
NO_SPONSOR_PHRASES = ["unable to sponsor", "not able to sponsor",
                      "cannot sponsor", "can't sponsor", "will not sponsor",
                      "does not sponsor", "do not sponsor",
                      "without sponsorship", "no sponsorship",
                      "sponsorship is not available"]


def _pattern(term):
    # Whole words only, ignoring case; a space in the term matches any run
    # of whitespace. (?<!\w) / (?!\w) instead of \b so terms that end in
    # punctuation still behave.
    body = r"\s+".join(re.escape(part) for part in term.split())
    return re.compile(r"(?<!\w)" + body + r"(?!\w)", re.IGNORECASE)


def find_terms(text, terms):
    """Return the terms (in list order) that occur in text as whole words."""
    text = text.replace("’", "'")  # curly apostrophe in "can’t"
    return [t for t in terms if _pattern(t).search(text)]


def description_text(posting):
    """The posting's `content`, HTML-unescaped with tags removed.

    Greenhouse escapes its HTML (&lt;p&gt;), so unescape once to get the HTML,
    drop the tags, then unescape again for entities like &nbsp;."""
    raw = html.unescape(posting.get("content") or "")
    no_tags = re.sub(r"<[^>]+>", " ", raw)
    return " ".join(html.unescape(no_tags).split())


def resume_skills(resume):
    """(field, skill) pairs from the four counted résumé fields, de-duplicated
    case-insensitively. familiar_with_not_shipped is deliberately excluded."""
    seen, out = set(), []
    for field in SKILL_FIELDS:
        for skill in resume.get("skills", {}).get(field.split(".", 1)[1], []):
            if skill.lower() not in seen:
                seen.add(skill.lower())
                out.append((field, skill))
    return out


def judge(posting, resume):
    """Apply the five checks. Returns a dict with posting_id, verdict and a
    justification: one entry per check citing its fields and matches."""
    title = posting.get("title") or ""
    location = (posting.get("location") or {}).get("name") or ""
    text = description_text(posting)

    good = find_terms(title, GOOD_TITLE_WORDS)
    bad = find_terms(title, BAD_TITLE_WORDS)
    us_parts = [p.strip() for p in location.split(";")
                if find_terms(p, US_MARKERS)]
    skills = resume_skills(resume)
    matched = [(f, s) for f, s in skills if find_terms(text, [s])]
    needs_sponsor = bool(resume.get("work_authorization", {})
                         .get("needs_sponsorship"))
    no_sponsor = find_terms(text, NO_SPONSOR_PHRASES) if needs_sponsor else []

    checks = [
        {"check": "good_title", "passed": bool(good),
         "posting_fields": ["title"], "resume_fields": [],
         "matched": good},
        {"check": "no_bad_title_word", "passed": not bad,
         "posting_fields": ["title"], "resume_fields": [],
         "matched": bad},
        {"check": "us_location", "passed": bool(us_parts),
         "posting_fields": ["location.name"], "resume_fields": [],
         "matched": us_parts},
        {"check": "at_least_2_skills", "passed": len(matched) >= MIN_SKILLS,
         "posting_fields": ["content"],
         "resume_fields": sorted({f for f, _ in matched}) or SKILL_FIELDS,
         "matched": [s for _, s in matched]},
        {"check": "no_cant_sponsor", "passed": not no_sponsor,
         "posting_fields": ["content"],
         "resume_fields": ["work_authorization.needs_sponsorship"],
         "matched": no_sponsor},
    ]
    return {
        "posting_id": posting["id"],
        "title": title,
        "location": location,
        "judge": "rule",
        "kind": "record",
        "verdict": "relevant" if all(c["passed"] for c in checks)
                   else "not_relevant",
        "justification": checks,
    }


def judge_all(postings, resume):
    """Verdicts keyed by posting id, so a verdict can never drift onto
    another posting by list position."""
    return {p["id"]: judge(p, resume) for p in postings}


def justification_cites_fields(verdict):
    """True if the justification names at least one posting field and one
    résumé field (wrong version 2 is a justification that cites nothing)."""
    checks = verdict.get("justification") or []
    posting = any(c.get("posting_fields") for c in checks)
    resume = any(c.get("resume_fields") for c in checks)
    return posting and resume
