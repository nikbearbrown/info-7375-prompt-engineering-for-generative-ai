"""Turn each ATS's JSON into a common posting shape: id, title, location, content.

Greenhouse and Ashby return {"jobs": [...]}; Lever returns a top-level list.
"""

SYSTEMS = ("greenhouse", "lever", "ashby")


def _usable_posting_id(value) -> bool:
    """JS2 loop id rule: a non-boolean int, or a non-empty string (Lever/Ashby use UUID strings)."""
    if isinstance(value, bool):
        return False
    return isinstance(value, int) or (isinstance(value, str) and value != "")


class BadResponse(ValueError):
    """The response parsed as JSON but does not have the shape this ATS should return."""


def _jobs_list(data, system):
    if system == "lever":
        if not isinstance(data, list):
            raise BadResponse(f"lever: expected a top-level list, got {type(data).__name__}")
        jobs = data
    else:
        if not isinstance(data, dict) or "jobs" not in data:
            raise BadResponse(f"{system}: expected an object with a 'jobs' key")
        jobs = data["jobs"]
        if not isinstance(jobs, list):
            raise BadResponse(f"{system}: 'jobs' is {type(jobs).__name__}, not a list")
    for i, job in enumerate(jobs):
        if not isinstance(job, dict):
            raise BadResponse(f"{system}: posting {i} is {type(job).__name__}, not an object")
    return jobs


def _greenhouse(job):
    loc = job.get("location")
    return {
        "id": job.get("id"),
        "title": job.get("title"),
        "location": loc.get("name") if isinstance(loc, dict) else loc,
        "content": job.get("content"),
    }


def _lever(job):
    cats = job.get("categories")
    return {
        "id": job.get("id"),
        "title": job.get("text"),
        "location": cats.get("location") if isinstance(cats, dict) else None,
        "content": job.get("descriptionPlain", job.get("description")),
    }


def _ashby(job):
    return {
        "id": job.get("id"),
        "title": job.get("title"),
        "location": job.get("location"),
        "content": job.get("descriptionPlain", job.get("descriptionHtml")),
    }


_PARSERS = {"greenhouse": _greenhouse, "lever": _lever, "ashby": _ashby}


def parse(system, data):
    if system not in _PARSERS:
        raise ValueError(f"unknown system: {system!r}")
    return [_PARSERS[system](job) for job in _jobs_list(data, system)]


def posting_key(board_key, posting):
    """'<system>:<board>:<id>', or None when _usable_posting_id rejects the id."""
    pid = posting.get("id")
    if not _usable_posting_id(pid):
        return None
    return f"{board_key}:{pid}"
