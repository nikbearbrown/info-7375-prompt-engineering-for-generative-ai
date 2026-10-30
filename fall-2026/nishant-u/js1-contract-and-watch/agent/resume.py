"""Refuse any résumé that is not a marked fictional persona (CONTRACT.md, Refuses)."""
import json
from pathlib import Path

MARKER = "FICTIONAL"
EMAIL_DOMAIN = "@example.com"


class RefusedResume(ValueError):
    pass


def check_resume(data):
    # The messages never echo résumé contents, so a refused real résumé is not printed.
    if not isinstance(data, dict):
        raise RefusedResume("résumé must be a JSON object")
    comment = data.get("_comment")
    if not isinstance(comment, str) or MARKER not in comment:
        raise RefusedResume(f"résumé _comment does not contain the {MARKER} marker")
    email = (data.get("personal") or {}).get("email")
    if not isinstance(email, str) or not email.lower().endswith(EMAIL_DOMAIN) or email.count("@") != 1:
        raise RefusedResume(f"résumé email is not an {EMAIL_DOMAIN} address")
    return data


def load_resume(path):
    return check_resume(json.loads(Path(path).read_text(encoding="utf-8")))
