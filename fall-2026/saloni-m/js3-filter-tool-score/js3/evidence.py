"""FILTER.md §3: label each claim supported / contradicted / insufficient against the posting's
own text, and decide when the agent must say "I cannot tell".

A claim is {"kind", "claim", "term", "quote"}. The checker never asks a model; it reads the
posting text and the claim and nothing else.
"""
import re

from js3.filter import phd_required, years_required
from js3.text import has_phrase, norm, sentences

KINDS = {"role", "skill", "experience", "seniority", "degree", "other"}
SUPPORTED, CONTRADICTED, INSUFFICIENT = "supported", "contradicted", "insufficient"
_NUM = re.compile(r"\d{1,2}")
_NOT_REQUIRED = re.compile(r"\b(not required|no experience (?:with|in) .{0,30}(?:needed|required)|not necessary)\b", re.I)


def posting_text(posting):
    """Everything the posting itself says: title, location, department, body."""
    parts = [posting.get("title"), posting.get("location"), posting.get("department"), posting.get("text")]
    return "\n".join(p for p in parts if p)


def label_claim(claim, posting, seniority_terms):
    """Return (label, why). Contradicted beats supported."""
    kind = claim.get("kind")
    term = (claim.get("term") or "").strip()
    quote = (claim.get("quote") or "").strip()
    full = posting_text(posting)
    text = posting.get("text") or ""

    contra = _contradiction(kind, term, posting, text, seniority_terms)
    if contra:
        return CONTRADICTED, contra

    if not quote:
        return INSUFFICIENT, "no quote: an absence in the text is not support"
    if norm(quote) not in norm(full):
        return INSUFFICIENT, "the quote is not in the posting text (paraphrased or invented)"
    if not term:
        return INSUFFICIENT, "the claim names no checkable term"
    if kind == "experience":
        if not any(n in _NUM.findall(quote) for n in _NUM.findall(term)):
            return INSUFFICIENT, f"the quote does not state the number in '{term}'"
    elif not has_phrase(quote, term):
        return INSUFFICIENT, f"the quote does not contain the term '{term}'"
    return SUPPORTED, "the quote is in the posting and contains the term"


def _contradiction(kind, term, posting, text, seniority_terms):
    title = posting.get("title") or ""
    if kind == "seniority":
        hits = [t for t in seniority_terms if has_phrase(title, t)]
        if hits:
            return f"the title has seniority word(s) {hits}"
    if kind == "experience":
        claimed = [int(n) for n in _NUM.findall(term)]
        asked, spans = years_required(text)
        if claimed and asked is not None and asked >= 5 and max(claimed) < asked:
            return f"the text asks for {asked}+ years: {spans[0]!r}"
    if kind == "degree":
        req, hits = phd_required(text)
        if req:
            return f"the text requires a PhD: {hits[0][:120]!r}"
    if kind == "skill" and term:
        for s in sentences(text):
            if has_phrase(s, term) and _NOT_REQUIRED.search(s):
                return f"the text says {term} is not required: {s[:120]!r}"
    return None


def label_justification(claims, posting, seniority_terms):
    out = []
    for c in claims:
        label, why = label_claim(c, posting, seniority_terms)
        out.append({**c, "label": label, "why": why})
    return out


def abstain(posting, labeled, filter_result, text_min_chars):
    """FILTER.md §3 'I cannot tell'. Returns a list of reasons; empty means the agent may answer."""
    reasons = []
    if len(posting.get("text") or "") < text_min_chars:
        reasons.append(f"posting text is under {text_min_chars} characters")
    if labeled:
        n_ins = sum(c["label"] == INSUFFICIENT for c in labeled)
        if n_ins * 2 >= len(labeled):
            reasons.append(f"{n_ins} of {len(labeled)} claims are insufficient")
    else:
        reasons.append("the justification has no claims")
    if filter_result.get("decision") == "keep":
        for c in labeled:
            if c["label"] == CONTRADICTED and c.get("kind") in ("experience", "seniority", "degree"):
                reasons.append(f"a {c['kind']} claim behind the keep is contradicted")
                break
    return reasons
