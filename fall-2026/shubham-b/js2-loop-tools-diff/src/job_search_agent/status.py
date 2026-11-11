"""Run-status decision: the PLAN §1.4 precedence table as one pure function.

``explain_status`` is the one public decision; it returns the status and the notes
that explain it (callers needing only the status read ``.status``).

CONTRACT §9 and §15: a fetch failure, an invalid response or an empty response is
never ``SUCCESS_NO_NEW``. A model judgment that is not ``VALID`` (including
``UNAVAILABLE``, A25), a pending judgment left unresolved, a data-quality error on a
non-baseline run, or a failed write makes the run ``PARTIAL_FAILURE`` (§10).
"""

from __future__ import annotations

from dataclasses import dataclass

from job_search_agent.models import FetchKind, RunStatus

NOTE_BASELINE_STATE_NOT_SAVED = "baseline_state_not_saved"
NOTE_BASELINE_RECORDS_NOT_SAVED = "baseline_records_not_saved"
NOTE_STATE_NOT_SAVED = "state_not_saved"
NOTE_RECORDS_NOT_SAVED = "records_not_saved"
NOTE_JUDGMENTS_FAILED = "judgments_not_valid"
NOTE_PENDING_UNRESOLVED = "pending_unresolved"
NOTE_DATA_QUALITY_ERRORS = "data_quality_errors"
NOTE_RULE_EVIDENCE_ERRORS = "rule_evidence_errors"


@dataclass(frozen=True, slots=True)
class StatusDecision:
    """The decided status plus the machine-readable reasons behind it.

    Attributes:
        status: The run status.
        notes: Short codes explaining a ``PARTIAL_FAILURE`` (empty otherwise).
    """

    status: RunStatus
    notes: tuple[str, ...] = ()


def explain_status(
    *,
    fetch: FetchKind,
    is_baseline: bool,
    new_count: int,
    failed_judgments: int,
    unresolved_pending: int,
    data_quality_errors: int,
    records_saved: bool,
    state_saved: bool,
    rule_evidence_errors: int = 0,
) -> StatusDecision:
    """Applies the PLAN §1.4 precedence and records why.

    Args:
        fetch: Outcome of obtaining and parsing the board.
        is_baseline: True when no prior state existed.
        new_count: Number of new posting IDs (always 0 on a baseline).
        failed_judgments: New or retried judgments whose status is not ``VALID``.
        unresolved_pending: Pending IDs still pending after this run.
        data_quality_errors: ``ERROR``-severity data-quality issues.
        records_saved: Whether ``records.json``/``retried.json`` were written.
        state_saved: Whether the state file was written.
        rule_evidence_errors: Records whose rule evidence failed the §7 validator.

    Returns:
        The status and the notes that explain it.

    Raises:
        ValueError: If a count is negative, or a baseline claims new postings.
    """
    counts = (
        new_count,
        failed_judgments,
        unresolved_pending,
        data_quality_errors,
        rule_evidence_errors,
    )
    if any(c < 0 for c in counts):
        raise ValueError("counts must not be negative")
    if fetch is FetchKind.FAILED:
        return StatusDecision(RunStatus.FETCH_FAILED)
    if fetch is FetchKind.INVALID:
        return StatusDecision(RunStatus.INVALID_RESPONSE)
    if fetch is FetchKind.EMPTY:
        return StatusDecision(RunStatus.EMPTY_RESPONSE)
    if is_baseline:
        if new_count:
            raise ValueError("a baseline never has new postings")
        notes: list[str] = []
        if not records_saved:
            notes.append(NOTE_BASELINE_RECORDS_NOT_SAVED)
        if not state_saved:
            notes.append(NOTE_BASELINE_STATE_NOT_SAVED)
        if notes:
            return StatusDecision(RunStatus.PARTIAL_FAILURE, tuple(notes))
        return StatusDecision(RunStatus.BASELINE)
    reasons = (
        (failed_judgments > 0, NOTE_JUDGMENTS_FAILED),
        (unresolved_pending > 0, NOTE_PENDING_UNRESOLVED),
        (data_quality_errors > 0, NOTE_DATA_QUALITY_ERRORS),
        (rule_evidence_errors > 0, NOTE_RULE_EVIDENCE_ERRORS),
        (not records_saved, NOTE_RECORDS_NOT_SAVED),
        (not state_saved, NOTE_STATE_NOT_SAVED),
    )
    partial = tuple(note for failed, note in reasons if failed)
    if partial:
        return StatusDecision(RunStatus.PARTIAL_FAILURE, partial)
    if new_count > 0:
        return StatusDecision(RunStatus.SUCCESS_WITH_NEW)
    return StatusDecision(RunStatus.SUCCESS_NO_NEW)
