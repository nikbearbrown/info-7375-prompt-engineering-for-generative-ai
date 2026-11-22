"""FILTER.md section 3: claims C1-C5, their labels, the quote check, and the answer.

The quote check is mechanical: a supported/contradicted label must carry a quote that appears
verbatim (after whitespace is normalized) in THIS posting's title, location or text. Whether
the quote really asserts the claim is a human check (SHORTLIST.md), not this module's.
"""
from __future__ import annotations

import re

LABELS = ("supported", "contradicted", "insufficient")
CLAIMS = ("C1", "C2", "C3", "C4", "C5")
WORTH, NOT_FOR, CANNOT = "worth reading", "not for Priya", "I cannot tell"

CLAIM_TEXT = {
    "C1": "This is an engineering, ML, data or AI role.",
    "C2": "The posting asks for {skill}.",
    "C3": "The level fits an early-career candidate (MS Dec 2025, one 8-month co-op).",
    "C4": "The role can be done from Boston or remotely.",
    "C5": "The employer will sponsor a work visa for this role.",
}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def quote_in_posting(quote: str, posting: dict) -> bool:
    q = _norm(quote)
    if not q:
        return False
    return any(q in _norm(posting.get(f) or "") for f in ("title", "location", "text"))


def claims_for(result: dict, max_skills: int = 3) -> list:
    """The justification of one shortlisted posting: C1, one C2 per matched skill (at most 3), C3, C4, C5."""
    out = [{"claim": "C1", "text": CLAIM_TEXT["C1"]}]
    for s in (result.get("skills") or [])[:max_skills]:
        out.append({"claim": "C2", "skill": s, "text": CLAIM_TEXT["C2"].format(skill=s)})
    out += [{"claim": c, "text": CLAIM_TEXT[c]} for c in ("C3", "C4", "C5")]
    return out


def validate_label(lab: dict, posting: dict) -> list:
    """Errors for one claim label (empty list = valid)."""
    errors = []
    if lab.get("claim") not in CLAIMS:
        errors.append(f"unknown claim {lab.get('claim')!r}")
    label = lab.get("label")
    if label not in LABELS:
        return errors + [f"label must be one of {LABELS}, got {label!r}"]
    quote, conflict = lab.get("quote"), lab.get("conflict")
    if label in ("supported", "contradicted"):
        if not quote:
            errors.append(f"a {label} label must carry a quote")
        elif not quote_in_posting(quote, posting):
            errors.append(f"quote not found in this posting: {quote[:80]!r}")
    else:
        if quote:
            errors.append("an insufficient label carries no quote (use 'conflict' for quotes on both sides)")
        if conflict:
            for side in ("for", "against"):
                q = (conflict or {}).get(side)
                if not q or not quote_in_posting(q, posting):
                    errors.append(f"conflict quote '{side}' missing or not found in this posting")
    return errors


def answer(labels: list, cannot_tell_reason: str = None) -> dict:
    """FILTER.md section 3: worth reading / not for Priya / I cannot tell. C4 and C5 never change it."""
    if cannot_tell_reason:
        return {"answer": CANNOT, "why": cannot_tell_reason}
    by = {}
    for lab in labels:
        by.setdefault(lab["claim"], []).append(lab["label"])
    c1 = (by.get("C1") or ["insufficient"])[0]
    c3 = (by.get("C3") or ["insufficient"])[0]
    if c1 == "contradicted" or c3 == "contradicted":
        return {"answer": NOT_FOR, "why": "C1 contradicted" if c1 == "contradicted" else "C3 (level) contradicted"}
    if c1 == "supported" and "supported" in (by.get("C2") or []):
        return {"answer": WORTH, "why": "C1 supported, a skill supported, level not contradicted"}
    why = "C1 insufficient" if c1 != "supported" else "no skill claim supported"
    return {"answer": CANNOT, "why": why}
