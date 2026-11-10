"""Persona guard, adapted from JS1 jobwatch/resume.py: refuse anything that looks like a real résumé."""
import re

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")


def problems(r):
    out = []
    if not isinstance(r, dict) or not isinstance(r.get("personal"), dict) or not r.get("experience"):
        return ["résumé missing personal/experience"]

    def walk(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                yield from walk(v, f"{path}.{k}" if path else k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                yield from walk(v, f"{path}[{i}]")
        else:
            yield path, o

    for path, v in walk(r):
        if not isinstance(v, str):
            continue
        for m in _EMAIL.finditer(v):
            if not m.group(0).lower().endswith("@example.com"):
                out.append(f"{path}: email not @example.com")
        if path.endswith("phone") and "555" not in v:
            out.append(f"{path}: phone without 555")
    return out
