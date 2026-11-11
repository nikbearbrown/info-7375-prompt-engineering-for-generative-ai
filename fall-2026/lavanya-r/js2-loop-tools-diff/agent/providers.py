"""Three applicant-tracking systems: how to build a board's URL and how to
read its response. Endpoints taken from Lectern's sources.json (instructor's
collector) and checked live on 2026-11-09.

parse() returns a list of postings, each {"id", "title", "location", "url"},
or raises BadBody. It never returns a made-up value for a field it can't read.
"""

import json
import re
import urllib.parse

BOARD_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,63}$")


class BadBody(ValueError):
    """HTTP 200, but the body is not the shape this ATS returns."""


def _check_board(board):
    if not BOARD_NAME.match(board):
        raise ValueError(f"bad board name {board!r}")
    return urllib.parse.quote(board)


def _load(raw):
    if not raw or not raw.strip():
        raise BadBody("empty body")
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise BadBody(f"not JSON: {e}") from None


def _need(obj, key, where):
    if not isinstance(obj, dict) or key not in obj:
        raise BadBody(f"{where}: missing {key!r}")
    return obj[key]


# ---------------- Greenhouse ----------------

def greenhouse_url(board):
    return (f"https://boards-api.greenhouse.io/v1/boards/"
            f"{_check_board(board)}/jobs")


def greenhouse_parse(raw):
    data = _load(raw)
    jobs = _need(data, "jobs", "greenhouse")
    if not isinstance(jobs, list):
        raise BadBody("greenhouse: 'jobs' is not a list")
    out = []
    for j in jobs:
        loc = _need(j, "location", "greenhouse job")
        out.append({"id": str(_need(j, "id", "greenhouse job")),
                    "title": _need(j, "title", "greenhouse job"),
                    "location": loc.get("name") if isinstance(loc, dict)
                    else None,
                    "url": j.get("absolute_url")})
    return out


# ---------------- Lever ----------------

def lever_url(board):
    return f"https://api.lever.co/v0/postings/{_check_board(board)}?mode=json"


def lever_parse(raw):
    data = _load(raw)
    if not isinstance(data, list):
        # Lever answers a missing board with {"ok": false, ...}
        raise BadBody("lever: body is not a list of postings")
    out = []
    for j in data:
        cats = j.get("categories") if isinstance(j, dict) else None
        out.append({"id": str(_need(j, "id", "lever posting")),
                    "title": _need(j, "text", "lever posting"),
                    "location": cats.get("location") if isinstance(cats, dict)
                    else None,
                    "url": j.get("hostedUrl")})
    return out


# ---------------- Ashby ----------------

def ashby_url(board):
    return (f"https://api.ashbyhq.com/posting-api/job-board/"
            f"{_check_board(board)}")


def ashby_parse(raw):
    data = _load(raw)
    jobs = _need(data, "jobs", "ashby")
    if not isinstance(jobs, list):
        raise BadBody("ashby: 'jobs' is not a list")
    return [{"id": str(_need(j, "id", "ashby job")),
             "title": _need(j, "title", "ashby job"),
             "location": j.get("location"),
             "url": j.get("jobUrl")} for j in jobs]


PROVIDERS = {
    "greenhouse": (greenhouse_url, greenhouse_parse),
    "lever": (lever_url, lever_parse),
    "ashby": (ashby_url, ashby_parse),
}


def url_for(ats, board):
    if ats not in PROVIDERS:
        raise ValueError(f"unknown ATS {ats!r}")
    return PROVIDERS[ats][0](board)


def parse(ats, raw):
    return PROVIDERS[ats][1](raw)
