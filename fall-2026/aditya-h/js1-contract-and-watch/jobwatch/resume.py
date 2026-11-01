"""Résumé validation and the persona guard (CONTRACT: In, Refuses 2)."""
import re

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")


class ResumeError(Exception):
    pass


def validate_resume(r):
    errors = []
    personal = r.get("personal") if isinstance(r, dict) else None
    if not isinstance(personal, dict):
        return ["personal: missing"]
    for key in ("name", "location", "email", "phone"):
        if not isinstance(personal.get(key), str) or not personal[key].strip():
            errors.append(f"personal.{key}: missing or empty")
    exp = r.get("experience")
    if not isinstance(exp, list) or not exp:
        errors.append("experience: missing or empty")
    else:
        for i, e in enumerate(exp):
            for key in ("title", "company"):
                if not isinstance(e, dict) or not isinstance(e.get(key), str) or not e[key].strip():
                    errors.append(f"experience[{i}].{key}: missing or empty")
    if not isinstance(r.get("skills"), dict):
        errors.append("skills: missing (must be an object)")
    return errors


def _walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{path}[{i}]")
    else:
        yield path, obj


def persona_guard(r):
    """Return problems that suggest a real résumé: non-example.com emails or non-555 phones."""
    problems = []
    for path, value in _walk(r):
        if not isinstance(value, str):
            continue
        leaf = path.rsplit(".", 1)[-1]
        for email in (m.group(0) for m in _EMAIL.finditer(value)):
            if not email.lower().endswith("@example.com"):
                problems.append(f"{path}: email not @example.com")
        if leaf == "phone" and "555" not in value:
            problems.append(f"{path}: phone does not contain 555")
    return problems


def load_checked(data):
    errors = validate_resume(data) + persona_guard(data)
    if errors:
        raise ResumeError("résumé refused: " + "; ".join(errors))
    return data
