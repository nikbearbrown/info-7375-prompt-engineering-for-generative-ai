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


def _address_country(holder):
    """addressCountry from holder["address"]["postalAddress"], or None."""
    address = holder.get("address") if isinstance(holder, dict) else None
    postal = address.get("postalAddress") if isinstance(address, dict) else None
    country = postal.get("addressCountry") if isinstance(postal, dict) else None
    return country.strip() if isinstance(country, str) and country.strip() else None


def parse_ashby(body):
    """isListed false postings are skipped and counted; secondaryLocations are
    joined after the primary location with "; " (GATE.md Revision 2026-11-04).
    Each place is followed by its own address's addressCountry in parentheses
    when the response gives one (GATE.md Revision 2026-11-05), because office
    names like "San Francisco HQ" name no US state. Shape checked against
    Plaid's live board on 2026-11-04: the posting and each secondaryLocations
    item may carry {"address": {"postalAddress": {"addressCountry": ...}}}."""
    postings, unlisted = [], 0
    for i, job in enumerate(_load_jobs(body, "ashby")):
        job_id, title = _id_and_title(job, i, "ashby")
        if job.get("isListed") is False:
            unlisted += 1
            continue
        names, places = [], []
        candidates = [(job.get("location"), job)]
        secondary = job.get("secondaryLocations")
        for item in secondary if isinstance(secondary, list) else []:
            candidates.append((item.get("location") if isinstance(item, dict) else None, item))
        for name, holder in candidates:
            if isinstance(name, str) and name.strip() and name not in names:
                names.append(name)
                country = _address_country(holder)
                places.append(f"{name} ({country})" if country else name)
        postings.append({"id": job_id, "title": title, "location": "; ".join(places),
                         "url": job.get("jobUrl")})
    return postings, unlisted


PARSERS = {"greenhouse": parse_greenhouse, "ashby": parse_ashby}
