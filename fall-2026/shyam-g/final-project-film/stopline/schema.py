"""Input shapes and validation for StopLine.

All incidents and evidence used with this prototype are SYNTHETIC.
Validation returns a list of error strings; an empty list means valid.
"""
from datetime import datetime

ACTIONS = {"release_lot", "rework_lot", "scrap_lot", "close_incident"}
SEVERITIES = {"minor", "major", "critical"}
EVIDENCE_KINDS = {"inspection", "containment", "root_cause", "verification", "supplier_cert"}
CLAIM_OPS = {"eq"}


def _is_iso(value):
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value)
    except ValueError:
        return False
    return True


def validate_incident(incident):
    errors = []
    if not isinstance(incident, dict):
        return ["incident is not an object"]
    for key in ("id", "lot", "description"):
        if not isinstance(incident.get(key), str) or not incident.get(key):
            errors.append(f"missing or empty '{key}'")
    if incident.get("severity") not in SEVERITIES:
        errors.append(f"severity must be one of {sorted(SEVERITIES)}")
    if not _is_iso(incident.get("opened_at")):
        errors.append("'opened_at' must be an ISO datetime")

    action = incident.get("proposed_action")
    if not isinstance(action, dict):
        errors.append("missing 'proposed_action' object")
        return errors
    if action.get("type") not in ACTIONS:
        errors.append(f"proposed_action.type must be one of {sorted(ACTIONS)}")
    if not _is_iso(action.get("decided_at")):
        errors.append("'proposed_action.decided_at' must be an ISO datetime")
    claims = action.get("claims")
    if not isinstance(claims, list):
        errors.append("'proposed_action.claims' must be a list")
        return errors
    for i, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"claim[{i}] is not an object")
            continue
        for key in ("id", "text", "evidence_id", "field"):
            if not isinstance(claim.get(key), str) or not claim.get(key):
                errors.append(f"claim[{i}] missing or empty '{key}'")
        if claim.get("op", "eq") not in CLAIM_OPS:
            errors.append(f"claim[{i}] op must be one of {sorted(CLAIM_OPS)}")
        if "value" not in claim:
            errors.append(f"claim[{i}] missing 'value'")
    return errors


def validate_evidence(record):
    errors = []
    if not isinstance(record, dict):
        return ["evidence record is not an object"]
    if not isinstance(record.get("id"), str) or not record.get("id"):
        errors.append("evidence missing 'id'")
    if record.get("kind") not in EVIDENCE_KINDS:
        errors.append(f"evidence {record.get('id')}: kind must be one of {sorted(EVIDENCE_KINDS)}")
    if not isinstance(record.get("lot"), str):
        errors.append(f"evidence {record.get('id')}: missing 'lot'")
    if not _is_iso(record.get("collected_at")):
        errors.append(f"evidence {record.get('id')}: 'collected_at' must be an ISO datetime")
    if not isinstance(record.get("fields"), dict):
        errors.append(f"evidence {record.get('id')}: 'fields' must be an object")
    spec = record.get("spec", {})
    if not isinstance(spec, dict):
        errors.append(f"evidence {record.get('id')}: 'spec' must be an object")
    return errors
