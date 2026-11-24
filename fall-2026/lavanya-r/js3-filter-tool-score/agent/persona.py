"""Load the résumé JSON and refuse anything that looks like a real person."""

import json


class NotFictional(ValueError):
    pass


def validate(resume):
    """Return a list of problems; an empty list means the persona is usable."""
    problems = []
    personal = resume.get("personal")
    if not isinstance(personal, dict):
        return ["missing 'personal' object"]
    email = personal.get("email") or ""
    phone = personal.get("phone") or ""
    if not email.lower().endswith("@example.com"):
        problems.append("email is not @example.com")
    if "555" not in phone:
        problems.append("phone number has no 555")
    if not isinstance(resume.get("skills"), dict):
        problems.append("missing 'skills' object")
    return problems


def load(path):
    with open(path, encoding="utf-8") as f:
        resume = json.load(f)
    problems = validate(resume)
    if problems:
        raise NotFictional(f"{path}: refusing a résumé that may be real: "
                           + "; ".join(problems))
    return resume
