"""Three applicant-tracking systems: board URL + parser into one normalized posting shape.

Normalized posting (the shape JS1's rule.judge() reads):
  {"id": str, "title": str, "location": {"name": str}, "offices": [{"location": str}],
   "content": str, "absolute_url": str}

Mapping from structured fields is deterministic and documented here so it can be recomputed:
  Ashby : location.name = location + secondaryLocations[].location, plus "Remote (<addressCountry>)"
          when isRemote; offices = [addressCountry]; content = descriptionPlain. Unlisted jobs dropped.
  Lever : location.name = categories.allLocations (or .location), plus "Remote (<country>)" when
          workplaceType == remote; offices = ["United States"] when country == "US";
          content = descriptionPlain + lists[].content + additionalPlain.
  Greenhouse: unchanged from JS1 (location.name, offices[].location, content).
"""
import json
import re
from urllib.parse import quote

SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]{0,63}$")


class BadResponse(Exception):
    """HTTP 200 whose body is not a posting list this ATS would send."""


class BadSlug(Exception):
    pass


def _check_slug(slug):
    if not isinstance(slug, str) or not SLUG.match(slug):
        raise BadSlug(f"board name {slug!r} is not a plain board slug")
    return slug


def board_url(ats, slug):
    _check_slug(slug)
    s = quote(slug.lower() if ats != "ashby" else slug, safe="")
    if ats == "greenhouse":
        return f"https://boards-api.greenhouse.io/v1/boards/{s}/jobs?content=true"
    if ats == "ashby":
        return f"https://api.ashbyhq.com/posting-api/job-board/{s}"
    if ats == "lever":
        return f"https://api.lever.co/v0/postings/{s}?mode=json"
    raise BadSlug(f"unknown ATS {ats!r}; known: greenhouse, ashby, lever")


def board_key(ats, slug):
    """Identity of a board for the repeat rule: ATS + case-folded slug."""
    return f"{(ats or '').lower()}:{(slug or '').strip().lower()}"


def _loads(body):
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise BadResponse(f"body is not JSON ({e.__class__.__name__})")


def _greenhouse(data):
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise BadResponse("greenhouse: no 'jobs' list")
    out = []
    for j in data["jobs"]:
        out.append({"id": str(j["id"]), "title": j.get("title") or "",
                    "location": {"name": (j.get("location") or {}).get("name") or ""},
                    "offices": [{"location": (o or {}).get("location") or ""} for o in j.get("offices") or []],
                    "content": j.get("content") or "", "absolute_url": j.get("absolute_url") or ""})
    return out


def _ashby(data):
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise BadResponse("ashby: no 'jobs' list")
    out = []
    for j in data["jobs"]:
        if j.get("isListed") is False:
            continue
        country = ((j.get("address") or {}).get("postalAddress") or {}).get("addressCountry") or ""
        names = [j.get("location") or ""] + [(s or {}).get("location") or "" for s in j.get("secondaryLocations") or []]
        if j.get("isRemote"):
            names.append(f"Remote ({country})" if country else "Remote")
        out.append({"id": str(j["id"]), "title": j.get("title") or "",
                    "location": {"name": "; ".join(n for n in names if n)},
                    "offices": [{"location": country}] if country else [],
                    "content": j.get("descriptionPlain") or j.get("descriptionHtml") or "",
                    "absolute_url": j.get("jobUrl") or ""})
    return out


def _lever(data):
    if not isinstance(data, list):
        raise BadResponse("lever: body is not a list of postings")
    out = []
    for j in data:
        cat = j.get("categories") or {}
        names = list(cat.get("allLocations") or ([cat["location"]] if cat.get("location") else []))
        country = j.get("country") or ""
        if (j.get("workplaceType") or "").lower() == "remote":
            names.append(f"Remote ({'United States' if country == 'US' else country})")
        parts = [j.get("descriptionPlain") or ""]
        parts += [f"{(l or {}).get('text', '')}: {(l or {}).get('content', '')}" for l in j.get("lists") or []]
        parts.append(j.get("additionalPlain") or "")
        out.append({"id": str(j["id"]), "title": j.get("text") or "",
                    "location": {"name": "; ".join(n for n in names if n)},
                    "offices": [{"location": "United States"}] if country == "US" else [],
                    "content": "\n".join(parts), "absolute_url": j.get("hostedUrl") or ""})
    return out


PARSERS = {"greenhouse": _greenhouse, "ashby": _ashby, "lever": _lever}


def parse(ats, body):
    """bytes -> list of normalized postings. Raises BadResponse; never returns None."""
    data = _loads(body)
    try:
        return PARSERS[ats](data)
    except (KeyError, TypeError, AttributeError) as e:
        raise BadResponse(f"{ats}: posting missing a required field ({e!r})")
