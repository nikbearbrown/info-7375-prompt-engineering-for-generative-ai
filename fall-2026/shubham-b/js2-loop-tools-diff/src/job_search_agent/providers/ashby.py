"""Ashby public job-board provider (GATE §9).

Ashby's posting API returns ``{"jobs": [...], "apiVersion": ...}`` with UUID posting
IDs. Each job is mapped onto the Greenhouse field names the CONTRACT §6 rule reads
(the table in GATE §9), then normalised by the shared Greenhouse code, so the rule,
its evidence validator and the record format stay unchanged. Record posting paths
therefore name the mapped view; the saved raw bytes keep Ashby's own names.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, Final

from job_search_agent.errors import ConfigError, InvalidResponse
from job_search_agent.models import (
    UUID_PATTERN,
    DataQualityCode,
    ParsedBoard,
    Severity,
)
from job_search_agent.providers.greenhouse import (
    IssueCollector,
    load_json,
    normalise_postings,
)

API_HOST: Final = "api.ashbyhq.com"
"""The only host this provider's URLs point to (GATE §6)."""

_TOKEN_PATTERN: Final = re.compile(r"[a-z0-9][a-z0-9_.-]*")
_UUID: Final = re.compile(UUID_PATTERN)


def _uuid_id(job: Mapping[str, Any], index: int, out: IssueCollector) -> str | None:
    """Returns the job's lowercase UUID, or records why it has none."""
    if "id" not in job:
        out.add(DataQualityCode.MISSING_ID, Severity.ERROR, index=index)
        return None
    raw_id = job["id"]
    if not isinstance(raw_id, str) or not _UUID.fullmatch(raw_id):
        detail = f"id is a JSON {type(raw_id).__name__}, not a lowercase UUID"
        out.add(DataQualityCode.INVALID_ID, Severity.ERROR, index=index, detail=detail)
        return None
    return raw_id


def _mapped(job: object) -> object:
    """Renames one Ashby job's fields to the rule's names (GATE §9); keeps non-objects.

    An absent Ashby field stays absent, so the shared code reports it the same way it
    reports a missing Greenhouse field.
    """
    if not isinstance(job, dict):
        return job
    out: dict[str, Any] = {}
    for src, dst in (
        ("id", "id"),
        ("title", "title"),
        ("descriptionHtml", "content"),
        ("publishedAt", "updated_at"),
    ):
        if src in job:
            out[dst] = job[src]
    if "location" in job:
        out["location"] = {"name": job["location"]}
    departments = [{"name": job[key]} for key in ("department", "team") if key in job]
    if departments:
        out["departments"] = departments
    return out


class AshbyProvider:
    """The Ashby posting API (``api.ashbyhq.com``)."""

    @property
    def name(self) -> str:
        """Registry name ``"ashby"``."""
        return "ashby"

    def jobs_url(self, board_token: str) -> str:
        """Returns the job-board URL for one organisation.

        Args:
            board_token: Ashby board name, e.g. ``"ramp"``: lowercase letters, digits,
                ``_``, ``.`` and ``-`` only, so it cannot alter the path or query.

        Returns:
            ``https://api.ashbyhq.com/posting-api/job-board/<token>``.

        Raises:
            ConfigError: If the token has any other character or is empty.
        """
        if not _TOKEN_PATTERN.fullmatch(board_token):
            raise ConfigError("board token must match [a-z0-9][a-z0-9_.-]*")
        return f"https://{API_HOST}/posting-api/job-board/{board_token}"

    def parse(self, body: bytes) -> ParsedBoard:
        """Validates the response shape and normalises the postings.

        Args:
            body: Raw response bytes.

        Returns:
            The parsed board. Ashby has no ``meta.total``, so ``meta_total`` is
            ``len(jobs)``. An empty ``jobs`` array gives ``is_empty``.

        Raises:
            InvalidResponse: ``not_json``, ``not_object``, ``jobs_not_list``, or
                ``no_valid_ids`` when a non-empty ``jobs`` array has no valid UUID.
        """
        document = load_json(body)
        if not isinstance(document, dict):
            raise InvalidResponse("not_object", type(document).__name__)
        jobs = document.get("jobs")
        if not isinstance(jobs, list):
            raise InvalidResponse("jobs_not_list")
        out = IssueCollector()
        postings = normalise_postings([_mapped(j) for j in jobs], out, _uuid_id)
        if jobs and not postings:
            raise InvalidResponse("no_valid_ids", f"{len(jobs)} entries")
        return ParsedBoard(
            postings=postings,
            fetched_count=len(jobs),
            meta_total=len(jobs),
            data_quality=tuple(out.issues),
        )
