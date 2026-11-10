"""Résumé loading and validation (CONTRACT.md §1 In, revision R3)."""
import json
import re

from .rules import SKILL_FIELDS

EMAIL_RE = re.compile(r"^[^@\s]+@([^@\s]+)$")
FICTIONAL_PHONE_RE = re.compile(r"^\(\d{3}\) 555-\d{4}$")


class ResumeError(ValueError):
    pass


def validate_resume(resume):
    """Raise ResumeError unless the résumé meets §1 and the R3 fictional-contact guard.

    R3 is an accidental-input safeguard only; it cannot prove a résumé is fictional.
    """
    if not isinstance(resume, dict):
        raise ResumeError("résumé must be a JSON object")
    skills = resume.get("skills")
    if not isinstance(skills, dict):
        raise ResumeError("résumé.skills must be an object")
    any_skill = False
    for path in SKILL_FIELDS:
        key = path.split(".", 1)[1]
        value = skills.get(key)
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise ResumeError(f"{path} must be an array of strings")
        any_skill = any_skill or any(x.strip() for x in value)
    if not any_skill:
        raise ResumeError(f"at least one of {', '.join(SKILL_FIELDS)} must contain a nonempty skill")

    personal = resume.get("personal")
    if not isinstance(personal, dict):
        raise ResumeError("refused: personal contact block missing; cannot confirm fictional persona (R3)")
    email, phone = personal.get("email"), personal.get("phone")
    match = EMAIL_RE.match(email) if isinstance(email, str) else None
    if not match:
        raise ResumeError("refused: personal.email missing or malformed (R3)")
    if match.group(1).lower() != "example.com":
        # Never echo the address itself: it might be real.
        raise ResumeError("refused: personal.email domain is not example.com; this may be a real résumé (R3)")
    if not isinstance(phone, str) or not FICTIONAL_PHONE_RE.match(phone):
        raise ResumeError("refused: personal.phone missing or not the fictional '(NNN) 555-NNNN' pattern (R3)")
    return resume


def load_resume(path):
    try:
        with open(path, encoding="utf-8") as f:
            resume = json.load(f)
    except FileNotFoundError:
        raise ResumeError(f"résumé file not found: {path}") from None
    except json.JSONDecodeError as e:
        raise ResumeError(f"résumé is not valid JSON ({e.msg} at line {e.lineno})") from None
    return validate_resume(resume)
