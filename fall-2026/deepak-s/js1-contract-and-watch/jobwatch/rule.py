"""The written rule: CONTRACT.md The rule. Its verdict is a record anyone can recompute."""
from jobwatch.paths import pointer
from jobwatch.postings import location_name
from jobwatch.textmatch import first_match, has_tokens


def _cite(source, path, value):
    return {"source": source, "path": path, "value": value}


def apply_rule(resume, job):
    """Return {"verdict", "citations"}, with citations in the order The rule lists them."""
    targets = resume["targets"]
    excludes, roles, locations = targets["exclude_title_terms"], targets["roles"], targets["locations"]
    title = job["title"]

    e = first_match(excludes, title)
    if e is not None:
        return {"verdict": "not_relevant", "citations": [
            _cite("resume", pointer("targets", "exclude_title_terms", e), excludes[e]),
            _cite("posting", "/title", excludes[e]),
        ]}

    r = first_match(roles, title)
    if r is None:
        return {"verdict": "not_relevant", "citations": [
            _cite("resume", pointer("targets", "roles", 0), roles[0]),
            _cite("posting", "/title", title),
        ]}
    role_cites = [
        _cite("resume", pointer("targets", "roles", r), roles[r]),
        _cite("posting", "/title", roles[r]),
    ]

    loc = location_name(job)
    usable = loc is not None and has_tokens(loc)
    j = first_match(locations, loc) if usable else None
    if j is None:
        extra = [_cite("posting", "/location/name", loc)] if usable else []
        return {"verdict": "not_relevant", "citations": role_cites + extra}

    return {"verdict": "relevant", "citations": role_cites + [
        _cite("resume", pointer("targets", "locations", j), locations[j]),
        _cite("posting", "/location/name", locations[j]),
    ]}
