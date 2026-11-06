"""Persona résumé check (CONTRACT.md §1 item 2, §3.2).

Reasons name fields only, never their values, so a real résumé loaded by
mistake is not echoed to the screen or logs (§3.2).
"""

import json
import re
from pathlib import Path

from .errors import Refusal, RunError

REQUIRED_STRINGS = ("name", "email", "phone")
# (field, minimum number of distinct entries)
REQUIRED_LISTS = (("target_titles", 1), ("skills", 2), ("locations", 1))
FICTIONAL_EMAIL_SUFFIX = "@example.com"
# §3.2 (v0.3): contains 555-01 plus two digits; an area code may come first.
FICTIONAL_PHONE = re.compile(r"555-01[0-9]{2}")


def load_persona(path):
    path = Path(path)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RunError(f"cannot read résumé {path.name}: {type(exc).__name__}") from exc


def persona_refusal_reasons(persona):
    """Every reason the agent refuses to run with this résumé. Empty means it runs."""
    if not isinstance(persona, dict):
        return ["résumé is not a JSON object"]
    reasons = []
    for field in REQUIRED_STRINGS:
        value = persona.get(field)
        if not isinstance(value, str) or not value.strip():
            reasons.append(f"{field}: missing or empty")
    for field, minimum in REQUIRED_LISTS:
        value = persona.get(field)
        if not isinstance(value, list):
            reasons.append(f"{field}: missing or not a list")
            continue
        # An empty entry is a substring of every text, so it would make its condition always true.
        if not all(isinstance(entry, str) and entry.strip() for entry in value):
            reasons.append(f"{field}: every entry must be a non-empty string")
            continue
        distinct = len(set(value))
        if distinct < minimum:
            reasons.append(f"{field}: {distinct} distinct entries, minimum is {minimum}")
    years = persona.get("max_years_required")
    if isinstance(years, bool) or not isinstance(years, int):
        reasons.append("max_years_required: missing or not a whole number")
    email = persona.get("email")
    if isinstance(email, str) and email.strip() and not email.endswith(FICTIONAL_EMAIL_SUFFIX):
        reasons.append(f"email: does not end in {FICTIONAL_EMAIL_SUFFIX} (§3.2)")
    phone = persona.get("phone")
    if isinstance(phone, str) and phone.strip() and not FICTIONAL_PHONE.search(phone):
        reasons.append("phone: does not contain 555-01 plus two digits (§3.2)")
    return reasons


def check_persona(persona):
    """Refuse to run unless the résumé is a complete fictional persona."""
    reasons = persona_refusal_reasons(persona)
    if reasons:
        raise Refusal("résumé refused, no verdicts produced: " + "; ".join(reasons))
