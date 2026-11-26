"""The evidence rules in FILTER.md section 4, as a first, mechanical pass over each claim in a justification.

The checker can prove a quote is not in the posting and can see some contradictions (years asked, "Senior" in the
text, a non-US location). It cannot judge meaning, so every "supported" it gives is marked for a hand check, and my
hand label is the one that counts (audit/claim-labels.csv).
"""
import re

from . import filter as filt
from . import rule

SUPPORTED, CONTRADICTED, INSUFFICIENT = "supported", "contradicted", "insufficient"
ABOUT = ("role", "experience", "location", "skills")
UNCOVERED = re.compile(r"\b(salary|visa|sponsor\w*|team size|interview\w*)\b", re.IGNORECASE)
CLAIM_YEARS = 3  # an ask of 3 or more years contradicts a claim that "about two years" fits, whatever G3's limit is
SENIOR_IN_TEXT = re.compile(r"\bsenior\s+(?:\w+\s+){0,2}(?:engineer|developer)s?\b", re.IGNORECASE)


def norm(text):
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = text.replace("–", "-").replace("—", "-").replace(" ", " ")
    return re.sub(r"\s+", " ", text).strip().lower()


def posting_text(job):
    return "\n".join((job.get("title") or "", (job.get("location") or {}).get("name") or "", rule.description_text(job)))


def label_claim(claim, job, spec, skills):
    """Returns (label, reason, needs_hand_check). `skills` is the résumé's skill list."""
    quote, about = claim.get("quote") or "", claim.get("about")
    title = job.get("title") or ""
    location = (job.get("location") or {}).get("name") or ""
    description = rule.description_text(job)
    if UNCOVERED.search(claim.get("claim", "")) and not UNCOVERED.search(description):
        return INSUFFICIENT, "the claim is about something the posting does not cover: I cannot tell", False
    if about == "experience":
        # Fixed 2026-11-25 after my claim labels (SHORTLIST.md, #15): a claim that itself states the years or the
        # seniority the posting asks for is not contradicted by them; only a claim that leaves them out is.
        text = claim.get("claim", "")
        too_many = [n for n in filt.years_asked(description) if n >= CLAIM_YEARS
                    and not re.search(rf"(?<![\d.]){n:g}(?![\d])", text)]
        senior = ((filt.find_words(title, spec["seniority_words"]) or SENIOR_IN_TEXT.findall(description))
                  and not re.search(r"\bsenior\b", text, re.IGNORECASE))
        if too_many or senior:
            what = (f"the posting asks for {', '.join(f'{n:g}' for n in too_many)} years" if too_many else
                    "the posting asks for a senior engineer")
            return CONTRADICTED, what, False
    if about == "location" and not filt.find_words(location, spec["us_words"]):
        return CONTRADICTED, f"the location \"{location}\" names no US place", False
    if not quote.strip():
        return INSUFFICIENT, "no quote: the posting has no sentence given for this claim", False
    if norm(quote) not in norm(posting_text(job)):
        return INSUFFICIENT, "the quote is not in the posting word for word", False
    if about == "skills" and not filt.find_words(quote, skills):
        return INSUFFICIENT, "the quote names none of the résumé's skills", False
    return SUPPORTED, "the quote is in the posting; whether it states the claim is checked by hand", True


def abstain(final_labels):
    """FILTER.md section 4: "I cannot tell if this fits" unless every role, experience and location claim is supported.

    final_labels: (about, label) pairs. A missing role, experience or location claim also means abstain."""
    needed = {"role", "experience", "location"}
    for about, label in final_labels:
        if about in needed and label != SUPPORTED:
            return True
    return not needed <= {about for about, _ in final_labels}
