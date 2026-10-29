"""The fixed output format for the Claude judge. Anything that is not exactly this JSON
object is rejected; a rejected answer is reported as rejected, never repaired or guessed."""
import json

KEYS = {"posting_id", "verdict", "failed_conditions", "resume_fields", "posting_fields", "justification"}
VERDICTS = {"Relevant", "Not Relevant"}
RESUME_FIELDS = {"target_roles", "experience_years", "skills", "location", "remote_ok", "exclusions"}
POSTING_FIELDS = {"id", "title", "departments", "location", "offices", "content"}


def validate(text, expected_id):
    """Returns (parsed, errors). parsed is None when errors is non-empty."""
    errors = []
    s = (text or "").strip()
    if not (s.startswith("{") and s.endswith("}")):
        return None, ["output is not a bare JSON object (no prose, no code fences)"]
    try:
        obj = json.loads(s)
    except json.JSONDecodeError as e:
        return None, [f"not valid JSON: {e.msg}"]
    if not isinstance(obj, dict):
        return None, ["output is not a JSON object"]
    if set(obj) != KEYS:
        missing, extra = KEYS - set(obj), set(obj) - KEYS
        errors.append(f"keys wrong (missing {sorted(missing)}, extra {sorted(extra)})")
        return None, errors
    pid = obj["posting_id"]
    if not isinstance(pid, int) or isinstance(pid, bool) or pid != expected_id:
        errors.append(f"posting_id {pid!r} is not the posting asked about ({expected_id})")
    if obj["verdict"] not in VERDICTS:
        errors.append(f"verdict {obj['verdict']!r} not in {sorted(VERDICTS)}")
    fc = obj["failed_conditions"]
    if not (isinstance(fc, list) and all(isinstance(n, int) and not isinstance(n, bool) and 1 <= n <= 6 for n in fc)
            and len(fc) == len(set(fc))):
        errors.append("failed_conditions must be distinct integers 1-6")
    elif (obj["verdict"] == "Relevant") != (len(fc) == 0):
        errors.append("verdict must be Relevant exactly when failed_conditions is empty")
    for key, allowed in (("resume_fields", RESUME_FIELDS), ("posting_fields", POSTING_FIELDS)):
        v = obj[key]
        if not (isinstance(v, list) and v and all(isinstance(x, str) for x in v)):
            errors.append(f"{key} must be a non-empty list of field names")
        elif set(v) - allowed:
            errors.append(f"{key} has unknown fields {sorted(set(v) - allowed)}")
    j = obj["justification"]
    if not isinstance(j, str) or len(j.strip()) < 20:
        errors.append("justification must be a sentence or more")
    elif not errors:
        cited_r = any(f in j for f in obj["resume_fields"])
        cited_p = any(f in j for f in obj["posting_fields"])
        if not (cited_r and cited_p):
            errors.append("justification does not name any of its own resume_fields and posting_fields")
    return (None, errors) if errors else (obj, [])
