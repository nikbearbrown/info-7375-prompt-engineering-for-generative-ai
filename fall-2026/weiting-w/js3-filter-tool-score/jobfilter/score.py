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
from dataclasses import dataclass, field

SCORER_VERSION = "S-v1"

#: name -> (words, points each, cap). Straight from the FILTER.md §1 table.
SIGNALS: dict[str, tuple[tuple[str, ...], int, int]] = {
    "S1_core": (
        ("api", "backend", "distributed systems", "database", "microservice",
         "microservices", "infrastructure"),
        2, 6,
    ),
    "S2_language": (
        ("python", "java", "c++", "typescript", "javascript", "go", "rust", "c#"),
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
    "S5_newgrad": (
        ("new grad", "new graduate", "entry level", "entry-level", "early career",
         "university graduate", "0-2 years", "1-2 years"),
        4, 4,
    ),
    "S6_experience_wall": (
        ("5+ years", "6+ years", "7+ years", "8+ years", "10+ years",
         "phd required", "ph.d. required"),
        -6, -6,
    ),
    "S7_clearance_wall": (
        ("security clearance", "ts/sci", "must be a u.s. citizen"),
        -8, -8,
    ),
}

#: FILTER.md §1. Hand-set before measuring; the only number allowed to move.
THRESHOLD = 6

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

    def as_dict(self) -> dict:
        return {
            "signal": self.signal, "word": self.word, "points": self.points,
            "span": [self.start, self.end], "sentence": self.sentence,
        }


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


def score(body: str | None) -> Score | None:
    """Score one body, or `None` when there is no body to score.

    `None` is not zero and the two must not be collapsed (W1).
    """
    if body is None or not body.strip():
        return None

    total = 0
    hits: list[Hit] = []
    per_signal: dict[str, int] = {}

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
            earned += awarded
            hits.append(
                Hit(
                    signal=name, word=word, points=awarded,
                    start=match.start(), end=match.end(),
                    sentence=_sentence_around(body, match.start(), match.end()),
                )
            )
        if earned:
            per_signal[name] = earned
            total += earned

    return Score(total=total, hits=hits, per_signal=per_signal)
