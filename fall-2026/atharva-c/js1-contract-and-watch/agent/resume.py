"""Résumé loading and validation. CONTRACT.md > In, and Refuses (persona only)."""
import json
from pathlib import Path

# Skill lists that count toward the rule; familiar_with_not_shipped is excluded.
EXCLUDED_SKILL_LISTS = {"familiar_with_not_shipped"}


class ResumeError(Exception):
    pass


def load(path):
    path = Path(path)
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        raise ResumeError(f"cannot read résumé {path}: {e}") from e
    if not isinstance(data, dict):
        raise ResumeError("résumé must be a JSON object")

    personal = data.get("personal")
    if not isinstance(personal, dict):
        raise ResumeError("résumé.personal is missing or not an object")
    loc = personal.get("location")
    if not isinstance(loc, str) or not loc.strip():
        raise ResumeError("résumé.personal.location is required")

    # Persona check: the agent only runs on a fictional résumé.
    email = personal.get("email", "")
    phone = personal.get("phone", "")
    if not (isinstance(email, str) and email.endswith("@example.com")):
        raise ResumeError("refusing résumé: personal.email must be an @example.com address (fictional persona only)")
    if phone and "555" not in str(phone):
        raise ResumeError("refusing résumé: personal.phone must be a 555 number (fictional persona only)")

    skills = data.get("skills")
    if skills is not None and not isinstance(skills, dict):
        raise ResumeError("résumé.skills must be an object of lists")
    return data


def counted_skills(data):
    """[(list_name, skill)] for every skill that counts toward the rule."""
    out = []
    for name, items in (data.get("skills") or {}).items():
        if name in EXCLUDED_SKILL_LISTS or not isinstance(items, list):
            continue
        out.extend((name, s) for s in items if isinstance(s, str) and s.strip())
    return out
