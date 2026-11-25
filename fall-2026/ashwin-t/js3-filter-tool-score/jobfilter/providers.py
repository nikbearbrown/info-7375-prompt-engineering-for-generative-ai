"""Three applicant-tracking systems: fixed URL templates and strict response parsers.

URLs are built only from these templates and a validated board name (GATE.md section 3).
Each parser returns postings in one common shape, keyed by provider/board/id so that ids
from different boards can never collide (GATE.md wrong version 10). An empty list is a
valid parse; deciding what an empty board means is the loop's job, not the parser's.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Callable


class ParseError(ValueError):
    """The response body is not a valid board listing. `kind` is malformed-json or invalid-schema."""

    def __init__(self, kind: str, message: str):
        super().__init__(message)
        self.kind = kind


@dataclass(frozen=True)
class Provider:
    name: str
    host: str
    path_template: str
    query: str
    parse: Callable


BOARD_NAME = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")


def _load(raw: bytes):
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ParseError("malformed-json", f"response is not valid UTF-8 JSON: {exc}") from None


def _nonempty_str(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _common(provider: str, board: str, pid: str, title: str, location, offices, content, url) -> dict:
    return {
        "key": f"{provider}/{board}/{pid}",
        "provider": provider,
        "board": board,
        "id": pid,
        "title": title,
        "location": {"name": location if isinstance(location, str) else None},
        "offices": [{"name": o} for o in offices if isinstance(o, str) and o.strip()],
        "content": content if isinstance(content, str) else "",
        "absolute_url": url if isinstance(url, str) else None,
    }


def _check_unique(postings: list) -> list:
    seen = set()
    for p in postings:
        if p["id"] in seen:
            raise ParseError("invalid-schema", f"duplicate posting id {p['id']}")
        seen.add(p["id"])
    return postings


def parse_greenhouse(raw: bytes, board: str) -> list:
    data = _load(raw)
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise ParseError("invalid-schema", "Greenhouse response has no 'jobs' list")
    out = []
    for i, job in enumerate(data["jobs"]):
        if not isinstance(job, dict):
            raise ParseError("invalid-schema", f"jobs[{i}] is not an object")
        jid = job.get("id")
        if isinstance(jid, bool) or not isinstance(jid, int):
            raise ParseError("invalid-schema", f"jobs[{i}] has a missing or non-integer id: {jid!r}")
        if not _nonempty_str(job.get("title")):
            raise ParseError("invalid-schema", f"posting {jid} has no title")
        if not isinstance(job.get("content"), str):
            raise ParseError("invalid-schema", f"posting {jid} has no content (was ?content=true used?)")
        offices = [o.get("name") for o in job.get("offices") or [] if isinstance(o, dict)]
        out.append(_common("greenhouse", board, str(jid), job["title"],
                           (job.get("location") or {}).get("name"), offices, job["content"],
                           job.get("absolute_url")))
    return _check_unique(out)


def parse_ashby(raw: bytes, board: str) -> list:
    data = _load(raw)
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise ParseError("invalid-schema", "Ashby response has no 'jobs' list")
    out = []
    for i, job in enumerate(data["jobs"]):
        if not isinstance(job, dict):
            raise ParseError("invalid-schema", f"jobs[{i}] is not an object")
        if not _nonempty_str(job.get("id")):
            raise ParseError("invalid-schema", f"jobs[{i}] has a missing id")
        if not _nonempty_str(job.get("title")):
            raise ParseError("invalid-schema", f"posting {job['id']} has no title")
        secondary = [s.get("location") for s in job.get("secondaryLocations") or [] if isinstance(s, dict)]
        content = job.get("descriptionPlain") if isinstance(job.get("descriptionPlain"), str) \
            else job.get("descriptionHtml")
        out.append(_common("ashby", board, job["id"], job["title"], job.get("location"),
                           secondary, content, job.get("jobUrl")))
    return _check_unique(out)


def parse_lever(raw: bytes, board: str) -> list:
    data = _load(raw)
    if not isinstance(data, list):
        raise ParseError("invalid-schema", "Lever response is not a list of postings")
    out = []
    for i, job in enumerate(data):
        if not isinstance(job, dict):
            raise ParseError("invalid-schema", f"[{i}] is not an object")
        if not _nonempty_str(job.get("id")):
            raise ParseError("invalid-schema", f"[{i}] has a missing id")
        if not _nonempty_str(job.get("text")):
            raise ParseError("invalid-schema", f"posting {job['id']} has no title ('text')")
        categories = job.get("categories") if isinstance(job.get("categories"), dict) else {}
        others = [c for c in categories.get("allLocations") or [] if c != categories.get("location")]
        pieces = [job.get("descriptionPlain")]
        pieces += [lst.get("text", "") + " " + lst.get("content", "")
                   for lst in job.get("lists") or [] if isinstance(lst, dict)]
        pieces.append(job.get("additionalPlain"))
        content = "\n".join(p for p in pieces if isinstance(p, str))
        out.append(_common("lever", board, job["id"], job["text"], categories.get("location"),
                           others, content, job.get("hostedUrl")))
    return _check_unique(out)


PROVIDERS = {
    "greenhouse": Provider("greenhouse", "boards-api.greenhouse.io", "/v1/boards/{board}/jobs",
                           "content=true", parse_greenhouse),
    "ashby": Provider("ashby", "api.ashbyhq.com", "/posting-api/job-board/{board}", "", parse_ashby),
    "lever": Provider("lever", "api.lever.co", "/v0/postings/{board}", "mode=json", parse_lever),
}


def validate_board_name(name) -> None:
    if not isinstance(name, str) or not BOARD_NAME.match(name):
        raise ValueError(f"board name {name!r} must match {BOARD_NAME.pattern}")


def endpoint(provider: str, board: str) -> str:
    """The one canonical URL for a board. Never built from free text."""
    if provider not in PROVIDERS:
        raise ValueError(f"unsupported provider {provider!r}; supported: {sorted(PROVIDERS)}")
    validate_board_name(board)
    p = PROVIDERS[provider]
    url = f"https://{p.host}{p.path_template.format(board=board)}"
    return f"{url}?{p.query}" if p.query else url


def parse(provider: str, board: str, raw: bytes) -> list:
    return PROVIDERS[provider].parse(raw, board)
