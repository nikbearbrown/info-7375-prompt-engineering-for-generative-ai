"""One adapter per applicant-tracking system: the board URL and a parser to a common shape.

Carried over from JS2 (commit 41ae85c). JS3 adds the fields FILTER.md "Expected sources" names:
department, every location, country and workplace where the system gives them, and the full
description as plain text.

Every parser returns a list of postings with string ids, or raises ParseError. It never returns
an empty list in place of a response it couldn't read. A field the system doesn't give is None
(or an empty list), never an invented value.
"""
import json
import re

from text import clean, html_to_text

TOKEN = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
FIELDS = ("id", "title", "location", "locations", "country", "workplace", "department", "text", "url")


class ParseError(Exception):
    pass


def _load(body):
    try:
        return json.loads(body)
    except (ValueError, UnicodeDecodeError) as e:
        raise ParseError(f"not JSON: {bytes(body[:40])!r}") from e


def _jobs(data, key="jobs"):
    jobs = data.get(key) if isinstance(data, dict) else None
    if not isinstance(jobs, list):
        raise ParseError(f"no {key!r} list in the response")
    return jobs


def _posting(**fields):
    p = {name: fields.get(name) for name in FIELDS}
    p["id"] = str(fields["id"])
    p["locations"] = [loc for loc in (fields.get("locations") or []) if loc]
    p["text"] = p["text"] or None  # an empty description is a missing description
    return p


def parse_greenhouse(body):
    out = []
    for j in _jobs(_load(body)):
        location = (j.get("location") or {}).get("name")
        offices = [o.get("location") or o.get("name") for o in (j.get("offices") or [])]
        departments = [d.get("name") for d in (j.get("departments") or []) if d.get("name")]
        out.append(_posting(id=j["id"], title=j.get("title"), location=location, locations=[location] + offices,
                            department=", ".join(departments) or None,
                            text=html_to_text(j.get("content"), escaped=True), url=j.get("absolute_url")))
    return out


def parse_ashby(body):
    out = []
    for j in _jobs(_load(body)):
        address = ((j.get("address") or {}).get("postalAddress") or {})
        secondary = [s.get("location") for s in (j.get("secondaryLocations") or [])]
        text = clean(j.get("descriptionPlain")) or html_to_text(j.get("descriptionHtml"))
        out.append(_posting(id=j["id"], title=j.get("title"), location=j.get("location"),
                            locations=[j.get("location")] + secondary, country=address.get("addressCountry"),
                            workplace=j.get("workplaceType") or ("Remote" if j.get("isRemote") else None),
                            department=j.get("department") or j.get("team"), text=text, url=j.get("jobUrl")))
    return out


def parse_lever(body):
    data = _load(body)
    if not isinstance(data, list):
        raise ParseError("Lever response is not a list")
    out = []
    for j in data:
        cats = j.get("categories") or {}
        sections = [clean(j.get("descriptionPlain"))]
        for item in j.get("lists") or []:
            sections += [clean(item.get("text")), html_to_text(item.get("content"))]
        sections.append(clean(j.get("additionalPlain")))
        out.append(_posting(id=j["id"], title=j.get("text"), location=cats.get("location"),
                            locations=[cats.get("location")] + list(cats.get("allLocations") or []),
                            country=j.get("country"), workplace=j.get("workplaceType"),
                            department=cats.get("department") or cats.get("team"),
                            text="\n".join(s for s in sections if s), url=j.get("hostedUrl")))
    return out


SYSTEMS = {
    "greenhouse": ("https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true", parse_greenhouse),
    "ashby": ("https://api.ashbyhq.com/posting-api/job-board/{token}", parse_ashby),
    "lever": ("https://api.lever.co/v0/postings/{token}?mode=json", parse_lever),
}


IDENTITY = {"greenhouse": "https://boards-api.greenhouse.io/v1/boards/{token}"}


def identity_url(board):
    """The board's own-name endpoint, where the system has one. Only Greenhouse does."""
    board_url(board)  # the same validation of system and token
    template = IDENTITY.get(board["system"])
    return template.format(token=board["token"]) if template else None


def parse_board_name(body):
    data = _load(body)
    name = data.get("name") if isinstance(data, dict) else None
    if not isinstance(name, str) or not name.strip():
        raise ParseError("no board name in the response")
    return name


def board_url(board):
    if board.get("system") not in SYSTEMS:
        raise ValueError(f"unknown system {board.get('system')!r}")
    if not TOKEN.match(board.get("token", "")):
        raise ValueError(f"board token {board.get('token')!r} is not a plain board name")
    return SYSTEMS[board["system"]][0].format(token=board["token"])


def parse(board, body):
    try:
        return SYSTEMS[board["system"]][1](body)
    except (KeyError, TypeError, AttributeError) as e:
        raise ParseError(f"unexpected shape: {type(e).__name__}: {e}") from e
