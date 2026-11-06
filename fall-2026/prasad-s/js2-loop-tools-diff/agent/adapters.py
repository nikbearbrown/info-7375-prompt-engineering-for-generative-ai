"""Board adapters: a 200 body into postings, or UnexpectedShape (GATE.md §4; CONTRACT v0.5 item 3).

Every posting comes out in the shape agent.rule reads: posting_id (a string),
title, location.name, content, absolute_url, plus "ats". A missing field
stays missing, so its condition is false (§4); only the list and the ids
decide whether the shape is the expected one.
"""

import json

from .errors import RunError
from .state import parse_board_response


class UnexpectedShape(Exception):
    """A 200 body that is not the ATS's job list. Never parsed as zero jobs (GATE.md §4)."""


def _jobs(body):
    try:
        data = json.loads(body)
    except (ValueError, UnicodeDecodeError) as exc:
        raise UnexpectedShape(f"body is not JSON: {exc}") from exc
    jobs = data.get("jobs") if isinstance(data, dict) else None
    if not isinstance(jobs, list):
        raise UnexpectedShape("body has no 'jobs' list")
    return jobs


def greenhouse(body):
    """JS1's parse, for any configured token. ids are numbers on the board; str() at the boundary (§1 item 3)."""
    for index, job in enumerate(_jobs(body)):
        job_id = job.get("id") if isinstance(job, dict) else None
        # Decision 2026-11-06: a Greenhouse id is a JSON number or a non-empty string.
        if isinstance(job_id, bool) or not (isinstance(job_id, int) or (isinstance(job_id, str) and job_id)):
            raise UnexpectedShape(f"job #{index} has no usable id")
    try:
        postings = parse_board_response(body)
    except RunError as exc:
        raise UnexpectedShape(str(exc)) from exc
    for posting in postings:
        posting["ats"] = "greenhouse"
    return postings


def ashby_location(job):
    """v0.5 item 3: location, then each secondaryLocations[].location, each trimmed, joined with "; ".

    Decision 2026-11-06: a part that is not a string, or is empty after
    trimming, is left out; with no parts left, the posting has no location.
    """
    parts = [job.get("location")]
    secondaries = job.get("secondaryLocations")
    if isinstance(secondaries, list):
        parts += [entry.get("location") for entry in secondaries if isinstance(entry, dict)]
    parts = [part.strip() for part in parts if isinstance(part, str) and part.strip()]
    return "; ".join(parts) if parts else None


def ashby(body):
    """v0.5 item 3. ids are UUID strings already. isRemote and workplaceType are not read."""
    postings = []
    for index, job in enumerate(_jobs(body)):
        if not isinstance(job, dict) or not isinstance(job.get("id"), str) or not job["id"]:
            raise UnexpectedShape(f"job #{index} has no string id")
        posting = {"posting_id": job["id"], "ats": "ashby"}
        if "title" in job:
            posting["title"] = job["title"]
        location = ashby_location(job)
        if location is not None:
            posting["location"] = {"name": location}
        if "descriptionPlain" in job:
            posting["content"] = job["descriptionPlain"]  # agent.rule applies §4 step 4 only
        if "jobUrl" in job:
            posting["absolute_url"] = job["jobUrl"]
        postings.append(posting)
    return postings


ADAPTERS = {"greenhouse": greenhouse, "ashby": ashby}
