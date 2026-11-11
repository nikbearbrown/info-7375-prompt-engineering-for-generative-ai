"""Two ATS providers (Greenhouse, Ashby): URL, parse, and the repeat-rule key.

Pattern adapted from the Reallocation Engine's scripts/ats/providers (greenhouse.mjs, ashby.mjs),
but keeping each posting's id (the RE providers drop it) and refusing malformed bodies.
"""
from __future__ import annotations

import json
from urllib.parse import quote, unquote

ATS = ("greenhouse", "ashby")


class Malformed(Exception):
    pass


def board_key(ats: str, slug: str) -> str:
    """Repeat rule (GATE §3): same ATS + same slug after URL-decoding and case-folding."""
    return f"{ats.casefold()}/{unquote(slug).strip().casefold()}"


def board_url(ats: str, slug: str) -> str:
    name = quote(unquote(slug), safe="")
    if ats == "greenhouse":
        return f"https://boards-api.greenhouse.io/v1/boards/{name}/jobs"
    if ats == "ashby":
        return f"https://api.ashbyhq.com/posting-api/job-board/{name}"
    raise ValueError(f"unknown ats {ats!r}")


def parse(ats: str, body: bytes) -> list[dict]:
    """Normalize to [{id, title, location, url, updated}] or raise Malformed. Never invents a field."""
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise Malformed(f"not JSON: {e}") from e
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise Malformed("expected an object with a 'jobs' list")
    out = []
    for j in data["jobs"]:
        if not isinstance(j, dict) or j.get("id") in (None, ""):
            raise Malformed("a job without an id")
        if ats == "greenhouse":
            loc = (j.get("location") or {}).get("name", "") if isinstance(j.get("location"), dict) else ""
            out.append({"id": str(j["id"]), "title": j.get("title", ""), "location": loc,
                        "url": j.get("absolute_url", ""), "updated": j.get("updated_at")})
        else:
            locs = [j.get("location") or ""] + [s.get("location", "") for s in j.get("secondaryLocations") or [] if isinstance(s, dict)]
            loc = "; ".join(x for x in locs if x) + ("; Remote" if j.get("isRemote") else "")
            out.append({"id": str(j["id"]), "title": j.get("title", ""), "location": loc,
                        "url": j.get("jobUrl", ""), "updated": j.get("publishedAt")})
    return out
