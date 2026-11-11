"""Clocks and run-id formatting.

Run IDs are the run's UTC start time truncated to seconds, formatted
``YYYY-MM-DDTHH-MM-SSZ`` (colons replaced so the ID is a safe folder name), with
``-SEEDED`` appended for replay runs, e.g. ``2026-10-30T02-11-07Z`` and
``2026-10-30T02-11-07Z-SEEDED``.
"""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

EASTERN = ZoneInfo("America/New_York")
"""The time zone that defines a "calendar day" for run scheduling (A22)."""

SEEDED_SUFFIX = "-SEEDED"

_RUN_ID_FORMAT = "%Y-%m-%dT%H-%M-%SZ"


def _require_aware(instant: datetime) -> datetime:
    """Returns ``instant`` converted to UTC.

    Args:
        instant: A timezone-aware datetime.

    Returns:
        The same instant in UTC.

    Raises:
        ValueError: If ``instant`` is naive.
    """
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("datetime must be timezone-aware")
    return instant.astimezone(UTC)


def format_run_id(started_at: datetime, *, seeded: bool = False) -> str:
    """Formats a run ID from the run's start time.

    Args:
        started_at: Timezone-aware start time; converted to UTC, sub-seconds dropped.
        seeded: Append ``-SEEDED`` (replay runs).

    Returns:
        The run ID, e.g. ``"2026-10-30T02-11-07Z"``.

    Raises:
        ValueError: If ``started_at`` is naive.
    """
    run_id = _require_aware(started_at).strftime(_RUN_ID_FORMAT)
    return run_id + SEEDED_SUFFIX if seeded else run_id


def to_eastern(instant: datetime) -> datetime:
    """Converts an aware datetime to America/New_York.

    Args:
        instant: Timezone-aware datetime.

    Returns:
        The same instant in Eastern time (EDT or EST as applicable).

    Raises:
        ValueError: If ``instant`` is naive.
    """
    return _require_aware(instant).astimezone(EASTERN)


class SystemClock:
    """The real clock."""

    def now_utc(self) -> datetime:
        """Returns the current time in UTC."""
        return datetime.now(UTC)
