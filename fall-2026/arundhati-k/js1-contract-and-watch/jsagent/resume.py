"""Load the persona résumé and refuse anything that does not look fictional (CONTRACT §4.2)."""

import json
import re
from pathlib import Path


class NotFictional(Exception):
    """Raised when a résumé could be a real person's."""


def validate_persona(resume):
    personal = resume.get("personal", {})
    problems = []
    if "FICTIONAL" not in str(resume.get("_comment", "")).upper():
        problems.append("_comment does not mark the résumé FICTIONAL")
    if not str(personal.get("email", "")).endswith("@example.com"):
        problems.append("email is not an @example.com address")
    if not re.search(r"\b555-\d{4}\b", str(personal.get("phone", ""))):
        problems.append("phone is not a 555 number")
    skills = resume.get("skills")
    if not isinstance(skills, dict) or not any(isinstance(v, list) and v for v in skills.values()):
        problems.append("skills section missing or empty")
    if problems:
        raise NotFictional("refused résumé: " + "; ".join(problems))
    return resume


def load_resume(path):
    path = Path(path)
    if path.name == "resume.json":
        raise NotFictional("refused: resume.json is the private, never-committed name; use a *.example.json persona")
    return validate_persona(json.loads(path.read_text()))


def skill_fields(resume):
    """Map lower-cased skill -> (field path, exact skill string), e.g. 'java' -> ('skills.languages[2]', 'Java')."""
    out = {}
    for group, values in resume["skills"].items():
        if group == "familiar_with_not_shipped" or not isinstance(values, list):
            continue
        for i, value in enumerate(values):
            out.setdefault(value.lower(), (f"skills.{group}[{i}]", value))
    return out


def resolve_field(resume, field):
    """Return the value at a path like 'skills.languages[2]', or None."""
    m = re.fullmatch(r"skills\.([a-z_]+)\[(\d+)\]", field or "")
    if not m:
        return None
    values = resume.get("skills", {}).get(m.group(1))
    index = int(m.group(2))
    if not isinstance(values, list) or index >= len(values):
        return None
    return values[index]
