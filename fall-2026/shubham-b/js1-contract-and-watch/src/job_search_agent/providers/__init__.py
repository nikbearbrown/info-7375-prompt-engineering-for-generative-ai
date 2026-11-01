"""Board-provider registry (PLAN §1.1; the JS2 seam for more job-board APIs).

``config.board.provider`` names an entry here; the pipeline asks ``get_provider`` for
it and talks to it only through the ``ports.BoardProvider`` Protocol.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Final

from job_search_agent.errors import ConfigError
from job_search_agent.ports import BoardProvider
from job_search_agent.providers.greenhouse import GreenhouseProvider

PROVIDERS: Final[Mapping[str, Callable[[], BoardProvider]]] = MappingProxyType(
    {"greenhouse": GreenhouseProvider}
)
"""Registry name -> provider factory. Read-only."""


def get_provider(name: str) -> BoardProvider:
    """Builds the provider registered under ``name``.

    Args:
        name: Registry name, e.g. ``"greenhouse"``.

    Returns:
        A fresh provider instance.

    Raises:
        ConfigError: If no provider is registered under that name.
    """
    factory = PROVIDERS.get(name)
    if factory is None:
        raise ConfigError(f"unknown board provider; known: {sorted(PROVIDERS)}")
    return factory()


__all__ = ["PROVIDERS", "GreenhouseProvider", "get_provider"]
