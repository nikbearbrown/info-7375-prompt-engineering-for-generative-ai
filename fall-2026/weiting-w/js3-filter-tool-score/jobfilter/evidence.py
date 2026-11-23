"""E-v1: labelling claims against a posting's own text.

The temptation this module exists to resist is wrong version W4: label a claim
`supported` because the signal that produced it fired. That is relevance
standing in for entailment, and it makes every shortlist entry look
well-evidenced at the cost of the entries meaning anything.

So the design is **abstention by construction**. A claim is not free text that
some heuristic guesses at. A claim is a typed object, and E-v1 can decide only
three kinds:

- `MENTIONS(word)` — "the posting's text contains <word>". Decidable: the span
  either contains the word or it does not.
- `REQUIRES_MIN_YEARS(n)` — "the posting asks for at least n years". Decidable
  from an experience-wall span, and it can **contradict** a claim about being
  open to newcomers.
- `OPEN_TO_NEW_GRADS` — decidable only when the text says so in words, or when
  an experience wall contradicts it.

Everything else returns `insufficient` with the reason "E-v1 has no rule that
decides this claim from a span". Not a guess, not a hedge: a statement that the
rules in FILTER.md §2 do not reach it. On this corpus that happens constantly,
and it should.

`label_claim(text, span)` is the loose front door used in tests and in the
report: it recognises the one mechanically-decidable English shape ("mentions
X") and abstains on everything else, which is the behaviour the whole section
is about.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

EVIDENCE_VERSION = "E-v1"

SUPPORTED = "supported"
CONTRADICTED = "contradicted"
INSUFFICIENT = "insufficient"

#: "5+ years", "at least 7 years", "7-10 years"
_YEARS = re.compile(
    r"(?:(\d+)\s*\+\s*years)|(?:at least\s+(\d+)\s+years)|(?:(\d+)\s*-\s*\d+\s*years)",
    re.IGNORECASE,
)

_NEWGRAD = re.compile(
    r"new grad(?:uate)?s?|entry[- ]level|early career|university graduate",
    re.IGNORECASE,
)


@dataclass
class Claim:
    """One assertion about a posting, with the span it is judged against."""

    kind: str
    text: str
    span: str | None = None
    span_field: str | None = None
    arg: object = None

    label: str = INSUFFICIENT
    reason: str = ""
    detail: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "kind": self.kind,
            "claim": self.text,
            "label": self.label,
            "reason": self.reason,
            "span": self.span,
            "span_field": self.span_field,
            **({"detail": self.detail} if self.detail else {}),
        }


def _min_years(span: str) -> int | None:
    best = None
    for m in _YEARS.finditer(span):
        value = next((int(g) for g in m.groups() if g), None)
        if value is not None:
            best = value if best is None else max(best, value)
    return best


def judge(claim: Claim) -> Claim:
    """Apply E-v1 to one claim. Mutates and returns it."""
    if claim.span is None or not claim.span.strip():
        claim.label = INSUFFICIENT
        claim.reason = (
            "no span: the posting carries no text for this claim to be judged "
            "against (FILTER.md §2, abstention case 1 or 2)"
        )
        return claim

    span = claim.span

    if claim.kind == "MENTIONS":
        word = str(claim.arg)
        pattern = re.compile(rf"(?<!\w){re.escape(word)}(?!\w)", re.IGNORECASE)
        if pattern.search(span):
            claim.label = SUPPORTED
            claim.reason = f"the span contains {word!r} as a whole word"
        else:
            claim.label = INSUFFICIENT
            claim.reason = f"{word!r} does not occur in this span"
        return claim

    if claim.kind == "REQUIRES_MIN_YEARS":
        found = _min_years(span)
        if found is None:
            claim.label = INSUFFICIENT
            claim.reason = "the span states no number of years"
        else:
            claim.detail = {"years_in_span": found}
            claim.label = SUPPORTED if found >= int(claim.arg) else CONTRADICTED
            claim.reason = (
                f"the span asks for {found} years; the claim was "
                f"'at least {claim.arg}'"
            )
        return claim

    if claim.kind == "OPEN_TO_NEW_GRADS":
        years = _min_years(span)
        if years is not None and years >= 3:
            claim.label = CONTRADICTED
            claim.detail = {"years_in_span": years}
            claim.reason = (
                f"the span asks for {years} years of experience, which is "
                "incompatible with being open to new graduates"
            )
        elif _NEWGRAD.search(span):
            claim.label = SUPPORTED
            claim.reason = "the span says so in words"
        else:
            claim.label = INSUFFICIENT
            claim.reason = (
                "the span neither says the posting is open to new graduates "
                "nor states an experience requirement; absence is not denial "
                "(FILTER.md §2 E3)"
            )
        return claim

    claim.label = INSUFFICIENT
    claim.reason = (
        f"E-v1 has no rule that decides a claim of kind {claim.kind!r} from a "
        "span. Abstention is the answer, not a guess."
    )
    return claim


_MENTIONS_SHAPE = re.compile(
    r"^(?:the posting(?:'s text)?\s+)?mentions\s+(.+?)\.?$", re.IGNORECASE
)


def label_claim(text: str, span: str | None) -> str:
    """Label a claim written in English. Abstains unless the shape is decidable.

    Exactly one English shape is decidable under E-v1 — "the posting mentions
    X" — because it is a statement about the text rather than about the job.
    "this is primarily a Python job" is a statement about the job and E-v1 has
    no rule that gets there from a span, so it abstains. That difference is the
    whole of rule E2.
    """
    m = _MENTIONS_SHAPE.match(text.strip())
    if m:
        return judge(Claim(kind="MENTIONS", text=text, span=span, arg=m.group(1))).label
    return judge(Claim(kind="UNDECIDABLE", text=text, span=span)).label


def claims_for(decision) -> list[Claim]:
    """The claims a shortlist entry makes, each tied to the span behind it.

    One `MENTIONS` claim per signal word that fired, judged against the
    sentence the scorer recorded — never against the whole body, so a claim
    cannot borrow support from a sentence somewhere else in the posting.
    Then one `OPEN_TO_NEW_GRADS` claim, judged against the posting's body,
    because that is the question a shortlist is really answering for me.
    """
    posting = decision.posting
    out: list[Claim] = []

    if decision.score is not None:
        for hit in decision.score.hits:
            out.append(judge(Claim(
                kind="MENTIONS",
                text=f"the posting mentions {hit.word}",
                span=hit.sentence,
                span_field="descriptionPlain (sentence around the match)",
                arg=hit.word,
            )))

    out.append(judge(Claim(
        kind="OPEN_TO_NEW_GRADS",
        text="this posting is open to someone with no professional experience",
        span=posting.body,
        span_field="descriptionPlain" if posting.has_body else None,
        arg=None,
    )))
    return out


def summarise(claims: list[Claim]) -> dict:
    counts = {SUPPORTED: 0, CONTRADICTED: 0, INSUFFICIENT: 0}
    for c in claims:
        counts[c.label] += 1
    return counts
