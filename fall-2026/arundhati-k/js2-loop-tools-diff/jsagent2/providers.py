"""Two applicant-tracking systems: URL for a board, and a parser to a common posting shape."""

import json
import re
from urllib.parse import quote

# Greenhouse: reused from JS1 (jsagent/fetch.py BOARD_SLUG).
# Ashby: board names may contain capitals and spaces (Lectern ATS.md: "Jasper AI"), so they get their own rule.
# It must start with a letter or digit (so ".", "..", " " are out) and may not contain / ? # % \ or control
# characters, so the name can only ever be one URL path segment. It is then percent-encoded.
BOARD_SLUG = {
    "greenhouse": re.compile(r"^[a-z0-9-]{1,64}$"),
    "ashby": re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]{0,63}$"),
}

URLS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
}


class BadShape(Exception):
    pass


def url_for(ats, slug):
    if ats not in URLS:
        raise ValueError(f"unknown applicant-tracking system {ats!r}; known: {sorted(URLS)}")
    rule = BOARD_SLUG[ats]
    if not isinstance(slug, str) or not rule.fullmatch(slug):
        raise ValueError(f"{ats} board name must match {rule.pattern}: {slug!r}")
    return URLS[ats].format(slug=quote(slug, safe=""))


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
