"""Parsers for the two applicant-tracking systems in GATE.md.

Both return (postings, unlisted_skipped), where each posting is normalized to
{"id": str, "title": str, "location": str, "url": str or None}, so the state,
the rule and the trace treat Greenhouse and Ashby the same way.

A body that is not JSON, or JSON of the wrong shape, raises ParseError: per
GATE.md's Revision that board is failed, never treated as empty. A posting
without an id or a title is the wrong shape (approved 2026-11-04).
"""
import json


class ParseError(ValueError):
    pass


def _load_jobs(body, system):
    try:
        data = json.loads(body)
    except ValueError:  # includes UnicodeDecodeError
        raise ParseError(f"{system}: response is not valid JSON") from None
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise ParseError(f"{system}: expected an object with a 'jobs' list")
    return data["jobs"]


def _id_and_title(job, index, system):
    if not isinstance(job, dict):
        raise ParseError(f"{system}: jobs[{index}] is not an object")
    job_id = job.get("id")
    if isinstance(job_id, bool) or not isinstance(job_id, (int, str)) or not str(job_id).strip():
        raise ParseError(f"{system}: jobs[{index}] has no id")
    title = job.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ParseError(f"{system}: jobs[{index}] has no title")
    return str(job_id), title


def parse_greenhouse(body):
    postings = []
    for i, job in enumerate(_load_jobs(body, "greenhouse")):
        job_id, title = _id_and_title(job, i, "greenhouse")
        location = job.get("location")
        name = location.get("name") if isinstance(location, dict) else None
        postings.append({"id": job_id, "title": title,
                         "location": name if isinstance(name, str) else "",
                         "url": job.get("absolute_url")})
    return postings, 0


def parse_ashby(body):
    """isListed false postings are skipped and counted; secondaryLocations are
    joined after the primary location with "; " (GATE.md Revision). Shape of
    secondaryLocations items checked against Plaid's live board on 2026-11-04:
    objects with a "location" string (and an "address" object, not used)."""
    postings, unlisted = [], 0
    for i, job in enumerate(_load_jobs(body, "ashby")):
        job_id, title = _id_and_title(job, i, "ashby")
        if job.get("isListed") is False:
            unlisted += 1
            continue
        places = []
        primary = job.get("location")
        if isinstance(primary, str) and primary.strip():
            places.append(primary)
        secondary = job.get("secondaryLocations")
        for item in secondary if isinstance(secondary, list) else []:
            place = item.get("location") if isinstance(item, dict) else None
            if isinstance(place, str) and place.strip() and place not in places:
                places.append(place)
        postings.append({"id": job_id, "title": title, "location": "; ".join(places),
                         "url": job.get("jobUrl")})
    return postings, unlisted


PARSERS = {"greenhouse": parse_greenhouse, "ashby": parse_ashby}
