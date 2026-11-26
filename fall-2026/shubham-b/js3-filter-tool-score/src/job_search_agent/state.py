"""The seen-ID state file (CONTRACT §9, §10): load, serialise, advance, drop.

``advance`` and ``drop_pending`` are pure. Reading is a thin edge function; writing is
the caller's job through an atomic writer (``fsio.OutputRoot.write_bytes_atomic``), so
an interrupted write leaves the previous state intact.

Rules kept here:

* The seen-ID set is cumulative. An ID is never removed, so a posting that disappears
  and reappears is not new again.
* A posting is pending while its judgment is not ``VALID``. It leaves the pending list
  only when a ``VALID`` judgment is stored, or by an explicit ``drop_pending`` decision
  with a reason, which moves it to ``abandoned``.
* A state file that exists but cannot be trusted raises ``StateCorrupt``; it never
  silently turns the next run into a new baseline.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping, Set
from datetime import datetime

from pydantic import ValidationError

from job_search_agent.errors import StateCorrupt
from job_search_agent.models import (
    AbandonedJudgment,
    JudgmentOutcome,
    PendingJudgment,
    RawRef,
    SeenState,
)

SCHEMA_VERSION = 1


def sort_ids(ids: Iterable[str]) -> list[str]:
    """Sorts canonical decimal posting IDs numerically (deterministic output).

    Args:
        ids: Canonical decimal ID strings.

    Returns:
        The IDs in ascending numeric order, duplicates removed.
    """
    return sorted(set(ids), key=lambda pid: (len(pid), pid))


def read_state_rel(rel: str, read_bytes: Callable[[str], bytes]) -> bytes | None:
    """Reads the raw state bytes through the write root's path policy.

    Every reader (the pipeline, ``jsa doctor`` and ``jsa pending``) passes
    ``OutputRoot.read_bytes``, so a symlinked state file (or parent directory) is
    refused, not followed.

    Args:
        rel: The state file relative to the data dir, e.g. ``"live/state.json"``.
        read_bytes: ``OutputRoot.read_bytes`` (or a double).

    Returns:
        The exact bytes, or ``None`` when the file does not exist.

    Raises:
        PathRejected: The path violates the file policy (e.g. a symlink).
    """
    try:
        return read_bytes(rel)
    except FileNotFoundError:
        return None


def parse_state(data: bytes) -> SeenState:
    """Parses and integrity-checks state bytes.

    Args:
        data: The state file's bytes.

    Returns:
        The validated state.

    Raises:
        StateCorrupt: ``"not_json"``, ``"not_object"``, ``"schema_version"`` or
            ``"integrity"`` (any other validation failure).
    """
    try:
        obj = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StateCorrupt("not_json") from exc
    if not isinstance(obj, dict):
        raise StateCorrupt("not_object")
    if obj.get("schema_version") != SCHEMA_VERSION or isinstance(
        obj.get("schema_version"), bool
    ):
        raise StateCorrupt("schema_version")
    try:
        return SeenState.model_validate(obj)
    except ValidationError as exc:
        raise StateCorrupt("integrity") from exc


def state_to_bytes(state: SeenState) -> bytes:
    """Serialises a state deterministically (field order, 2-space indent, newline).

    Args:
        state: The state.

    Returns:
        UTF-8 JSON bytes; equal states always give equal bytes.
    """
    obj = state.model_dump(mode="json")
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def advance(
    prior: SeenState | None,
    *,
    valid_ids: Set[str],
    run_id: str,
    fetched_at: datetime,
    run_started_at: datetime,
    outcomes: Mapping[str, JudgmentOutcome],
    pending_sources: Mapping[str, RawRef],
    provider: str,
    board: str,
    seeded: bool,
) -> SeenState:
    """Computes the state after a successful, validated fetch (pure).

    Args:
        prior: The state before the run, or ``None`` on a baseline.
        valid_ids: Every valid posting ID in this fetch.
        run_id: This run's ID.
        fetched_at: When the raw response was fetched (for a replay: the original
            fetch time).
        run_started_at: When this run started.
        outcomes: Judgment outcomes of this run (new and retried), by posting ID.
        pending_sources: Where each *newly* judged posting can be re-read (the raw
            file plus its ``$.jobs`` index). Required for every new non-VALID outcome.
        provider: Provider name, e.g. ``"greenhouse"``.
        board: Board token, e.g. ``"stripe"``.
        seeded: True for the seeded (replay) state.

    Returns:
        The new state: seen IDs are the union of prior and current IDs; non-VALID
        outcomes are (re)queued as pending; VALID outcomes leave the pending list.

    Raises:
        ValueError: If a new non-VALID outcome has no pending source, or an outcome
            is for an ID never seen.
    """
    prior_seen = set(prior.seen_ids) if prior else set()
    seen = prior_seen | set(valid_ids)
    pending: dict[str, PendingJudgment] = (
        {p.posting_id: p for p in prior.pending} if prior else {}
    )
    abandoned = list(prior.abandoned) if prior else []
    for posting_id, outcome in outcomes.items():
        if posting_id not in seen:
            raise ValueError("an outcome must be for a seen posting ID")
        if outcome.is_valid:
            pending.pop(posting_id, None)
            continue
        existing = pending.get(posting_id)
        if existing is not None:
            pending[posting_id] = PendingJudgment(
                posting_id=posting_id,
                last_status=outcome.status,
                queued_run_id=existing.queued_run_id,
                last_attempt_run_id=run_id,
                attempts=existing.attempts + 1,
                source=existing.source,
            )
            continue
        source = pending_sources.get(posting_id)
        if source is None:
            raise ValueError("a newly pending posting needs a pending source")
        pending[posting_id] = PendingJudgment(
            posting_id=posting_id,
            last_status=outcome.status,
            queued_run_id=run_id,
            last_attempt_run_id=run_id,
            attempts=1,
            source=source,
        )
    return SeenState(
        schema_version=1,
        provider=provider,
        board=board,
        seeded=seeded,
        seen_ids=sort_ids(seen),
        last_successful_fetch_utc=fetched_at,
        last_successful_run_id=run_id,
        run_started_at_utc=run_started_at,
        pending=[pending[pid] for pid in sort_ids(pending)],
        abandoned=abandoned,
    )


def drop_pending(
    state: SeenState, posting_id: str, *, reason: str, dropped_at: datetime
) -> SeenState:
    """Records an explicit, documented decision to stop retrying one posting (§10).

    Args:
        state: The current state.
        posting_id: The pending posting to drop.
        reason: Why retrying stops; must not be blank.
        dropped_at: When the decision was made (timezone-aware).

    Returns:
        A new state with the posting moved from ``pending`` to ``abandoned``. The ID
        stays in ``seen_ids``.

    Raises:
        ValueError: If the reason is blank.
        KeyError: If the posting is not pending.
    """
    if not reason.strip():
        raise ValueError("a drop decision needs a non-empty reason")
    match = [p for p in state.pending if p.posting_id == posting_id]
    if not match:
        raise KeyError(posting_id)
    dropped = match[0]
    record = AbandonedJudgment(
        posting_id=dropped.posting_id,
        last_status=dropped.last_status,
        queued_run_id=dropped.queued_run_id,
        dropped_at_utc=dropped_at,
        reason=reason,
    )
    fields = state.model_dump()
    fields["pending"] = [p for p in state.pending if p.posting_id != posting_id]
    fields["abandoned"] = [*state.abandoned, record]
    return SeenState.model_validate(fields)
