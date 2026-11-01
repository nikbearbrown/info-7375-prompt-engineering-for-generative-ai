"""Greenhouse Job Board API adapter (D1): where the board lives and how its response becomes Postings.

Everything Greenhouse-specific (URL shape, the {"jobs": [...]} envelope, location.name) stays in
this file, so the watch and the judges don't change if the board does.
"""

import json

from ...common.errors import WatchError
from ...common.posting import Posting


def board_url(board: str) -> str:
    # ?content=true is needed because checks 3-6 read the JD text, which the plain list omits.
    return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"


def parse(body: bytes) -> list[Posting]:
    """A response that isn't the Greenhouse shape is treated as a failed fetch, so state is never updated from junk."""
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        raise WatchError(f"board response is not JSON: {e}") from e
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise WatchError("board response has no 'jobs' list")
    postings = []
    for job in data["jobs"]:
        if not isinstance(job, dict) or not isinstance(job.get("id"), int):
            raise WatchError("board response has a job without an integer 'id'")
        postings.append(Posting(
            id=job["id"],
            # Stripe titles sometimes carry leading tabs; strip for display only, matching splits anyway.
            title=(job.get("title") or "").strip(),
            location=(job.get("location") or {}).get("name") or "",
            content=job.get("content") or "",
        ))
    return postings
