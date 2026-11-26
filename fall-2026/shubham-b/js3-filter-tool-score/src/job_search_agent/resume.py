"""The résumé gate (CONTRACT §12) and read-only views of a verified résumé (§4).

``load_verified_resume`` is the only code that constructs a ``VerifiedResume`` (the
constructor demands this module's private ``_GATE_TOKEN``). It
reads the fixture bytes exactly once, checks their SHA-256 against a digest pinned in
configuration (never one computed from the same file at runtime), then parses those
same bytes and runs every content check. All failing checks are collected into one
``ResumeRefused``; its message holds refusal codes only, never résumé values.

``source_path`` derivation: ``VerifiedResume.source_path`` must be repo-relative. The
caller may pass ``project_root``; by default it is the repository root found by
walking up from this module's location (the first ancestor holding both
``pyproject.toml`` and ``config/agent.toml``), falling back to the current directory
when it holds them. A fixture path that does not resolve inside the project root is a
``ConfigError``: it is refused before it is read.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any, Final

from job_search_agent.errors import ConfigError, PathRejected, ResumeRefused
from job_search_agent.fsio import relative_within
from job_search_agent.models import RefusalCode, VerifiedResume
from job_search_agent.rule.skills import SKILL_PATHS
from job_search_agent.strict_json import reject_constant, reject_duplicate_keys

PERSONA_NAME: Final = "Kiran Joshi"
"""The only approved persona (A13)."""

PERSONA_LABEL: Final = "kiran-joshi (fictional)"
"""The fixture label outputs may show (§12); it never contains the persona name."""

EMAIL_DOMAIN: Final = "example.com"
"""The only accepted email domain, compared exactly (no suffix test, §12.2)."""

PHONE_PATTERN: Final = re.compile(
    r"(?:\+1[ .-]?)?(?:\([0-9]{3}\) ?|[0-9]{3}[ .-])?555-01[0-9]{2}"
)
"""Reserved fictional ``555-01xx`` numbers (A12); applied with ``fullmatch``."""

TARGET_KEYS: Final = ("roles", "levels", "locations", "excluded")
"""The four ``$.target`` arrays (§4)."""

COUNTED_SKILL_KEYS: Final = tuple(p.removeprefix("$.skills.") for p in SKILL_PATHS)
"""The seven skill arrays the rule counts, in §4 order (owned by ``rule.skills``)."""

REQUIRED_SKILL_KEYS: Final = (*COUNTED_SKILL_KEYS, "familiar_with_not_shipped")
"""All eight skill arrays that must be present (A13); the last is never counted."""

_SHA256_HEX = re.compile(r"[0-9a-f]{64}")

_GATE_TOKEN: Final = object()
"""Module-private sentinel: ``VerifiedResume`` refuses to be built without it, so only
``load_verified_resume`` can mint one (review fix 6)."""
_MARKERS: Final = ("pyproject.toml", "config/agent.toml")


def default_project_root() -> Path:
    """Finds the repository root used to make ``source_path`` repo-relative.

    Returns:
        The first ancestor of this module (then the current directory) that holds
        both ``pyproject.toml`` and ``config/agent.toml``.

    Raises:
        ConfigError: If no such directory is found.
    """
    candidates = [*Path(__file__).resolve().parents, Path.cwd().resolve()]
    for candidate in candidates:
        if all((candidate / marker).is_file() for marker in _MARKERS):
            return candidate
    raise ConfigError("project root not found; pass project_root explicitly")


def _repo_relative(path: Path, project_root: Path) -> tuple[Path, str]:
    """Returns the absolute fixture path and its repo-relative POSIX form.

    Raises:
        ConfigError: If the path does not resolve inside ``project_root``.
    """
    root = project_root.resolve()
    absolute = path if path.is_absolute() else root / path
    try:
        return absolute, relative_within(absolute, root)
    except PathRejected:
        raise ConfigError("resume path must resolve inside the project root") from None


def _parse(data: bytes) -> Any:  # noqa: ANN401 - arbitrary JSON
    """Parses strict UTF-8 JSON; raises ``ValueError`` on anything else."""
    text = data.decode("utf-8")  # UnicodeDecodeError is a ValueError
    return json.loads(
        text, object_pairs_hook=reject_duplicate_keys, parse_constant=reject_constant
    )


def _is_str_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _email_ok(email: str) -> bool:
    """Checks for exactly one ``@`` and the domain exactly ``example.com``.

    The local part must be non-empty and free of whitespace and control characters.
    """
    if email.count("@") != 1:
        return False
    local, domain = email.split("@")
    clean_local = bool(local) and all(
        ch.isprintable() and not ch.isspace() for ch in local
    )
    return clean_local and domain == EMAIL_DOMAIN


def _check_personal(personal: object, codes: set[RefusalCode]) -> None:
    if not isinstance(personal, dict):
        codes.add(RefusalCode.MISSING_FIELD)
        return
    name = personal.get("name")
    if not isinstance(name, str):
        codes.add(RefusalCode.MISSING_FIELD)
    elif name != PERSONA_NAME:
        codes.add(RefusalCode.PERSONA_MISMATCH)
    email = personal.get("email")
    if not isinstance(email, str):
        codes.add(RefusalCode.MISSING_FIELD)
    elif not _email_ok(email):
        codes.add(RefusalCode.EMAIL_DOMAIN)
    phone = personal.get("phone")
    if not isinstance(phone, str):
        codes.add(RefusalCode.MISSING_FIELD)
    elif PHONE_PATTERN.fullmatch(phone.strip()) is None:
        codes.add(RefusalCode.PHONE_PATTERN)


def _arrays_ok(section: object, keys: tuple[str, ...]) -> bool:
    return isinstance(section, dict) and all(
        _is_str_list(section.get(key)) for key in keys
    )


def _bullets_ok(items: object) -> bool:
    return isinstance(items, list) and all(
        isinstance(item, dict) and _is_str_list(item.get("bullets")) for item in items
    )


def _content_codes(doc: object) -> set[RefusalCode]:
    """Runs every content check (§12.1-12.4, A12, A13) and returns all failures."""
    codes: set[RefusalCode] = set()
    if not isinstance(doc, dict):
        return {RefusalCode.NOT_FICTIONAL, RefusalCode.MISSING_FIELD}
    if doc.get("fictional") is not True:
        codes.add(RefusalCode.NOT_FICTIONAL)
    _check_personal(doc.get("personal"), codes)
    if not _arrays_ok(doc.get("target"), TARGET_KEYS):
        codes.add(RefusalCode.MISSING_FIELD)
    if not _arrays_ok(doc.get("skills"), REQUIRED_SKILL_KEYS):
        codes.add(RefusalCode.MISSING_FIELD)
    if not _bullets_ok(doc.get("experience")) or not _bullets_ok(doc.get("projects")):
        codes.add(RefusalCode.MISSING_FIELD)
    return codes


def load_verified_resume(
    path: Path,
    pinned_sha256: str | None,
    *,
    read_bytes: Callable[[Path], bytes] = Path.read_bytes,
    project_root: Path | None = None,
) -> VerifiedResume:
    """Verifies the résumé fixture and returns proof of verification.

    Order: the path is placed inside the project root; the bytes are read once; their
    digest is compared with the pin; then the same bytes are parsed and every content
    check runs. Failures are collected, not short-circuited, except that an
    unreadable file stops at ``UNREADABLE``.

    Args:
        path: Fixture path, absolute or relative to ``project_root``.
        pinned_sha256: The expected lowercase hex digest from configuration or the
            test suite. ``None``, empty or malformed counts as not set.
        read_bytes: Reads the file. The CLI passes ``fsio.ReadPolicy.read_bytes``,
            so a fixture outside the read roots is refused; tests may spy on it.
        project_root: Repository root used for ``source_path``; defaults to
            ``default_project_root()``.

    Returns:
        The verified résumé, with a repo-relative ``source_path``.

    Raises:
        ResumeRefused: With every failing ``RefusalCode``; the message holds codes
            only.
        ConfigError: If the path is outside the project root, the reader refuses
            it (``PathRejected``, e.g. outside ``fsio.DEFAULT_READ_ROOTS``), or no
            root is found.
    """
    root = project_root if project_root is not None else default_project_root()
    absolute, source_path = _repo_relative(path, root)
    try:
        data = read_bytes(absolute)
    except PathRejected:
        raise ConfigError("resume path is outside the readable roots") from None
    except OSError:
        raise ResumeRefused({RefusalCode.UNREADABLE}) from None

    codes: set[RefusalCode] = set()
    digest = hashlib.sha256(data).hexdigest()
    pin_set = pinned_sha256 is not None and _SHA256_HEX.fullmatch(pinned_sha256)
    if not pin_set:
        codes.add(RefusalCode.PIN_NOT_SET)
    elif digest != pinned_sha256:
        codes.add(RefusalCode.DIGEST_MISMATCH)

    try:
        doc = _parse(data)
    except ValueError:
        codes.add(RefusalCode.NOT_JSON)
    else:
        codes |= _content_codes(doc)

    if codes:
        raise ResumeRefused(codes)
    return VerifiedResume(
        doc, sha256=digest, source_path=source_path, token=_GATE_TOKEN
    )
