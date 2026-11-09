"""The two providers: exact API host, exact listing route (F2), URL builder, token check (F7).

No response parsing here yet.
"""

import re
from dataclasses import dataclass

from .errors import ConfigError

# F7: the whole token must match. re.fullmatch avoids the "$ matches before a final
# newline" trap, and [a-z0-9-] is ASCII-only in a str pattern.
TOKEN_PATTERN = re.compile(r"[a-z0-9-]+")


@dataclass(frozen=True)
class Provider:
    name: str
    host: str
    route_template: str  # holds "{token}"


PROVIDERS = {
    "greenhouse": Provider("greenhouse", "boards-api.greenhouse.io", "/v1/boards/{token}/jobs"),
    "ashby": Provider("ashby", "api.ashbyhq.com", "/posting-api/job-board/{token}"),
}


def check_board(provider: str, token: str) -> Provider:
    """The Provider for a valid (provider, token) pair; otherwise raise ConfigError."""
    if not isinstance(provider, str) or provider not in PROVIDERS:
        raise ConfigError(f"unknown provider {provider!r}; expected one of {sorted(PROVIDERS)}")
    if not isinstance(token, str) or TOKEN_PATTERN.fullmatch(token) is None:
        raise ConfigError(f"board token {token!r} must fully match [a-z0-9-]+")
    return PROVIDERS[provider]


@dataclass(frozen=True)
class Board:
    """One configured board. Construction validates the provider and token."""

    provider: str
    token: str

    def __post_init__(self):
        check_board(self.provider, self.token)

    @property
    def key(self) -> str:
        return f"{self.provider}/{self.token}"


def listing_route(board: Board) -> str:
    provider = check_board(board.provider, board.token)
    return provider.route_template.format(token=board.token)


def listing_url(board: Board) -> str:
    """The only URL the agent may request for this board: HTTPS, default port, no query."""
    provider = check_board(board.provider, board.token)
    return f"https://{provider.host}{listing_route(board)}"
