"""Which part of a posting a span sits in (FILTER.md §7 A4).

A posting is not one undifferentiated block of text. It has a company blurb, a
description of the work, a list of requirements, a list of things that would be
nice, and a tail of benefits and legal notices. A word in the first and the
last of those says nothing about the job, and a word in the "nice to have" list
says something much weaker than the same word in the requirements.

The scorer could not tell them apart, and two consequences showed up in the
measurements before this module existed:

- every Ramp posting scored +2 on `infrastructure` from "Ramp is building the
  smart infrastructure for finance teams", its company blurb (A2 cut the word);
- two of the six shortlisted postings scored **all** their points from a
  NICE TO HAVES block while their requirements asked for Swift and a year of
  mobile development (recorded, unfixed, until A4).

The headings are regular enough to read. These are the ones that occur in the
corpus, grouped by what they introduce; matching is on a normalised line, so
`WHAT YOU'LL DO`, `What You'll Do` and `WHAT YOU’LL DO` are one entry.
"""

from __future__ import annotations

import re

COMPANY = "company"        # blurb, benefits, legal, location, compensation
DUTIES = "duties"          # what the job involves
REQUIRED = "required"      # what the posting demands
OPTIONAL = "optional"      # nice to have
UNLABELLED = "unlabelled"  # before any heading, or a heading we do not know

#: normalised heading -> kind. Normalisation lower-cases, converts curly
#: apostrophes and collapses whitespace and hyphens.
HEADINGS: dict[str, str] = {}

def _add(kind: str, *names: str) -> None:
    for n in names:
        HEADINGS[normalise(n)] = kind


def normalise(line: str) -> str:
    s = line.strip().lower().replace("’", "'").replace("‘", "'")
    s = s.replace("-", " ").replace("_", " ")
    return re.sub(r"\s+", " ", s).strip(" :")


# "about the role" describes the job, not the company -- it is the section that
# says "In this role, you will build ...". Classifying it as COMPANY was the
# first version's bug, caught by reading the predicted effect before applying
# it: it would have dropped a posting whose points came from its own role
# description.
_add(DUTIES, "what you'll do", "what you will do", "the role", "responsibilities",
     "what you'll be doing", "in this role", "about the role", "about this role",
     "role overview", "the opportunity")
_add(REQUIRED, "what you need", "what you'll need", "who you are",
     "what we're looking for", "requirements", "qualifications",
     "minimum qualifications", "what you bring", "you have")
_add(OPTIONAL, "nice to haves", "nice to have", "nice to haves:", "bonus points",
     "preferred qualifications", "it's a plus if", "pluses")
_add(COMPANY, "about ramp", "about us", "about linear",
     "about spotify", "benefits available to all full time ramp employees (global)",
     "united states", "canada", "united kingdom", "referral instructions",
     "other notices", "where you'll be", "what we offer", "compensation",
     "location & work mode", "learn how we think and work", "our tech",
     "benefits", "equal opportunity", "perks")

#: A heading line: short, no sentence punctuation, and either all caps or
#: title-ish. The classifier only trusts lines it can also find in HEADINGS,
#: so a wrong guess here costs nothing -- see `kind_at`.
_HEADING_SHAPE = re.compile(r"^[A-Za-z][A-Za-z'’/&()\-, ]{2,70}:?$")


def heading_spans(body: str) -> list[tuple[int, str]]:
    """(offset, kind) for every recognised heading, in order."""
    out: list[tuple[int, str]] = []
    offset = 0
    for line in body.splitlines(keepends=True):
        stripped = line.strip()
        if stripped and _HEADING_SHAPE.match(stripped):
            kind = HEADINGS.get(normalise(stripped))
            if kind:
                out.append((offset, kind))
        offset += len(line)
    return out


def kind_at(body: str, position: int, spans=None) -> str:
    """Which kind of section `position` falls in. UNLABELLED when unknown."""
    spans = heading_spans(body) if spans is None else spans
    kind = UNLABELLED
    for offset, k in spans:
        if offset <= position:
            kind = k
        else:
            break
    return kind


def coverage(body: str) -> dict:
    """How much of a body this module can attribute. Used by the report."""
    spans = heading_spans(body)
    return {
        "headings_found": len(spans),
        "kinds": sorted({k for _, k in spans}),
        "first_heading_at": spans[0][0] if spans else None,
    }
