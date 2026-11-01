"""Fetch one Greenhouse board and save the raw response byte-for-byte."""

import re
import urllib.request
from pathlib import Path

from js1.allowlist import check_url

BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
USER_AGENT = "INFO7375-JS1-student-agent"
_TOKEN_RE = re.compile(r"^[a-z0-9_-]+$")


class _AllowListRedirects(urllib.request.HTTPRedirectHandler):
    """Re-check every redirect target, so a redirect cannot leave the allow-list."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def board_url(token):
    if not _TOKEN_RE.match(token):
        raise ValueError(f"invalid board token {token!r}")
    return check_url(BOARD_URL.format(token=token))


def fetch_board(token, opener=None, timeout=30):
    """Return the raw response body as bytes. Exactly one request."""
    url = board_url(token)
    opener = opener or urllib.request.build_opener(_AllowListRedirects)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with opener.open(req, timeout=timeout) as resp:
        return resp.read()


def save_raw(raw, raw_dir, stamp):
    """Write raw bytes unchanged to <raw_dir>/<stamp>.json and return the path."""
    path = Path(raw_dir) / f"{stamp}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return path
