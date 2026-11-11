"""Turn each applicant-tracking system's public JSON into a list of postings.

Each parser returns a list of dicts with id, title, location, url, or raises BadResponse
when the body does not have the shape that system documents. Parsers never fill in a
missing field with a guess; a missing id makes the whole response bad.
"""


class BadResponse(Exception):
    pass


def board_url(ats, slug):
    if ats == "greenhouse":
        return f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    if ats == "lever":
        return f"https://api.lever.co/v0/postings/{slug}?mode=json"
    if ats == "ashby":
        return f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    raise ValueError(f"unknown ATS {ats!r}")


def _require_id(job):
    if not isinstance(job, dict) or job.get("id") in (None, ""):
        raise BadResponse("posting without an id")
    return str(job["id"])


def parse_greenhouse(body):
    if not isinstance(body, dict) or not isinstance(body.get("jobs"), list):
        raise BadResponse("greenhouse: expected an object with a 'jobs' list")
    out = []
    for job in body["jobs"]:
        out.append({
            "id": _require_id(job),
            "title": job.get("title"),
            "location": (job.get("location") or {}).get("name"),
            "url": job.get("absolute_url"),
        })
    return out


def parse_lever(body):
    if not isinstance(body, list):
        raise BadResponse("lever: expected a list of postings")
    out = []
    for job in body:
        out.append({
            "id": _require_id(job),
            "title": job.get("text"),
            "location": (job.get("categories") or {}).get("location"),
            "url": job.get("hostedUrl"),
        })
    return out


def parse_ashby(body):
    if not isinstance(body, dict) or not isinstance(body.get("jobs"), list):
        raise BadResponse("ashby: expected an object with a 'jobs' list")
    out = []
    for job in body["jobs"]:
        posting_id = _require_id(job)
        if job.get("isListed") is False:  # unlisted postings are not public openings
            continue
        out.append({
            "id": posting_id,
            "title": job.get("title"),
            "location": job.get("location"),
            "url": job.get("jobUrl"),
        })
    return out


PARSERS = {"greenhouse": parse_greenhouse, "lever": parse_lever, "ashby": parse_ashby}
