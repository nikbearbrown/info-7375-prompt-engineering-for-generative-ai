"""Load and validate the fictional résumé (CONTRACT.md, In, section 2)."""
from __future__ import annotations

import json
import re
from pathlib import Path

FIELDS = {
    "name": str,
    "email": str,
    "phone": str,
    "location": str,
    "target_titles": list,
    "skills": list,
    "preferred_locations": list,
    "experience_level": str,
}
EMAIL = re.compile(r"^[^@\s]+@example\.com$")
PHONE = re.compile(r"^\d{3}-555-01\d{2}$")


class PersonaError(ValueError):
    """The résumé is invalid; the run must stop before fetching or changing state."""


def validate_resume(data: object) -> dict:
    """Return the résumé unchanged if valid, else raise PersonaError listing every problem."""
    if not isinstance(data, dict):
        raise PersonaError("résumé must be a JSON object")
    problems = []
    missing = sorted(set(FIELDS) - set(data))
    unknown = sorted(set(data) - set(FIELDS))
    if missing:
        problems.append(f"missing fields: {missing}")
    if unknown:
        problems.append(f"unknown fields: {unknown}")
    for field, kind in FIELDS.items():
        if field not in data:
            continue
        value = data[field]
        if not isinstance(value, kind):
            problems.append(f"{field} must be {kind.__name__}, got {type(value).__name__}")
        elif kind is str and not value.strip():
            problems.append(f"{field} must not be empty")
        elif kind is list:
            if not value:
                problems.append(f"{field} must not be an empty list")
            for i, item in enumerate(value):
                if not isinstance(item, str) or not item.strip():
                    problems.append(f"{field}[{i}] must be a nonempty string")
    if isinstance(data.get("email"), str) and data["email"].strip() and not EMAIL.match(data["email"]):
        problems.append("email must be a fictional @example.com address")
    if isinstance(data.get("phone"), str) and data["phone"].strip() and not PHONE.match(data["phone"]):
        problems.append("phone must follow the fictional NNN-555-01NN pattern")
    if problems:
        raise PersonaError("; ".join(problems))
    return data


def load_resume(path: Path) -> dict:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PersonaError(f"résumé file not found: {path}") from None
    except json.JSONDecodeError as exc:
        raise PersonaError(f"résumé is not valid JSON: {exc}") from None
    return validate_resume(data)
