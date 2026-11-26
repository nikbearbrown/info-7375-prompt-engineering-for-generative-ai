"""Shared test builders: the fixture résumé and constructed postings.

``fixture_resume`` goes through the real résumé gate (``resume.load_verified_resume``)
with the independently pinned digest in ``tests.conftest``; a ``VerifiedResume`` cannot
be built any other way (review fix 6). A mutated copy is written to a temporary
project and verified against the digest of the mutated bytes, so it must still pass
every §12 content check.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from functools import cache
from pathlib import Path
from typing import Any

from job_search_agent.models import ParsedBoard, Posting, RuleVerdict, VerifiedResume
from job_search_agent.providers.greenhouse import GreenhouseProvider
from job_search_agent.resume import load_verified_resume
from job_search_agent.rule.verdict import evaluate
from tests.conftest import (
    HANDCHECK_RAW_REL,
    PINNED_RESUME_SHA256,
    REPO_ROOT,
    RESUME_FIXTURE_REL,
)


@cache
def _fixture_bytes() -> bytes:
    body = (REPO_ROOT / RESUME_FIXTURE_REL).read_bytes()
    digest = hashlib.sha256(body).hexdigest()
    if digest != PINNED_RESUME_SHA256:
        raise AssertionError("fixture bytes differ from the pinned digest")
    return body


def fixture_resume_data() -> dict[str, Any]:
    """Returns a fresh parsed copy of the committed fixture."""
    data: dict[str, Any] = json.loads(_fixture_bytes())
    return data


@cache
def _committed_resume() -> VerifiedResume:
    _fixture_bytes()
    return load_verified_resume(
        REPO_ROOT / RESUME_FIXTURE_REL, PINNED_RESUME_SHA256, project_root=REPO_ROOT
    )


def fixture_resume(data: dict[str, Any] | None = None) -> VerifiedResume:
    """Verifies the fixture (or a mutated copy of it) through the real gate.

    Args:
        data: A mutated copy of the fixture for tests that change one field; the
            committed fixture when omitted. The copy is pinned to its own digest
            and must pass the §12 content checks.

    Returns:
        The verified résumé.
    """
    if data is None:
        return _committed_resume()
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = root / RESUME_FIXTURE_REL
        path.parent.mkdir(parents=True)
        path.write_bytes(body)
        return load_verified_resume(
            path, hashlib.sha256(body).hexdigest(), project_root=root
        )


def job(**fields: Any) -> dict[str, Any]:
    """A constructed Greenhouse job object; keyword arguments override defaults.

    Defaults: ``Software Engineer`` in ``Seattle, WA`` with empty content and one
    ``Engineering`` department. Delete keys from the result when a field must be
    absent.
    """
    base: dict[str, Any] = {
        "id": 1,
        "title": "Software Engineer",
        "location": {"name": "Seattle, WA"},
        "updated_at": None,
        "content": "",
        "departments": [{"name": "Engineering"}],
    }
    base.update(fields)
    return base


def posting(**fields: Any) -> Posting:
    """A constructed posting, normalised through the real Greenhouse parser.

    Args:
        **fields: Overrides for ``job``. ``content`` is plain text or HTML; it is
            stored as given (not escaped).

    Returns:
        The single parsed posting.
    """
    return posting_from_job(job(**fields))


def small_posting(**fields: Any) -> Posting:
    """``posting`` with escaped-HTML content naming Java, Python and AWS, ID 1234."""
    base: dict[str, Any] = {
        "id": 1234,
        "content": "&lt;p&gt;Java and Python on AWS&lt;/p&gt;",
        "absolute_url": "https://example.invalid/jobs/1234",
        "updated_at": "2026-10-29T10:00:00-04:00",
    }
    base.update(fields)
    return posting(**base)


def posting_from_job(raw_job: dict[str, Any]) -> Posting:
    """Normalises one job object through the real Greenhouse parser."""
    body = json.dumps({"jobs": [raw_job], "meta": {"total": 1}}).encode()
    (only,) = GreenhouseProvider().parse(body).postings
    return only


@cache
def handcheck_board() -> ParsedBoard:
    """The committed §13 raw response, parsed once per test session."""
    return GreenhouseProvider().parse((REPO_ROOT / HANDCHECK_RAW_REL).read_bytes())


@cache
def handcheck_verdicts() -> tuple[tuple[Posting, RuleVerdict], ...]:
    """Every committed §13 posting with its rule verdict, evaluated once per session."""
    resume = fixture_resume()
    return tuple((p, evaluate(p, resume)) for p in handcheck_board().postings)


def handcheck_posting(posting_id: str) -> Posting:
    """One posting of the committed §13 raw response, by ID."""
    (found,) = [p for p in handcheck_board().postings if p.posting_id == posting_id]
    return found
