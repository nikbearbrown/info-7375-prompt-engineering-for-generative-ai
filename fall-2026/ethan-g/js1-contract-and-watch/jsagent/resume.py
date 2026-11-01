"""Load and validate a fictional résumé; resolve cited field paths."""
import copy
import json
import re
from pathlib import Path

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
FAKE_PHONE_RE = re.compile(r"\b555-\d{4}\b")
NOT_COUNTED_SKILLS = "familiar_with_not_shipped"


class ResumeRefused(Exception):
    pass


def skill_groups(r):
    """Skill lists R4 counts, in file order: every list under `skills` except familiar_with_not_shipped."""
    return [g for g, v in r["skills"].items() if g != NOT_COUNTED_SKILLS and isinstance(v, list)]


def _strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v)


def _str_list(value):
    return isinstance(value, list) and all(isinstance(x, str) for x in value)


def validate_resume(r):
    """Return a list of problems; empty means the résumé may be used."""
    errors = []
    if not isinstance(r, dict):
        return ["résumé is not a JSON object"]
    if "FICTIONAL" not in str(r.get("_comment", "")):
        errors.append("_comment must mark the résumé FICTIONAL")
    personal = r.get("personal") or {}
    for key in ["name", "location", "email", "phone"]:
        if not isinstance(personal.get(key), str) or not personal.get(key):
            errors.append(f"personal.{key} is required")
    if not str(personal.get("email", "")).endswith("@example.com"):
        errors.append("personal.email must end in @example.com")
    if not FAKE_PHONE_RE.search(str(personal.get("phone", ""))):
        errors.append("personal.phone must be a 555- number")
    for s in _strings(r):
        for email in EMAIL_RE.findall(s):
            if not email.endswith("@example.com"):
                errors.append(f"non-example email found in résumé: {email[:3]}…")
    for key in ["education", "experience"]:
        if not isinstance(r.get(key), list):
            errors.append(f"{key} must be a list")
    skills = r.get("skills")
    if not isinstance(skills, dict) or not any(_str_list(v) and v for k, v in skills.items() if k != NOT_COUNTED_SKILLS):
        errors.append("skills must be an object with at least one non-empty list of strings")
    else:
        for g, v in skills.items():
            if not _str_list(v):
                errors.append(f"skills.{g} must be a list of strings")
    search = r.get("search") or {}
    if not _str_list(search.get("target_titles")) or not search.get("target_titles"):
        errors.append("search.target_titles must be a non-empty list of strings")
    if not _str_list(search.get("excluded_title_terms")):
        errors.append("search.excluded_title_terms must be a list of strings")
    locs = search.get("locations")
    if not _str_list(locs) or not locs or not all("," in x for x in locs):
        errors.append('search.locations must be a non-empty list of "City, ST" strings')
    if not isinstance(search.get("open_to_remote"), bool):
        errors.append("search.open_to_remote must be true or false")
    if not isinstance(search.get("open_to_relocate"), bool):
        errors.append("search.open_to_relocate must be true or false")
    if not _str_list(search.get("us_location_markers")) or not search.get("us_location_markers"):
        errors.append("search.us_location_markers must be a non-empty list of strings")
    for key in ["max_required_years", "preferred_max_years"]:
        if not isinstance(search.get(key), int) or isinstance(search.get(key), bool):
            errors.append(f"search.{key} must be an integer")
    return errors


def load_resume(path):
    r = json.loads(Path(path).read_text())
    errors = validate_resume(r)
    if errors:
        raise ResumeRefused("refusing résumé: " + "; ".join(errors))
    return r


_SEG = r"[A-Za-z_][A-Za-z0-9_]*(?:\[\d+\])*"
_PATH_RE = re.compile(rf"^{_SEG}(?:\.{_SEG})*$")
_TOKEN = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)|\[(\d+)\]")


def resolve(r, path):
    """Resolve a dotted path like 'education[0].degree'. Raises KeyError if absent or malformed."""
    if not isinstance(path, str) or not _PATH_RE.match(path):
        raise KeyError(path)
    cur = r
    for name, index in _TOKEN.findall(path):
        if name:
            if not isinstance(cur, dict) or name not in cur:
                raise KeyError(path)
            cur = cur[name]
        else:
            i = int(index)
            if not isinstance(cur, list) or i >= len(cur):
                raise KeyError(path)
            cur = cur[i]
    return cur


def redact_for_model(r):
    """Copy safe to send to a model: no name or contact fields, location kept."""
    red = copy.deepcopy(r)
    red.pop("_comment", None)
    for k in ["attested", "attested_date", "attestation_note"]:
        red.pop(k, None)
    red["personal"] = {"location": r["personal"]["location"]}
    return red
