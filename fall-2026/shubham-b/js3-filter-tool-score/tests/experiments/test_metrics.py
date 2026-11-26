"""Pure metrics (PLAN §6.2)."""

from __future__ import annotations

import pytest

from job_search_agent.experiments._calls import CallRecord
from job_search_agent.experiments.metrics import (
    discordant,
    outcome,
    rate,
    rule_vs_hand_audit,
    score_cell,
    wilson_interval,
)
from job_search_agent.experiments.metrics import model_to_verdict as to_verdict
from job_search_agent.models import JudgmentStatus, VerdictLabel

M, N = VerdictLabel.MATCH, VerdictLabel.NO_MATCH


def _score(
    pid: str, label: str | None, *, entries: int = 1, valid: int = 1
) -> CallRecord:
    return CallRecord(
        posting_id=pid,
        status=JudgmentStatus.VALID if label else JudgmentStatus.INVALID_OUTPUT,
        first_reply_valid=label is not None,
        validation_codes=[],
        label=label,  # type: ignore[arg-type]
        evidence_paths=[],
        parseable=label is not None or entries > 0,
        path_entries=entries,
        path_entries_valid=valid,
        session_id=None,
        model_served=[],
        raw_log_ref=None,
        started_at_utc=None,
        started_at_et=None,
        prompt_id="judge.v1",
        prompt_sha256="0" * 64,
    )


def test_label_mapping_relevant_is_match() -> None:
    assert to_verdict("RELEVANT") is VerdictLabel.MATCH
    assert to_verdict("NOT_RELEVANT") is VerdictLabel.NO_MATCH
    assert outcome(_score("1", "RELEVANT")) == "MATCH"
    assert outcome(_score("1", "NOT_RELEVANT")) == "NO_MATCH"
    assert outcome(_score("1", None)) == "INVALID"


def test_wilson_interval_known_values() -> None:
    low, high = wilson_interval(8, 10)
    assert low == pytest.approx(0.4902, abs=1e-4)
    assert high == pytest.approx(0.9433, abs=1e-4)
    assert wilson_interval(0, 10)[0] == pytest.approx(0.0)
    assert wilson_interval(10, 10)[1] == pytest.approx(1.0)
    assert wilson_interval(5, 10) == pytest.approx((0.2366, 0.7634), abs=1e-4)
    with pytest.raises(ValueError):
        wilson_interval(1, 0)
    assert rate(0, 0).value is None and rate(0, 0).wilson_low is None


def test_metrics_format_acceptance_named_separately() -> None:
    scores = [_score("1", "RELEVANT"), _score("2", None, entries=0, valid=0)]
    cell = score_cell(scores, {"1": M, "2": N})
    dumped = cell.model_dump()
    assert "format_acceptance" in dumped
    assert not any("accuracy" in key for key in dumped)
    assert (cell.format_acceptance.k, cell.format_acceptance.n) == (1, 2)


def test_invalid_counts_as_disagreement() -> None:
    hand = {"1": M, "2": N, "3": N, "4": M}
    scores = [
        _score("1", "RELEVANT"),
        _score("2", "NOT_RELEVANT"),
        _score("3", None, entries=2, valid=1),
        _score("4", "NOT_RELEVANT", entries=2, valid=0),
    ]
    cell = score_cell(scores, hand)
    assert (
        cell.agreement_invalid_as_disagreement.k,
        cell.agreement_invalid_as_disagreement.n,
    ) == (2, 4)
    assert (cell.agreement_among_valid.k, cell.agreement_among_valid.n) == (2, 3)
    assert cell.confusion == {
        "MATCH": {"MATCH": 1, "NO_MATCH": 1, "INVALID": 0},
        "NO_MATCH": {"MATCH": 0, "NO_MATCH": 1, "INVALID": 1},
    }
    paths = cell.evidence_paths
    assert (paths.entries, paths.valid_entries, paths.replies_with_bad_path) == (
        6,
        3,
        2,
    )
    assert paths.fraction_valid == pytest.approx(0.5)


def test_discordant_lists_by_id_and_stratum() -> None:
    v1 = [_score("20", "RELEVANT"), _score("3", "RELEVANT"), _score("4", None)]
    v2 = [
        _score("20", "RELEVANT"),
        _score("3", "NOT_RELEVANT"),
        _score("4", "RELEVANT"),
    ]
    rows = discordant(
        v1, v2, {"20": "M", "3": "N1", "4": "N3"}, {"20": M, "3": N, "4": N}
    )
    assert [(r.posting_id, r.stratum, r.v1, r.v2) for r in rows] == [
        ("3", "N1", "MATCH", "NO_MATCH"),
        ("4", "N3", "INVALID", "MATCH"),
    ]


def test_rule_vs_hand_audit() -> None:
    rows = rule_vs_hand_audit({"9": M, "10": N}, {"9": N, "10": N}, {"9": ["SKILLS"]})
    assert [
        (r.posting_id, r.hand_label, r.rule_label, r.rule_failed_gates) for r in rows
    ] == [("9", M, N, ["SKILLS"])]
