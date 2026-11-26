"""Prompt contract files: loading, section parsing, rendering (PLAN §5.3).

A prompt file such as ``prompts/judge.v1.md`` consists of marked sections::

    <!-- section:NAME -->
    ...body...
    <!-- /section -->

Text outside the sections (the provenance header) is documentation only and is never
sent. The rendered prompt is the section bodies, in file order, each stripped of
surrounding blank lines and joined by one blank line, with ``{{RESUME_JSON}}`` and
``{{POSTING_JSON}}`` substituted in a single pass (so text inside a payload is never
re-scanned for placeholders). Each placeholder must occur exactly once, inside the
``inputs`` section.

The file's SHA-256 (over its exact bytes) is the prompt's identity and is recorded in
every raw-reply log entry and every judgment diagnostic.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

REQUIRED_SECTIONS: tuple[str, ...] = (
    "role",
    "task",
    "label_definition",
    "output_schema",
    "path_rules",
    "uncertainty_rules",
    "untrusted_input",
    "inputs",
)
"""Section names, in the required order."""

RESUME_PLACEHOLDER = "{{RESUME_JSON}}"
POSTING_PLACEHOLDER = "{{POSTING_JSON}}"

_SECTION = re.compile(r"<!-- section:([a-z_]+) -->\n(.*?)<!-- /section -->", re.DOTALL)
_ANY_MARKER = re.compile(r"<!-- (?:section:[^>]*|/section) -->")
_PLACEHOLDER = re.compile(r"\{\{(RESUME_JSON|POSTING_JSON)\}\}")
_VERSION = re.compile(r"^v[0-9]+$")


class PromptError(ValueError):
    """A prompt file is missing, malformed or breaks the section rules."""


@dataclass(frozen=True, slots=True)
class PromptContract:
    """A loaded, checked prompt file.

    Attributes:
        prompt_id: ``"judge.<version>"``, e.g. ``"judge.v1"``.
        version: ``"v1"``, ``"v2"``, ...
        repo_path: Repo-relative path of the file, e.g. ``"prompts/judge.v1.md"``.
        sha256: SHA-256 of the file's exact bytes.
        sections: Section name to body, in file order.
    """

    prompt_id: str
    version: str
    repo_path: str
    sha256: str
    sections: Mapping[str, str] = field(repr=False)

    def render(self, resume_json: str, posting_json: str) -> str:
        """Renders the full prompt text.

        Args:
            resume_json: The serialised résumé payload.
            posting_json: The serialised posting payload.

        Returns:
            The prompt; identical inputs always give byte-identical output.
        """
        template = "\n\n".join(self.sections.values()) + "\n"
        values = {"RESUME_JSON": resume_json, "POSTING_JSON": posting_json}
        return _PLACEHOLDER.sub(lambda m: values[m.group(1)], template)


def parse_sections(text: str) -> dict[str, str]:
    """Extracts and checks the marked sections of a prompt file.

    Args:
        text: The whole file as text.

    Returns:
        Section name to body (surrounding blank lines removed), in file order.

    Raises:
        PromptError: If sections are missing, duplicated, out of order, nested or
            unbalanced, or if a placeholder is not exactly once inside ``inputs``.
    """
    sections: dict[str, str] = {}
    for match in _SECTION.finditer(text):
        name, body = match.group(1), match.group(2)
        if name in sections:
            raise PromptError(f"duplicate section: {name}")
        if _ANY_MARKER.search(body):
            raise PromptError(f"nested or unbalanced marker in section: {name}")
        sections[name] = body.strip("\n")
    if len(_ANY_MARKER.findall(text)) != 2 * len(sections):
        raise PromptError("unbalanced section markers")
    if tuple(sections) != REQUIRED_SECTIONS:
        raise PromptError(
            "sections must be exactly, in order: " + ", ".join(REQUIRED_SECTIONS)
        )
    for placeholder in (RESUME_PLACEHOLDER, POSTING_PLACEHOLDER):
        if text.count(placeholder) != 1 or sections["inputs"].count(placeholder) != 1:
            raise PromptError(f"{placeholder} must occur exactly once, in 'inputs'")
    return sections


def prompt_repo_path(version: str) -> str:
    """Returns the repo-relative path of a prompt version.

    Args:
        version: ``"v1"``, ``"v2"``, ...

    Returns:
        E.g. ``"prompts/judge.v1.md"``.

    Raises:
        PromptError: If ``version`` is not ``v<digits>``.
    """
    if not _VERSION.match(version):
        raise PromptError("prompt version must look like 'v1'")
    return f"prompts/judge.{version}.md"


def load_prompt(
    repo_root: Path,
    version: str,
    *,
    read_bytes: Callable[[Path], bytes] = Path.read_bytes,
) -> PromptContract:
    """Loads and checks ``prompts/judge.<version>.md``.

    Args:
        repo_root: The project root.
        version: ``"v1"``, ``"v2"``, ...
        read_bytes: File reader (injectable for tests and read policies).

    Returns:
        The checked prompt contract.

    Raises:
        PromptError: If the file is missing, not UTF-8 or malformed.
    """
    rel = prompt_repo_path(version)
    try:
        raw = read_bytes(repo_root / rel)
    except FileNotFoundError as exc:
        raise PromptError(f"prompt file not found: {rel}") from exc
    return contract_from_bytes(raw, version=version, repo_path=rel)


def contract_from_bytes(raw: bytes, *, version: str, repo_path: str) -> PromptContract:
    """Builds a ``PromptContract`` from file bytes.

    Args:
        raw: The exact file bytes.
        version: The version string.
        repo_path: Repo-relative path, for provenance.

    Returns:
        The checked contract.

    Raises:
        PromptError: If the bytes are not UTF-8 or the sections are malformed.
    """
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PromptError(f"prompt file is not UTF-8: {repo_path}") from exc
    return PromptContract(
        prompt_id=f"judge.{version}",
        version=version,
        repo_path=repo_path,
        sha256=hashlib.sha256(raw).hexdigest(),
        sections=parse_sections(text),
    )


def changed_sections(old: PromptContract, new: PromptContract) -> list[str]:
    """Lists the sections whose bodies differ between two prompt versions.

    Both contracts have the same section names in the same order (enforced by
    ``parse_sections``), so the comparison is per name.

    Args:
        old: The earlier version (v1).
        new: The later version (v2).

    Returns:
        Names of changed sections in file order; ``freeze`` requires exactly one.
    """
    return [name for name in old.sections if old.sections[name] != new.sections[name]]
