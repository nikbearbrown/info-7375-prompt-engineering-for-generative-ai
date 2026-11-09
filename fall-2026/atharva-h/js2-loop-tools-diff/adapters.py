"""One adapter per applicant-tracking system: the board URL and a parser to a common shape.

Every parser returns a list of {"id", "title", "location", "url"} with string ids, or
raises ParseError. It never returns an empty list in place of a response it couldn't read.
"""
import json
import re

TOKEN = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


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


def parse_greenhouse(body):
    return [{"id": str(j["id"]), "title": j.get("title"), "location": (j.get("location") or {}).get("name"),
             "url": j.get("absolute_url")} for j in _jobs(_load(body))]


def parse_ashby(body):
    return [{"id": str(j["id"]), "title": j.get("title"), "location": j.get("location"), "url": j.get("jobUrl")}
            for j in _jobs(_load(body))]


def parse_lever(body):
    data = _load(body)
    if not isinstance(data, list):
        raise ParseError("Lever response is not a list")
    return [{"id": str(j["id"]), "title": j.get("text"), "location": (j.get("categories") or {}).get("location"),
             "url": j.get("hostedUrl")} for j in data]


SYSTEMS = {
    "greenhouse": ("https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true", parse_greenhouse),
    "ashby": ("https://api.ashbyhq.com/posting-api/job-board/{token}", parse_ashby),
    "lever": ("https://api.lever.co/v0/postings/{token}?mode=json", parse_lever),
}


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
