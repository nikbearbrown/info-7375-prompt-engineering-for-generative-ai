"""Two applicant-tracking systems: URL for a board, and a parser to a common posting shape."""

import json
import re

# Reused from JS1 (jsagent/fetch.py BOARD_SLUG).
BOARD_SLUG = re.compile(r"^[a-z0-9-]{1,64}$")

URLS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
}


class BadShape(Exception):
    pass


def url_for(ats, slug):
    if ats not in URLS:
        raise ValueError(f"unknown applicant-tracking system {ats!r}; known: {sorted(URLS)}")
    if not BOARD_SLUG.match(slug):
        raise ValueError(f"board name must match {BOARD_SLUG.pattern}: {slug!r}")
    return URLS[ats].format(slug=slug)


def parse(ats, body):
    try:
        data = json.loads(body)
    except (ValueError, UnicodeDecodeError) as e:
        raise BadShape(f"not JSON: {e}")
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise BadShape("no 'jobs' list")
    out = []
    for j in data["jobs"]:
        if not isinstance(j, dict) or "id" not in j:
            raise BadShape("a job without an id")
        if ats == "greenhouse":
            loc = (j.get("location") or {}).get("name")
            out.append({"id": j["id"], "title": j.get("title"), "location": loc, "url": j.get("absolute_url")})
        else:
            out.append({"id": j["id"], "title": j.get("title"), "location": j.get("location"), "url": j.get("jobUrl")})
    return out
