"""Privacy audit: find résumé values, absolute paths and credentials in outputs (§12).

CONTRACT §12 allows only matched skill terms, their JSON paths and the fictional
persona label in outputs. ``sensitive_values`` lists the résumé values that must not
appear (the persona name, contact details, experience and project bullets, school and
employer names, work-authorisation status). ``scan_text`` and ``scan_tree`` report
*where* a value or pattern occurs (file, line, column, and the résumé JSON path or
pattern name), never the matched text itself, so the audit report cannot leak what it
found.

Matching is case-insensitive. Each value is also searched in its JSON-escaped forms,
so a value inside a JSON string (for example a quoted bullet in a model reply,
A24) is still found.

An ``allow`` string suppresses only a match that lies entirely inside one of its
occurrences (for example the persona label around the persona name). It never hides
a longer value that merely contains it, so allowing the skill terms cannot hide a
whole résumé bullet that mentions one of them. The judge uses ``scan_text`` this way
to reject replies that echo résumé values (``RESUME_VALUE_ECHO``, PLAN R10).
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Final

from job_search_agent.models import VerifiedResume

MIN_NEEDLE_LENGTH: Final = 6
"""Shorter forms are not searched (they would match unrelated text)."""

_FICTIONAL_SUFFIX = re.compile(r"\s*\(fictional\)\s*$", re.IGNORECASE)
_PHONE_TAIL = re.compile(r"555-01[0-9]{2}")


class FindingKind(StrEnum):
    """What a finding is."""

    RESUME_VALUE = "RESUME_VALUE"
    ABSOLUTE_PATH = "ABSOLUTE_PATH"
    CREDENTIAL = "CREDENTIAL"


PATTERNS: Final[Mapping[str, tuple[FindingKind, re.Pattern[str]]]] = {
    "home_dir_macos": (FindingKind.ABSOLUTE_PATH, re.compile(r"/Users/[^/\s\"']+")),
    "home_dir_linux": (FindingKind.ABSOLUTE_PATH, re.compile(r"/home/[^/\s\"']+")),
    "home_dir_windows": (
        FindingKind.ABSOLUTE_PATH,
        re.compile(r"[A-Za-z]:(?:\\\\|\\|/)Users(?:\\\\|\\|/)", re.IGNORECASE),
    ),
    "macos_tmp": (FindingKind.ABSOLUTE_PATH, re.compile(r"/private/var/folders/")),
    "anthropic_key": (
        FindingKind.CREDENTIAL,
        re.compile(r"sk-ant-[A-Za-z0-9_-]{8,}"),
    ),
    "credential_assignment": (
        FindingKind.CREDENTIAL,
        re.compile(
            r"(?:ANTHROPIC_API_KEY|ANTHROPIC_AUTH_TOKEN|CLAUDE_CODE_OAUTH_TOKEN)"
            r"\"?\s*[=:]\s*\"?[A-Za-z0-9_\-]{8,}",
            re.IGNORECASE,
        ),
    ),
    "bearer_token": (
        FindingKind.CREDENTIAL,
        re.compile(r"authorization\"?\s*:\s*\"?bearer\s+[A-Za-z0-9._~+/=-]{8,}", re.I),
    ),
}
"""Non-résumé patterns: name -> (kind, regex). Names appear in findings, text never."""


@dataclass(frozen=True, slots=True)
class SensitiveValue:
    """One résumé value that must not appear in outputs.

    Attributes:
        category: ``"name"``, ``"contact"``, ``"bullet"``, ``"institution"``,
            ``"employer"`` or ``"work_authorization"``.
        resume_path: Where the value lives, e.g. ``"$.experience[0].bullets[2]"``.
        value: The value itself (hidden from ``repr``; never print it).
    """

    category: str
    resume_path: str
    value: str = field(repr=False)

    def needles(self) -> tuple[str, ...]:
        """Returns the lowercase forms searched for (raw and JSON-escaped)."""
        forms: set[str] = set()
        bases = {self.value.strip()}
        stripped = _FICTIONAL_SUFFIX.sub("", self.value).strip()
        bases.add(stripped)
        if self.resume_path == "$.personal.phone":
            bases.update(_PHONE_TAIL.findall(self.value))
        for base in bases:
            forms.add(base)
            forms.add(json.dumps(base)[1:-1])
            forms.add(json.dumps(base, ensure_ascii=False)[1:-1])
        return tuple(
            sorted(
                {form.lower() for form in forms if len(form) >= MIN_NEEDLE_LENGTH},
                key=lambda form: (-len(form), form),
            )
        )


@dataclass(frozen=True, slots=True)
class Finding:
    """Where something sensitive occurs. Holds no matched text.

    Attributes:
        kind: What was found.
        location: File path relative to the scanned root, or the label given to
            ``scan_text``.
        line: 1-based line.
        column: 1-based column.
        label: The résumé JSON path (for ``RESUME_VALUE``) or the pattern name.
    """

    kind: FindingKind
    location: str
    line: int
    column: int
    label: str

    def describe(self) -> str:
        """Returns ``location:line:column KIND label`` (safe to print)."""
        return f"{self.location}:{self.line}:{self.column} {self.kind} {self.label}"


def _str_at(container: object, key: str | int) -> str | None:
    if isinstance(container, dict) and isinstance(key, str):
        value = container.get(key)
    elif isinstance(container, list) and isinstance(key, int) and key < len(container):
        value = container[key]
    else:
        return None
    return value if isinstance(value, str) else None


def _items(container: object) -> Iterator[tuple[int, Any]]:
    if isinstance(container, list):
        yield from enumerate(container)


def sensitive_values(resume: VerifiedResume) -> tuple[SensitiveValue, ...]:
    """Lists the résumé values that must never appear in outputs (§12).

    Skill terms are deliberately absent: matched terms and their paths are allowed.

    Args:
        resume: The verified résumé.

    Returns:
        The values with their categories and JSON paths.

    """
    doc = resume.to_dict()
    found: list[SensitiveValue] = []

    def add(category: str, path: str, value: str | None) -> None:
        if value and value.strip():
            found.append(SensitiveValue(category, path, value))

    personal = doc.get("personal")
    add("name", "$.personal.name", _str_at(personal, "name"))
    for key in ("email", "phone", "linkedin", "github"):
        add("contact", f"$.personal.{key}", _str_at(personal, key))
    add(
        "work_authorization",
        "$.work_authorization.status",
        _str_at(doc.get("work_authorization"), "status"),
    )
    for i, school in _items(doc.get("education")):
        add(
            "institution",
            f"$.education[{i}].institution",
            _str_at(school, "institution"),
        )
    for i, job in _items(doc.get("experience")):
        add("employer", f"$.experience[{i}].company", _str_at(job, "company"))
    for section in ("experience", "projects"):
        for i, item in _items(doc.get(section)):
            bullets = item.get("bullets") if isinstance(item, dict) else None
            for j, _ in _items(bullets):
                add("bullet", f"$.{section}[{i}].bullets[{j}]", _str_at(bullets, j))
    return tuple(found)


def _line_col(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    start = text.rfind("\n", 0, offset) + 1
    return line, offset - start + 1


def _allowed_spans(lowered: str, allow: Iterable[str]) -> list[tuple[int, int]]:
    """Returns every ``(start, end)`` occurrence of an allowed string (lowercased)."""
    spans: list[tuple[int, int]] = []
    for allowed in {a.lower() for a in allow if a}:
        start = lowered.find(allowed)
        while start != -1:
            spans.append((start, start + len(allowed)))
            start = lowered.find(allowed, start + 1)
    return spans


def _inside(start: int, end: int, spans: Iterable[tuple[int, int]]) -> bool:
    return any(s <= start and end <= e for s, e in spans)


def scan_text(
    text: str,
    values: Iterable[SensitiveValue],
    *,
    location: str = "<text>",
    allow: Iterable[str] = (),
    patterns: bool = True,
) -> list[Finding]:
    """Finds résumé values and sensitive patterns in ``text``.

    Args:
        text: Text to scan.
        values: From ``sensitive_values``.
        location: Label used in findings (e.g. a relative file path).
        allow: Strings that may appear even if they contain a value (e.g. the
            persona label); a match is suppressed only when it lies wholly inside
            an occurrence of one of them.
        patterns: Also search for absolute paths and credentials (``PATTERNS``).

    Returns:
        Findings ordered by position; one per distinct (position, label).
    """
    lowered = text.lower()
    allowed = _allowed_spans(lowered, allow)
    hits: set[tuple[int, FindingKind, str]] = set()
    for value in values:
        covered: list[tuple[int, int]] = []
        for needle in value.needles():
            start = lowered.find(needle)
            while start != -1:
                end = start + len(needle)
                if not _inside(start, end, covered) and not _inside(
                    start, end, allowed
                ):
                    covered.append((start, end))
                    hits.add((start, FindingKind.RESUME_VALUE, value.resume_path))
                start = lowered.find(needle, start + 1)
    if patterns:
        for name, (kind, regex) in PATTERNS.items():
            for match in regex.finditer(text):
                if not _inside(match.start(), match.end(), allowed):
                    hits.add((match.start(), kind, name))
    findings = []
    for offset, kind, label in sorted(hits):
        line, column = _line_col(text, offset)
        findings.append(Finding(kind, location, line, column, label))
    return findings


def scan_tree(
    root: Path,
    values: Iterable[SensitiveValue],
    *,
    allow: Iterable[str] = (),
    patterns: bool = True,
) -> list[Finding]:
    """Scans every regular file below ``root`` (symlinks are not followed).

    Args:
        root: Directory (or single file) to scan.
        values: From ``sensitive_values``.
        allow: As for ``scan_text``.
        patterns: As for ``scan_text``.

    Returns:
        Findings with ``location`` relative to ``root`` (POSIX), ordered by file.
        Bytes that are not UTF-8 are replaced before scanning.
    """
    value_list = tuple(values)
    allow_list = tuple(allow)
    root = Path(root)
    if root.is_file() and not root.is_symlink():
        files = [(root, root.name)]
    else:
        files = []
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            dirnames.sort()
            for name in sorted(filenames):
                path = Path(dirpath) / name
                if path.is_symlink() or not path.is_file():
                    continue
                files.append((path, path.relative_to(root).as_posix()))
    findings: list[Finding] = []
    for path, rel in files:
        text = path.read_bytes().decode("utf-8", errors="replace")
        findings.extend(
            scan_text(
                text, value_list, location=rel, allow=allow_list, patterns=patterns
            )
        )
    return findings
