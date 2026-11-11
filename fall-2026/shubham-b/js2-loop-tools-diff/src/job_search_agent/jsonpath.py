"""A deliberately tiny JSONPath subset for evidence paths (CONTRACT §5, §7, §8).

Grammar: ``$`` followed by any number of ``.key`` or ``[index]`` steps, where ``key``
matches ``[A-Za-z_][A-Za-z0-9_]*`` and ``index`` is a non-negative decimal integer
without leading zeros. Wildcards (``[*]``), filters, slices, quoted keys, recursive
descent and negative indices are rejected, so every valid path names exactly one
value. A ``.key`` step only addresses a JSON object and an ``[index]`` step only a
JSON array.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any, Final

PathPart = str | int
"""One step: an object key or an array index."""

_STEP: Final = re.compile(r"\.([A-Za-z_][A-Za-z0-9_]*)|\[(0|[1-9][0-9]*)\]")
_KEY: Final = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class JsonPathSyntaxError(ValueError):
    """The path is not in the supported grammar."""


class PathNotFoundError(LookupError):
    """The path is well-formed but does not exist in the document."""


def parse_path(path: str) -> tuple[PathPart, ...]:
    """Parses a path into its steps.

    Args:
        path: For example ``"$.skills.backend[4]"``.

    Returns:
        The steps, e.g. ``("skills", "backend", 4)``; ``()`` for ``"$"``.

    Raises:
        JsonPathSyntaxError: If the path is outside the grammar.
    """
    if not path.startswith("$"):
        raise JsonPathSyntaxError("path must start with '$'")
    parts: list[PathPart] = []
    pos = 1
    while pos < len(path):
        step = _STEP.match(path, pos)
        if step is None:
            raise JsonPathSyntaxError(f"unsupported syntax at offset {pos}")
        key, index = step.groups()
        parts.append(key if key is not None else int(index))
        pos = step.end()
    return tuple(parts)


def format_path(parts: Sequence[PathPart]) -> str:
    """Formats steps as a path; the inverse of ``parse_path``.

    Args:
        parts: Keys (identifier strings) and non-negative ``int`` indices.

    Returns:
        The path string, e.g. ``"$.departments[0].name"``.

    Raises:
        JsonPathSyntaxError: If a key is not an identifier or an index is negative or
            a ``bool``.
    """
    out = ["$"]
    for part in parts:
        if isinstance(part, bool):
            raise JsonPathSyntaxError("bool is not an index")
        if isinstance(part, int):
            if part < 0:
                raise JsonPathSyntaxError("negative index")
            out.append(f"[{part}]")
        elif _KEY.fullmatch(part):
            out.append(f".{part}")
        else:
            raise JsonPathSyntaxError("key is not an identifier")
    return "".join(out)


def _step(node: Any, part: PathPart) -> Any:  # noqa: ANN401 - arbitrary JSON
    """Follows one step.

    Args:
        node: The current JSON value.
        part: A key (objects only) or an index (arrays only).

    Returns:
        The child value.

    Raises:
        PathNotFoundError: If the step does not exist on this node.
    """
    if isinstance(part, str):
        if isinstance(node, Mapping) and part in node:
            return node[part]
    elif (
        isinstance(node, Sequence)
        and not isinstance(node, str | bytes)
        and part < len(node)
    ):
        return node[part]
    raise PathNotFoundError(format_path((part,)))


def resolve(document: Any, path: str) -> Any:  # noqa: ANN401 - arbitrary JSON
    """Returns the value a path names.

    Args:
        document: A parsed JSON document (or a posting object).
        path: A path in the supported grammar.

    Returns:
        The value; ``document`` itself for ``"$"``.

    Raises:
        JsonPathSyntaxError: If the path is outside the grammar.
        PathNotFoundError: If any step does not exist.
    """
    node = document
    for part in parse_path(path):
        node = _step(node, part)
    return node


def exists(document: Any, path: str) -> bool:  # noqa: ANN401 - arbitrary JSON
    """Returns True if ``path`` is well-formed and names a value in ``document``.

    Args:
        document: A parsed JSON document.
        path: Any string.

    Returns:
        False for a malformed path or a missing value.
    """
    try:
        resolve(document, path)
    except (JsonPathSyntaxError, PathNotFoundError):
        return False
    return True
