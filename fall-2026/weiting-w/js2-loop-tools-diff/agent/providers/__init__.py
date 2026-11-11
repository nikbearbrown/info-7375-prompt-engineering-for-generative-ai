"""The provider registry.

A board plan entry names its provider by string; this is where that string
becomes code. Adding a provider means adding it here and to
`policy.ALLOWED_HOSTS` — two edits, both reviewable, neither of them a prompt.
"""

from __future__ import annotations

from .ashby import Ashby
from .base import Posting, Provider
from .greenhouse import Greenhouse
from .lever import Lever

REGISTRY: dict[str, Provider] = {
    Greenhouse.name: Greenhouse(),
    Lever.name: Lever(),
    Ashby.name: Ashby(),
}


def get(name: str) -> Provider:
    try:
        return REGISTRY[name]
    except KeyError:
        raise KeyError(
            f"unknown provider {name!r}; known: {sorted(REGISTRY)}"
        ) from None


__all__ = ["REGISTRY", "get", "Posting", "Provider", "Greenhouse", "Lever", "Ashby"]
