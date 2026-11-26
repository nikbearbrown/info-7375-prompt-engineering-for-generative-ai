"""Provider-specific parsing. Each provider has its own shape; neither parser accepts the other's.

An empty job list is a failure, not "no new jobs" (GATE.md, Failed-board policy).
Postings are normalized to {id, title, location: {name}, content, url} so CONTRACT.md's rule applies.
"""
import json


class BoardInvalid(Exception):
    """The response cannot be trusted as an observation of the board."""


def _load(raw):
    try:
        return json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise BoardInvalid(f"response is not JSON: {exc.__class__.__name__}") from None


def _no_duplicates(postings):
    seen = set()
    for p in postings:
        if p["id"] in seen:
            raise BoardInvalid(f"duplicate posting id {p['id']} in one response")
        seen.add(p["id"])
    return postings


EMPTY = "empty job list: zero postings is not evidence that there are no new jobs"


def parse_greenhouse(raw):
    data = _load(raw)
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise BoardInvalid("not a Greenhouse board: expected an object with a 'jobs' array")
    if not data["jobs"]:
        raise BoardInvalid(EMPTY)
    postings = []
    for i, job in enumerate(data["jobs"]):
        location = job.get("location") if isinstance(job, dict) else None
        if not (isinstance(job, dict)
                and isinstance(job.get("id"), int) and not isinstance(job.get("id"), bool)
                and isinstance(job.get("title"), str)
                and isinstance(location, dict) and isinstance(location.get("name"), str)
                and isinstance(job.get("content"), str)):
            raise BoardInvalid(f"jobs[{i}] is missing id, title, location.name, or content")
        postings.append({"id": str(job["id"]), "title": job["title"], "location": {"name": location["name"]},
                         "content": job["content"], "url": job.get("absolute_url")})
    return _no_duplicates(postings)


def parse_lever(raw):
    data = _load(raw)
    if not isinstance(data, list):
        raise BoardInvalid("not a Lever postings list: expected a top-level JSON array")
    if not data:
        raise BoardInvalid(EMPTY)
    postings = []
    for i, item in enumerate(data):
        categories = item.get("categories") if isinstance(item, dict) else None
        if not (isinstance(item, dict)
                and isinstance(item.get("id"), str) and item["id"]
                and isinstance(item.get("text"), str)
                and isinstance(categories, dict) and isinstance(categories.get("location"), str)
                and isinstance(item.get("description"), str)):
            raise BoardInvalid(f"postings[{i}] is missing id, text, categories.location, or description")
        lists = item.get("lists") if isinstance(item.get("lists"), list) else []
        content = " ".join([item["description"]]
                           + [entry.get("content", "") for entry in lists if isinstance(entry, dict)]
                           + [item.get("additional") or ""])
        location = categories["location"]
        workplace = item.get("workplaceType")
        if isinstance(workplace, str) and workplace.strip().lower() == "remote":
            # Lever states "remote" in workplaceType, not in the location. CONTRACT.md's location condition
            # reads only location.name, so the arrangement is added there, labeled with the field it came from.
            location = f"{location} (Lever workplaceType: remote)"
        postings.append({"id": item["id"], "title": item["text"], "location": {"name": location},
                         "content": content, "url": item.get("hostedUrl"),
                         "workplace_type": item.get("workplaceType")})
    return _no_duplicates(postings)


PARSERS = {"greenhouse": parse_greenhouse, "lever": parse_lever}
