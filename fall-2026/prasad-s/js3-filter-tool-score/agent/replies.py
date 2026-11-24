"""Saved Claude replies and their validator (CONTRACT.md §1 item 5, §2, §6).

The agent never calls Claude. It reads only the .txt files that
claude_outputs/metadata.json lists, matched by posting_id, never by file order.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .rule import find_term, posting_field

CLAUDE_LABEL = "judgment (Claude)"
VERDICTS = ("relevant", "not_relevant")
# Decision 2026-10-27: résumé citations name one of the three list fields and
# must equal one entry exactly, case-sensitive.
RESUME_FIELDS = ("target_titles", "locations", "skills")
POSTING_FIELDS = ("title", "location.name", "content")
METADATA_KEYS = ("file", "collected", "model", "prompt_version")

# Each §6 line starts with its label exactly as written, in capitals.
_PREFIXES = (
    ("V", "VERDICT: "),
    ("R", "RESUME_FIELD: "),
    ("P", "POSTING_FIELD: "),
    ("E", "REASON: "),
)
# One VERDICT, then RESUME_FIELD lines, then POSTING_FIELD lines, then one REASON.
_ORDER = re.compile(r"VR+P+E")


@dataclass
class Validation:
    ok: bool
    reasons: list = field(default_factory=list)
    parsed: dict = None


def _split_field(body, allowed, label, lineno, reasons):
    """Split a *_FIELD line at its first '=' only, so the value may hold commas."""
    name, sep, value = body.partition("=")
    if not sep:
        reasons.append(f"line {lineno}: {label} has no '='")
    elif not name:
        reasons.append(f"line {lineno}: {label} has no field name")
    elif not value:
        reasons.append(f"line {lineno}: {label} {name} has an empty value")
    elif name not in allowed:
        reasons.append(f"line {lineno}: {label} name {name!r} is not one of {', '.join(allowed)}")
    else:
        return name, value
    return None


def check_format(text):
    """§6 validator step 1. Returns (reasons, parsed); parsed is None if any reason."""
    reasons = []
    if "\r" in text:
        reasons.append("reply contains a carriage return; lines must end in \\n only")
    # Decision 2026-10-27: exactly one final newline is allowed and stripped.
    if text.endswith("\n"):
        text = text[:-1]
    lines = text.split("\n")
    kinds = []
    for lineno, line in enumerate(lines, start=1):
        kind = next((k for k, prefix in _PREFIXES if line.startswith(prefix)), None)
        if kind is None:
            reasons.append(f"line {lineno} is not a §6 line: {line!r}")
            kind = "?"
        kinds.append(kind)
    if not _ORDER.fullmatch("".join(kinds)):
        reasons.append(
            "lines are not exactly one VERDICT, then one or more RESUME_FIELD, "
            "then one or more POSTING_FIELD, then one REASON (§6)"
        )

    parsed = {"verdict": None, "resume_fields": [], "posting_fields": [], "reason": None}
    for lineno, (kind, line) in enumerate(zip(kinds, lines), start=1):
        if kind == "?":
            continue
        prefix = dict(_PREFIXES)[kind]
        body = line[len(prefix):]
        if kind == "V":
            if body not in VERDICTS:
                reasons.append(f"line {lineno}: VERDICT {body!r} is not relevant or not_relevant")
            parsed["verdict"] = body
        elif kind == "R":
            pair = _split_field(body, RESUME_FIELDS, "RESUME_FIELD", lineno, reasons)
            if pair:
                parsed["resume_fields"].append({"field": pair[0], "value": pair[1]})
        elif kind == "P":
            pair = _split_field(body, POSTING_FIELDS, "POSTING_FIELD", lineno, reasons)
            if pair:
                parsed["posting_fields"].append({"field": pair[0], "value": pair[1]})
        else:
            if not body.strip():
                reasons.append(f"line {lineno}: REASON is empty")
            parsed["reason"] = body
    return reasons, (None if reasons else parsed)


def check_citations(parsed, persona, posting):
    """§6 validator step 2: every cited value exists, in the field it names."""
    reasons = []
    for item in parsed["resume_fields"]:
        if item["value"] not in persona.get(item["field"], []):
            reasons.append(f"RESUME_FIELD {item['field']}={item['value']!r} is not a résumé {item['field']} value")
    # Decision 2026-10-27: posting citations use §4 matching (case-insensitive substring).
    for item in parsed["posting_fields"]:
        text = posting_field(posting, item["field"])
        if text is None:
            reasons.append(f"POSTING_FIELD {item['field']}: the posting has no {item['field']}")
        elif find_term(item["value"], text) is None:
            reasons.append(f"POSTING_FIELD {item['field']}={item['value']!r} is not in the posting's {item['field']} after §4 cleanup")
    return reasons


def validate_reply(text, persona, posting):
    """Format check, then citation check. A reply is never repaired."""
    reasons, parsed = check_format(text)
    if reasons:
        return Validation(ok=False, reasons=reasons + ["citations not checked: format failed"])
    reasons = check_citations(parsed, persona, posting)
    return Validation(ok=not reasons, reasons=reasons, parsed=parsed)


def load_metadata(outputs_dir):
    """Returns (metadata keyed by posting_id, error or None)."""
    path = Path(outputs_dir) / "metadata.json"
    if not path.exists():
        return {}, f"{path.parent.name}/metadata.json does not exist"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, f"metadata.json cannot be read: {exc}"
    if not isinstance(data, dict):
        return {}, "metadata.json is not a JSON object keyed by posting_id"
    return data, None


def _rejected(reasons, reply=None, metadata=None):
    justification = {"reply": reply, "reasons": reasons}
    if reply is None:
        justification["note"] = "no saved reply was read"
    if metadata is not None:
        justification["metadata"] = metadata
    return "rejected", justification


def claude_judgment(posting_id, posting, persona, outputs_dir, metadata, metadata_error=None):
    """Returns (claude_verdict, claude_justification) for one new posting.

    A missing or invalid reply gives "rejected"; the record is always kept.
    """
    if metadata_error:
        return _rejected([metadata_error])
    entry = metadata.get(posting_id)
    if entry is None:
        return _rejected([f"no metadata.json entry for {posting_id}; a reply without one is not read (§1 item 5)"])
    if not isinstance(entry, dict):
        return _rejected([f"metadata.json entry for {posting_id} is not an object"])
    problems = [f"metadata.json entry for {posting_id} has no {key}"
                for key in METADATA_KEYS if not isinstance(entry.get(key), str) or not entry.get(key)]
    expected_file = f"{posting_id}.txt"
    if isinstance(entry.get("file"), str) and entry["file"] != expected_file:
        problems.append(f"metadata.json lists {entry['file']!r} for {posting_id}; the reply must be {expected_file}")
    if problems:
        return _rejected(problems, metadata=entry)
    path = Path(outputs_dir) / expected_file
    if not path.is_file():
        return _rejected([f"{expected_file} is listed in metadata.json but was not saved"], metadata=entry)
    try:
        text = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return _rejected([f"{expected_file} cannot be read as UTF-8: {exc}"], metadata=entry)
    result = validate_reply(text, persona, posting)
    if not result.ok:
        return _rejected(result.reasons, reply=text, metadata=entry)
    return result.parsed["verdict"], {"reply": text, "metadata": entry, "parsed": result.parsed}
