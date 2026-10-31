"""Validate the fictional persona résumé before any run (CONTRACT.md: In)."""
import json

REQUIRED_TARGETS = ("titles", "excluded_seniority", "max_required_years", "degree", "work_authorization")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate(resume):
    """Return a list of problems; an empty list means the persona may be used."""
    errors = []
    if resume.get("_fictional") is not True:
        errors.append('"_fictional" must be true: only a fictional persona may be used')
    basics = resume.get("basics") or {}
    if not str(basics.get("name", "")).strip():
        errors.append("basics.name is missing")
    if not str(basics.get("email", "")).endswith("@example.com"):
        errors.append("basics.email must be an @example.com address")
    if "555" not in str(basics.get("phone", "")):
        errors.append("basics.phone must be a 555 number")
    targets = resume.get("targets") or {}
    for key in REQUIRED_TARGETS:
        if key not in targets:
            errors.append(f"targets.{key} is missing")
    titles = targets.get("titles")
    if not (isinstance(titles, list) and titles and all(isinstance(t, str) and t.strip() for t in titles)):
        errors.append("targets.titles must be a non-empty list of strings")
    if not isinstance(targets.get("max_required_years"), int):
        errors.append("targets.max_required_years must be an integer")
    if not resume.get("education"):
        errors.append("education is missing")
    return errors
