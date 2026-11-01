"""Validators for the contract's inputs and outputs. Anything that fails is rejected, not repaired."""

import json
import re

VERDICTS = {"relevant", "not_relevant"}
POSTING_FIELDS = {"title", "content", "location.name"}
CLAUDE_KEYS = {"id", "verdict", "resume_fields", "posting_fields", "justification"}
RESUME_FIELD = re.compile(r"^(skills(\.\w+)?|experience|projects|education)$")


class ContractError(ValueError):
    pass


def validate_resume(resume):
    """Refuse anything that is not a clearly fictional persona."""
    personal = resume.get("personal", {})
    email, phone = personal.get("email", ""), personal.get("phone", "")
    if not email.endswith("@example.com"):
        raise ContractError(f"résumé email must be @example.com (fictional persona only), got {email!r}")
    if "555" not in phone:
        raise ContractError("résumé phone must be a 555 number (fictional persona only)")
    if not isinstance(resume.get("skills"), dict) or not resume["skills"]:
        raise ContractError("résumé needs a non-empty 'skills' object")
    return resume


def validate_verdict(v, expected_id):
    """Every verdict, from either judge, must belong to its posting and cite fields on both sides."""
    if v.get("id") != expected_id:
        raise ContractError(f"verdict id {v.get('id')!r} does not match posting id {expected_id!r}")
    if v.get("verdict") not in VERDICTS:
        raise ContractError(f"verdict must be one of {sorted(VERDICTS)}, got {v.get('verdict')!r}")
    rf, pf = v.get("resume_fields"), v.get("posting_fields")
    if not isinstance(rf, list) or not rf or not all(isinstance(f, str) and RESUME_FIELD.match(f) for f in rf):
        raise ContractError(f"resume_fields must name at least one résumé field, got {rf!r}")
    if not isinstance(pf, list) or not pf or not set(pf) <= POSTING_FIELDS:
        raise ContractError(f"posting_fields must be a non-empty subset of {sorted(POSTING_FIELDS)}, got {pf!r}")
    just = v.get("justification")
    if not isinstance(just, str) or not just.strip():
        raise ContractError("justification is empty")
    # The justification text itself must mention a résumé field and a posting field, not just "good fit".
    if not re.search(r"skills|experience|projects|education", just, re.I):
        raise ContractError("justification names no résumé field")
    if not re.search(r"title|content|location", just, re.I):
        raise ContractError("justification names no posting field")
    return v


def parse_claude_output(text, expected_id):
    """Claude's reply must be exactly one JSON object with exactly the contract keys."""
    text = text.strip()
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as e:
        raise ContractError(f"not a single JSON object: {e}") from None
    if not isinstance(obj, dict) or set(obj) != CLAUDE_KEYS:
        raise ContractError(f"keys must be exactly {sorted(CLAUDE_KEYS)}, got {sorted(obj) if isinstance(obj, dict) else type(obj)}")
    validate_verdict(obj, expected_id)
    if len(obj["justification"]) > 600:
        raise ContractError("justification longer than 600 characters")
    return {**obj, "judge": "claude", "kind": "judgment"}
