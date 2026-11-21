"""Questions refused before any model call (CONTRACT.md items 3 and 4)."""

import re
from dataclasses import dataclass

RULES = (
    ("contact_data",
     re.compile(r"\b(e-?mails?|phones?|telephone|contact (person|details|info\w*)|"
                r"point of contact|poc|attorneys?|lawyers?|preparers?|addresses?)\b", re.I),
     "Contact, attorney, preparer and address data are not loaded and are never revealed."),
    ("immigration_prediction",
     re.compile(r"\b(will|would|could|can)\b[^?]*\b(i|my|me|he|she|they|someone)\b[^?]*"
                r"\b(get|be|receive)\b[^?]*\b(approved|selected|sponsored|a visa|an h-?1b|h-?1b)\b", re.I),
     "SponsorSQL does not predict whether a person will be approved, selected or sponsored."),
    ("immigration_prediction",
     re.compile(r"\b(chances?|odds|probability|likel(y|ihood)|guarantee\w*)\b[^?]*"
                r"\b(approv\w*|sponsor\w*|visa|selected|lottery)\b", re.I),
     "SponsorSQL does not estimate approval or sponsorship odds; an LCA is not an approval."),
    ("modification",
     re.compile(r"\b(delete|drop|update|insert|modify|change|alter|overwrite)\b[^?]*"
                r"\b(data|table|records?|rows?|answer key|key|database)\b", re.I),
     "SponsorSQL is read-only; changes to the data or answer key need a human outside the agent."),
)


@dataclass
class ScreenResult:
    refuse: bool
    category: str = ""
    reason: str = ""


def screen(question) -> ScreenResult:
    text = question or ""
    if not text.strip():
        return ScreenResult(True, "empty", "No question was given.")
    for category, pattern, reason in RULES:
        if pattern.search(text):
            return ScreenResult(True, category, reason)
    return ScreenResult(False)
