"""Load and validate the fictional résumé (CONTRACT.md, In and Refuses)."""
import json
import pathlib

import jsonschema

SCHEMA_PATH = pathlib.Path(__file__).resolve().parent.parent / "resume.schema.json"


class ResumeError(Exception):
    """The résumé is invalid or does not look fictional. Its contents are never echoed."""


def load_resume(path):
    try:
        data = json.loads(pathlib.Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ResumeError(f"cannot read résumé JSON at {path}: {exc.__class__.__name__}") from None

    schema = json.loads(SCHEMA_PATH.read_text())
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        # Report where it failed, not the offending value, so a real résumé is never printed.
        where = ["/".join(map(str, e.path)) or "(root)" for e in errors]
        raise ResumeError(f"résumé failed {SCHEMA_PATH.name} at: {', '.join(where)}")

    personal = data["personal"]
    if not personal["email"].endswith("@example.com") or "555" not in personal["phone"]:
        raise ResumeError("refusing a résumé without an @example.com email and a 555 phone")
    return data
