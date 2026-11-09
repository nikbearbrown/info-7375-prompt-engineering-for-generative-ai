"""The two providers: exact API host, exact listing route (F2), URL builder, token check (F7),
and listing-response parsing (F3).
"""

import json
import re
from dataclasses import dataclass

from .errors import ConfigError, MalformedResponse

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


# ---------- Response parsing (F3) ----------

def valid_id(provider: str, value) -> bool:
    """Greenhouse IDs are integers excluding booleans; Ashby IDs are non-empty strings."""
    if provider == "greenhouse":
        return isinstance(value, int) and not isinstance(value, bool)
    if provider == "ashby":
        return isinstance(value, str) and value != ""
    raise ConfigError(f"unknown provider {provider!r}")


@dataclass(frozen=True)
class ParsedJobs:
    ids: tuple            # unique IDs, in response order
    jobs_in_response: int
    duplicates_removed: int


def parse_ids(provider: str, body: bytes) -> ParsedJobs:
    """Unique posting IDs from a listing response, or raise MalformedResponse (F3).

    An empty body, invalid JSON, a top level that isn't an object, a missing or non-list
    `jobs`, or any job without a valid `id` is malformed. A valid empty `jobs` list is zero.
    """
    if provider not in PROVIDERS:
        raise ConfigError(f"unknown provider {provider!r}")
    if not body:
        raise MalformedResponse("empty body")
    try:
        data = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as err:
        raise MalformedResponse(f"not valid JSON: {err}") from None
    if not isinstance(data, dict):
        raise MalformedResponse(f"top level is {type(data).__name__}, not an object")
    if "jobs" not in data:
        raise MalformedResponse("'jobs' is missing")
    jobs = data["jobs"]
    if not isinstance(jobs, list):
        raise MalformedResponse(f"'jobs' is {type(jobs).__name__}, not a list")
    unique, seen = [], set()
    for index, job in enumerate(jobs):
        if not isinstance(job, dict) or "id" not in job:
            raise MalformedResponse(f"job {index} has no 'id'")
        posting_id = job["id"]
        if not valid_id(provider, posting_id):
            kind = "a non-bool integer" if provider == "greenhouse" else "a non-empty string"
            raise MalformedResponse(f"job {index} id {posting_id!r} is not {kind}")
        if posting_id not in seen:
            seen.add(posting_id)
            unique.append(posting_id)
    return ParsedJobs(ids=tuple(unique), jobs_in_response=len(jobs),
                      duplicates_removed=len(jobs) - len(unique))
