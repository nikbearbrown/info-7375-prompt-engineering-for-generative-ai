"""Parse Greenhouse and Ashby job-board responses into one posting shape.

Each parser takes the raw response bytes and returns a list of
    {"id": str, "title": str, "location": str, "content": str, "url": str}
in response order. Duplicate ids are kept here; the loop counts them once.

Ids are normalised to strings: Greenhouse ids are integers, Ashby ids are
UUID strings, and one state file format has to hold both.

A body that is not valid JSON, has no "jobs" list, or has a posting without
a usable id raises MalformedResponse (reason malformed_response).
"""

import json

MALFORMED_RESPONSE = "malformed_response"


class MalformedResponse(Exception):
    """The server answered 200, but the answer is not a usable job list."""

    code = MALFORMED_RESPONSE

    def __init__(self, detail):
        self.detail = detail
        super().__init__(f"{MALFORMED_RESPONSE}: {detail}")


def _load_jobs(body):
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MalformedResponse(f"not valid JSON ({exc.__class__.__name__})") \
            from None
    if not isinstance(data, dict):
        raise MalformedResponse("top-level JSON is not an object")
    if "jobs" not in data:
        raise MalformedResponse("missing 'jobs' field")
    jobs = data["jobs"]
    if not isinstance(jobs, list):
        raise MalformedResponse("'jobs' is not a list")
    for index, job in enumerate(jobs):
        if not isinstance(job, dict):
            raise MalformedResponse(f"jobs[{index}] is not an object")
    return jobs


def _posting_id(job, index):
    pid = job.get("id")
    if isinstance(pid, bool) or not isinstance(pid, (int, str)):
        raise MalformedResponse(f"jobs[{index}] has no usable id: {pid!r}")
    pid = str(pid).strip()
    if not pid:
        raise MalformedResponse(f"jobs[{index}] has an empty id")
    return pid


def _text(value):
    return value if isinstance(value, str) else ""


def parse_greenhouse(body):
    """Parse a Greenhouse /v1/boards/<board>/jobs response."""
    postings = []
    for index, job in enumerate(_load_jobs(body)):
        location = job.get("location")
        postings.append({
            "id": _posting_id(job, index),
            "title": _text(job.get("title")),
            "location": _text(location.get("name"))
            if isinstance(location, dict) else _text(location),
            "content": _text(job.get("content")),
            "url": _text(job.get("absolute_url")),
        })
    return postings


def parse_ashby(body):
    """Parse an Ashby /posting-api/job-board/<board> response."""
    postings = []
    for index, job in enumerate(_load_jobs(body)):
        postings.append({
            "id": _posting_id(job, index),
            "title": _text(job.get("title")),
            "location": _text(job.get("location")),
            "content": _text(job.get("descriptionHtml"))
            or _text(job.get("descriptionPlain")),
            "url": _text(job.get("jobUrl")),
        })
    return postings


PARSERS = {"greenhouse": parse_greenhouse, "ashby": parse_ashby}
