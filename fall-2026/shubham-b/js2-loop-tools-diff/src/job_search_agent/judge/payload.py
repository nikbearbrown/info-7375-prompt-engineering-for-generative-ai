"""The two objects sent to Claude (PLAN §5.2; CONTRACT §4, §12).

**Résumé payload.** An index-preserving projection of the verified fixture: the four
``target`` arrays, the eight ``skills`` arrays, and only the ``bullets`` of each
``experience`` and ``projects`` entry, at their original indices. Every path in the
payload therefore means the same thing in the original fixture
(``$.skills.backend[4]``, ``$.experience[1].bullets[0]``). ``personal``,
``education``, ``work_authorization``, ``_comment``, ``fictional`` and the company,
title, dates and location of each job are never sent.

**Posting payload.** ``id``, ``title``, ``location.name``, the cleaned ``content`` and
the department names. No URL of any kind is included, so the prompt offers nothing to
fetch. A posting without a ``location.name`` gets no ``location`` key, so Claude cannot
cite a path that does not exist in the source.

Validator paths resolve against exactly these objects (A18).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any, cast

from job_search_agent.models import Posting, VerifiedResume
from job_search_agent.resume import REQUIRED_SKILL_KEYS, TARGET_KEYS
from job_search_agent.text import clean_html

BULLET_SECTIONS: tuple[str, ...] = ("experience", "projects")


class PayloadError(ValueError):
    """The verified résumé lacks a field the projection needs (a gate bug)."""


def _string_list(value: object, where: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise PayloadError(f"{where} must be a list of strings")
    return list(cast(list[str], value))


def build_resume_payload(resume: VerifiedResume) -> dict[str, Any]:
    """Projects the verified résumé onto the fields Claude may see.

    Args:
        resume: The verified fixture (the judge checks its type).

    Returns:
        A fresh dict with ``target``, ``skills``, ``experience`` and ``projects``.

    Raises:
        PayloadError: If a projected field is missing or has the wrong type.
    """
    data = resume.to_dict()
    target = data.get("target")
    skills = data.get("skills")
    if not isinstance(target, Mapping) or not isinstance(skills, Mapping):
        raise PayloadError("target and skills must be objects")
    payload: dict[str, Any] = {
        "target": {k: _string_list(target.get(k), f"target.{k}") for k in TARGET_KEYS},
        "skills": {
            k: _string_list(skills.get(k), f"skills.{k}") for k in REQUIRED_SKILL_KEYS
        },
    }
    for section in BULLET_SECTIONS:
        entries = data.get(section)
        if not isinstance(entries, list):
            raise PayloadError(f"{section} must be a list")
        projected: list[dict[str, list[str]]] = []
        for number, entry in enumerate(entries):
            if not isinstance(entry, Mapping):
                raise PayloadError(f"{section}[{number}] must be an object")
            bullets = _string_list(entry.get("bullets"), f"{section}[{number}].bullets")
            projected.append({"bullets": bullets})
        payload[section] = projected
    return payload


def build_posting_payload(posting: Posting) -> dict[str, Any]:
    """Builds the posting object sent to Claude (content cleaned per CONTRACT §5).

    Args:
        posting: The normalised posting.

    Returns:
        ``{"id", "title", "location": {"name"}, "content", "departments": [{"name"}]}``
        with ``location`` omitted when the posting has no ``location.name``.
    """
    payload: dict[str, Any] = {"id": posting.posting_id, "title": posting.title}
    if posting.location_name is not None:
        payload["location"] = {"name": posting.location_name}
    payload["content"] = clean_html(posting.content_raw)
    payload["departments"] = [{"name": name} for name in posting.department_names]
    return payload


def canonical_json(obj: object) -> str:
    """Serialises ``obj`` deterministically (sorted keys, compact, UTF-8 text)."""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def render_json(obj: object) -> str:
    """Serialises a payload for the prompt (insertion order, 2-space indent)."""
    return json.dumps(obj, ensure_ascii=False, indent=2)


def payload_sha256(
    resume_payload: Mapping[str, Any], posting_payload: Mapping[str, Any]
) -> str:
    """Digest of both payloads, recorded in every raw-reply log entry.

    Args:
        resume_payload: The résumé object as sent.
        posting_payload: The posting object as sent.

    Returns:
        Lowercase hex SHA-256 of the canonical JSON of ``[resume, posting]``.
    """
    pair: Sequence[Mapping[str, Any]] = (resume_payload, posting_payload)
    return hashlib.sha256(canonical_json(list(pair)).encode("utf-8")).hexdigest()
