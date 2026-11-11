"""Pure metrics for the prompt experiment and the sampling report (PLAN §6.1, §6.2).

Vocabulary is deliberate:

* **Format acceptance** is the validator pass rate of first replies. It is reported
  on its own and is never called accuracy.
* **Agreement** compares Claude's label with the student's hand label through the
  CONTRACT §16 mapping (``RELEVANT`` = ``MATCH``, ``NOT_RELEVANT`` = ``NO_MATCH``).
  It is reported twice: over all calls with an invalid reply counted as a
  disagreement, and over valid replies only.
* Every k/n gets a Wilson 95% score interval.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict

from job_search_agent.experiments._calls import CallRecord
from job_search_agent.models import ModelLabel, VerdictLabel

Z_95 = 1.959963984540054
"""Two-sided 95% normal quantile."""

INVALID: Final = "INVALID"
"""Outcome name for a first reply that failed validation or a failed call."""

Outcome = Literal["MATCH", "NO_MATCH", "INVALID"]

_LABEL_TO_VERDICT: Mapping[str, VerdictLabel] = {
    "RELEVANT": VerdictLabel.MATCH,
    "NOT_RELEVANT": VerdictLabel.NO_MATCH,
}


def model_to_verdict(label: ModelLabel) -> VerdictLabel:
    """Maps Claude's label to the rule vocabulary (CONTRACT §16).

    Args:
        label: ``"RELEVANT"`` or ``"NOT_RELEVANT"``.

    Returns:
        ``MATCH`` for ``RELEVANT``, ``NO_MATCH`` for ``NOT_RELEVANT``.
    """
    return _LABEL_TO_VERDICT[label]


class _Out(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Rate(_Out):
    """k out of n with its Wilson 95% interval (``None`` bounds when n is 0)."""

    k: int
    n: int
    value: float | None
    wilson_low: float | None
    wilson_high: float | None


def wilson_interval(k: int, n: int) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion.

    Args:
        k: Successes, ``0 <= k <= n``.
        n: Trials, ``n > 0``.

    Returns:
        ``(low, high)``, both within ``[0, 1]``.

    Raises:
        ValueError: If ``n <= 0`` or ``k`` is outside ``[0, n]``.
    """
    if n <= 0 or not 0 <= k <= n:
        raise ValueError("need n > 0 and 0 <= k <= n")
    z = Z_95
    p = k / n
    z2 = z * z
    denominator = 1 + z2 / n
    center = (p + z2 / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / denominator
    return max(0.0, center - half), min(1.0, center + half)


def rate(k: int, n: int) -> Rate:
    """Builds a ``Rate``; the interval is omitted when ``n`` is 0."""
    if n == 0:
        return Rate(k=k, n=n, value=None, wilson_low=None, wilson_high=None)
    low, high = wilson_interval(k, n)
    return Rate(k=k, n=n, value=k / n, wilson_low=low, wilson_high=high)


def outcome(call: CallRecord) -> Outcome:
    """``MATCH``/``NO_MATCH`` for a valid first reply (§16 mapping), else ``INVALID``.

    Args:
        call: One experiment call.

    Returns:
        The outcome compared with the hand label.
    """
    if not call.first_reply_valid or call.label is None:
        return INVALID
    return "MATCH" if model_to_verdict(call.label) is VerdictLabel.MATCH else "NO_MATCH"


class EvidencePathStats(_Out):
    """Evidence-path validity over parseable replies."""

    parseable_replies: int
    entries: int
    valid_entries: int
    fraction_valid: float | None
    replies_with_bad_path: int


class CellMetrics(_Out):
    """Metrics for one (prompt, set) cell; first reply only."""

    n: int
    format_acceptance: Rate
    agreement_invalid_as_disagreement: Rate
    agreement_among_valid: Rate
    confusion: dict[str, dict[str, int]]
    """``confusion[hand][model]`` with hand in MATCH/NO_MATCH and model in
    MATCH/NO_MATCH/INVALID; the MATCH/NO_MATCH columns are the 2x2 matrix."""
    evidence_paths: EvidencePathStats


def score_cell(
    scores: Sequence[CallRecord], hand: Mapping[str, VerdictLabel]
) -> CellMetrics:
    """Computes the metrics of one cell.

    Args:
        scores: One first-reply call per posting.
        hand: The student's hand label per posting ID.

    Returns:
        The metrics.

    Raises:
        KeyError: If a scored posting has no hand label.
    """
    n = len(scores)
    valid = [s for s in scores if outcome(s) != INVALID]
    agree = [s for s in valid if outcome(s) == hand[s.posting_id].value]
    confusion: dict[str, dict[str, int]] = {
        h.value: {"MATCH": 0, "NO_MATCH": 0, INVALID: 0} for h in VerdictLabel
    }
    for score in scores:
        confusion[hand[score.posting_id].value][outcome(score)] += 1
    parseable = [s for s in scores if s.parseable]
    entries = sum(s.path_entries for s in parseable)
    valid_entries = sum(s.path_entries_valid for s in parseable)
    return CellMetrics(
        n=n,
        format_acceptance=rate(sum(1 for s in scores if s.first_reply_valid), n),
        agreement_invalid_as_disagreement=rate(len(agree), n),
        agreement_among_valid=rate(len(agree), len(valid)),
        confusion=confusion,
        evidence_paths=EvidencePathStats(
            parseable_replies=len(parseable),
            entries=entries,
            valid_entries=valid_entries,
            fraction_valid=valid_entries / entries if entries else None,
            replies_with_bad_path=sum(
                1 for s in parseable if s.path_entries_valid < s.path_entries
            ),
        ),
    )


class Discordance(_Out):
    """A posting where v1 and v2 gave different first-reply outcomes."""

    posting_id: str
    stratum: str
    hand_label: VerdictLabel
    v1: str
    v2: str


def discordant(
    v1: Sequence[CallRecord],
    v2: Sequence[CallRecord],
    strata: Mapping[str, str],
    hand: Mapping[str, VerdictLabel],
) -> list[Discordance]:
    """Lists postings whose v1 and v2 outcomes differ, by ID.

    Args:
        v1: First-reply calls under v1.
        v2: First-reply calls under v2 (same postings).
        strata: Stratum per posting ID.
        hand: Hand label per posting ID.

    Returns:
        The discordant postings, sorted by numeric ID.
    """
    second = {s.posting_id: s for s in v2}
    rows = [
        Discordance(
            posting_id=s.posting_id,
            stratum=strata[s.posting_id],
            hand_label=hand[s.posting_id],
            v1=outcome(s),
            v2=outcome(second[s.posting_id]),
        )
        for s in v1
        if s.posting_id in second and outcome(s) != outcome(second[s.posting_id])
    ]
    return sorted(rows, key=lambda r: int(r.posting_id))


class AuditRow(_Out):
    """A posting where the hand label and the coded rule's verdict differ.

    Either the hand label is a slip or the rule has a bug; the student decides which.
    """

    posting_id: str
    hand_label: VerdictLabel
    rule_label: VerdictLabel
    rule_failed_gates: list[str]
    decision: None = None
    """Always ``None`` here: the student records the decision in the write-up."""


def rule_vs_hand_audit(
    hand: Mapping[str, VerdictLabel],
    rule: Mapping[str, VerdictLabel],
    failed_gates: Mapping[str, Sequence[str]],
) -> list[AuditRow]:
    """Lists every posting where the student's label differs from the code's verdict.

    Args:
        hand: Hand label per posting ID.
        rule: Rule verdict per posting ID (revealed only at ``score``).
        failed_gates: The rule's failed gates per posting ID.

    Returns:
        The disagreements, sorted by numeric ID.
    """
    rows = [
        AuditRow(
            posting_id=pid,
            hand_label=label,
            rule_label=rule[pid],
            rule_failed_gates=list(failed_gates.get(pid, ())),
        )
        for pid, label in hand.items()
        if rule[pid] is not label
    ]
    return sorted(rows, key=lambda r: int(r.posting_id))
