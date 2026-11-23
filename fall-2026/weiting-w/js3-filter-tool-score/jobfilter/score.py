"""S-v1, the scorer from FILTER.md §1, with a traceable point for every point.

Three properties the implementation owes the document:

1. **Whole word, case-insensitive, body only.** `go` must not fire on "ongoing"
   or "Chicago"; that is wrong version W2. Multi-word signals match as phrases
   with the same word boundaries at each end.
2. **One firing per signal per posting.** Repetition is a property of the
   writer, not of the job.
3. **Every point carries its sentence.** A signal that fires records the word
   it matched, the character offsets, and the sentence it sat in. A score with
   no sentence behind it is a number I cannot defend, and the evidence rules in
   FILTER.md §2 need the span to label anything.

A posting with no body is **not** scored zero. `score()` returns `None` and the
caller must route it to `cannot_score`. Scoring it zero is wrong version W1.
"""

from __future__ import annotations

import re

from . import sections
from dataclasses import dataclass, field

SCORER_VERSION = "S-v5"

#: name -> (words, points each, cap). Straight from the FILTER.md §1 table.
SIGNALS: dict[str, tuple[tuple[str, ...], int, int]] = {
    # `infrastructure` was cut by A2 and reinstated by A5. A2's measurement
    # was right -- 177/177 of one board -- and its diagnosis was wrong: the
    # problem was the scorer being unable to tell a sentence about the company
    # from a sentence about the job. A4 fixed that, and with sections in place
    # the word fires 21 times across the scored postings, 20 of them in a
    # `company` section earning 0.
    "S1_core": (
        ("api", "backend", "distributed systems", "database", "microservice",
         "microservices", "infrastructure"),
        2, 6,
    ),
    # `go` cut by A2: 55 matches, at most 9 the language, 46 the English verb
    # ("you'll go deep", "go-to-market"). `golang` appears nowhere in the
    # corpus, so the Go language is simply undetectable here. Stated cost.
    "S2_language": (
        ("python", "java", "c++", "typescript", "javascript", "rust", "c#"),
        2, 4,
    ),
    "S3_graphics": (
        ("unity", "unreal", "rendering", "shader", "shaders", "game engine",
         "real-time 3d"),
        3, 6,
    ),
    "S4_ml": (
        ("machine learning", "pytorch", "tensorflow", "model training", "inference"),
        2, 4,
    ),
    # `0-2 years` / `1-2 years` cut by A2: one match in the corpus, on
    # "1-2 years of quota-carrying SaaS sales experience". A year range states
    # how much experience is wanted, not that new graduates may apply.
    #
    # None of the phrases that remain occurs in any of the 295 postings, so
    # S5 cannot fire on this corpus at all. That is not a bug: none of these
    # four boards said in words that a posting was open to new graduates.
    # tests/test_amendment_a2.py pins it, so the day a board does say it, the
    # test fails and this comment gets rewritten.
    "S5_newgrad": (
        ("new grad", "new graduate", "entry level", "entry-level", "early career",
         "university graduate"),
        4, 4,
    ),
    # A3: S6 was a list of literal strings and missed both other phrasings
    # ("minimum of 5 years") and other numbers in the same shape (3+, 4+, 9+
    # were never listed). An experience requirement is a NUMBER with a
    # threshold; `EXPERIENCE_WALL` below reads it as one. The entries here are
    # the non-numeric walls only.
    "S6_experience_wall": (
        ("phd required", "ph.d. required"),
        -6, -6,
    ),
    "S7_clearance_wall": (
        ("security clearance", "ts/sci", "must be a u.s. citizen"),
        -8, -8,
    ),
}

#: FILTER.md §1. Hand-set before measuring; the only number allowed to move.
THRESHOLD = 6

#: A3. The four ways this corpus writes an experience requirement. Read as a
#: number so that 3+, 4+ and 9+ are covered without being enumerated.
MIN_WALL_YEARS = 3
#: The range alternative comes FIRST on purpose. "2-5 years of experience"
#: states a minimum of two, and a generic `(\d+) years of experience` would
#: otherwise grab the 5 and report a five-year wall. Found by
#: test_the_scorer_and_the_evidence_rules_agree_about_every_body, which exists
#: because A3 applied one rule in two places and they could drift.
EXPERIENCE_WALL = re.compile(
    r"(?<!\w)(?:"
    r"(\d+)\s*-\s*\d+\s*years"
    r"|(\d+)\s*\+\s*years"
    r"|minimum of\s+(\d+)\s+years"
    r"|at least\s+(\d+)\s+years"
    r"|(\d+)\s+years of (?:industry |professional |relevant )?experience"
    r")",
    re.IGNORECASE,
)
EXPERIENCE_WALL_POINTS = -6

#: A4. A positive hit is worth less where the posting itself says it matters
#: less, and nothing where the text is not about the job. Penalties are never
#: scaled: a rule that can be evaded by moving a sentence is not a rule.
SECTION_WEIGHT = {
    sections.REQUIRED: 1.0,
    sections.DUTIES: 1.0,
    sections.OPTIONAL: 0.5,
    sections.COMPANY: 0.0,
    sections.UNLABELLED: 1.0,
}

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?\n])\s+")


def _pattern(word: str) -> re.Pattern:
    """Whole-word match that survives `+`, `#`, `-` and `/` inside a signal.

    `\\b` does the wrong thing next to a non-word character: `c++\\b` can never
    match, because there is no word boundary after `+`. So the boundary is
    written as "not flanked by a word character", which behaves correctly for
    `c++`, `c#`, `ts/sci`, `0-2 years` and plain words alike.
    """
    return re.compile(rf"(?<!\w){re.escape(word)}(?!\w)", re.IGNORECASE)


_COMPILED = {
    name: [(word, _pattern(word)) for word in words]
    for name, (words, _, _) in SIGNALS.items()
}


def _sentence_around(text: str, start: int, end: int, limit: int = 240) -> str:
    left = max(text.rfind(".", 0, start), text.rfind("\n", 0, start)) + 1
    right_candidates = [i for i in (text.find(".", end), text.find("\n", end)) if i != -1]
    right = min(right_candidates) + 1 if right_candidates else len(text)
    sentence = text[left:right].strip()
    if len(sentence) > limit:
        local = start - left
        sentence = sentence[max(0, local - limit // 2): local + limit // 2].strip()
    return " ".join(sentence.split())


@dataclass
class Hit:
    signal: str
    word: str
    points: int
    start: int
    end: int
    sentence: str
    section: str = sections.UNLABELLED
    raw_points: int | None = None     # before the A4 section weight

    def as_dict(self) -> dict:
        out = {
            "signal": self.signal, "word": self.word, "points": self.points,
            "span": [self.start, self.end], "sentence": self.sentence,
            "section": self.section,
        }
        if self.raw_points is not None and self.raw_points != self.points:
            out["points_before_section_weight"] = self.raw_points
        return out


@dataclass
class Score:
    total: int
    hits: list[Hit] = field(default_factory=list)
    per_signal: dict[str, int] = field(default_factory=dict)

    @property
    def shortlisted(self) -> bool:
        return self.total >= THRESHOLD

    def as_dict(self) -> dict:
        return {
            "scorer_version": SCORER_VERSION,
            "total": self.total,
            "threshold": THRESHOLD,
            "shortlisted": self.shortlisted,
            "per_signal": self.per_signal,
            "hits": [h.as_dict() for h in self.hits],
        }


def _experience_wall(body: str) -> Hit | None:
    """The highest stated requirement of >= MIN_WALL_YEARS, in any of A3's forms.

    Fires at most once, like every other signal, and records the span so the
    penalty can be read back to the sentence that caused it.
    """
    best = None
    for m in EXPERIENCE_WALL.finditer(body):
        years = next((int(g) for g in m.groups() if g), None)
        if years is None or years < MIN_WALL_YEARS:
            continue
        if best is None or years > best[0]:
            best = (years, m)
    if best is None:
        return None
    years, m = best
    return Hit(
        signal="S6_experience_wall", word=m.group(0), points=EXPERIENCE_WALL_POINTS,
        start=m.start(), end=m.end(),
        sentence=_sentence_around(body, m.start(), m.end()),
    )


def score(body: str | None) -> Score | None:
    """Score one body, or `None` when there is no body to score.

    `None` is not zero and the two must not be collapsed (W1).
    """
    if body is None or not body.strip():
        return None

    total = 0
    hits: list[Hit] = []
    per_signal: dict[str, int] = {}

    heading_spans = sections.heading_spans(body)

    wall = _experience_wall(body)
    if wall is not None:
        wall.section = sections.kind_at(body, wall.start, heading_spans)
        hits.append(wall)
        per_signal["S6_experience_wall"] = EXPERIENCE_WALL_POINTS
        total += EXPERIENCE_WALL_POINTS

    for name, (_, points, cap) in SIGNALS.items():
        earned = 0
        for word, pattern in _COMPILED[name]:
            match = pattern.search(body)
            if not match:
                continue
            # cap is a floor for the penalty signals and a ceiling for the rest
            if points >= 0:
                remaining = cap - earned
                if remaining <= 0:
                    break
                awarded = min(points, remaining)
            else:
                remaining = cap - earned
                if remaining >= 0:
                    break
                awarded = max(points, remaining)
            section = sections.kind_at(body, match.start(), heading_spans)
            weighted = (
                int(awarded * SECTION_WEIGHT[section]) if awarded > 0 else awarded
            )
            earned += weighted
            hits.append(
                Hit(
                    signal=name, word=word, points=weighted,
                    start=match.start(), end=match.end(),
                    sentence=_sentence_around(body, match.start(), match.end()),
                    section=section, raw_points=awarded,
                )
            )
        if earned:
            per_signal[name] = earned
            total += earned

    return Score(total=total, hits=hits, per_signal=per_signal)
