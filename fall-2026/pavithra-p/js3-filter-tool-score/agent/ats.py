"""The three applicant-tracking systems: where each board lives, and how its answer becomes the jobs the rule reads.

Each job comes out in the shape the JS1 rule already reads: id, title, location.name, content (HTML or text), url.
"""
import html
import json

SYSTEMS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true",
    "lever": "https://api.lever.co/v0/postings/{board}?mode=json",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{board}",
}


class BadData(Exception):
    """The board answered, but not with a job list of the expected shape. Not retried (GATE.md)."""


def board_url(system, board):
    if system not in SYSTEMS:
        raise BadData(f"unknown system {system!r}")
    return SYSTEMS[system].format(board=board)


def _job(native_id, title, location, content, url):
    if native_id in (None, "") or not isinstance(title, str):
        raise BadData("a job without an id or a title")
    # Greenhouse sends some titles HTML-escaped ("Strategy &amp; Operations"); the report shows them as written.
    return {"id": str(native_id), "title": html.unescape(title), "location": {"name": location}, "content": content or "",
            "url": url or ""}


def _greenhouse(data):
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise BadData("expected an object with a 'jobs' list")
    return [_job(j.get("id"), j.get("title"), (j.get("location") or {}).get("name", ""),
                 html.unescape(j.get("content") or ""), j.get("absolute_url")) for j in data["jobs"]]


def _lever(data):
    if not isinstance(data, list):
        raise BadData("expected a list of postings")
    jobs = []
    for j in data:
        categories = j.get("categories") or {}
        places = categories.get("allLocations") or [categories.get("location", "")]
        location = "; ".join(p for p in places if p) + (f" ({j['country']})" if j.get("country") else "")
        lists = " ".join(f"{item.get('text', '')} {item.get('content', '')}" for item in j.get("lists") or [])
        content = " ".join(part for part in (j.get("description"), lists, j.get("additional")) if part)
        jobs.append(_job(j.get("id"), j.get("text"), location, content, j.get("hostedUrl")))
    return jobs


def _ashby(data):
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise BadData("expected an object with a 'jobs' list")
    jobs = []
    for j in data["jobs"]:
        if j.get("isListed") is False:
            continue
        places = [j.get("location", "")] + [s.get("location", "") for s in j.get("secondaryLocations") or []]
        country = ((j.get("address") or {}).get("postalAddress") or {}).get("addressCountry", "")
        location = "; ".join(p for p in places if p) + (f" ({country})" if country else "")
        jobs.append(_job(j.get("id"), j.get("title"), location, j.get("descriptionHtml") or j.get("descriptionPlain"), j.get("jobUrl")))
    return jobs


PARSERS = {"greenhouse": _greenhouse, "lever": _lever, "ashby": _ashby}


def parse(system, body):
    """The jobs in one saved response. Raises BadData instead of guessing."""
    try:
        data = json.loads(body)
    except (ValueError, UnicodeDecodeError) as e:
        raise BadData(f"not JSON: {e}") from e
    return PARSERS[system](data)
