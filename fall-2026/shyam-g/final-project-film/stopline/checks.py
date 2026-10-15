"""Deterministic checks. Each check compares the proposed action's claims
against evidence records using explicit rules only -- no model, no fuzzy
matching. That is the point, and also the main limitation: a claim whose
structured value matches but whose wording misleads will pass.
"""
import math
from dataclasses import dataclass, field
from datetime import datetime

HUMAN_REVIEW = "HUMAN REVIEW REQUIRED"
NEEDS_EVIDENCE = "NEEDS MORE EVIDENCE"
ACCEPT = "ACCEPT FOR REVIEW"

# Evidence kinds an action must cite before it can be accepted for review.
REQUIRED_KINDS = {
    "release_lot": {"inspection", "containment"},
    "rework_lot": {"inspection"},
    "scrap_lot": {"inspection"},
    "close_incident": {"root_cause", "verification"},
}
# Actions that put parts back into flow or end the investigation.
SPEC_GATED_ACTIONS = {"release_lot", "close_incident"}
SEVERITY_GATED_ACTIONS = {"release_lot", "close_incident"}


@dataclass
class CheckResult:
    name: str
    passed: bool
    on_fail: str
    details: list = field(default_factory=list)

    def to_dict(self):
        return {
            "check": self.name,
            "status": "pass" if self.passed else "fail",
            "on_fail": self.on_fail,
            "details": self.details,
        }


def _values_match(claimed, actual):
    if isinstance(claimed, bool) or isinstance(actual, bool):
        return claimed is actual
    if isinstance(claimed, (int, float)) and isinstance(actual, (int, float)):
        return math.isclose(claimed, actual, rel_tol=1e-9, abs_tol=1e-9)
    return claimed == actual


def has_claims(incident, cited, index):
    claims = incident["proposed_action"]["claims"]
    details = [] if claims else ["proposed action cites no evidence at all"]
    return CheckResult("has_claims", bool(claims), NEEDS_EVIDENCE, details)


def evidence_refs_resolve(incident, cited, index):
    missing = [
        f"claim {c['id']} cites {c['evidence_id']}, which does not exist"
        for c in incident["proposed_action"]["claims"]
        if c["evidence_id"] not in index
    ]
    return CheckResult("evidence_refs_resolve", not missing, NEEDS_EVIDENCE, missing)


def evidence_lot_matches(incident, cited, index):
    wrong = [
        f"{ev['id']} is for lot {ev['lot']}, incident is lot {incident['lot']}"
        for ev in cited.values()
        if ev["lot"] != incident["lot"]
    ]
    return CheckResult("evidence_lot_matches", not wrong, HUMAN_REVIEW, wrong)


def claims_match_evidence(incident, cited, index):
    """Contradictions escalate; a field the evidence does not contain is a gap.

    Returns two results so the audit record keeps them apart.
    """
    contradictions, gaps = [], []
    for c in incident["proposed_action"]["claims"]:
        ev = cited.get(c["evidence_id"])
        if ev is None:
            continue  # reported by evidence_refs_resolve
        if c["field"] not in ev["fields"]:
            gaps.append(f"claim {c['id']}: {ev['id']} has no field '{c['field']}'")
            continue
        actual = ev["fields"][c["field"]]
        if not _values_match(c["value"], actual):
            contradictions.append(
                f"claim {c['id']} says {c['field']}={c['value']!r}; {ev['id']} records {actual!r}"
            )
    return [
        CheckResult("claims_match_evidence", not contradictions, HUMAN_REVIEW, contradictions),
        CheckResult("claimed_fields_present", not gaps, NEEDS_EVIDENCE, gaps),
    ]


def required_evidence_kinds(incident, cited, index):
    action = incident["proposed_action"]["type"]
    have = {ev["kind"] for ev in cited.values()}
    missing = sorted(REQUIRED_KINDS[action] - have)
    details = [f"{action} requires cited {kind} evidence" for kind in missing]
    return CheckResult("required_evidence_kinds", not missing, NEEDS_EVIDENCE, details)


def within_spec(incident, cited, index):
    action = incident["proposed_action"]["type"]
    if action not in SPEC_GATED_ACTIONS:
        return CheckResult("within_spec", True, HUMAN_REVIEW, [f"not applied to {action}"])
    out = []
    for ev in cited.values():
        for name, limits in sorted(ev.get("spec", {}).items()):
            value = ev["fields"].get(name)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                out.append(f"{ev['id']}: spec field '{name}' has no numeric value")
                continue
            lo, hi = limits.get("min"), limits.get("max")
            if (lo is not None and value < lo) or (hi is not None and value > hi):
                out.append(f"{ev['id']}: {name}={value} outside [{lo}, {hi}]")
    return CheckResult("within_spec", not out, HUMAN_REVIEW, out)


def evidence_timing(incident, cited, index):
    """Evidence older than the incident is stale (a gap); evidence dated after
    the decision cannot have informed it (escalate)."""
    opened = datetime.fromisoformat(incident["opened_at"])
    decided = datetime.fromisoformat(incident["proposed_action"]["decided_at"])
    stale, after = [], []
    for ev in cited.values():
        collected = datetime.fromisoformat(ev["collected_at"])
        if collected < opened:
            stale.append(f"{ev['id']} collected {ev['collected_at']}, before incident opened {incident['opened_at']}")
        elif collected > decided:
            after.append(f"{ev['id']} collected {ev['collected_at']}, after decision at {incident['proposed_action']['decided_at']}")
    return [
        CheckResult("evidence_not_stale", not stale, NEEDS_EVIDENCE, stale),
        CheckResult("evidence_precedes_decision", not after, HUMAN_REVIEW, after),
    ]


def severity_gate(incident, cited, index):
    action = incident["proposed_action"]["type"]
    blocked = incident["severity"] == "critical" and action in SEVERITY_GATED_ACTIONS
    details = [f"critical incident: {action} always needs a named human decision"] if blocked else []
    return CheckResult("severity_gate", not blocked, HUMAN_REVIEW, details)


ALL_CHECKS = [
    has_claims,
    evidence_refs_resolve,
    evidence_lot_matches,
    claims_match_evidence,
    required_evidence_kinds,
    within_spec,
    evidence_timing,
    severity_gate,
]
