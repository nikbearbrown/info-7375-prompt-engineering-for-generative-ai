"""Validator for the Claude judge's output (CONTRACT.md, Claude prompt contract).

Passing this validator means the output is well-formed and every citation is real.
It does not mean the verdict is correct.
"""
import json

from .text import contains_sequence, normalize, strip_html

VERDICTS = ("relevant", "not_relevant")
TOP_KEYS = {"verdict", "justification"}
ENTRY_KEYS = {"resume_field", "resume_value", "posting_field", "posting_value"}
ALLOWED_RESUME_PATHS = (
    "target_titles",
    "personal.location",
    "years_experience",
    "target_role.excluded",
    "skills.languages",
    "skills.backend_automation",
    "skills.database_cloud",
    "skills.devops_cicd",
)
POSTING_FIELDS = ("title", "location.name", "content")


def _resume_value_at(resume, path):
    value = resume
    for part in path.split("."):
        value = value[part]
    return value


def _posting_text(posting, field):
    if field == "title":
        return posting["title"]
    if field == "location.name":
        return posting["location"]["name"]
    return strip_html(posting["content"])


def _resume_value_ok(actual, cited):
    if isinstance(actual, list):
        return isinstance(cited, str) and cited in actual  # one exact element
    # Same type as the résumé value: 2 is accepted; "2", 2.0, and true are not.
    return type(cited) is type(actual) and cited == actual


def validate_claude_output(text, resume, posting):
    """Return (ok, parsed_or_None, errors)."""
    errors = []
    stripped = text.strip()
    if not (stripped.startswith("{") and stripped.endswith("}")):
        return False, None, ["output is not a single bare JSON object (prose or code fence present)"]
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError as exc:
        return False, None, [f"invalid JSON: {exc.msg}"]
    if not isinstance(data, dict):
        return False, None, ["top level is not an object"]

    if set(data) != TOP_KEYS:
        errors.append(f"top-level keys must be exactly {sorted(TOP_KEYS)}, got {sorted(data)}")
    if data.get("verdict") not in VERDICTS:
        errors.append(f"verdict must be one of {VERDICTS}, got {data.get('verdict')!r}")
    justification = data.get("justification")
    if not isinstance(justification, list) or not justification:
        errors.append("justification must be a nonempty array")
        justification = []

    for i, entry in enumerate(justification):
        where = f"justification[{i}]"
        if not isinstance(entry, dict) or set(entry) != ENTRY_KEYS:
            errors.append(f"{where}: keys must be exactly {sorted(ENTRY_KEYS)}")
            continue
        field = entry["resume_field"]
        if field not in ALLOWED_RESUME_PATHS:
            errors.append(f"{where}: resume_field {field!r} is not an allowed path")
        elif not _resume_value_ok(_resume_value_at(resume, field), entry["resume_value"]):
            errors.append(f"{where}: resume_value {entry['resume_value']!r} is not a value at {field}")

        pfield, pvalue = entry["posting_field"], entry["posting_value"]
        if pfield not in POSTING_FIELDS:
            errors.append(f"{where}: posting_field {pfield!r} is not allowed")
        elif not isinstance(pvalue, str) or not normalize(pvalue):
            errors.append(f"{where}: posting_value must be nonempty text")
        elif not contains_sequence(normalize(_posting_text(posting, pfield)), normalize(pvalue)):
            errors.append(f"{where}: posting_value {pvalue!r} does not appear in this posting's {pfield}")

    if errors:
        return False, None, errors
    return True, data, []
