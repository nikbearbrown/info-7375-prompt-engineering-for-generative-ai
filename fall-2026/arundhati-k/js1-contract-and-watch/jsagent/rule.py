"""The deterministic relevance rule, CONTRACT §5 — a record anyone can recompute.

Interpretations (CONTRACT §5 requires these to be documented; see README "How the rule reads a posting"):
  role      — the title (case-insensitive) contains "software engineer", "software developer",
              "backend/back-end engineer" or "full-stack/full stack/fullstack engineer" as whole words.
  level     — the title contains "intern", "internship", "co-op" or "new grad"/"new graduate" as whole
              words. Only the title is read; "Early Career" is not on the contract's list, so it fails.
  location  — the posting's location.name contains a US marker from US_MARKERS (whole words).
              "Remote", "AMER", "N/A" alone cannot be verified as US and fail.
  skills    — at least two of the ten contract skills appear (whole words) anywhere in the description
              text (HTML removed). The rule does not distinguish "required" from "preferred".
              "Go" counts as "Golang", or as capitalised "Go" that does not start a sentence.
"""

import html
import re

ROLE = re.compile(r"\b(software engineer|software developer|back-?end engineer|full[- ]?stack engineer)\b", re.I)
LEVEL = re.compile(r"\b(intern|internship|co-?op|new grad|new graduate)\b", re.I)
US_MARKERS = re.compile(
    r"\b(US|USA|U\.S\.|United States|San Francisco|SF|Seattle|SEA|New York|New-York|NYC|Chicago|CHI|Atlanta"
    r"|WA|CA|NY|IL)\b"
)

# The ten skills of CONTRACT §5, in contract order, with the pattern used to find each one.
RULE_SKILLS = {
    "Python": re.compile(r"\bpython\b", re.I),
    # "Golang" anywhere; "Go" only capitalised and NOT starting a sentence ("Go build…" is the verb).
    "Go": re.compile(r"\b[Gg]olang\b|(?<![.!?:]\s)(?<!^)\bGo\b"),
    "Java": re.compile(r"\bjava\b", re.I),
    "JavaScript": re.compile(r"\bjavascript\b", re.I),
    "SQL": re.compile(r"\bsql\b", re.I),
    "PostgreSQL": re.compile(r"\b(?:postgresql|postgres)\b", re.I),
    "AWS": re.compile(r"\b(?:aws|amazon web services)\b", re.I),
    "Docker": re.compile(r"\bdocker\b", re.I),
    "Kubernetes": re.compile(r"\b(?:kubernetes|k8s)\b", re.I),
    "Jenkins": re.compile(r"\bjenkins\b", re.I),
}
MIN_SKILLS = 2


def description_text(job):
    """Greenhouse double-escapes content: unescape, drop tags, unescape again, collapse whitespace."""
    text = html.unescape(job.get("content") or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def location_name(job):
    return ((job.get("location") or {}).get("name") or "").strip()


def departments(job):
    return [d["name"] for d in job.get("departments") or []]


def quote_around(text, match, width=50):
    start, end = max(0, match.start() - width), min(len(text), match.end() + width)
    return text[start:end].strip()


def judge(job, resume_skills):
    """Return the rule record for one posting. resume_skills comes from resume.skill_fields()."""
    title = job["title"]
    loc = location_name(job)
    text = description_text(job)

    role = ROLE.search(title)
    level = LEVEL.search(title)
    us = US_MARKERS.search(loc)

    matches = []
    for skill, pattern in RULE_SKILLS.items():
        if skill.lower() not in resume_skills:
            continue  # never cite a skill the résumé does not have (CONTRACT §4.9)
        found = pattern.search(text)
        if found:
            resume_field, resume_value = resume_skills[skill.lower()]
            matches.append({
                "skill": skill,
                "resume_field": resume_field,
                "resume_value": resume_value,
                "posting_field": "content",
                "posting_quote": quote_around(text, found),
            })

    conditions = {
        "role": {"passed": bool(role), "posting_field": "title", "value": title,
                 "matched": role.group(0) if role else None},
        "level": {"passed": bool(level), "posting_field": "title", "value": title,
                  "matched": level.group(0) if level else None},
        "location": {"passed": bool(us), "posting_field": "location.name", "value": loc,
                     "matched": us.group(0) if us else None},
        "skills": {"passed": len(matches) >= MIN_SKILLS, "posting_field": "content",
                   "count": len(matches), "matches": matches},
    }
    verdict = "RELEVANT" if all(c["passed"] for c in conditions.values()) else "NOT RELEVANT"
    return {
        "posting_id": str(job["id"]),
        "title": title,
        "verdict": verdict,
        "conditions": conditions,
        "justification": justification(verdict, conditions),
    }


def justification(verdict, c):
    parts = [
        f"role {'met' if c['role']['passed'] else 'NOT met'} (title={c['role']['value']!r})",
        f"level {'met' if c['level']['passed'] else 'NOT met'}"
        + (f" (title contains {c['level']['matched']!r})" if c['level']['passed'] else " (title names no intern/co-op/new-grad term)"),
        f"US location {'met' if c['location']['passed'] else 'NOT met'} (location.name={c['location']['value']!r})",
    ]
    skill_bits = "; ".join(f"{m['resume_field']}={m['resume_value']!r} ↔ content: \"…{m['posting_quote']}…\"" for m in c["skills"]["matches"])
    parts.append(f"skills {c['skills']['count']}/{MIN_SKILLS} needed" + (f": {skill_bits}" if skill_bits else ""))
    return f"{verdict} — " + " · ".join(parts)
