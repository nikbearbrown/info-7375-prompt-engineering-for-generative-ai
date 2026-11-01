"""Raw-response sources (``ports.RawSource``) and saved-evidence verification.

* ``LiveSource`` makes the run's one GET through an injected allow-listed fetcher. A
  body received with an unsuccessful status is still returned (with its sha256) so the
  pipeline can save it byte-for-byte as evidence; the error is kept beside it.
* ``ReplaySource`` re-reads a saved raw response and checks its sha256 against the
  ``.meta.json`` next to it before anything uses it. A replay is always a seeded run.
* ``verify_saved_evidence`` re-hashes every saved raw file against its meta (and every
  seeded run's ``REPLAYED_FROM.json`` pointer) for ``jsa verify-evidence``.

Paths written anywhere are repo-relative; absolute paths are used only to open files.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from job_search_agent.errors import PathRejected
from job_search_agent.models import (
    FetchErrorKind,
    RawRef,
    SourceKind,
    SourceResult,
)
from job_search_agent.ports import HttpFetcher

REPLAYED_FROM_NAME = "REPLAYED_FROM.json"
"""File in a seeded run's ``raw/`` folder pointing at the replayed response."""

ReadBytes = Callable[[Path], bytes]
"""Reads one file; the CLI wires ``fsio.ReadPolicy`` in front of ``Path.read_bytes``."""


def sha256_hex(data: bytes) -> str:
    """Returns the lowercase hex SHA-256 of ``data``."""
    return hashlib.sha256(data).hexdigest()


def meta_path_for(raw_path: Path) -> Path:
    """Returns the ``.meta.json`` path that describes a raw ``.json`` file.

    Args:
        raw_path: E.g. ``.../raw/greenhouse-stripe.json``.

    Returns:
        E.g. ``.../raw/greenhouse-stripe.meta.json``.
    """
    return raw_path.with_name(raw_path.stem + ".meta.json")


def parse_fetched_at(value: object) -> datetime | None:
    """Parses a meta file's ``fetched_at_utc``.

    Accepts ISO 8601 with an offset (written by the agent) and the run-id style
    ``2026-10-29T22-41-31Z`` used by the committed hand-check meta.

    Args:
        value: The raw JSON value.

    Returns:
        An aware UTC datetime, or ``None`` if the value is missing or unparseable.
    """
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        try:
            parsed = datetime.strptime(value, "%Y-%m-%dT%H-%M-%SZ").replace(tzinfo=UTC)
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(UTC)


class LiveSource:
    """One GET of the board's jobs URL through the allow-listed fetcher.

    Args:
        fetcher: The allow-listed HTTPS client (``http.build_fetcher``).
        url: The provider's jobs URL.
    """

    def __init__(self, fetcher: HttpFetcher, url: str) -> None:
        self._fetcher = fetcher
        self._url = url

    def obtain(self) -> SourceResult:
        """Fetches once; never raises for expected network failures.

        Returns:
            The body (also for non-2xx responses) with its sha256 and any error.
        """
        fetch = self._fetcher.get(self._url)
        body = fetch.body
        return SourceResult(
            kind=SourceKind.NETWORK,
            body=body,
            sha256=sha256_hex(body) if body is not None else None,
            error=fetch.error,
            error_detail=fetch.error_detail,
            fetch=fetch,
        )


class ReplaySource:
    """Replays a saved raw response after checking it against its meta file.

    Args:
        raw_path: Absolute path used to open the raw file.
        repo_rel: The same file as a repo-relative POSIX path (written to outputs).
        read_bytes: File reader; the CLI puts the read policy in front of it.
    """

    def __init__(
        self,
        raw_path: Path,
        repo_rel: str,
        *,
        read_bytes: ReadBytes = Path.read_bytes,
    ) -> None:
        self._raw_path = raw_path
        self._repo_rel = repo_rel
        self._read = read_bytes

    def obtain(self) -> SourceResult:
        """Reads the raw file and its meta and verifies the digest.

        Returns:
            The replayed bytes, or a ``REPLAY_UNREADABLE`` /
            ``REPLAY_DIGEST_MISMATCH`` error. No network request is made.
        """
        try:
            meta = json.loads(self._read(meta_path_for(self._raw_path)))
            body = self._read(self._raw_path)
        except (OSError, ValueError, PathRejected) as exc:
            detail = exc.reason if isinstance(exc, PathRejected) else type(exc).__name__
            return SourceResult(
                kind=SourceKind.REPLAY,
                body=None,
                sha256=None,
                error=FetchErrorKind.REPLAY_UNREADABLE,
                error_detail=detail,
            )
        digest = sha256_hex(body)
        expected = meta.get("sha256") if isinstance(meta, dict) else None
        original = (
            parse_fetched_at(meta.get("fetched_at_utc"))
            if isinstance(meta, dict)
            else None
        )
        ref = RawRef(path=self._repo_rel, sha256=digest)
        if expected != digest:
            return SourceResult(
                kind=SourceKind.REPLAY,
                body=None,
                sha256=digest,
                error=FetchErrorKind.REPLAY_DIGEST_MISMATCH,
                error_detail="sha256 differs from meta",
                replayed_from=ref,
                original_fetched_at_utc=original,
            )
        return SourceResult(
            kind=SourceKind.REPLAY,
            body=body,
            sha256=digest,
            error=None,
            replayed_from=ref,
            original_fetched_at_utc=original,
        )


# --- evidence verification ----------------------------------------------------


class EvidenceStatus(StrEnum):
    """Outcome of re-hashing one saved raw file."""

    OK = "OK"
    MISMATCH = "MISMATCH"
    MISSING = "MISSING"
    UNREADABLE = "UNREADABLE"


@dataclass(frozen=True, slots=True)
class EvidenceCheck:
    """One verified pointer: a meta (or REPLAYED_FROM) file and its raw file.

    Attributes:
        descriptor: Repo-relative path of the meta or pointer file.
        raw: Repo-relative path of the raw file it describes.
        status: The result.
    """

    descriptor: str
    raw: str
    status: EvidenceStatus


def _check_one(
    project_root: Path, descriptor: Path, raw_rel: str, expected: object
) -> EvidenceCheck:
    descriptor_rel = descriptor.relative_to(project_root).as_posix()
    raw_path = project_root / raw_rel
    if not raw_path.is_file():
        return EvidenceCheck(descriptor_rel, raw_rel, EvidenceStatus.MISSING)
    try:
        digest = sha256_hex(raw_path.read_bytes())
    except OSError:
        return EvidenceCheck(descriptor_rel, raw_rel, EvidenceStatus.UNREADABLE)
    status = EvidenceStatus.OK if digest == expected else EvidenceStatus.MISMATCH
    return EvidenceCheck(descriptor_rel, raw_rel, status)


def _load_json(path: Path) -> Mapping[str, Any] | None:
    try:
        obj = json.loads(path.read_bytes())
    except (OSError, ValueError):
        return None
    return obj if isinstance(obj, dict) else None


def verify_saved_evidence(
    project_root: Path, roots: tuple[str, ...] = ("evidence", "data")
) -> list[EvidenceCheck]:
    """Re-hashes every saved raw response against its recorded sha256.

    Covers ``*.meta.json`` files (the raw file is the sibling ``.json``) and seeded
    ``REPLAYED_FROM.json`` pointers (the raw file is their ``path``).

    Args:
        project_root: The repository root.
        roots: Repo-relative folders to scan.

    Returns:
        One check per descriptor, sorted by descriptor path.
    """
    checks: list[EvidenceCheck] = []
    for root in roots:
        base = project_root / root
        if not base.is_dir():
            continue
        for meta in sorted(base.rglob("*.meta.json")):
            if "tmp" in meta.relative_to(project_root).parts:
                continue
            raw = meta.with_name(meta.name.removesuffix(".meta.json") + ".json")
            obj = _load_json(meta)
            raw_rel = raw.relative_to(project_root).as_posix()
            if obj is None:
                rel = meta.relative_to(project_root).as_posix()
                checks.append(EvidenceCheck(rel, raw_rel, EvidenceStatus.UNREADABLE))
                continue
            checks.append(_check_one(project_root, meta, raw_rel, obj.get("sha256")))
        for pointer in sorted(base.rglob(REPLAYED_FROM_NAME)):
            obj = _load_json(pointer) or {}
            rel = pointer.relative_to(project_root).as_posix()
            target = obj.get("path")
            if not isinstance(target, str) or target.startswith("/") or ".." in target:
                checks.append(EvidenceCheck(rel, "", EvidenceStatus.UNREADABLE))
                continue
            checks.append(_check_one(project_root, pointer, target, obj.get("sha256")))
    return sorted(checks, key=lambda c: c.descriptor)
