"""Load and validate the résumé and target files.

Error messages name the failing field but never echo contact values.
"""

import json
from pathlib import Path

CONTACT_FIELDS = ("email", "phone", "linkedin", "github")
SKILL_GROUPS = ("languages", "data_bi", "backend_automation", "database_cloud")
NOT_COUNTED_GROUP = "familiar_with_not_shipped"


class ResumeInvalid(Exception):
    """Raised when the résumé fails the contract's acceptance checks."""


class TargetInvalid(Exception):
    """Raised when the target file is missing required keys."""


def _load_json(path, error):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise error(f"{path}: file not found") from None
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise error(f"{path}: not valid JSON ({exc.__class__.__name__})") from None


def validate_resume(data):
    """Raise ResumeInvalid unless data meets every contract check."""
    if not isinstance(data, dict):
        raise ResumeInvalid("résumé must be a JSON object")
    personal = data.get("personal")
    if not isinstance(personal, dict):
        raise ResumeInvalid("missing personal object")
    for field in ("name", "email", "phone"):
        value = personal.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ResumeInvalid(f"missing or empty personal.{field}")
    if not personal["email"].strip().lower().endswith("@example.com"):
        raise ResumeInvalid("personal.email must end in @example.com")
    if "555" not in personal["phone"]:
        raise ResumeInvalid("personal.phone must contain 555")
    skills = data.get("skills")
    if not isinstance(skills, dict) or not skills:
        raise ResumeInvalid("skills must be a non-empty object")
    for group in SKILL_GROUPS + (NOT_COUNTED_GROUP,):
        values = skills.get(group, [])
        if not isinstance(values, list) or not all(
                isinstance(v, str) and v.strip() for v in values):
            raise ResumeInvalid(f"skills.{group} must be a list of strings")
    return data


def load_resume(path):
    return validate_resume(_load_json(path, ResumeInvalid))


def load_target(path):
    data = _load_json(path, TargetInvalid)
    for key in ("target_title_keywords", "excluded_terms"):
        values = data.get(key) if isinstance(data, dict) else None
        if not isinstance(values, list) or not all(
                isinstance(v, str) and v.strip() for v in values):
            raise TargetInvalid(f"target.{key} must be a list of strings")
    if not data["target_title_keywords"]:
        raise TargetInvalid("target.target_title_keywords must not be empty")
    return data


def contact_values(resume):
    """Return the contact strings that must never appear in any output."""
    personal = resume.get("personal", {})
    return [personal[f] for f in CONTACT_FIELDS
            if isinstance(personal.get(f), str) and personal[f].strip()]


def counted_skills(resume):
    """Return [(field_path, skill)] for the four groups that count."""
    skills = resume["skills"]
    return [(f"skills.{group}", skill)
            for group in SKILL_GROUPS for skill in skills.get(group, [])]
