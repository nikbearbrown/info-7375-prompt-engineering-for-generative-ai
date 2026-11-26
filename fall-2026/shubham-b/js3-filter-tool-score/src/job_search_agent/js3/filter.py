"""The FILTER.md §1 scored filter.

The numbers live in the ``toml`` block between ``<!-- filter:begin -->`` and
``<!-- filter:end -->`` in FILTER.md; this module reads them from there and holds none
of its own. Matching reuses the CONTRACT §6 helpers (role phrases, skills, location,
exclusion phrases) so the JS1 golden tests still pin those parts.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from job_search_agent.errors import ConfigError
from job_search_agent.models import LocationCheck, LocationLabel, Posting, SkillEvidence
from job_search_agent.rule.exclusions import find_exclusions
from job_search_agent.rule.location import CONTENT_PATH, classify_location
from job_search_agent.rule.skills import match_skills
from job_search_agent.rule.title import normalize_title, title_check
from job_search_agent.rule.verdict import RuleInputs
from job_search_agent.text import clean_html

_BLOCK = re.compile(
    r"<!-- filter:begin -->\s*```toml\n(.*?)```\s*<!-- filter:end -->", re.DOTALL
)


@dataclass(frozen=True, slots=True)
class FilterSpec:
    """The FILTER.md §1 numbers and word lists."""

    version: str
    threshold: int
    family_phrase: int
    generic_words: tuple[str, ...]
    generic_weight: int
    generic_blockers: tuple[str, ...]
    seniority_markers: tuple[str, ...]
    seniority_weight: int
    per_skill: int
    skill_cap: int
    topic_words: tuple[str, ...]
    topic_weight: int
    location_points: dict[LocationLabel, int]
    exclusion_weight: int


def parse_filter(text: str) -> FilterSpec:
    """Parses the filter block of a FILTER.md text.

    Raises:
        ConfigError: If there is not exactly one block, or a key is missing.
    """
    blocks = _BLOCK.findall(text)
    if len(blocks) != 1:
        raise ConfigError(
            f"FILTER.md must hold exactly one filter block, found {len(blocks)}"
        )
    try:
        d: dict[str, Any] = tomllib.loads(blocks[0])
        t, s, tp, loc = d["title"], d["skills"], d["topic"], d["location"]
        return FilterSpec(
            version=str(d["version"]),
            threshold=int(d["threshold"]),
            family_phrase=int(t["family_phrase"]),
            generic_words=tuple(t["generic_words"]),
            generic_weight=int(t["generic_weight"]),
            generic_blockers=tuple(t.get("generic_blockers", ())),  # added in v0.3
            seniority_markers=tuple(t["seniority_markers"]),
            seniority_weight=int(t["seniority_weight"]),
            per_skill=int(s["per_skill"]),
            skill_cap=int(s["cap"]),
            topic_words=tuple(tp["words"]),
            topic_weight=int(tp["weight"]),
            location_points={
                LocationLabel.US_BASED: int(loc["us_based"]),
                LocationLabel.NOT_ESTABLISHED: int(loc["not_established"]),
                LocationLabel.NON_US: int(loc["non_us"]),
            },
            exclusion_weight=int(d["exclusion"]["weight"]),
        )
    except (tomllib.TOMLDecodeError, KeyError, TypeError, ValueError) as exc:
        raise ConfigError(f"FILTER.md filter block is invalid: {exc}") from exc


def load_filter(path: Path) -> FilterSpec:
    """Reads and parses a FILTER.md file."""
    return parse_filter(path.read_text(encoding="utf-8"))


def whole_words(words: tuple[str, ...]) -> re.Pattern[str] | None:
    """Case-insensitive pattern for any of ``words``.

    A match has no letter or digit around it.
    """
    if not words:
        return None
    alts = "|".join(r"\s+".join(map(re.escape, w.split())) for w in words)
    return re.compile(rf"(?<![A-Za-z0-9])(?:{alts})(?![A-Za-z0-9])", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class Scored:
    """One posting's score, every component kept so it can be recomputed by hand."""

    key: str
    board: str
    posting: Posting
    title_basis: str  # "family" | "generic" | "none"
    family_roles: tuple[str, ...]
    generic_word: str | None
    generic_blocker: str | None
    markers: tuple[str, ...]
    skills: tuple[SkillEvidence, ...]
    topic_words: tuple[str, ...]
    location: LocationCheck
    exclusions: tuple[str, ...]
    points: dict[str, int]
    total: int
    kept: bool

    def breakdown(self) -> str:
        """``R1 4 + R4 2 + ... = 7`` with only non-zero components."""
        parts = " + ".join(f"{k} {v}" for k, v in self.points.items() if v)
        return f"{parts or '0'} = {self.total}"


def score(
    posting: Posting, key: str, board: str, spec: FilterSpec, inputs: RuleInputs
) -> Scored:
    """Scores one posting under FILTER.md §1. The caller handles a missing title."""
    norm = normalize_title(posting.title)
    family = tuple(title_check(posting.title, inputs.roles).matched_roles)
    generic_pat = whole_words(spec.generic_words)
    generic = generic_pat.search(norm) if generic_pat and not family else None
    blocker_pat = whole_words(spec.generic_blockers)
    blocker = blocker_pat.search(norm) if blocker_pat and generic else None
    if blocker:  # v0.3: a specialty word means R2's generic word names a different job
        generic = None
    marker_pat = whole_words(spec.seniority_markers)
    markers = (
        tuple(dict.fromkeys(m.group(0).lower() for m in marker_pat.finditer(norm)))
        if marker_pat
        else ()
    )
    skills = tuple(match_skills(posting, inputs.skills))
    content = clean_html(posting.content_raw)
    topic_pat = whole_words(spec.topic_words)
    topics = (
        tuple(dict.fromkeys(m.group(0).lower() for m in topic_pat.finditer(content)))
        if topic_pat
        else ()
    )
    fallback = CONTENT_PATH if "content" in posting.raw else "$.id"
    location = classify_location(posting.location_name, content, fallback_path=fallback)
    exclusions = tuple(find_exclusions(posting))

    title_pts = (
        spec.family_phrase if family else (spec.generic_weight if generic else 0)
    )
    points = {
        "R1": title_pts if family else 0,
        "R2": title_pts if not family else 0,
        "R3": spec.seniority_weight if markers else 0,
        "R4": min(len(skills), spec.skill_cap) * spec.per_skill,
        "R5": spec.topic_weight if topics else 0,
        "R6": spec.location_points[location.label],
        "R7": spec.exclusion_weight if exclusions else 0,
    }
    total = sum(points.values())
    return Scored(
        key=key,
        board=board,
        posting=posting,
        title_basis="family" if family else ("generic" if generic else "none"),
        family_roles=family,
        generic_word=generic.group(0) if generic else None,
        generic_blocker=blocker.group(0).lower() if blocker else None,
        markers=markers,
        skills=skills,
        topic_words=topics,
        location=location,
        exclusions=exclusions,
        points=points,
        total=total,
        kept=total >= spec.threshold,
    )
