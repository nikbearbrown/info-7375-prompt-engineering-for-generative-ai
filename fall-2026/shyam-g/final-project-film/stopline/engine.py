"""Run every check on an incident and pick one outcome.

Precedence: HUMAN REVIEW REQUIRED > NEEDS MORE EVIDENCE > ACCEPT FOR REVIEW.
Every failed check is recorded in the audit record, not only the decisive one.
"ACCEPT FOR REVIEW" means "a person may now review this"; StopLine never approves.
"""
import hashlib
import json

from . import checks, schema
from .checks import ACCEPT, HUMAN_REVIEW, NEEDS_EVIDENCE

ENGINE_VERSION = "0.1.0"
PRECEDENCE = [HUMAN_REVIEW, NEEDS_EVIDENCE, ACCEPT]


def pick_outcome(failed_outcomes):
    for outcome in PRECEDENCE:
        if outcome in failed_outcomes:
            return outcome
    return ACCEPT


def _digest(obj):
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("ascii")).hexdigest()


def index_evidence(records):
    """Return (id -> record, list of validation errors). Invalid records are dropped."""
    index, errors = {}, []
    for record in records:
        problems = schema.validate_evidence(record)
        if problems:
            errors.extend(problems)
            continue
        if record["id"] in index:
            errors.append(f"duplicate evidence id {record['id']}")
            continue
        index[record["id"]] = record
    return index, errors


def evaluate(incident, index):
    """Return an audit record (a plain dict) for one incident."""
    incident_id = incident.get("id") if isinstance(incident, dict) else None
    problems = schema.validate_incident(incident)
    if problems:
        result = checks.CheckResult("schema_valid", False, HUMAN_REVIEW, problems)
        return {
            "incident_id": incident_id,
            "outcome": HUMAN_REVIEW,
            "decided_by": ["schema_valid"],
            "checks": [result.to_dict()],
            "note": "input could not be checked; remaining checks skipped",
            "engine_version": ENGINE_VERSION,
            "input_sha256": _digest(incident),
        }

    cited = {
        c["evidence_id"]: index[c["evidence_id"]]
        for c in incident["proposed_action"]["claims"]
        if c["evidence_id"] in index
    }
    results = [checks.CheckResult("schema_valid", True, HUMAN_REVIEW, [])]
    for check in checks.ALL_CHECKS:
        out = check(incident, cited, index)
        results.extend(out if isinstance(out, list) else [out])

    failed = [r for r in results if not r.passed]
    outcome = pick_outcome({r.on_fail for r in failed})
    return {
        "incident_id": incident_id,
        "action": incident["proposed_action"]["type"],
        "outcome": outcome,
        "decided_by": [r.name for r in failed if r.on_fail == outcome],
        "failed_checks": [r.name for r in failed],
        "checks": [r.to_dict() for r in results],
        "engine_version": ENGINE_VERSION,
        "input_sha256": _digest({"incident": incident, "cited_evidence": [cited[k] for k in sorted(cited)]}),
    }


def evaluate_all(incidents, evidence_records):
    index, evidence_errors = index_evidence(evidence_records)
    return [evaluate(inc, index) for inc in incidents], evidence_errors
