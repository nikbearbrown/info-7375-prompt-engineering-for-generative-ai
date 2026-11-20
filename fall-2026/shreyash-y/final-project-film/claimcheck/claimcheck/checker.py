"""The citation checker: plain code, no model. It decides whether an answer may be shown.

An "answered" reply passes only if all of these hold:
  1. doc_id names a document we actually gave the answerer;
  2. the quote is at least MIN_QUOTE_CHARS long;
  3. the quote appears in that document word for word (whitespace and quote marks normalised);
  4. every number in the answer (amounts, percentages, day counts) appears in the quote;
  5. at least half of the answer's content words appear in the quote.
A "not_in_documents" reply always passes: refusing is allowed.

Rules 4 and 5 are proxies for "the quote contains the answer". They can be fooled
(see the Limits section of each eval report); they are deliberately simple so a
reviewer can predict every verdict by hand.
"""

import re
from dataclasses import dataclass, field

from .contract import Answer

CHECKER_VERSION = "0.1.0"
MIN_QUOTE_CHARS = 15
MIN_WORD_SUPPORT = 0.5

_QUOTE_MARKS = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-"})
_SECTION_REF = re.compile(r"\b\d+\([a-z]\)", re.IGNORECASE)
_NUMBER = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")
_WORD = re.compile(r"[a-z]+")
STOPWORDS = frozenset(
    """that this with from have were will would there their which about under other these those
    than then them they what when where your yours does into only also each such over more most
    some very just being been covered cover covers coverage policy section insured answer yes""".split()
)


def normalise(text: str) -> str:
    return " ".join(text.translate(_QUOTE_MARKS).split())


def numbers(text: str) -> set[str]:
    text = _SECTION_REF.sub(" ", text)
    return {n.rstrip(",.") for n in _NUMBER.findall(text)}


def content_words(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if len(w) >= 4 and w not in STOPWORDS}


@dataclass
class CheckResult:
    passed: bool
    reasons: list[str] = field(default_factory=list)


def check(ans: Answer, docs: dict[str, str]) -> CheckResult:
    if ans.status == "not_in_documents":
        return CheckResult(True, ["refusal: nothing to verify"])

    reasons = []
    if ans.doc_id not in docs:
        reasons.append(f"unknown doc_id {ans.doc_id!r}")
    quote = normalise(ans.quote)
    if len(quote) < MIN_QUOTE_CHARS:
        reasons.append(f"quote shorter than {MIN_QUOTE_CHARS} characters")
    elif ans.doc_id in docs and quote not in normalise(docs[ans.doc_id]):
        reasons.append("quote not found word for word in the document")

    missing_numbers = sorted(numbers(ans.answer) - numbers(ans.quote))
    if missing_numbers:
        reasons.append(f"answer has number(s) not in the quote: {', '.join(missing_numbers)}")

    words = content_words(ans.answer)
    if len(words) >= 2:
        supported = len(words & content_words(ans.quote)) / len(words)
        if supported < MIN_WORD_SUPPORT:
            reasons.append(f"only {supported:.0%} of the answer's content words are in the quote")

    return CheckResult(not reasons, reasons or ["quote verified"])
