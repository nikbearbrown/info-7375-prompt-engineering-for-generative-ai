"""Three applicant-tracking systems: listing URL and normalization to the fields the rule reads."""
import datetime as dt
import json

ATS = ("greenhouse", "ashby", "lever")
US_COUNTRIES = {"united states", "us", "usa", "united states of america"}


class ShapeError(Exception):
    pass


def url(name, slug):
    if name == "greenhouse":
        return f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    if name == "ashby":
        return f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    if name == "lever":
        return f"https://api.lever.co/v0/postings/{slug}?mode=json"
    raise ValueError(f"unknown ATS {name!r}")


def _load(raw):
    try:
        return json.loads(raw)
    except (ValueError, UnicodeDecodeError) as e:
        raise ShapeError("body is not JSON") from e


def _need(obj, kind):
    if not isinstance(obj, kind):
        raise ShapeError(f"expected {kind.__name__}, got {type(obj).__name__}")
    return obj


def parse(name, raw):
    data = _load(raw)
    out = []
    if name == "greenhouse":
        for j in _need(_need(data, dict).get("jobs"), list):
            _need(j, dict)
            offices = [o.get("name") or "" for o in j.get("offices") or []]
            out.append({"id": str(j["id"]), "title": j.get("title") or "",
                        "location_name": (j.get("location") or {}).get("name") or "",
                        "us_office": any(o == "US" or o.startswith("US-") for o in offices),
                        "published": j.get("first_published"), "url": j.get("absolute_url")})
    elif name == "ashby":
        for j in _need(_need(data, dict).get("jobs"), list):
            _need(j, dict)
            locs = [j.get("location") or ""] + [s.get("location") or "" for s in j.get("secondaryLocations") or []]
            addrs = [j.get("address")] + [s.get("address") for s in j.get("secondaryLocations") or []]
            countries = {((a or {}).get("postalAddress") or {}).get("addressCountry", "").lower() for a in addrs}
            out.append({"id": str(j["id"]), "title": j.get("title") or "",
                        "location_name": "; ".join(l for l in locs if l),
                        "us_office": bool(countries & US_COUNTRIES),
                        "published": j.get("publishedAt"), "url": j.get("jobUrl")})
    elif name == "lever":
        for j in _need(data, list):
            _need(j, dict)
            cat = j.get("categories") or {}
            locs = cat.get("allLocations") or ([cat["location"]] if cat.get("location") else [])
            created = j.get("createdAt")
            out.append({"id": str(j["id"]), "title": j.get("text") or "",
                        "location_name": "; ".join(locs),
                        "us_office": (j.get("country") or "").upper() == "US",
                        "published": dt.datetime.fromtimestamp(created / 1000, dt.timezone.utc).isoformat()
                        if isinstance(created, (int, float)) else None,
                        "url": j.get("hostedUrl")})
    else:
        raise ValueError(f"unknown ATS {name!r}")
    return out
