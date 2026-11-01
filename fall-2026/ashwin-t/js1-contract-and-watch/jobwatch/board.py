"""The one allowed job-board request, and validation of its response (CONTRACT.md, In 1, Refuses)."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlsplit

BOARD = "klaviyo"
ALLOWED_HOST = "boards-api.greenhouse.io"
ALLOWED_URL = f"https://{ALLOWED_HOST}/v1/boards/{BOARD}/jobs?content=true"


class BoardError(RuntimeError):
    """The fetch or the response is not acceptable; state must not change."""


def check_url(url: str) -> None:
    """Refuse anything but the exact contract endpoint, and say why."""
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise BoardError(f"refused {url!r}: scheme must be https")
    if parts.hostname != ALLOWED_HOST:
        raise BoardError(f"refused {url!r}: host {parts.hostname!r} is not on the allow-list")
    if parts.port is not None or parts.username or parts.password:
        raise BoardError(f"refused {url!r}: ports and credentials are not allowed")
    if url != ALLOWED_URL:
        raise BoardError(f"refused {url!r}: only {ALLOWED_URL} is allowed")


class RefuseRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise BoardError(f"refused redirect ({code}) from {req.full_url} to {newurl}")


def fetch(url: str = ALLOWED_URL, timeout: float = 30.0) -> tuple:
    """GET the board. Returns (raw bytes, metadata). Raises BoardError on any failure."""
    check_url(url)
    opener = urllib.request.build_opener(RefuseRedirects)
    request = urllib.request.Request(url, headers={"Accept": "application/json",
                                                   "User-Agent": "info7375-js1-jobwatch"})
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read()
            meta = {"url": url, "status": response.status, "fetched_at": fetched_at,
                    "server_date": response.headers.get("Date"),
                    "content_type": response.headers.get("Content-Type")}
    except BoardError:
        raise
    except (urllib.error.URLError, OSError) as exc:
        raise BoardError(f"network error fetching {url}: {exc}") from None
    if meta["status"] != 200:
        raise BoardError(f"unexpected HTTP status {meta['status']}")
    if "json" not in (meta["content_type"] or ""):
        raise BoardError(f"unexpected content type {meta['content_type']!r}")
    return raw, meta


def parse_board(raw: bytes) -> list:
    """Validate a Greenhouse jobs response and return its postings. Never deduplicates silently."""
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BoardError(f"response is not valid JSON: {exc}") from None
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise BoardError("response has no 'jobs' list")
    seen = set()
    for i, job in enumerate(data["jobs"]):
        if not isinstance(job, dict):
            raise BoardError(f"jobs[{i}] is not an object")
        jid = job.get("id")
        if isinstance(jid, bool) or not isinstance(jid, int):
            raise BoardError(f"jobs[{i}] has a missing or non-integer id: {jid!r}")
        if jid in seen:
            raise BoardError(f"duplicate posting id {jid}")
        seen.add(jid)
        if not isinstance(job.get("title"), str) or not job["title"].strip():
            raise BoardError(f"posting {jid} has no title")
        if not isinstance(job.get("content"), str):
            raise BoardError(f"posting {jid} has no content (was ?content=true used?)")
    return data["jobs"]
