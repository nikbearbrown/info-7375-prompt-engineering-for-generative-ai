"""Load the fictional résumé and refuse identities that do not look fictional."""

import json
import re
from pathlib import Path

REQUIRED_FIELDS = ("name", "email", "phone", "target_titles", "skills", "locations")
FICTIONAL_PHONE = re.compile(r"555-\d{4}(?!\d)")


def load_resume(path) -> dict:
    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict):
        raise ValueError("résumé must be a JSON object")

    for field in REQUIRED_FIELDS:
        value = data.get(field)
        if value is None or (isinstance(value, (str, list, dict)) and not value):
            raise ValueError(f"résumé field {field!r} is missing or empty")
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"résumé field {field!r} is missing or empty")

    email = data["email"]
    if not isinstance(email, str) or not email.endswith("@example.com"):
        raise ValueError("résumé email must end with @example.com")

    phone = data["phone"]
    if not isinstance(phone, str) or not FICTIONAL_PHONE.search(phone):
        raise ValueError("résumé phone must contain 555- followed by exactly four digits")

    return data
