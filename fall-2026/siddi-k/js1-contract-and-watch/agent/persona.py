"""Persona validator (CONTRACT.md, In > Persona validator). Runs before anything is fetched."""
from __future__ import annotations

import json
import re
from pathlib import Path

PHONE_RE = re.compile(r"^\(555\) \d{3}-\d{4}$")
LIST_FIELDS = ("target_title_keywords", "title_exclusions", "skills", "preferred_cities")
FIELDS = ("name", "email", "phone", "education", "highest_degree", *LIST_FIELDS, "years_experience", "remote_ok")
DEGREES = ("bachelors", "masters", "phd")


class PersonaError(Exception):
    pass


def problems(persona, vocab: dict) -> list[str]:
    """Every rule the persona breaks; an empty list means it is valid."""
    if not isinstance(persona, dict):
        return ["persona is not a JSON object"]
    out = [f"missing field: {k}" for k in FIELDS if k not in persona]
    out += [f"extra field: {k}" for k in persona if k not in FIELDS]
    p = persona
    if "name" in p and not (isinstance(p["name"], str) and p["name"].strip()):
        out.append("name must be a non-empty string")
    if "email" in p and not (isinstance(p["email"], str) and p["email"].endswith("@example.com")):
        out.append("email must end in @example.com")
    if "phone" in p and not (isinstance(p["phone"], str) and PHONE_RE.match(p["phone"])):
        out.append("phone must match (555) ddd-dddd")
    if "education" in p and not isinstance(p["education"], str):
        out.append("education must be a string")
    if "highest_degree" in p and p["highest_degree"] not in DEGREES:
        out.append(f"highest_degree must be one of {', '.join(DEGREES)}")
    for k in LIST_FIELDS:
        v = p.get(k)
        if k in p and not (isinstance(v, list) and v and all(isinstance(s, str) and s and s == s.lower() for s in v)):
            out.append(f"{k} must be a non-empty list of lowercase strings")
    y = p.get("years_experience")
    if "years_experience" in p and not (type(y) is int and 0 <= y <= 40):
        out.append("years_experience must be an integer from 0 to 40")
    if "remote_ok" in p and not isinstance(p["remote_ok"], bool):
        out.append("remote_ok must be a boolean")
    if isinstance(p.get("skills"), list):
        out += [f"skill not in skill_vocab.json: {s}" for s in p["skills"] if s not in vocab]
    return out


def load(path: Path, vocab: dict) -> dict:
    persona = json.loads(path.read_text(encoding="utf-8"))
    bad = problems(persona, vocab)
    if bad:
        raise PersonaError(f"{path.name} failed the persona validator: " + "; ".join(bad))
    return persona
