"""Three applicant-tracking systems, one posting shape (the Greenhouse shape the JS1 rule already reads).
Only fields present in the response are used; nothing is filled in when a field is missing."""
import json
import re

from agent.policy import Refused

URLS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{b}/jobs?content=true",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{b}",
    "lever": "https://api.lever.co/v0/postings/{b}?mode=json",
}
SLUG = re.compile(r"^[a-z0-9-]{1,64}$")
COUNTRY = {"USA": "US", "United States": "US"}


class BadShape(ValueError):
    pass


def url(system, board):
    if system not in URLS:
        raise BadShape(f"unknown applicant-tracking system '{system}'")
    if not SLUG.match(board):
        raise Refused(f"refused: board name '{board}' may only use a-z, 0-9 and - (GATE §6)")
    return URLS[system].format(b=board)


def _loc(*parts):
    return ", ".join(p for p in parts if p)


def parse(system, raw):
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise BadShape(f"{system}: response is not JSON ({e})")
    try:
        if system == "greenhouse":
            if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
                raise BadShape("greenhouse: no 'jobs' list")
            return [{"id": j["id"], "title": j.get("title", ""), "location": j.get("location") or {},
                     "absolute_url": j.get("absolute_url", ""), "content": j.get("content", "")}
                    for j in data["jobs"]]
        if system == "ashby":
            if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
                raise BadShape("ashby: no 'jobs' list")
            out = []
            for j in data["jobs"]:
                if j.get("isListed") is False:
                    continue
                pa = ((j.get("address") or {}).get("postalAddress") or {})
                country = pa.get("addressCountry")
                out.append({"id": j["id"], "title": j.get("title", ""),
                            "location": {"name": _loc(j.get("location"), pa.get("addressRegion"),
                                                      COUNTRY.get(country, country))},
                            "absolute_url": j.get("jobUrl", ""), "content": j.get("descriptionHtml", "")})
            return out
        if system == "lever":
            if not isinstance(data, list):
                raise BadShape("lever: response is not a list")
            return [{"id": j["id"], "title": j.get("text", ""),
                     "location": {"name": _loc((j.get("categories") or {}).get("location"), j.get("country"))},
                     "absolute_url": j.get("hostedUrl", ""),
                     "content": (j.get("description") or "") + " " + " ".join(
                         f"{x.get('text', '')} {x.get('content', '')}" for x in j.get("lists") or [])
                     + " " + (j.get("additional") or "")}
                    for j in data]
    except (KeyError, TypeError, AttributeError) as e:
        raise BadShape(f"{system}: a posting is missing a required field ({e})")
    raise BadShape(f"unknown applicant-tracking system '{system}'")
