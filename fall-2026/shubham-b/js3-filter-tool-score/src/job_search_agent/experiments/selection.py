"""Prompt-experiment selection, worksheets and hand-label files (PLAN §6.2).

The rule is injected (``evaluate``) so the draw is testable with synthetic verdicts;
``experiments._wiring`` binds ``rule.verdict.evaluate`` to the verified résumé.

Draw procedure (also written in ``experiments/prompt/PROCEDURE.md``):

1. Every posting in the committed hand-check raw file except the five §13 IDs is
   evaluated by the rule and put in at most one stratum (``classify_stratum``).
2. One ``random.Random(20261029)`` is used for everything, in this order. For each
   stratum in the order M, N1, N2, N3: the candidates are sorted by numeric ID,
   ``rng.sample(candidates, quota)`` draws the quota, ``rng.shuffle`` shuffles the
   draw, the first half goes to dev and the second half to held-out.
3. Each set's IDs are then shuffled once more with the same ``rng`` (dev first, then
   held-out) to give the worksheet order, so strata are not grouped.
4. If any stratum has fewer candidates than its quota, selection fails loudly.
"""

from __future__ import annotations

import random
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from job_search_agent.experiments._io import ExperimentError
from job_search_agent.models import (
    Gate,
    LocationLabel,
    Posting,
    RuleVerdict,
    VerdictLabel,
)
from job_search_agent.text import clean_html

SEED = 20261029
"""The pre-registered seed."""

STRATA: tuple[str, ...] = ("M", "N1", "N2", "N3")
QUOTAS: Mapping[str, int] = {"M": 8, "N1": 4, "N2": 4, "N3": 4}
"""Per-stratum quotas; each is split evenly between dev and held-out."""

STRATUM_DEFINITIONS: Mapping[str, str] = {
    "M": "rule verdict MATCH",
    "N1": "title pass, >=2 skills, location label not US_BASED",
    "N2": "title pass, <2 skills",
    "N3": "title fail, >=2 skills, location label US_BASED",
}

HANDCHECK_IDS: tuple[str, ...] = (
    "8249901",
    "7543868",
    "8175099",
    "8127182",
    "8234357",
)
"""The five CONTRACT §13 postings (the sampling set), excluded from selection."""

SETS: tuple[str, ...] = ("dev", "heldout")

Evaluate = Callable[[Posting], RuleVerdict]
"""The deterministic rule for one posting (``rule.verdict.evaluate``, résumé bound)."""


def classify_stratum(verdict: RuleVerdict) -> str | None:
    """Puts a rule verdict into at most one stratum.

    Args:
        verdict: The rule's verdict for a posting.

    Returns:
        ``"M"``, ``"N1"``, ``"N2"``, ``"N3"`` or ``None`` (not sampled).
    """
    if verdict.label is VerdictLabel.MATCH:
        return "M"
    failed = set(verdict.failed_gates)
    title_pass = Gate.TITLE not in failed
    skills_pass = Gate.SKILLS not in failed
    us_based = verdict.location_check.label is LocationLabel.US_BASED
    if title_pass and skills_pass and not us_based:
        return "N1"
    if title_pass and not skills_pass:
        return "N2"
    if not title_pass and skills_pass and us_based:
        return "N3"
    return None


@dataclass(frozen=True, slots=True)
class RuleFacts:
    """What the rule said about one selected posting (revealed only at ``score``)."""

    stratum: str
    label: VerdictLabel
    failed_gates: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Selection:
    """The drawn sets.

    Attributes:
        dev: Dev IDs in worksheet order.
        heldout: Held-out IDs in worksheet order.
        facts: Stratum and rule verdict per selected ID.
        pool_sizes: Candidates per stratum before drawing.
    """

    dev: tuple[str, ...]
    heldout: tuple[str, ...]
    facts: Mapping[str, RuleFacts]
    pool_sizes: Mapping[str, int]

    def ids(self, set_name: str) -> tuple[str, ...]:
        """Returns the IDs of ``"dev"`` or ``"heldout"``."""
        return self.dev if set_name == "dev" else self.heldout


def select_postings(
    postings: Iterable[Posting],
    evaluate: Evaluate,
    *,
    seed: int = SEED,
) -> Selection:
    """Draws the dev and held-out sets (``QUOTAS``; the §13 postings never drawn).

    Args:
        postings: Every posting of the source board.
        evaluate: The rule.
        seed: Random seed.

    Returns:
        The selection.

    Raises:
        ExperimentError: If a stratum's pool is smaller than its quota.
    """
    pools: dict[str, list[str]] = {s: [] for s in STRATA}
    verdicts: dict[str, RuleVerdict] = {}
    for posting in postings:
        if posting.posting_id in HANDCHECK_IDS:
            continue
        verdict = evaluate(posting)
        stratum = classify_stratum(verdict)
        if stratum is not None:
            pools[stratum].append(posting.posting_id)
            verdicts[posting.posting_id] = verdict
    short = [
        f"{s}: {len(pools[s])} < {QUOTAS[s]}"
        for s in STRATA
        if len(pools[s]) < QUOTAS[s]
    ]
    if short:
        raise ExperimentError("stratum pool smaller than quota: " + "; ".join(short))
    rng = random.Random(seed)  # noqa: S311 - reproducible draw, not security
    dev: list[str] = []
    heldout: list[str] = []
    facts: dict[str, RuleFacts] = {}
    for stratum in STRATA:
        quota = QUOTAS[stratum]
        candidates = sorted(pools[stratum], key=int)
        drawn = rng.sample(candidates, quota)
        rng.shuffle(drawn)
        dev.extend(drawn[: quota // 2])
        heldout.extend(drawn[quota // 2 :])
        for pid in drawn:
            verdict = verdicts[pid]
            facts[pid] = RuleFacts(
                stratum=stratum,
                label=verdict.label,
                failed_gates=tuple(g.value for g in verdict.failed_gates),
            )
    rng.shuffle(dev)
    rng.shuffle(heldout)
    return Selection(
        dev=tuple(dev),
        heldout=tuple(heldout),
        facts=facts,
        pool_sizes={s: len(pools[s]) for s in STRATA},
    )


# --- worksheets ----------------------------------------------------------------


def render_worksheet(
    set_name: str,
    ids: Sequence[str],
    postings: Mapping[str, Posting],
) -> str:
    """Renders a hand-labeling worksheet. It shows no verdict and no stratum.

    Args:
        set_name: ``"dev"`` or ``"heldout"``.
        ids: Posting IDs in worksheet order.
        postings: Postings by ID.

    Returns:
        Markdown text.
    """
    lines = [
        f"# Prompt experiment worksheet: {set_name}",
        "",
        "Label each posting by hand with the CONTRACT.md §6 rule exactly as written "
        "(§16). Do not run `jsa rule` on these postings before `jsa exp prompt seal`.",
        f"Record your answers in `experiments/prompt/labels/{set_name}.labels.json`.",
        "",
    ]
    for number, pid in enumerate(ids, start=1):
        posting = postings[pid]
        url = posting.raw.get("absolute_url")
        departments = ", ".join(n for n in posting.department_names if n) or "(none)"
        lines += [
            f"## {number}. Posting {pid}",
            "",
            f"- ID: `{pid}`",
            f"- Title: {posting.title}",
            f"- location.name: {posting.location_name or '(absent)'}",
            f"- Departments: {departments}",
            f"- URL: {url if isinstance(url, str) else '(none)'}",
            "",
            "Fill in:",
            "",
            "- hand_label (MATCH / NO_MATCH):",
            "- title_pass (true / false):",
            "- skills (term / resume path / posting path):",
            "- exclusion phrase (or none):",
            "- location label (US_BASED / NON_US / NOT_ESTABLISHED):",
            "- notes:",
            "",
            "<details><summary>Cleaned content</summary>",
            "",
            clean_html(posting.content_raw),
            "",
            "</details>",
            "",
        ]
    return "\n".join(lines)


def label_template(set_name: str, ids: Sequence[str]) -> dict[str, Any]:
    """Returns a blank label file for one set (all answers ``null``).

    Args:
        set_name: ``"dev"`` or ``"heldout"``.
        ids: Posting IDs in worksheet order.

    Returns:
        A JSON-ready dict matching ``LabelFile`` once filled in.
    """
    return {
        "set": set_name,
        "labeled_by": None,
        "labels": [
            {
                "posting_id": pid,
                "hand_label": None,
                "title_pass": None,
                "skills": [],
                "exclusion_phrase": None,
                "location_label": None,
                "notes": "",
            }
            for pid in ids
        ],
    }


# --- hand-label files ------------------------------------------------------------

_PATH = re.compile(r"^\$(\.[A-Za-z_][A-Za-z0-9_]*|\[(0|[1-9][0-9]*)\])+$")


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class HandSkill(_Strict):
    """One skill the student matched by hand."""

    term: str = Field(min_length=1)
    resume_path: str = Field(pattern=_PATH.pattern)
    posting_path: str = Field(pattern=_PATH.pattern)


class HandLabel(_Strict):
    """The student's §16 label for one posting."""

    posting_id: str = Field(pattern=r"^[1-9][0-9]*$")
    hand_label: Literal["MATCH", "NO_MATCH"]
    title_pass: bool
    skills: list[HandSkill]
    exclusion_phrase: str | None
    location_label: Literal["US_BASED", "NON_US", "NOT_ESTABLISHED"]
    notes: str


class LabelFile(_Strict):
    """``experiments/prompt/labels/<set>.labels.json``."""

    set: Literal["dev", "heldout"]
    labeled_by: str = Field(min_length=1)
    labels: list[HandLabel]

    def by_id(self) -> dict[str, VerdictLabel]:
        """Returns the hand label per posting ID."""
        return {item.posting_id: VerdictLabel(item.hand_label) for item in self.labels}


def _rule_consistency(label: HandLabel) -> str | None:
    distinct = {skill.term for skill in label.skills}
    implied = (
        label.title_pass
        and len(distinct) >= 2
        and label.exclusion_phrase is None
        and label.location_label == "US_BASED"
    )
    if implied != (label.hand_label == "MATCH"):
        return (
            f"{label.posting_id}: hand_label {label.hand_label} does not follow from "
            "the recorded gates (title_pass, >=2 distinct skills, no exclusion, "
            "US_BASED)"
        )
    return None


def validate_label_file(
    obj: object, *, expected_set: str, expected_ids: Sequence[str]
) -> LabelFile:
    """Checks one filled-in label file.

    Args:
        obj: The parsed JSON.
        expected_set: ``"dev"`` or ``"heldout"``.
        expected_ids: The selected IDs for that set.

    Returns:
        The parsed file.

    Raises:
        ExperimentError: Listing every problem: schema errors, a wrong set name,
            missing, extra or duplicated IDs, or a label that does not follow from its
            own recorded gates under §6.5.
    """
    try:
        parsed = LabelFile.model_validate(obj, strict=True)
    except ValidationError as exc:
        where = sorted(
            {
                ".".join(str(p) for p in e["loc"]) or "<root>"
                for e in exc.errors(include_input=False)
            }
        )
        raise ExperimentError(
            f"{expected_set} labels invalid at: {', '.join(where)}"
        ) from exc
    problems: list[str] = []
    if parsed.set != expected_set:
        problems.append(f"set is {parsed.set!r}, expected {expected_set!r}")
    seen = [item.posting_id for item in parsed.labels]
    duplicates = sorted({pid for pid in seen if seen.count(pid) > 1}, key=int)
    missing = sorted(set(expected_ids) - set(seen), key=int)
    extra = sorted(set(seen) - set(expected_ids), key=int)
    if duplicates:
        problems.append("duplicate IDs: " + ", ".join(duplicates))
    if missing:
        problems.append("missing IDs: " + ", ".join(missing))
    if extra:
        problems.append("unexpected IDs: " + ", ".join(extra))
    problems += [p for p in (_rule_consistency(i) for i in parsed.labels) if p]
    if problems:
        raise ExperimentError(f"{expected_set} labels rejected: " + "; ".join(problems))
    return parsed
