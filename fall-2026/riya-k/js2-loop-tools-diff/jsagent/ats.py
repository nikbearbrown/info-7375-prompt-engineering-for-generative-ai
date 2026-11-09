"""One adapter per applicant-tracking system: the public board URL, and a parser into one common posting shape.

Common shape (what jsagent.rules.judge already reads, from JS1):
    {"id": str, "title": str, "content": str (HTML or text), "location": {"name": str}, "absolute_url": str}

A parser raises ParseError on a body with the wrong shape. It never fills in a missing value.
"""

import json
import urllib.parse


class ParseError(ValueError):
    pass


def _q(board):
    return urllib.parse.quote(board, safe="")


def _load(raw, top_key):
    try:
        obj = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as e:
        raise ParseError(f"body is not JSON: {e}") from None
    if not isinstance(obj, dict) or not isinstance(obj.get(top_key), list):
        raise ParseError(f"body has no '{top_key}' list (keys: {sorted(obj)[:6] if isinstance(obj, dict) else type(obj).__name__})")
    return obj, obj[top_key]


def _need(item, *keys):
    for k in keys:
        if item.get(k) in (None, ""):
            raise ParseError(f"posting missing '{k}': {str(item)[:120]}")


def greenhouse_url(board):
    return f"https://boards-api.greenhouse.io/v1/boards/{_q(board)}/jobs?content=true"


def greenhouse_parse(raw, board=""):
    _, jobs = _load(raw, "jobs")
    out = []
    for j in jobs:
        _need(j, "id", "title")
        out.append({"id": str(j["id"]), "title": j["title"], "content": j.get("content") or "",
                    "location": {"name": (j.get("location") or {}).get("name") or ""},
                    "absolute_url": j.get("absolute_url") or ""})
    return out


def ashby_url(board):
    return f"https://api.ashbyhq.com/posting-api/job-board/{_q(board)}"


def ashby_parse(raw, board=""):
    _, jobs = _load(raw, "jobs")
    out = []
    for j in jobs:
        _need(j, "id", "title")
        places = [j.get("location") or ""] + [s.get("location") or "" for s in j.get("secondaryLocations") or []]
        if j.get("isRemote") and not any("remote" in p.lower() for p in places):
            places.append("Remote")
        out.append({"id": str(j["id"]), "title": j["title"],
                    "content": j.get("descriptionHtml") or j.get("descriptionPlain") or "",
                    "location": {"name": "; ".join(p for p in places if p)},
                    "absolute_url": j.get("jobUrl") or ""})
    return out


def smartrecruiters_url(board):
    return f"https://api.smartrecruiters.com/v1/companies/{_q(board)}/postings"


def smartrecruiters_parse(raw, board=""):
    _, jobs = _load(raw, "content")
    out = []
    for j in jobs:
        _need(j, "id", "name")
        loc = j.get("location") or {}
        parts = [loc.get("city"), loc.get("region"), (loc.get("country") or "").upper()]
        name = ", ".join(p for p in parts if p) + ("; Remote" if loc.get("remote") else "")
        out.append({"id": str(j["id"]), "title": j["name"], "content": "",  # list endpoint has no description
                    "location": {"name": name},
                    "absolute_url": f"https://jobs.smartrecruiters.com/{_q(board)}/{j['id']}"})
    return out


SYSTEMS = {
    "greenhouse": (greenhouse_url, greenhouse_parse),
    "ashby": (ashby_url, ashby_parse),
    "smartrecruiters": (smartrecruiters_url, smartrecruiters_parse),
}
