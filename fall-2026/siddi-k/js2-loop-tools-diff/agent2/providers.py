"""The three applicant-tracking systems: one URL builder and one structural parser each.
Field names for Ashby and SmartRecruiters were taken from the instructor's Lectern collector; the code is new."""
from __future__ import annotations

import json
from urllib.parse import quote, urlencode


class Malformed(Exception):
    pass


def _url_greenhouse(slug: str, offset: int) -> str:
    return f"https://boards-api.greenhouse.io/v1/boards/{quote(slug, safe='')}/jobs"


def _url_ashby(slug: str, offset: int) -> str:
    return f"https://api.ashbyhq.com/posting-api/job-board/{quote(slug, safe='')}"


def _url_smartrecruiters(slug: str, offset: int) -> str:
    return (f"https://api.smartrecruiters.com/v1/companies/{quote(slug, safe='')}/postings?"
            + urlencode({"limit": 100, "offset": offset}))


def _parse_greenhouse(d) -> tuple[list[dict], int | None]:
    if not isinstance(d, dict) or not isinstance(d.get("jobs"), list):
        raise Malformed("Greenhouse body has no 'jobs' list")
    out = [{"id": str(j["id"]), "title": (j.get("title") or "").strip(),
            "location": ((j.get("location") or {}).get("name") or "")} for j in d["jobs"]]
    return out, None


def _parse_ashby(d) -> tuple[list[dict], int | None]:
    if not isinstance(d, dict) or not isinstance(d.get("jobs"), list):
        raise Malformed("Ashby body has no 'jobs' list")
    out = [{"id": str(j["id"]), "title": (j.get("title") or "").strip(), "location": j.get("location") or ""}
           for j in d["jobs"]]
    return out, None


def _parse_smartrecruiters(d) -> tuple[list[dict], int | None]:
    if not isinstance(d, dict) or not isinstance(d.get("content"), list) or not isinstance(d.get("totalFound"), int):
        raise Malformed("SmartRecruiters body needs a 'content' list and an integer 'totalFound'")
    out = [{"id": str(j["id"]), "title": (j.get("name") or "").strip(),
            "location": ((j.get("location") or {}).get("fullLocation") or "")} for j in d["content"]]
    return out, d["totalFound"]


PROVIDERS = {
    "greenhouse": (_url_greenhouse, _parse_greenhouse),
    "ashby": (_url_ashby, _parse_ashby),
    "smartrecruiters": (_url_smartrecruiters, _parse_smartrecruiters),
}


def url(provider: str, slug: str, offset: int = 0) -> str:
    return PROVIDERS[provider][0](slug, offset)


def parse(provider: str, body: bytes) -> tuple[list[dict], int | None]:
    """(postings, total reported by the board or None). Raises Malformed if the structure is wrong."""
    try:
        d = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        raise Malformed(f"body is not UTF-8 JSON: {e}") from None
    try:
        return PROVIDERS[provider][1](d)
    except (KeyError, TypeError) as e:
        raise Malformed(f"posting missing a required field: {e}") from None
