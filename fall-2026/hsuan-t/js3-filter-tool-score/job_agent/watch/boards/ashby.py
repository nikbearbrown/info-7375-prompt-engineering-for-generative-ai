"""Ashby public job-board API adapter: the second applicant-tracking system the brief requires (JS2 R14, D2).

Everything Ashby-specific stays in this file: the URL, string (UUID) job ids, a plain-string
location plus "secondaryLocations", and the JD in "descriptionHtml". It maps them onto the same
Posting fields the Greenhouse adapter fills, so the judges read both systems the same way.
"""

import json

from ...common.errors import WatchError
from ...common.posting import Posting
from ._places import join_places

ATS = "ashby"
ID_TYPE = str  # Ashby ids are UUID strings, e.g. "8fb1615c-34bf-47c4-a1d1-b7b2f836bbd3"


def board_url(board: str) -> str:
    # The plain endpoint already includes descriptionHtml (checked 2026-11-07 on openai), which
    # checks 3-6 need; no query flag is required, unlike Greenhouse's ?content=true.
    return f"https://api.ashbyhq.com/posting-api/job-board/{board}"


def parse(body: bytes) -> list[Posting]:
    """Same rule as Greenhouse: a response that isn't the Ashby shape is a failed fetch, never "0 jobs"."""
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        raise WatchError(f"board response is not JSON: {e}") from e
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise WatchError("board response has no 'jobs' list")
    postings = []
    for job in data["jobs"]:
        if not isinstance(job, dict) or not isinstance(job.get("id"), str) or not job["id"]:
            raise WatchError("board response has a job without a string 'id'")
        postings.append(Posting(
            id=job["id"],
            title=(job.get("title") or "").strip(),
            location=_location(job),
            content=job.get("descriptionHtml") or "",
        ))
    return postings


def _location(job: dict) -> str:
    """Primary location plus every secondary one, each with its country, joined, because rule
    check 2 looks for a US place anywhere in the text: a London-first posting that is also open in
    San Francisco must not be cut just because Ashby lists London first (155 of 816 OpenAI postings
    had secondaries on 11/07). The country matters because Ashby's location is a bare city
    ("San Francisco"): without it 144 OpenAI postings were cut at check 2 on 11/08 (JS2 D7)."""
    names = [job.get("location") or "", _country(job)]
    for extra in job.get("secondaryLocations") or []:
        if isinstance(extra, dict):
            names += [extra.get("location") or "", _country(extra)]
    return join_places(names)


def _country(entry: dict) -> str:
    """address.postalAddress.addressCountry, e.g. "United States"; empty when Ashby leaves it out."""
    address = entry.get("address") if isinstance(entry.get("address"), dict) else {}
    postal = address.get("postalAddress") if isinstance(address.get("postalAddress"), dict) else {}
    return postal.get("addressCountry") or ""
