"""Grounding check for shortlist justification claims - FILTER.md "Evidence
rules". This is the deterministic layer every claim must pass through; the
shortlist step (js3/shortlist.py, shortlist-v1, committed in 0fb5cef) calls
it on every claim before a justification is shown.

A claim is {"claim": str, "quote": str | None}. The quote is the evidence the
claim cites. Labels:

  supported     the quote, whitespace-collapsed, is an exact (case-sensitive)
                substring of field_text(posting, "title") or
                field_text(posting, "content"). "field" names which one.
  insufficient  anything else: no quote, a blank quote, or a quote that is not
                in the posting's own text. A claim is never upgraded to
                supported without the substring check passing.
  contradicted  NOT produced by this layer. Detecting that the posting's text
                conflicts with a claim needs judgment (the shortlist's Claude
                step, still to build); this layer can only verify that a
                cited quote exists. Until then, contradicted never appears.

The same text normalization as js3.filter.field_text is used, so a quote the
filter extracted always verifies here.
"""
import re

from js3.filter import FIELDS, field_text

LABELS = ("supported", "contradicted", "insufficient")


def _norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def label_claim(posting, claim):
    quote = _norm(claim.get("quote"))
    out = {"claim": claim["claim"], "quote": claim.get("quote"), "label": "insufficient", "field": None}
    if not quote:
        return out
    for field in FIELDS:
        if quote in field_text(posting, field):
            out["label"], out["field"] = "supported", field
            return out
    return out


def label_claims(posting, claims):
    return [label_claim(posting, c) for c in claims]
