"""Load and validate the persona résumé (CONTRACT.md: In, Refuses (2)).

Error messages name the field that failed, never its value, so a real
résumé passed by mistake is not echoed to the screen.
"""
import json
import re
from pathlib import Path

FIELDS = {
    "name": str,
    "email": str,
    "phone": str,
    "target_titles": list,
    "skills": list,
    "seniority": str,
    "locations": list,
    "education": list,
    "experience": list,
    "needs_sponsorship": bool,
}
IDENTITY_FIELDS = ("name", "email", "phone")


class ResumeRejected(Exception):
    pass


def is_555_phone(phone: str) -> bool:
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return digits[3:6] == "555"
    if len(digits) == 7:
        return digits[:3] == "555"
    return False


def validate_resume(d) -> list[str]:
    if not isinstance(d, dict):
        return ["résumé must be a JSON object"]
    problems = []
    for key, typ in FIELDS.items():
        if key not in d:
            problems.append(f"missing field: {key}")
        elif not isinstance(d[key], typ):
            problems.append(f"field {key} must be {typ.__name__}")
    for key in sorted(set(d) - set(FIELDS)):
        problems.append(f"unexpected field: {key}")
    if problems:
        return problems
    if not d["email"].lower().endswith("@example.com"):
        problems.append("email does not end in @example.com")
    if not is_555_phone(d["phone"]):
        problems.append("phone is not a 555 number")
    for key in ("target_titles", "skills"):
        if not d[key] or not all(isinstance(x, str) and x.strip() for x in d[key]):
            problems.append(f"field {key} must be a non-empty list of strings")
    return problems


def load_resume(path: Path) -> dict:
    """Return the résumé, or raise ResumeRejected (the agent then stops)."""
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ResumeRejected([f"cannot read résumé JSON: {type(e).__name__}"])
    problems = validate_resume(d)
    if problems:
        raise ResumeRejected(problems)
    return d
