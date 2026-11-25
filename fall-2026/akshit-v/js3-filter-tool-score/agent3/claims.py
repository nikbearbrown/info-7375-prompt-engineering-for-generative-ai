"""The evidence rules (FILTER.md section 2): label each claim, then answer or abstain.

A claim is {"kind", "claim", "quote"}. Kinds:
  core_work   - "the main work is data engineering"            (core, rule A2)
  level       - "the level fits a 5-year individual contributor" (core, rule A2)
  employment  - full-time or not
  has         - a must-have the job seeker meets
  lacks       - a must-have the job seeker does not meet

Labels: supported | contradicted | insufficient.
  * The verbatim check is code (E1/E3): no quote, or a quote not in the posting -> insufficient.
  * The meaning check is a separate function, passed in (E4): in production a fresh Claude
    session; in tests a stub. A verbatim quote alone is never "supported" (E5, guards WV2).
"""
import re
import unicodedata

KINDS = ("core_work", "level", "employment", "has", "lacks")
CORE = ("core_work", "level")
LABELS = ("supported", "contradicted", "insufficient")
MIN_QUOTE_CHARS = 3


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip().lower()


def posting_text(posting: dict) -> str:
    """Everything a quote may come from: the title, the content, and the structured employment type."""
    return " \n ".join([posting.get("title") or "", posting.get("content_text") or "",
                        f"employment type: {posting.get('employment_type')}" if posting.get("employment_type") else ""])


def quote_in_posting(quote: str, posting: dict) -> bool:
    q = normalize(quote)
    return len(q) >= MIN_QUOTE_CHARS and q in normalize(posting_text(posting))


def label_claim(claim: dict, posting: dict, meaning_check) -> dict:
    """Return the claim with "label" and "why". meaning_check(claim, posting) -> {"label", "why", "contra_quote"?}."""
    quote = claim.get("quote") or ""
    if not quote.strip():
        return {**claim, "label": "insufficient", "why": "E3: no quote", "checked_by": "code"}
    if not quote_in_posting(quote, posting):
        return {**claim, "label": "insufficient", "why": "E3: quote is not in the posting verbatim", "checked_by": "code"}
    m = meaning_check(claim, posting)
    label = m.get("label")
    if label not in LABELS:
        return {**claim, "label": "insufficient", "why": f"meaning check gave no valid label ({label!r})",
                "checked_by": "code"}
    if label == "contradicted":
        contra = m.get("contra_quote") or quote
        if not quote_in_posting(contra, posting):
            return {**claim, "label": "insufficient", "why": "E2 needs a contradicting span quoted verbatim; none was",
                    "checked_by": "code"}
        return {**claim, "label": "contradicted", "why": m.get("why", ""), "contra_quote": contra,
                "checked_by": m.get("checked_by", "meaning_check")}
    return {**claim, "label": label, "why": m.get("why", ""), "checked_by": m.get("checked_by", "meaning_check")}


def answer(filter_result: dict | None, labeled_claims: list[dict] | None, board_failed: bool = False) -> dict:
    """The agent's answer for one posting: relevant | not_relevant | cannot_tell, with the rule that decided it."""
    if board_failed:
        return {"answer": "cannot_tell", "rule": "A3", "why": "the board failed this run: no data, I cannot tell"}
    if filter_result is None:
        return {"answer": "cannot_tell", "rule": "A3", "why": "no posting record: I cannot tell"}
    if filter_result["verdict"] == "cannot_tell":
        return {"answer": "cannot_tell", "rule": "A1", "why": filter_result["because"]}
    if filter_result["verdict"] == "reject":
        return {"answer": "not_relevant", "rule": "filter", "why": filter_result["because"]}
    labeled_claims = labeled_claims or []
    for kind in CORE:
        mine = [c for c in labeled_claims if c.get("kind") == kind]
        if any(c["label"] == "contradicted" for c in mine):
            return {"answer": "not_relevant", "rule": "A2", "why": f"core claim '{kind}' is contradicted by the posting"}
    for kind in CORE:
        mine = [c for c in labeled_claims if c.get("kind") == kind]
        if not any(c["label"] == "supported" for c in mine):
            return {"answer": "cannot_tell", "rule": "A2", "why": f"core claim '{kind}' is not supported by the posting text"}
    return {"answer": "relevant", "rule": "A2", "why": "both core claims are supported by quoted text"}
