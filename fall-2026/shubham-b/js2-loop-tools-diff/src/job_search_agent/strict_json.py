"""Strict-JSON hooks for ``json.loads`` shared by every parser of untrusted JSON.

``reject_duplicate_keys`` (``object_pairs_hook``) refuses an object that repeats a key,
which could otherwise hide a value. ``reject_constant`` (``parse_constant``) refuses
the non-standard constants ``NaN``, ``Infinity`` and ``-Infinity``. Both raise
``ValueError`` subclasses, so callers that only need "not strict JSON" can catch
``ValueError`` and callers that report the reason can catch each class.
"""

from __future__ import annotations

from typing import Any, NoReturn


class DuplicateKeyError(ValueError):
    """A JSON object repeats a key."""


class NonStandardConstantError(ValueError):
    """The text uses ``NaN``, ``Infinity`` or ``-Infinity``."""


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """``object_pairs_hook`` that builds the object or refuses a repeated key.

    Args:
        pairs: The object's key/value pairs in document order.

    Returns:
        The object.

    Raises:
        DuplicateKeyError: If a key appears twice.
    """
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError("duplicate key")
        result[key] = value
    return result


def reject_constant(name: str) -> NoReturn:
    """``parse_constant`` hook that refuses every non-standard constant.

    Args:
        name: The constant's spelling.

    Raises:
        NonStandardConstantError: Always.
    """
    raise NonStandardConstantError(f"non-standard JSON constant {name}")
