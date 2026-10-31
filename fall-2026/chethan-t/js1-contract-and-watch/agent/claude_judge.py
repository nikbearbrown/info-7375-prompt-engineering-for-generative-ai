"""The Claude verdict (labeled `judgment`)."""

import json

VERDICTS = {"relevant", "not_relevant"}


def _string_list(value):
    return isinstance(value, list) and bool(value) and all(isinstance(v, str) and v for v in value)


def validate(text):
    """Return the parsed verdict dict if Claude's reply is valid, else None.

    Valid means a JSON object with a known `verdict`, non-empty
    `resume_fields` and `posting_fields` lists, and a non-empty `reason`.
    """
    try:
        data = json.loads(text)
    except (TypeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    if data.get("verdict") not in VERDICTS:
        return None
    if not _string_list(data.get("resume_fields")) or not _string_list(data.get("posting_fields")):
        return None
    reason = data.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        return None
    return {k: data[k] for k in ("verdict", "resume_fields", "posting_fields", "reason")}
