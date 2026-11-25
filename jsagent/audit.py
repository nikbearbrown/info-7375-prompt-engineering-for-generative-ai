"""Audit verdicts against CONTRACT.md (sections 2 and 5): right posting, real citations, recomputable."""
from . import rule
from .fetch import posting_field
from .resume import resolve

ALLOWED_POSTING_FIELDS = {"title", "location.name", "content"}


def _value_in_posting(value, field_text):
    if isinstance(value, str):
        return value.lower() in field_text.lower()
    if isinstance(value, list):
        return all(isinstance(v, str) and v in field_text for v in value)
    return False


def audit_verdicts(postings, r, verdicts):
    """Return a list of problems; empty means every verdict meets the contract."""
    errors = []
    by_id = {p["id"]: p for p in postings}
    ids = [v.get("posting_id") for v in verdicts]
    if sorted(ids) != sorted(by_id):
        errors.append(f"verdict ids {sorted(map(str, ids))} do not match posting ids {sorted(by_id)}")
    for v in verdicts:
        pid = v.get("posting_id")
        p = by_id.get(pid)
        if p is None:
            errors.append(f"{pid}: verdict for a posting not in this run")
            continue
        checks = v.get("checks") or []
        if [c.get("check") for c in checks] != ["R1", "R2", "R3", "R4", "R5"]:
            errors.append(f"{pid}: justification must cite checks R1-R5, got {[c.get('check') for c in checks]}")
            continue
        for c in checks:
            if not c.get("resume"):
                errors.append(f"{pid} {c['check']}: cites no résumé field")
            for cite in c.get("resume", []):
                try:
                    actual = resolve(r, cite.get("field"))
                except KeyError:
                    errors.append(f"{pid} {c['check']}: résumé path {cite.get('field')!r} does not exist")
                    continue
                if actual != cite.get("value"):
                    errors.append(f"{pid} {c['check']}: résumé value for {cite['field']} is not what the résumé says")
            pf = (c.get("posting") or {}).get("field")
            if pf not in ALLOWED_POSTING_FIELDS:
                errors.append(f"{pid} {c['check']}: posting field {pf!r} not allowed")
                continue
            if not _value_in_posting(c["posting"].get("value"), posting_field(p, pf)):
                errors.append(f"{pid} {c['check']}: cited posting value is not in this posting's {pf}")
        expected = rule.judge(p, r)
        if v.get("verdict") != expected["verdict"]:
            errors.append(f"{pid}: verdict {v.get('verdict')!r} does not recompute (rule says {expected['verdict']!r})")
        if [c.get("passed") for c in checks] != [c["passed"] for c in expected["checks"]]:
            errors.append(f"{pid}: check results do not recompute")
        for key in ["preferred_location", "preferred_years"]:
            if v.get(key) != expected[key]:
                errors.append(f"{pid}: {key} does not recompute")
    return errors
