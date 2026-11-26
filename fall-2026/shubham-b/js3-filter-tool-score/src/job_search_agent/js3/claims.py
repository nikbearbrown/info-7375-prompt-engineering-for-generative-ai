"""FILTER.md §2: the justification claims C1–C5 and their evidence labels.

Every label rests on a quoted span of the posting's own text (title, ``location.name``,
content, department names) or on the absence of one. Silence is never support.
"""

from __future__ import annotations

import html
import re
from dataclasses import asdict, dataclass
from typing import Any

from job_search_agent.js3.filter import Scored
from job_search_agent.models import LocationLabel
from job_search_agent.rule.exclusions import phrases_in_text
from job_search_agent.rule.skills import _pattern  # same §6.2 pattern the filter used
from job_search_agent.text import clean_html

SUPPORTED, CONTRADICTED, INSUFFICIENT = "supported", "contradicted", "insufficient"

KIRAN_YEARS = 4
"""FILTER.md §2 C4: résumé experience 2020-08..2022-08 and 2022-09..2024-12,
52 months."""

MIN_CONTENT_CHARS = 200
"""FILTER.md §2 rule 3: below this the agent cannot tell anything but the title."""

_BLOCK_TAG = re.compile(r"</?(?:li|p|br|div|h[1-6]|ul|ol|tr|td)\b[^>]*>", re.IGNORECASE)
_SENTENCE = re.compile(r"(?<=[.!?;])\s+")
_EXPERIENCE = re.compile(r"\bexperience\b", re.IGNORECASE)
_YEARS = re.compile(
    r"(?<![\d.])(\d{1,2})\s*(?:\+|plus)?\s*(?:(?:-|–|—|to)\s*\d{1,2}\s*\+?\s*)?years?\b",
    re.IGNORECASE,
)
_SPONSOR_NO = re.compile(
    r"\b(?:unable|not able) to (?:provide |offer )?(?:visa |immigration )?sponsor"
    r"|\b(?:will|do|does|can|could|is|are) not (?:be )?"
    r"(?:provide |offer |able to )?(?:visa |immigration )?sponsor"
    r"|\b(?:cannot|can't|won't|don't|doesn't) (?:provide |offer )?"
    r"(?:visa |immigration )?sponsor"
    r"|\bwithout (?:the need for |requiring )?(?:current or future )?"
    r"(?:visa |employer |immigration )?sponsorship"
    r"|\bnot (?:eligible for|offering|provide) (?:visa |immigration )?sponsorship"
    r"|\bno (?:visa |immigration )?sponsorship"
    r"|\b(?:do|does|will) not (?:currently )?(?:offer |provide )?(?:visa )?sponsor"
    r"|\bsponsorship is not (?:currently )?(?:available|offered|provided)",
    re.IGNORECASE,
)
_SPONSOR_YES = re.compile(
    r"\bvisa sponsorship (?:is )?(?:available|offered|provided)"
    r"|\bsponsorship (?:is )?available"
    r"|\bwill sponsor\b"
    r"|\b(?:we|stripe|figma|ramp|linear) (?:can |do |does |will )?"
    r"(?:offer |provide )?(?:visa )?sponsor",
    re.IGNORECASE,
)
_VISA_CONTEXT = re.compile(
    r"\b(?:visas?|immigration|h-?1b|opt|work authori[sz]ation|green card)\b",
    re.IGNORECASE,
)
"""A YES match counts only in a sentence about visas or work authorization (review fix:
"We sponsored Neal Shipley" and "We will sponsor you for relocation" are not offers)."""


@dataclass(frozen=True, slots=True)
class Claim:
    """One justification claim and its evidence label."""

    claim_id: str
    statement: str
    label: str
    field: str | None  # the posting field the quote comes from
    quote: str | None  # the span, with a little context
    note: str


@dataclass(frozen=True, slots=True)
class Justification:
    """The claims for one kept posting and the agent's overall answer."""

    key: str
    title: str
    claims: tuple[Claim, ...]
    answer: str
    abstained: bool

    def to_dict(self) -> dict[str, Any]:
        """JSON-ready form."""
        return {**asdict(self), "claims": [asdict(c) for c in self.claims]}


def _quote(text: str, start: int, end: int, pad: int = 60) -> str:
    left = max(0, start - pad)
    right = min(len(text), end + pad)
    return ("…" if left else "") + text[left:right] + ("…" if right < len(text) else "")


def segments(content_raw: str) -> list[str]:
    """Cleaned sentences of the content, split at block tags and sentence ends."""
    blocks = _BLOCK_TAG.sub("\n", html.unescape(content_raw)).split("\n")
    out: list[str] = []
    for block in blocks:
        cleaned = clean_html(block)
        out += [s for s in _SENTENCE.split(cleaned) if s]
    return out


def stated_minimum_years(content_raw: str) -> tuple[int, str] | None:
    """The highest minimum number of years in a sentence that mentions experience."""
    best: tuple[int, str] | None = None
    for sentence in segments(content_raw):
        if not _EXPERIENCE.search(sentence):
            continue
        for m in _YEARS.finditer(sentence):
            years = int(m.group(1))
            if years <= 30 and (best is None or years > best[0]):
                best = (years, _quote(sentence, m.start(), m.end()))
    return best


def _role(s: Scored) -> Claim:
    title = s.posting.title
    statement = "The job is a role Kiran targets."
    if s.markers:
        return Claim(
            "C1",
            statement,
            CONTRADICTED,
            "$.title",
            title,
            f"seniority marker(s): {', '.join(s.markers)}",
        )
    if s.family_roles:
        return Claim(
            "C1",
            f"The job is a {s.family_roles[0]} role, one Kiran targets.",
            SUPPORTED,
            "$.title",
            title,
            "R1 role phrase in the title",
        )
    if s.generic_word:
        return Claim(
            "C1",
            statement,
            INSUFFICIENT,
            "$.title",
            title,
            f"only the generic word '{s.generic_word}': "
            "I cannot tell which kind of engineering",
        )
    return Claim(
        "C1", statement, CONTRADICTED, "$.title", title, "no role word in the title"
    )


def _skills(s: Scored) -> list[Claim]:
    claims = []
    fields = {"$.title": s.posting.title, "$.content": s.posting.content_raw}
    fields |= {
        f"$.departments[{i}].name": d for i, d in enumerate(s.posting.department_names)
    }
    for ev in s.skills:
        text = clean_html(fields.get(ev.posting_path, ""))
        m = _pattern(ev.term).search(text)
        quote = _quote(text, m.start(), m.end()) if m else None
        claims.append(
            Claim(
                "C2",
                f"The posting asks for {ev.term}, which Kiran has.",
                SUPPORTED,
                ev.posting_path,
                quote,
                f"résumé {ev.resume_path}",
            )
        )
    return claims


def _location(s: Scored) -> Claim:
    statement = "The job is in the United States."
    label = {
        LocationLabel.US_BASED: SUPPORTED,
        LocationLabel.NON_US: CONTRADICTED,
        LocationLabel.NOT_ESTABLISHED: INSUFFICIENT,
    }[s.location.label]
    field = s.location.evidence[0]
    quote = s.posting.location_name if field == "$.location.name" else None
    note = (
        s.location.reason
        if label != INSUFFICIENT
        else f"I cannot tell: {s.location.reason}"
    )
    return Claim("C3", statement, label, field, quote, note)


def _experience(s: Scored) -> Claim:
    statement = (
        f"Kiran's experience ({KIRAN_YEARS} years) meets the posting's stated minimum."
    )
    found = stated_minimum_years(s.posting.content_raw)
    if found is None:
        return Claim(
            "C4",
            statement,
            INSUFFICIENT,
            None,
            None,
            "I cannot tell: no number of years in a sentence about experience",
        )
    years, quote = found
    label = SUPPORTED if years <= KIRAN_YEARS else CONTRADICTED
    return Claim(
        "C4",
        statement,
        label,
        "$.content",
        quote,
        f"highest stated minimum: {years} years",
    )


def _authorization(s: Scored) -> Claim:
    statement = (
        "The posting's terms do not rule out a candidate on F-1/OPT "
        "who will need sponsorship."
    )
    no: tuple[str, str] | None = None
    yes: tuple[str, str] | None = None
    for sentence in segments(s.posting.content_raw):
        if no is None and (m := _SPONSOR_NO.search(sentence)):
            no = ("$.content", _quote(sentence, m.start(), m.end()))
        elif (
            yes is None
            and (m := _SPONSOR_YES.search(sentence))
            and _VISA_CONTEXT.search(sentence)
        ):
            yes = ("$.content", _quote(sentence, m.start(), m.end()))
    barred = [
        p
        for p in phrases_in_text(clean_html(s.posting.content_raw))
        if "unpaid" not in p
    ]
    if barred and no is None:
        no = ("$.content", barred[0])
    if no and yes:
        return Claim(
            "C5",
            statement,
            INSUFFICIENT,
            "$.content",
            f"{no[1]} | {yes[1]}",
            "I cannot tell: the text says both",
        )
    if no:
        return Claim(
            "C5",
            statement,
            CONTRADICTED,
            no[0],
            no[1],
            "the text rules out sponsorship, or requires citizenship or clearance",
        )
    if yes:
        return Claim(
            "C5", statement, SUPPORTED, yes[0], yes[1], "the text offers sponsorship"
        )
    return Claim(
        "C5",
        statement,
        INSUFFICIENT,
        None,
        None,
        "I cannot tell: the text says nothing about sponsorship, "
        "citizenship or clearance",
    )


def justify(s: Scored) -> Justification:
    """Builds and labels the C1–C5 claims for one posting and the overall answer."""
    claims = [_role(s), *_skills(s), _location(s), _experience(s), _authorization(s)]
    short = len(clean_html(s.posting.content_raw)) < MIN_CONTENT_CHARS
    if short:  # FILTER.md §2 rule 3
        claims = [
            c
            if c.claim_id == "C1"
            else Claim(
                c.claim_id,
                c.statement,
                INSUFFICIENT,
                None,
                None,
                "I cannot tell: under 200 characters of text",
            )
            for c in claims
        ]
    contradicted = [c.claim_id for c in claims if c.label == CONTRADICTED]
    unsure = sorted(
        {
            c.claim_id
            for c in claims
            if c.label == INSUFFICIENT and c.claim_id in ("C3", "C4", "C5")
        }
    )
    if short:
        answer, abstained = (
            "I cannot tell: the posting has too little text to check.",
            True,
        )
    elif contradicted:
        answer = (
            "Matches the filter, but the posting's text contradicts "
            f"{', '.join(contradicted)}."
        )
        abstained = bool(unsure)
        if unsure:
            answer += f" I cannot tell on: {', '.join(unsure)}."
    elif unsure:
        answer, abstained = (
            "Matches the filter; I cannot tell whether it fits on: "
            f"{', '.join(unsure)}.",
            True,
        )
    else:
        answer, abstained = (
            "Matches the filter and every claim is supported by the posting's text.",
            False,
        )
    order = {CONTRADICTED: 0, SUPPORTED: 1, INSUFFICIENT: 2}  # FILTER.md §2 rule 4
    claims.sort(key=lambda c: order[c.label])
    return Justification(s.key, s.posting.title, tuple(claims), answer, abstained)
