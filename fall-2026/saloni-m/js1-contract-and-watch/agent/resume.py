"""Résumé loading, validation, and field-path lookup (CONTRACT.md "In")."""
import json
import re


class ResumeError(ValueError):
    pass


def load_resume(path):
    with open(path, encoding="utf-8") as f:
        resume = json.load(f)
    validate_resume(resume)
    return resume


def validate_resume(resume):
    """Refuse anything that is not a fictional persona with a usable search block."""
    personal = resume.get("personal") or {}
    email = str(personal.get("email", ""))
    phone = str(personal.get("phone", ""))
    if not email.endswith("@example.com"):
        raise ResumeError("refused: personal.email must end in @example.com (fictional persona only)")
    if "555" not in phone:
        raise ResumeError("refused: personal.phone must be a 555 number (fictional persona only)")
    search = resume.get("search") or {}
    for key in ("title_keywords", "exclude_title_terms"):
        terms = search.get(key)
        if not isinstance(terms, list) or not terms or not all(isinstance(t, str) and t.strip() for t in terms):
            raise ResumeError(f"refused: search.{key} must be a non-empty list of strings")
    return True


_PART = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)(?:\[(\d+)\])?")


def resolve_field(resume, path):
    """Return the value at a dotted path like 'search.title_keywords[1]'; raise KeyError if absent."""
    node = resume
    for segment in path.split("."):
        m = _PART.fullmatch(segment)
        if not m:
            raise KeyError(path)
        key, index = m.group(1), m.group(2)
        if not isinstance(node, dict) or key not in node:
            raise KeyError(path)
        node = node[key]
        if index is not None:
            if not isinstance(node, list) or int(index) >= len(node):
                raise KeyError(path)
            node = node[int(index)]
    return node


def field_exists(resume, path):
    try:
        resolve_field(resume, path)
        return True
    except KeyError:
        return False
