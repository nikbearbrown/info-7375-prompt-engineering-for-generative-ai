"""CONTRACT.md R2 — the persona guard.

The agent refuses to load a resume that is not a validated fictional persona,
so that a real resume cannot end up on screen, in a run report, or in a commit
by accident. The guard is a refusal rather than a warning on purpose: a warning
would be read once and ignored afterwards.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .errors import NonPersonaResume

PHONE_RE = re.compile(r"^\+1-555-01\d\d$")

REQUIRED_FIELDS = (
    "schema_version",
    "persona",
    "name",
    "email",
    "phone",
    "title_block",
    "target_title_phrases",
    "target_job_families",
    "locations_ok",
    "remote_ok",
)

LIST_FIELDS = (
    "title_block",
    "target_title_phrases",
    "target_job_families",
    "locations_ok",
)


def validate(resume: dict) -> dict:
    missing = [f for f in REQUIRED_FIELDS if f not in resume]
    if missing:
        raise NonPersonaResume(f"resume is missing required fields: {missing}")
    if resume["persona"] is not True:
        raise NonPersonaResume('resume is not marked "persona": true')
    email = resume["email"]
    if not isinstance(email, str) or not email.casefold().endswith("@example.com"):
        raise NonPersonaResume("persona email must end in @example.com")
    if not isinstance(resume["phone"], str) or not PHONE_RE.match(resume["phone"]):
        raise NonPersonaResume("persona phone must match +1-555-01NN")
    for field in LIST_FIELDS:
        value = resume[field]
        if not isinstance(value, list) or not value:
            raise NonPersonaResume(f"{field} must be a non-empty list")
        for item in value:
            if not isinstance(item, str):
                raise NonPersonaResume(f"{field} must contain only strings")
            if item != item.casefold():
                raise NonPersonaResume(
                    f"{field} entry {item!r} must already be lower-case "
                    "(the rule does not case-fold the resume for you)"
                )
    if not isinstance(resume["remote_ok"], bool):
        raise NonPersonaResume("remote_ok must be a boolean")
    return resume


def load(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate(data)


def public_summary(resume: dict) -> dict:
    """What the agent is allowed to print about the resume: shapes, not content.

    R2 forbids showing a resume on screen. Even for the persona, the agent
    prints only the field names and sizes, so that pointing it at a real
    resume by mistake cannot leak one.
    """
    return {
        "schema_version": resume["schema_version"],
        "persona": resume["persona"],
        "title_block_count": len(resume["title_block"]),
        "target_title_phrases_count": len(resume["target_title_phrases"]),
        "target_job_families_count": len(resume["target_job_families"]),
        "locations_ok_count": len(resume["locations_ok"]),
        "remote_ok": resume["remote_ok"],
    }
