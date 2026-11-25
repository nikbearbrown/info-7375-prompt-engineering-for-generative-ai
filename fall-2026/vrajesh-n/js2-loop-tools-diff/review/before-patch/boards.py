"""Board list, URLs, and one parser per ATS. Each posting is normalized to the field names JS1's rule reads."""
import html
import json
import re

URLS = {
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{name}",
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{name}/jobs?content=true",
    "lever": "https://api.lever.co/v0/postings/{name}?mode=json",
}


class ShapeError(ValueError):
    """The response is not JSON, or not the shape this platform sends. Never treated as an empty board."""


def load(text):
    boards = json.loads(text)
    for b in boards:
        if b["platform"] not in URLS:
            raise ValueError(f"unknown platform {b['platform']!r} for {b['key']}")
        if b["key"] != f"{b['platform']}:{b['name']}":
            raise ValueError(f"key {b['key']!r} must be platform:name")
    return boards


def url(board):
    return URLS[board["platform"]].format(name=board["name"])


def raw_name(board):
    return f"{board['platform']}_{board['name']}.json"


def plain(markup):
    """Greenhouse content is HTML escaped once more; unescape twice, drop tags, squeeze spaces."""
    text = html.unescape(html.unescape(markup or ""))
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()


def parse(platform, body):
    try:
        data = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ShapeError(f"not JSON: {e}") from e
    if platform in ("ashby", "greenhouse"):
        if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
            raise ShapeError(f"{platform} response has no 'jobs' list")
        items = data["jobs"]
    elif platform == "lever":
        if not isinstance(data, list):
            raise ShapeError("lever response is not a list")
        items = data
    else:
        raise ShapeError(f"unknown platform {platform!r}")
    return [normalize(platform, j) for j in items]


def normalize(platform, j):
    if platform == "ashby":
        return {"id": str(j["id"]), "title": j.get("title", ""), "location": j.get("location"),
                "address": j.get("address"), "descriptionPlain": j.get("descriptionPlain", ""),
                "url": j.get("jobUrl")}
    if platform == "greenhouse":
        return {"id": str(j["id"]), "title": j.get("title", ""),
                "location": (j.get("location") or {}).get("name"),
                "descriptionPlain": plain(j.get("content")), "url": j.get("absolute_url")}
    # lever
    lists = " ".join(f"{li.get('text', '')} {plain(li.get('content'))}" for li in j.get("lists") or [])
    country = j.get("country")
    return {"id": str(j["id"]), "title": j.get("text", ""),
            "location": (j.get("categories") or {}).get("location"),
            "address": {"postalAddress": {"addressCountry": country}} if country else None,
            "descriptionPlain": " ".join(x for x in (j.get("descriptionPlain", ""), lists,
                                                    j.get("additionalPlain", "")) if x).strip(),
            "url": j.get("hostedUrl")}
