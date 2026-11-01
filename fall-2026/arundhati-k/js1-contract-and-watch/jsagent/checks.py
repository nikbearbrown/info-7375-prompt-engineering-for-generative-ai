"""Checks for the two wrong versions in CONTRACT §6. Both judges' outputs go through these.

Wrong version 1 — a verdict or justification paired with the wrong posting.
Wrong version 2 — a RELEVANT verdict whose justification cites no real evidence.
"""

import re

from .resume import resolve_field
from .rule import RULE_SKILLS, description_text


def _norm(s):
    return re.sub(r"\s+", " ", s or "").strip().lower()


def _mentions(skill, quote):
    pattern = RULE_SKILLS.get(skill)
    if pattern is not None:
        return bool(pattern.search(quote))
    return skill.lower() in quote.lower()


def evidence_errors(record, job, resume):
    """Wrong version 2: each citation must resolve in the résumé AND be found in THIS posting's field."""
    errors = []
    matches = record.get("evidence", [])
    text = _norm(description_text(job))
    seen = set()
    for m in matches:
        skill = m.get("skill", "")
        value = resolve_field(resume, m.get("resume_field"))
        if value is None or value.lower() != skill.lower():
            errors.append(f"résumé field {m.get('resume_field')!r} does not hold {skill!r}")
        quote = _norm(m.get("posting_quote"))
        if not quote or quote not in text:
            errors.append(f"quote for {skill!r} is not in posting {record.get('posting_id')} content")
        elif not _mentions(skill, m.get("posting_quote", "")):
            errors.append(f"quote for {skill!r} does not mention it")
        seen.add(skill.lower())
    if record.get("verdict") == "RELEVANT" and len(seen) < 2:
        errors.append(f"RELEVANT with {len(seen)} distinct cited skill(s); the contract needs at least 2")
    return errors


def alignment_errors(jobs, records):
    """Wrong version 1: one record per posting, same id, same title, evidence drawn from that posting."""
    errors = []
    by_id = {str(j["id"]): j for j in jobs}
    ids = [r.get("posting_id") for r in records]
    if sorted(ids) != sorted(by_id):
        errors.append(f"record ids {sorted(map(str, ids))} != posting ids {sorted(by_id)}")
    for r in records:
        job = by_id.get(r.get("posting_id"))
        if job is None:
            continue
        if r.get("title") is not None and r["title"] != job["title"]:
            errors.append(f"posting {r['posting_id']}: record title {r['title']!r} != posting title {job['title']!r}")
        text = _norm(description_text(job))
        for m in r.get("evidence", []):
            if _norm(m.get("posting_quote")) not in text:
                errors.append(f"posting {r['posting_id']}: quote {m.get('posting_quote')!r} comes from another posting")
    return errors


def rule_record_as_evidence(rule_record):
    """Present a rule record in the shared {posting_id, title, verdict, evidence} shape."""
    return {
        "posting_id": rule_record["posting_id"],
        "title": rule_record["title"],
        "verdict": rule_record["verdict"],
        "evidence": rule_record["conditions"]["skills"]["matches"],
    }
