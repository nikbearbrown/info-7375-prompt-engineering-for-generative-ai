"""Load and validate the persona résumé (CONTRACT.md, Refuses item 7).

Only the fictional persona is allowed: every email must end in @example.com and
every phone number must be a 555 number. The fields the rule and the Claude judge
may see are returned by `judge_view`; contact fields never leave this module.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

SKILL_LISTS_EXCLUDED = {"familiar_with_not_shipped", "agent_note"}


class ResumeInvalid(ValueError):
    """The résumé fails validation; the run must not judge anything."""


def validate(resume: dict) -> list:
    """Return a list of problems; an empty list means the résumé is valid."""
    problems = []
    if not isinstance(resume, dict):
        return ["résumé is not a JSON object"]
    personal = resume.get("personal")
    if not isinstance(personal, dict):
        problems.append("missing personal")
    else:
        email = str(personal.get("email", ""))
        if not email.endswith("@example.com"):
            problems.append("personal.email does not end in @example.com (real résumé?)")
        phone = str(personal.get("phone", ""))
        if phone and not re.search(r"\b555\b", phone):
            problems.append("personal.phone is not a 555 number (real résumé?)")
    exp = resume.get("experience")
    if not isinstance(exp, list) or not exp or not all(
        isinstance(e, dict) and str(e.get("title", "")).strip() for e in exp
    ):
        problems.append("experience missing, empty, or an entry has no title")
    skills = resume.get("skills")
    if not isinstance(skills, dict) or not any(
        isinstance(v, list) and v for k, v in skills.items() if k not in SKILL_LISTS_EXCLUDED
    ):
        problems.append("skills missing or empty")
    return problems


def load(path) -> dict:
    try:
        resume = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as e:
        raise ResumeInvalid(f"cannot read résumé JSON: {e}") from e
    problems = validate(resume)
    if problems:
        raise ResumeInvalid("; ".join(problems))
    return resume


def experience_titles(resume: dict) -> list:
    return [str(e["title"]).strip() for e in resume["experience"]]


def skills(resume: dict) -> list:
    """Every skill except the familiar_with_not_shipped list (CONTRACT.md, The rule, test 2)."""
    out = []
    for key, values in resume["skills"].items():
        if key in SKILL_LISTS_EXCLUDED or not isinstance(values, list):
            continue
        out.extend(str(v) for v in values)
    return out


def judge_view(resume: dict) -> dict:
    """The only résumé fields the judges see (CONTRACT.md, Refuses item 5)."""
    return {"experience[].title": experience_titles(resume), "skills": skills(resume)}
