"""PLAN §1.4 status precedence (CONTRACT §9, §10, §15)."""

from __future__ import annotations

from typing import Any

import pytest

from job_search_agent import status as status_module
from job_search_agent.models import FetchKind, RunStatus
from job_search_agent.status import (
    NOTE_BASELINE_STATE_NOT_SAVED,
    explain_status,
)

OK: dict[str, Any] = {
    "fetch": FetchKind.OK,
    "is_baseline": False,
    "new_count": 0,
    "failed_judgments": 0,
    "unresolved_pending": 0,
    "data_quality_errors": 0,
    "records_saved": True,
    "state_saved": True,
}


def status(**changes: Any) -> RunStatus:
    return explain_status(**{**OK, **changes}).status


def test_explain_status_is_the_one_public_decision() -> None:
    assert not hasattr(status_module, "decide_status")


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        # 1. fetch failure beats everything
        ({"fetch": FetchKind.FAILED, "failed_judgments": 3}, RunStatus.FETCH_FAILED),
        # 2. invalid beats empty/baseline
        ({"fetch": FetchKind.INVALID, "is_baseline": True}, RunStatus.INVALID_RESPONSE),
        # 3. empty
        ({"fetch": FetchKind.EMPTY, "is_baseline": True}, RunStatus.EMPTY_RESPONSE),
        # 4. baseline
        ({"is_baseline": True}, RunStatus.BASELINE),
        ({"is_baseline": True, "data_quality_errors": 2}, RunStatus.BASELINE),
        ({"is_baseline": True, "state_saved": False}, RunStatus.PARTIAL_FAILURE),
        # 5. partial failure causes
        ({"new_count": 2, "failed_judgments": 1}, RunStatus.PARTIAL_FAILURE),
        ({"unresolved_pending": 1}, RunStatus.PARTIAL_FAILURE),
        ({"new_count": 1, "data_quality_errors": 1}, RunStatus.PARTIAL_FAILURE),
        ({"new_count": 1, "records_saved": False}, RunStatus.PARTIAL_FAILURE),
        ({"state_saved": False}, RunStatus.PARTIAL_FAILURE),
        ({"rule_evidence_errors": 1, "new_count": 1}, RunStatus.PARTIAL_FAILURE),
        # 6. / 7.
        ({"new_count": 3}, RunStatus.SUCCESS_WITH_NEW),
        ({}, RunStatus.SUCCESS_NO_NEW),
    ],
)
def test_precedence_table(changes: dict[str, Any], expected: RunStatus) -> None:
    assert status(**changes) is expected


@pytest.mark.parametrize("baseline", [True, False])
def test_fetch_failure_never_success_no_new(baseline: bool) -> None:
    assert (
        status(fetch=FetchKind.FAILED, is_baseline=baseline) is RunStatus.FETCH_FAILED
    )


@pytest.mark.parametrize("baseline", [True, False])
def test_empty_never_success_no_new(baseline: bool) -> None:
    assert status(fetch=FetchKind.EMPTY, is_baseline=baseline) is (
        RunStatus.EMPTY_RESPONSE
    )


@pytest.mark.parametrize("baseline", [True, False])
def test_invalid_never_success_no_new(baseline: bool) -> None:
    assert status(fetch=FetchKind.INVALID, is_baseline=baseline) is (
        RunStatus.INVALID_RESPONSE
    )


def test_unavailable_judgment_is_partial() -> None:
    # An UNAVAILABLE judgment counts as a failed judgment (A25).
    assert status(new_count=1, failed_judgments=1) is RunStatus.PARTIAL_FAILURE


def test_failed_pending_retry_without_new_is_partial() -> None:
    assert (
        status(new_count=0, failed_judgments=1, unresolved_pending=1)
        is RunStatus.PARTIAL_FAILURE
    )


def test_baseline_state_save_failure_is_partial() -> None:
    decision = explain_status(**{**OK, "is_baseline": True, "state_saved": False})
    assert decision.status is RunStatus.PARTIAL_FAILURE
    assert NOTE_BASELINE_STATE_NOT_SAVED in decision.notes


def test_no_failure_status_ever_maps_to_success_no_new() -> None:
    for kind in (FetchKind.FAILED, FetchKind.EMPTY, FetchKind.INVALID):
        for baseline in (True, False):
            for saved in (True, False):
                result = status(
                    fetch=kind,
                    is_baseline=baseline,
                    state_saved=saved,
                    records_saved=saved,
                )
                assert result is not RunStatus.SUCCESS_NO_NEW


def test_negative_counts_rejected() -> None:
    with pytest.raises(ValueError):
        status(new_count=-1)


def test_baseline_with_new_postings_rejected() -> None:
    with pytest.raises(ValueError):
        status(is_baseline=True, new_count=1)
