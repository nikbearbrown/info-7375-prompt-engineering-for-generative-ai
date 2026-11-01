"""Loads and checks résumé, profile and the two built-in word lists before anything else runs.

Inputs are checked up front so a bad file stops the run before the board is fetched or the state
moves: otherwise the new postings of that run would be marked seen without ever being judged
(CONTRACT In: "missing or broken -> report and stop, name the missing field").
"""

import json
from pathlib import Path

from .common.errors import InputError
from .common.paths import Paths
from .judges.checks import Criteria

REQUIRED_PROFILE_LISTS = ("target_roles", "exclude_title_words", "locations")


def load_criteria(resume_path: Path, profile_path: Path, paths: Paths) -> Criteria:
    """Everything the judges need from the job seeker's side, loaded and checked in one call."""
    resume = load_resume(resume_path)
    profile = load_profile(profile_path)
    return Criteria(
        resume_keywords=resume_keywords(resume),
        profile=profile,
        aliases=load_aliases(paths.skill_aliases, profile),
        phrases=load_phrases(paths.no_sponsorship_phrases),
        resume=resume,
    )


def _load_json(path: Path, label: str):
    if not path.exists():
        raise InputError(f"{label} file not found: {path}")
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise InputError(f"{label} file is not valid JSON: {path} ({e})") from e


def load_resume(path: Path) -> dict:
    r = _load_json(path, "resume")
    basics = r.get("basics") if isinstance(r, dict) else None
    if not isinstance(basics, dict):
        raise InputError("missing resume.basics")
    for key in ("name", "email", "phone"):
        if not basics.get(key):
            raise InputError(f"missing resume.basics.{key}")
    if not isinstance(basics.get("profiles"), list):
        raise InputError("missing resume.basics.profiles")
    for key in ("work", "projects"):
        if not isinstance(r.get(key), list):
            raise InputError(f"missing resume.{key}")
    skills = r.get("skills")
    if not isinstance(skills, list) or not any(isinstance(s, dict) and s.get("keywords") for s in skills):
        raise InputError("missing resume.skills[].keywords")
    # CONTRACT Refuses: only fictional personas are allowed into this tool at the JS1 stage, so a
    # real résumé can't reach the screen or GitHub by accident. A later layer must replace this guard
    # for real users (01-action-plan P1 note, 2026-10-31).
    if not basics["email"].lower().endswith("@example.com"):
        raise InputError("resume.basics.email must end with @example.com (fictional personas only)")
    return r


def resume_keywords(resume: dict) -> list[str]:
    return [k for s in resume["skills"] if isinstance(s, dict) for k in s.get("keywords", [])]


def load_profile(path: Path) -> dict:
    p = _load_json(path, "profile")
    if not isinstance(p, dict):
        raise InputError("profile must be a JSON object")
    for key in REQUIRED_PROFILE_LISTS:
        value = p.get(key)
        if not isinstance(value, list) or not value or not all(isinstance(v, str) for v in value):
            raise InputError(f"missing profile.{key} (needs at least one value)")
    for key in ("years_experience", "years_stretch", "min_salary"):
        if key in p and not isinstance(p[key], (int, float)):
            raise InputError(f"profile.{key} must be a number")
    if "needs_sponsorship" in p and not isinstance(p["needs_sponsorship"], bool):
        raise InputError("profile.needs_sponsorship must be true or false")
    if "skill_aliases" in p:
        _check_aliases(p["skill_aliases"], "profile.skill_aliases")
    return p


def _check_aliases(table, label: str) -> None:
    if not isinstance(table, dict) or not all(
        isinstance(k, str) and isinstance(v, list) and all(isinstance(a, str) for a in v) for k, v in table.items()
    ):
        raise InputError(f'{label} must look like {{"PostgreSQL": ["postgres"]}}')


def load_aliases(builtin_path: Path, profile: dict) -> dict[str, list[str]]:
    """Built-in table plus the user's own additions, merged per skill (D9). Keys are lowercased so
    "postgresql" in a profile adds to "PostgreSQL" in the built-in table."""
    builtin = _load_json(builtin_path, "skill aliases")
    _check_aliases(builtin, str(builtin_path))
    merged: dict[str, list[str]] = {}
    for table in (builtin, profile.get("skill_aliases", {})):
        for skill, aliases in table.items():
            bucket = merged.setdefault(skill.lower(), [])
            bucket.extend(a for a in aliases if a not in bucket)
    return merged


def load_phrases(path: Path) -> list[str]:
    phrases = _load_json(path, "no-sponsorship phrases")
    if not isinstance(phrases, list) or not phrases or not all(isinstance(x, str) for x in phrases):
        raise InputError(f"{path} must be a non-empty list of phrases")
    return phrases
