"""Greenhouse public job-board provider (CONTRACT §2, §5, §9; PLAN A21, A30, A31).

``parse`` validates the response shape (a top-level object with a ``jobs`` list and
an integer ``meta.total``), canonicalises posting IDs to decimal strings and lists
every per-posting data-quality problem instead of inventing or repairing values.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Final, TypeGuard

from job_search_agent.errors import ConfigError, InvalidResponse
from job_search_agent.models import (
    DataQualityCode,
    DataQualityIssue,
    ParsedBoard,
    Posting,
    Severity,
)
from job_search_agent.strict_json import reject_constant

API_HOST: Final = "boards-api.greenhouse.io"
"""The only host this provider's URLs point to (CONTRACT §2, §11)."""

_TOKEN_PATTERN: Final = re.compile(r"[a-z0-9][a-z0-9_-]*")


def _is_json_int(value: object) -> TypeGuard[int]:
    """Returns True for a JSON integer (a Python ``int`` that is not a ``bool``)."""
    return isinstance(value, int) and not isinstance(value, bool)


@dataclass
class _Collector:
    """Accumulates data-quality issues while one board is parsed."""

    issues: list[DataQualityIssue] = field(default_factory=list)

    def add(
        self,
        code: DataQualityCode,
        severity: Severity,
        *,
        index: int | None = None,
        posting_id: str | None = None,
        detail: str = "",
    ) -> None:
        """Records one issue.

        Args:
            code: The issue code.
            severity: ``ERROR`` or ``WARNING``.
            index: Position in ``$.jobs``, if the issue concerns one entry.
            posting_id: The entry's valid ID, if it has one.
            detail: Short factual description without posting content.
        """
        self.issues.append(
            DataQualityIssue(
                code=code,
                severity=severity,
                index=index,
                posting_id=posting_id,
                detail=detail,
            )
        )


def _load_json(body: bytes) -> Any:  # noqa: ANN401 - arbitrary JSON document
    """Decodes the response body as strict JSON.

    Args:
        body: Raw response bytes.

    Returns:
        The decoded JSON value.

    Raises:
        InvalidResponse: ``not_json`` if the bytes are not UTF-8 JSON.
    """
    try:
        return json.loads(body.decode("utf-8"), parse_constant=reject_constant)
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise InvalidResponse("not_json", type(exc).__name__) from exc


def _check_shape(document: object) -> tuple[list[Any], int]:
    """Validates the top-level response shape (A21).

    Args:
        document: The decoded JSON value.

    Returns:
        The ``jobs`` list and the integer ``meta.total``.

    Raises:
        InvalidResponse: ``not_object``, ``jobs_not_list`` or ``meta_total``.
    """
    if not isinstance(document, dict):
        raise InvalidResponse("not_object", type(document).__name__)
    jobs = document.get("jobs")
    if not isinstance(jobs, list):
        raise InvalidResponse("jobs_not_list")
    meta = document.get("meta")
    total = meta.get("total") if isinstance(meta, dict) else None
    if not _is_json_int(total):
        raise InvalidResponse("meta_total")
    return jobs, total


def _posting_id(job: Mapping[str, Any], index: int, out: _Collector) -> str | None:
    """Returns the canonical ID of one job, or records why it has none (A31).

    Args:
        job: One ``jobs`` entry.
        index: Its position in ``$.jobs``.
        out: Issue collector.

    Returns:
        The decimal string of a positive JSON integer ID, else ``None``.
    """
    if "id" not in job:
        out.add(DataQualityCode.MISSING_ID, Severity.ERROR, index=index)
        return None
    raw_id = job["id"]
    if not _is_json_int(raw_id) or raw_id <= 0:
        detail = f"id is a JSON {type(raw_id).__name__}, not a positive integer"
        out.add(DataQualityCode.INVALID_ID, Severity.ERROR, index=index, detail=detail)
        return None
    return str(raw_id)


def _wrong_type(
    value: object, path: str, ctx: tuple[int, str], out: _Collector
) -> None:
    """Records a ``WRONG_FIELD_TYPE`` warning for one optional field.

    Args:
        value: The offending value (only its type is reported).
        path: The field's posting-relative path.
        ctx: ``(index, posting_id)`` of the posting.
        out: Issue collector.
    """
    index, posting_id = ctx
    out.add(
        DataQualityCode.WRONG_FIELD_TYPE,
        Severity.WARNING,
        index=index,
        posting_id=posting_id,
        detail=f"{path} is a JSON {type(value).__name__}",
    )


def _optional_str(
    value: object, path: str, ctx: tuple[int, str], out: _Collector
) -> str | None:
    """Returns ``value`` if it is a string; records a warning if it has another type.

    ``None`` (absent or JSON ``null``) is not an issue for an optional field.

    Args:
        value: The field value, ``None`` when absent.
        path: The field's posting-relative path, for the detail message.
        ctx: ``(index, posting_id)`` of the posting.
        out: Issue collector.

    Returns:
        The string, or ``None`` when absent, null or of the wrong type.
    """
    if value is None or isinstance(value, str):
        return value
    _wrong_type(value, path, ctx, out)
    return None


def _location_name(
    job: Mapping[str, Any], ctx: tuple[int, str], out: _Collector
) -> str | None:
    """Reads ``$.location.name``; ``None`` when it is absent or not a string (A30).

    An absent name is a ``MISSING_LOCATION`` warning. When ``$.content`` is absent
    too, its detail says so: the rule's location evidence then cites ``$.id``, which
    is a real path but holds neither a location nor content.

    A present but non-string name (``null`` included) is a ``WRONG_FIELD_TYPE``
    warning: the rule must never cite ``$.location.name`` as evidence for a value
    that is not a location string.

    Args:
        job: One ``jobs`` entry.
        ctx: ``(index, posting_id)`` of the posting.
        out: Issue collector.

    Returns:
        The location string, or ``None``.
    """
    location = job.get("location")
    if not isinstance(location, dict) or "name" not in location:
        index, posting_id = ctx
        detail = "$.location.name is absent"
        if "content" not in job:
            # A30: neither path exists, so the rule's location evidence is $.id.
            detail = (
                "$.location.name and $.content are absent; the location check "
                "cites $.id as its only real path (A30)"
            )
        out.add(
            DataQualityCode.MISSING_LOCATION,
            Severity.WARNING,
            index=index,
            posting_id=posting_id,
            detail=detail,
        )
        return None
    name = location["name"]
    if isinstance(name, str):
        return name
    _wrong_type(name, "$.location.name", ctx, out)
    return None


def _department_names(
    job: Mapping[str, Any], ctx: tuple[int, str], out: _Collector
) -> tuple[str, ...]:
    """Reads ``$.departments[i].name``; wrong types contribute ``""`` (index-aligned).

    Args:
        job: One ``jobs`` entry.
        ctx: ``(index, posting_id)`` of the posting.
        out: Issue collector.

    Returns:
        One string per ``departments`` entry, in order.
    """
    departments = job.get("departments")
    if departments is None:
        return ()
    if not isinstance(departments, list):
        _wrong_type(departments, "$.departments", ctx, out)
        return ()
    names: list[str] = []
    for i, department in enumerate(departments):
        path = f"$.departments[{i}].name"
        raw = department.get("name") if isinstance(department, dict) else department
        names.append(_optional_str(raw, path, ctx, out) or "")
    return tuple(names)


def _posting(
    job: Mapping[str, Any], index: int, posting_id: str, out: _Collector
) -> Posting:
    """Builds the normalised view of one job with a valid ID.

    Args:
        job: One ``jobs`` entry.
        index: Its position in ``$.jobs``.
        posting_id: Its canonical ID.
        out: Issue collector.

    Returns:
        The posting; missing optional fields contribute empty values (§5).
    """
    ctx = (index, posting_id)
    return Posting(
        posting_id=posting_id,
        index=index,
        raw=job,
        title=_optional_str(job.get("title"), "$.title", ctx, out) or "",
        location_name=_location_name(job, ctx, out),
        updated_at=_optional_str(job.get("updated_at"), "$.updated_at", ctx, out),
        content_raw=_optional_str(job.get("content"), "$.content", ctx, out) or "",
        department_names=_department_names(job, ctx, out),
    )


def _postings(jobs: Sequence[Any], out: _Collector) -> tuple[Posting, ...]:
    """Normalises every job with a valid, first-seen ID, in board order.

    Args:
        jobs: The ``jobs`` array.
        out: Issue collector.

    Returns:
        The valid postings; later duplicates of an ID are reported and skipped.
    """
    seen: set[str] = set()
    postings: list[Posting] = []
    for index, job in enumerate(jobs):
        if not isinstance(job, dict):
            out.add(DataQualityCode.NOT_AN_OBJECT, Severity.ERROR, index=index)
            continue
        posting_id = _posting_id(job, index, out)
        if posting_id is None:
            continue
        if posting_id in seen:
            out.add(
                DataQualityCode.DUPLICATE_ID,
                Severity.ERROR,
                index=index,
                posting_id=posting_id,
                detail="the first occurrence is kept",
            )
            continue
        seen.add(posting_id)
        postings.append(_posting(job, index, posting_id, out))
    return tuple(postings)


class GreenhouseProvider:
    """The Greenhouse Job Board API (``boards-api.greenhouse.io``)."""

    @property
    def name(self) -> str:
        """Registry name ``"greenhouse"``."""
        return "greenhouse"

    def jobs_url(self, board_token: str) -> str:
        """Returns the exact jobs URL, with ``content=true`` (CONTRACT §2).

        Args:
            board_token: Board identifier, e.g. ``"stripe"``: lowercase letters,
                digits, ``_`` and ``-`` only, so it cannot alter the path or query.

        Returns:
            ``https://boards-api.greenhouse.io/v1/boards/<token>/jobs?content=true``.

        Raises:
            ConfigError: If the token has any other character or is empty.
        """
        if not _TOKEN_PATTERN.fullmatch(board_token):
            raise ConfigError("board token must match [a-z0-9][a-z0-9_-]*")
        return f"https://{API_HOST}/v1/boards/{board_token}/jobs?content=true"

    def parse(self, body: bytes) -> ParsedBoard:
        """Validates the response shape and normalises the postings.

        Args:
            body: Raw response bytes.

        Returns:
            The parsed board. An empty ``jobs`` array gives ``is_empty``. Every
            per-posting problem is listed in ``data_quality``; a ``meta.total`` that
            differs from ``len(jobs)`` is a warning only (A21).

        Raises:
            InvalidResponse: ``not_json``, ``not_object``, ``jobs_not_list``,
                ``meta_total``, or ``no_valid_ids`` when a non-empty ``jobs`` array
                has no posting with a valid ID.
        """
        jobs, total = _check_shape(_load_json(body))
        out = _Collector()
        postings = _postings(jobs, out)
        if jobs and not postings:
            raise InvalidResponse("no_valid_ids", f"{len(jobs)} entries")
        if total != len(jobs):
            out.add(
                DataQualityCode.TOTAL_MISMATCH,
                Severity.WARNING,
                detail=f"meta.total={total}, len(jobs)={len(jobs)}",
            )
        return ParsedBoard(
            postings=postings,
            fetched_count=len(jobs),
            meta_total=total,
            data_quality=tuple(out.issues),
        )
