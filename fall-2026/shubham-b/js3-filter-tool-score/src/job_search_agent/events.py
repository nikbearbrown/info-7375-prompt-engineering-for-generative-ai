"""Structured run trace: ``runs/<run_id>/events.jsonl`` (JS2 trace seam).

``EventLog`` implements ``ports.EventSink``. It is created before the run folder is
known (the HTTP fetcher is built first and holds a reference to it), so events emitted
before ``attach`` are buffered and flushed when the log is attached to its file. Each
call to ``emit`` writes exactly one JSON line: one event per observation.

Events must never carry résumé values, credentials or absolute paths. ``EventLog``
enforces the last of these mechanically: a string field that looks like an absolute
filesystem path is replaced by a placeholder before it is written.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from job_search_agent.fsio import OutputRoot
from job_search_agent.ports import Clock, JsonValue

ABS_PATH_PLACEHOLDER = "[withheld: absolute path]"

_ABS_PATH = re.compile(r"(?:^|[\s'\"=(])(?:/(?:Users|home|private|var|tmp|etc)/|~/)")


def _scrub(value: JsonValue) -> JsonValue:
    """Replaces absolute-path-looking strings, recursively.

    Args:
        value: A JSON value.

    Returns:
        The value with offending strings replaced by ``ABS_PATH_PLACEHOLDER``.
    """
    if isinstance(value, str):
        return ABS_PATH_PLACEHOLDER if _ABS_PATH.search(value) else value
    if isinstance(value, Mapping):
        return {str(k): _scrub(v) for k, v in value.items()}
    if isinstance(value, Sequence):
        return [_scrub(v) for v in value]
    return value


class EventLog:
    """Buffered JSONL event sink for one run.

    Args:
        clock: Optional clock; when given, each event carries ``at_utc``.

    Attributes:
        events: Every event emitted so far, in order (for tests and summaries).
    """

    def __init__(self, clock: Clock | None = None) -> None:
        self._clock = clock
        self._writer: OutputRoot | None = None
        self._rel: str | None = None
        self._buffer: list[dict[str, JsonValue]] = []
        self.events: list[dict[str, JsonValue]] = []

    @property
    def rel(self) -> str | None:
        """The data-root-relative file the log writes to, once attached."""
        return self._rel

    def attach(self, writer: OutputRoot, rel: str) -> None:
        """Binds the log to its file and flushes buffered events.

        Args:
            writer: The output root.
            rel: Data-root-relative path, e.g. ``"live/runs/<id>/events.jsonl"``.

        Raises:
            RuntimeError: If the log is already attached.
        """
        if self._writer is not None:
            raise RuntimeError("event log already attached")
        self._writer = writer
        self._rel = rel
        buffered, self._buffer = self._buffer, []
        for line in buffered:
            writer.append_jsonl(rel, line)

    def emit(self, event: str, fields: Mapping[str, JsonValue]) -> None:
        """Records one event (``ports.EventSink``).

        Args:
            event: Dotted event name, e.g. ``"source.obtained"``.
            fields: JSON-serialisable details; reserved keys ``seq``, ``event`` and
                ``at_utc`` are rejected.

        Raises:
            ValueError: If ``fields`` uses a reserved key.
        """
        reserved = {"seq", "event", "at_utc"} & set(fields)
        if reserved:
            raise ValueError(f"reserved event keys: {sorted(reserved)}")
        line: dict[str, JsonValue] = {"seq": len(self.events) + 1, "event": event}
        if self._clock is not None:
            line["at_utc"] = self._clock.now_utc().isoformat()
        for key, value in fields.items():
            line[key] = _scrub(value)
        self.events.append(line)
        if self._writer is None or self._rel is None:
            self._buffer.append(line)
        else:
            self._writer.append_jsonl(self._rel, line)

    def names(self) -> list[str]:
        """Returns the event names in emission order."""
        return [str(e["event"]) for e in self.events]
