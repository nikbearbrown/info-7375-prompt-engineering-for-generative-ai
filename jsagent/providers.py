"""Provider adapters (GATE.md Scope and section 4): fixed URL templates and response-shape checks for Greenhouse and Lever.

Greenhouse returns {"jobs": [...], "meta": {"total": N}} without descriptions, so new data-titled postings need a detail request.
Lever returns a bare JSON array with descriptions included, so it never needs a detail request.
"""
import json
import re

from . import fetch

GREENHOUSE, LEVER = "greenhouse", "lever"
PROVIDERS = (GREENHOUSE, LEVER)
BOARD_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
GH_ID_RE = re.compile(r"^\d+$")


class ShapeError(Exception):
    pass


def validate(provider, board):
    if provider not in PROVIDERS:
        raise ValueError(f"unsupported provider: {provider!r}")
    if not isinstance(board, str) or not BOARD_RE.match(board):
        raise ValueError(f"bad board name: {board!r}")


def list_url(provider, board):
    validate(provider, board)
    if provider == GREENHOUSE:
        return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    return f"https://api.lever.co/v0/postings/{board}?mode=json"


def detail_url(provider, board, job_id):
    validate(provider, board)
    if provider != GREENHOUSE:
        raise ValueError("only Greenhouse needs detail requests")
    if not GH_ID_RE.match(str(job_id)):
        raise ValueError(f"bad job id: {job_id!r}")
    return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{job_id}"


def needs_detail(provider):
    return provider == GREENHOUSE


def _load(body):
    if body is None or not body.strip():
        raise ShapeError("empty body")
    try:
        return json.loads(body)
    except (ValueError, UnicodeDecodeError) as e:
        raise ShapeError(f"invalid JSON ({e})") from None


def _lever_posting(j):
    if not isinstance(j, dict) or "id" not in j:
        raise ShapeError("Lever: a posting without an id")
    cats = j.get("categories") or {}
    parts = [j.get("descriptionPlain") or ""]
    for item in j.get("lists") or []:
        parts += [item.get("text") or "", fetch.html_to_text(item.get("content"))]
    parts.append(j.get("additionalPlain") or "")
    return {"id": str(j["id"]), "title": (j.get("text") or "").strip(),
            "location": {"name": (cats.get("location") or "").strip()},
            "departments": [cats.get("team") or ""], "content": " ".join(x for x in parts if x).strip(),
            "absolute_url": j.get("hostedUrl", ""), "updated_at": str(j.get("createdAt", ""))}


def parse_list(provider, body, board):
    """Raises ShapeError unless the body is the provider's expected shape (GATE.md section 4)."""
    d = _load(body)
    if provider == GREENHOUSE:
        if not isinstance(d, dict) or not isinstance(d.get("jobs"), list):
            raise ShapeError("Greenhouse: expected an object with a 'jobs' list")
        try:
            postings = [fetch._normalize(j) for j in d["jobs"]]
        except (KeyError, TypeError, AttributeError) as e:
            raise ShapeError(f"Greenhouse: malformed posting ({e!r})") from None
    else:
        if not isinstance(d, list):
            raise ShapeError("Lever: expected a JSON array")
        postings = [_lever_posting(j) for j in d]
    for p in postings:
        p["board"], p["provider"] = board, provider
    return postings


def parse_detail(provider, body, board):
    d = _load(body)
    if not isinstance(d, dict) or "id" not in d:
        raise ShapeError("Greenhouse detail: expected an object with an id")
    p = fetch._normalize(d)
    p["board"], p["provider"] = board, provider
    return p
