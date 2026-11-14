"""One public job-list endpoint per applicant-tracking system, and a parser that turns each
response into the posting fields the JS1 rule reads. A parser never guesses a count: anything
that is not a well-formed job list raises BadResponse."""
import html
import json
import re

from jsagent import posting

ATS = ("greenhouse", "ashby", "lever")
TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,63}$")


class BadResponse(Exception):
    def __init__(self, kind, message=""):
        super().__init__(f"{kind}: {message}" if message else kind)
        self.kind = kind


def board_url(ats, token):
    if ats not in ATS:
        raise ValueError(f"unknown applicant-tracking system {ats!r}")
    if not TOKEN_RE.match(token or ""):
        raise ValueError(f"bad board token {token!r}")
    if ats == "greenhouse":
        return f"https://boards-api.greenhouse.io/v1/boards/{token.lower()}/jobs?content=true"
    if ats == "ashby":
        return f"https://api.ashbyhq.com/posting-api/job-board/{token}?includeCompensation=false"
    return f"https://api.lever.co/v0/postings/{token}?mode=json"


def _strip(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h or ""))).strip()


def _greenhouse(job, token):
    p = posting.normalize(job, token)
    p["id"] = str(p["id"])
    return p


def _ashby(job, token):
    places = [job.get("location") or ""] + [s.get("location", "") for s in job.get("secondaryLocations") or []]
    remote = job.get("isRemote") or job.get("workplaceType") == "Remote"
    return {"id": str(job["id"]), "board_token": token, "title": (job.get("title") or "").strip(),
            "departments": [d for d in (job.get("department"), job.get("team")) if d],
            "location": job.get("location") or "", "offices": [x for x in places if x] + (["Remote"] if remote else []),
            "content": job.get("descriptionPlain") or _strip(job.get("descriptionHtml")),
            "absolute_url": job.get("jobUrl"), "workplace_type": job.get("workplaceType")}


def _lever(job, token):
    c = job.get("categories") or {}
    lists = " ".join(f"{l.get('text', '')}: {_strip(l.get('content'))}" for l in job.get("lists") or [])
    remote = (job.get("workplaceType") or "").lower() == "remote"
    return {"id": str(job["id"]), "board_token": token, "title": (job.get("text") or "").strip(),
            "departments": [d for d in (c.get("department"), c.get("team")) if d],
            "location": c.get("location") or "", "offices": list(c.get("allLocations") or []) + (["Remote"] if remote else []),
            "content": " ".join(x for x in (job.get("descriptionPlain"), lists, job.get("additionalPlain")) if x),
            "absolute_url": job.get("hostedUrl"), "workplace_type": job.get("workplaceType")}


def parse(ats, token, status, body):
    """Returns (postings, info). Raises BadResponse; kind 'server-error' is the only retryable one.
    A posting missing a field (no id, a list where an object belongs) is 'bad-shape', so the board
    fails and the run still ends with one of its exits (added 2026-11-10 after the second regrade)."""
    try:
        return _parse(ats, token, status, body)
    except (KeyError, TypeError, AttributeError) as e:
        raise BadResponse("bad-shape", f"a posting is missing a field or has the wrong type: {e!r}")


def _parse(ats, token, status, body):
    if status == 404:
        raise BadResponse("not-found", "the board name does not exist on this system")
    if status is not None and status >= 500:
        raise BadResponse("server-error", f"HTTP {status}")
    if status != 200:
        raise BadResponse("http-error", f"HTTP {status}")
    try:
        data = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        raise BadResponse("bad-json")
    if ats == "greenhouse":
        if not (isinstance(data, dict) and isinstance(data.get("jobs"), list)):
            raise BadResponse("bad-shape", "no jobs list")
        meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
        return [_greenhouse(j, token) for j in data["jobs"]], {"meta_total": meta.get("total")}
    if ats == "ashby":
        if not (isinstance(data, dict) and isinstance(data.get("jobs"), list)):
            raise BadResponse("bad-shape", "no jobs list")
        return [_ashby(j, token) for j in data["jobs"]], {}
    if not isinstance(data, list):
        raise BadResponse("bad-shape", "Lever returned an object, not a list")
    return [_lever(j, token) for j in data], {}
