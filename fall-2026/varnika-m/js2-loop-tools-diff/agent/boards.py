"""The three applicant-tracking systems: each board's URL, its response shape, and its posting fields.

The endpoints and field names follow the Reallocation Engine's providers
(scripts/ats/providers/{greenhouse,lever,ashby}.mjs, read only) and the responses
the boards returned on 2026-11-10. normalize() reshapes every posting into the
Greenhouse shape JS1's rule reads (title, location.name, content), so the rule is unchanged.
"""

import html
import json

URLS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/%s/jobs?content=true",
    "lever": "https://api.lever.co/v0/postings/%s?mode=json",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/%s",
}


class BadShape(ValueError):
    pass


def board_url(system, board):
    if system not in URLS:
        raise ValueError("unknown applicant-tracking system %r (known: %s)" % (system, ", ".join(sorted(URLS))))
    return URLS[system] % board


def parse_postings(system, body):
    """The list of postings, or BadShape. An empty list is returned as it is; the loop decides about it."""
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise BadShape("the body is not JSON")
    if system in ("greenhouse", "ashby"):
        if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
            raise BadShape("no `jobs` list in the response")
        jobs = data["jobs"]
    elif system == "lever":
        if not isinstance(data, list):
            raise BadShape("the response is not a list of postings")
        jobs = data
    else:
        raise ValueError("unknown applicant-tracking system %r" % system)
    for job in jobs:
        if not isinstance(job, dict) or job.get("id") in (None, ""):
            raise BadShape("a posting without an id")
    return jobs


def normalize(system, job, company):
    """One posting in the shape JS1's rule reads. `content` is HTML escaped once, as Greenhouse sends it."""
    if system == "greenhouse":
        return {"id": str(job["id"]), "title": job.get("title"),
                "location": {"name": (job.get("location") or {}).get("name")},
                "content": job.get("content"), "absolute_url": job.get("absolute_url"),
                "company_name": job.get("company_name") or company, "first_published": job.get("first_published")}
    if system == "lever":
        categories = job.get("categories") or {}
        locations = categories.get("allLocations") or [categories.get("location")]
        # Lever keeps requirements in `lists`, outside the description.
        parts = [job.get("description") or ""]
        for item in job.get("lists") or []:
            parts.append("<h3>%s</h3><ul>%s</ul>" % (html.escape(item.get("text") or ""), item.get("content") or ""))
        parts.append(job.get("additional") or "")
        return {"id": str(job["id"]), "title": job.get("text"),
                "location": {"name": " | ".join(l for l in locations if l)},
                "content": html.escape("\n".join(parts)), "absolute_url": job.get("hostedUrl"),
                "company_name": company, "first_published": job.get("createdAt")}
    if system == "ashby":
        locations = [job.get("location")] + [s.get("location") for s in job.get("secondaryLocations") or []]
        return {"id": str(job["id"]), "title": job.get("title"),
                "location": {"name": " | ".join(l for l in locations if l)},
                "content": html.escape(job.get("descriptionHtml") or ""), "absolute_url": job.get("jobUrl"),
                "company_name": company, "first_published": job.get("publishedAt")}
    raise ValueError("unknown applicant-tracking system %r" % system)
