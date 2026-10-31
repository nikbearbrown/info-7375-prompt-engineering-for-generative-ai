"""Résumé loading. Refuses anything that is not a fictional persona."""

import json
from pathlib import Path


def load_resume(path):
    """Load a résumé JSON; raise ValueError unless email ends in @example.com and phone contains 555."""
    data = json.loads(Path(path).read_text())
    personal = data.get("personal") or {}
    email = personal.get("email") or ""
    phone = personal.get("phone") or ""
    if not email.lower().endswith("@example.com"):
        raise ValueError(f"refusing résumé {path}: email must end in @example.com")
    if "555" not in phone:
        raise ValueError(f"refusing résumé {path}: phone must contain 555")
    return data
