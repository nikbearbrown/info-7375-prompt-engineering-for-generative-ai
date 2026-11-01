"""Persona loader. Refuses to run unless every email is @example.com and every phone contains 555."""

import json
import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\(?\d{3}\)?[\s.-]?\d{3}[\s.-]\d{4}")


class PersonaRefused(Exception):
    pass


def _strings(obj, path="$"):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from _strings(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from _strings(value, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def problems(doc):
    found = []
    for path, text in _strings(doc):
        for email in EMAIL_RE.findall(text):
            if not email.lower().endswith("@example.com"):
                found.append(f"{path}: email {email!r} is not @example.com")
        phones = PHONE_RE.findall(text)
        if path.rsplit(".", 1)[-1].lower() == "phone" and text and not phones:
            phones = [text]
        for phone in phones:
            if "555" not in phone:
                found.append(f"{path}: phone {phone!r} does not contain 555")
    return found


def validate(*docs):
    found = [p for doc in docs for p in problems(doc)]
    if found:
        raise PersonaRefused("refusing to run on a non-fictional persona:\n  " + "\n  ".join(found))


def load_persona(resume_path, profile_path):
    with open(resume_path, encoding="utf-8") as f:
        resume = json.load(f)
    with open(profile_path, encoding="utf-8") as f:
        profile = json.load(f)
    validate(resume, profile)
    return resume, profile
