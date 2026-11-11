"""The agent's only network step (CONTRACT.md, Refuses): GET one allow-listed URL, follow no redirects."""
from __future__ import annotations

import hashlib
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse

from .config import ALLOWED_HOSTS, BOARD_URL


class RefusedHost(Exception):
    pass


def check_allowed(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise RefusedHost(f"refusing to fetch {url!r}: host not on the allow-list {list(ALLOWED_HOSTS)}")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RefusedHost(f"refusing redirect {code} to {newurl!r}: redirects are never followed")


def _open(url: str, timeout: float) -> tuple[int, bytes]:
    opener = urllib.request.build_opener(_NoRedirect())
    req = urllib.request.Request(url, headers={"User-Agent": "js1-job-search-agent (INFO 7375 course project)"})
    with opener.open(req, timeout=timeout) as r:
        return r.status, r.read()


def fetch_board(url: str = BOARD_URL, timeout: float = 60.0) -> tuple[bytes, dict]:
    check_allowed(url)
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    status, body = _open(url, timeout)
    return body, {"url": url, "http_status": status, "fetched_at": fetched_at, "bytes": len(body),
                  "sha256": hashlib.sha256(body).hexdigest()}
