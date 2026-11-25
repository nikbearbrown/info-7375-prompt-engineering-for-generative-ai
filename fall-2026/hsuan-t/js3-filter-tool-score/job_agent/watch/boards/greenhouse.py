"""Greenhouse Job Board API adapter (D1): where the board lives and how its response becomes Postings.

Everything Greenhouse-specific (URL shape, the {"jobs": [...]} envelope, location.name) stays in
this file, so the watch and the judges don't change if the board does.
"""

import json

from ...common.errors import CountMismatchError, WatchError
from ...common.posting import Posting
from ._places import join_places

ATS = "greenhouse"
ID_TYPE = int  # Greenhouse job ids are integers (JS1 state files store them as such)


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
        # type() is, not isinstance: True is an int in Python, and a saved True would make state.load
        # reject the file on the next run (found by test_adapter_conformance, JS2 Step 3c).
        if not isinstance(job, dict) or type(job.get("id")) is not int:
            raise WatchError("board response has a job without an integer 'id'")
        postings.append(Posting(
            id=job["id"],
            # Stripe titles sometimes carry leading tabs; strip for display only, matching splits anyway.
            title=(job.get("title") or "").strip(),
            location=_location(job),
            content=job.get("content") or "",
        ))
    _check_total(data, len(postings))
    return postings


def _check_total(data: dict, n_jobs: int) -> None:
    """Compare the list with Greenhouse's own count (JS2 D21). Every observed response had them
    equal (Stripe 765/765, 766/766, Cloudflare 464/464), so any difference, either way, means the
    list can't be trusted. A missing or non-integer total can't be checked and is let through, as
    checks/total_check.py does; type() is, not isinstance, so True is not read as a total of 1."""
    meta = data.get("meta")
    total = meta.get("total") if isinstance(meta, dict) else None
    if type(total) is int and total != n_jobs:
        raise CountMismatchError(f"the job list has {n_jobs} jobs but the board's meta.total says {total}")


def _location(job: dict) -> str:
    """location.name plus every office's place (JS2 D7). Some boards put a work mode in
    location.name ("Hybrid": 348 of 464 Cloudflare postings on 11/08) and the place only in
    offices[]; Stripe's offices add "US", which "Seattle, WA" alone lacked (JS1 Known limit).
    An office's full "location" ("Austin, TX, United States") is preferred over its short name."""
    names = [(job.get("location") or {}).get("name") or ""]
    for office in job.get("offices") or []:
        if isinstance(office, dict):
            names.append(office.get("location") or office.get("name") or "")
    return join_places(names)
