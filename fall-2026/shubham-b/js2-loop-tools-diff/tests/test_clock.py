"""Clocks and run IDs."""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta, timezone

import pytest

from job_search_agent.clock import SystemClock, format_run_id, to_eastern
from job_search_agent.models import RUN_ID_PATTERN


def test_run_id_format() -> None:
    instant = datetime(2026, 10, 30, 2, 11, 7, 987654, tzinfo=UTC)
    assert format_run_id(instant) == "2026-10-30T02-11-07Z"
    assert format_run_id(instant, seeded=True) == "2026-10-30T02-11-07Z-SEEDED"
    assert re.fullmatch(RUN_ID_PATTERN, format_run_id(instant, seeded=True))


def test_run_id_converts_to_utc() -> None:
    eastern = datetime(2026, 10, 29, 22, 11, 7, tzinfo=timezone(timedelta(hours=-4)))
    assert format_run_id(eastern) == "2026-10-30T02-11-07Z"


def test_naive_datetimes_rejected() -> None:
    with pytest.raises(ValueError, match="aware"):
        format_run_id(datetime(2026, 10, 30))


def test_to_eastern_crosses_calendar_day() -> None:
    # A22: after 20:00 EDT it is already the next day in UTC.
    eastern = to_eastern(datetime(2026, 10, 30, 0, 5, tzinfo=UTC))
    assert (eastern.date().isoformat(), eastern.hour) == ("2026-10-29", 20)


def test_system_clock_is_aware_utc() -> None:
    assert SystemClock().now_utc().utcoffset() == timedelta(0)
