"""The résumé validator (CONTRACT.md, In: Résumé; Refuses 2).

Only a fictional persona passes: "fictional": true, an @example.com email, a phone number from
555-0100 to 555-0199, and every field the rule reads present with the right type. The contact
fields (name, email, phone, links) are never printed and never sent to Claude.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

from .errors import BrokenInput, Refused

CONTACT_FIELDS = ("name", "email", "phone", "links")
MONTH = re.compile(r"\d{4}-(0[1-9]|1[0-2])")

# The fields the rule reads, with the type each must have (CONTRACT.md, In).
RULE_FIELDS = {
    "experience.full_time_years": "number",
    "work_authorization.needs_sponsorship": "bool",
    "work_authorization.us_person": "bool",
    "availability.earliest_full_time_start": "month",
    "preferences.employment_types": "nonempty_list",
    "preferences.regions": "list",
    "preferences.cities": "list",
    "preferences.remote_locations": "list",
    "preferences.title_includes": "nonempty_list",
    "preferences.title_excludes": "list",
}


PERSONA_PROBLEMS = ("it is not a JSON object", 'it is not marked "fictional": true', "name is missing",
                    "email does not end in @example.com", "phone is not a number from 555-0100 to 555-0199")


def load(path: Path) -> dict:
    """A valid fictional persona, or Refused (not a fictional persona) or BrokenInput (a field the rule reads is wrong).

    Messages name fields, never values, and never the file's name.
    """
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise BrokenInput(f"the résumé file could not be read as JSON ({type(exc).__name__})") from None
    problems = problems_with(data)
    persona = [p for p in problems if p in PERSONA_PROBLEMS]
    if persona:
        raise Refused("refused: the résumé file is not a fictional persona: " + "; ".join(persona))
    if problems:
        raise BrokenInput("the résumé file fails validation: " + "; ".join(problems))
    return data


def problems_with(data) -> list:
    """Every reason the résumé fails. The messages name fields, never their values."""
    if not isinstance(data, dict):
        return ["it is not a JSON object"]
    problems = []
    if data.get("fictional") is not True:
        problems.append('it is not marked "fictional": true')
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        problems.append("name is missing")
    email = data.get("email")
    if not isinstance(email, str) or not re.fullmatch(r"[^@\s]+@example\.com", email):
        problems.append("email does not end in @example.com")
    if not _fictional_phone(data.get("phone")):
        problems.append("phone is not a number from 555-0100 to 555-0199")
    links = data.get("links")
    if not isinstance(links, list) or not all(isinstance(link, str) for link in links):
        problems.append("links is not a list of strings")
    for dotted, kind in RULE_FIELDS.items():
        found, value = lookup(data, dotted)
        if not found:
            problems.append(f"{dotted} is missing")
        elif not _has_kind(value, kind):
            problems.append(f"{dotted} is not a {kind.replace('_', ' ')}")
    return problems


def _fictional_phone(phone) -> bool:
    if not isinstance(phone, str) or not re.fullmatch(r"[0-9()+.\- ]+", phone):
        return False
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return len(digits) == 10 and digits[3:6] == "555" and digits[6:8] == "01"


def _has_kind(value, kind: str) -> bool:
    if kind == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0
    if kind == "bool":
        return isinstance(value, bool)
    if kind == "month":
        return isinstance(value, str) and MONTH.fullmatch(value) is not None
    if kind in ("list", "nonempty_list"):
        ok = isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)
        return ok and (kind == "list" or len(value) > 0)
    raise ValueError(kind)


def lookup(data: dict, dotted: str):
    """(True, value) for a dotted path like "preferences.cities", or (False, None)."""
    value = data
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            return False, None
        value = value[part]
    return True, value


def for_claude(data: dict) -> dict:
    """The résumé as Claude may see it: everything except the contact fields."""
    return {key: copy.deepcopy(value) for key, value in data.items() if key not in CONTACT_FIELDS}


def field_paths(data) -> set:
    """Every field path in a JSON value: "skills", "skills.languages", "education[0].degree", ..."""
    paths = set()

    def walk(value, prefix):
        if isinstance(value, dict):
            for key, inner in value.items():
                path = f"{prefix}.{key}" if prefix else key
                paths.add(path)
                walk(inner, path)
        elif isinstance(value, list):
            for index, inner in enumerate(value):
                path = f"{prefix}[{index}]"
                paths.add(path)
                walk(inner, path)

    walk(data, "")
    return paths
