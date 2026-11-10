"""Job-Search Agent 2: the two applicant-tracking systems (Greenhouse and Ashby).

Each provider builds one listing URL per board and checks the response's structure. A
well-formed empty list (`{"jobs": []}`) is a valid observation. Anything else that does not
match the structure raises ResponseError and is never treated as an empty board (GATE.md
section 4).

The Ashby URL and field names follow the instructor's Lectern collector
(fall-2026/nik-bear-brown/lectern/collect.py). Every posting keeps the source's record,
untouched, under `original`.
"""
import json
import re
from urllib.parse import quote

GREENHOUSE, ASHBY = "greenhouse", "ashby"
SLUG = {GREENHOUSE: re.compile(r"[a-z0-9][a-z0-9-]*"), ASHBY: re.compile(r"[A-Za-z0-9][A-Za-z0-9 ._-]*")}
ID_TYPE = {GREENHOUSE: int, ASHBY: str}            # Greenhouse ids are numbers, Ashby ids are strings


class ResponseError(Exception):
    """The response is not a well-formed job list: the board failed; nothing is guessed."""


class ConfigError(Exception):
    """A board in the run configuration is not one this agent can watch."""


def board_url(ats, slug):
    if ats not in SLUG:
        raise ConfigError(f"unknown applicant-tracking system {ats!r}; known: {sorted(SLUG)}")
    if not isinstance(slug, str) or not SLUG[ats].fullmatch(slug):
        raise ConfigError(f"board name {slug!r} is not a valid {ats} board name")
    if ats == GREENHOUSE:
        return f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    return f"https://api.ashbyhq.com/posting-api/job-board/{quote(slug)}?includeCompensation=true"


def parse(ats, raw):
    """Postings from one raw response, or ResponseError. Never returns a guess."""
    try:
        payload = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as e:
        raise ResponseError(f"not JSON: {e}") from e
    jobs = payload.get("jobs") if isinstance(payload, dict) else None
    if not isinstance(jobs, list):
        raise ResponseError("no 'jobs' list in the response")
    out = []
    for j in jobs:
        if not isinstance(j, dict) or type(j.get("id")) is not ID_TYPE[ats] or j.get("id") in ("", None):
            raise ResponseError(f"a posting without a valid {ID_TYPE[ats].__name__} id: {str(j)[:80]}")
        if ats == GREENHOUSE:
            out.append({"id": j["id"], "title": (j.get("title") or "").strip(),
                        "location": ((j.get("location") or {}).get("name") or "").strip(),
                        "url": j.get("absolute_url"), "content": j.get("content") or "", "original": j})
        else:
            locs = [j.get("location") or ""] + [(x or {}).get("location") or "" for x in (j.get("secondaryLocations") or [])]
            out.append({"id": j["id"], "title": (j.get("title") or "").strip(),
                        "location": " · ".join(x for x in locs if x),
                        "url": j.get("jobUrl"), "content": j.get("descriptionHtml") or j.get("descriptionPlain") or "",
                        "original": j})
    return out
