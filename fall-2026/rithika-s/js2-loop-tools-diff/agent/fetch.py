"""Fetch the board from the single allow-listed host and save it unchanged.

Every URL, including any redirect target, is checked against the allow-list
before a connection is opened.
"""

import hashlib
import re
import urllib.parse
import urllib.request
from pathlib import Path

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io"})
ALLOWED_BOARDS = frozenset({"scaleai"})
BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
TIMEOUT_SECONDS = 30


class FetchRefused(Exception):
    """Raised when a URL or board is refused before any network call."""


def check_url(url):
    """Return url if it is HTTPS on an allow-listed host; raise otherwise."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https":
        raise FetchRefused(
            f"refused: scheme {parts.scheme!r} is not https (url: {url})")
    if parts.username is not None or parts.password is not None:
        raise FetchRefused(f"refused: credentials in url are not allowed ({url})")
    host = (parts.hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        raise FetchRefused(
            f"refused: host {host!r} is not on the allow-list "
            f"{sorted(ALLOWED_HOSTS)}")
    if parts.port not in (None, 443):
        raise FetchRefused(f"refused: port {parts.port} is not 443")
    return url


def board_url(board):
    """Build the jobs URL for an allowed board token."""
    if board not in ALLOWED_BOARDS or not re.fullmatch(r"[a-z0-9_-]+", board):
        raise FetchRefused(
            f"refused: board {board!r} is not one of {sorted(ALLOWED_BOARDS)}")
    return check_url(BOARD_URL.format(board=board))


class _AllowListRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Re-check the allow-list before following any redirect."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _default_opener():
    return urllib.request.build_opener(_AllowListRedirectHandler())


def fetch_bytes(url, opener=None):
    """Return the response body; the URL is checked before opening."""
    check_url(url)
    opener = opener or _default_opener()
    request = urllib.request.Request(
        url, headers={"User-Agent": "js1-job-search-agent/1.0"})
    with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
        return response.read()


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def save_raw(data, raw_dir, timestamp, board):
    """Write bytes unchanged to <raw_dir>/<timestamp>_<board>.json.

    Returns (path, sha256). Refuses to overwrite an existing file.
    """
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{timestamp}_{board}.json"
    with open(path, "xb") as handle:
        handle.write(data)
    return path, sha256_hex(data)


def fetch_board(board, raw_dir, timestamp, opener=None):
    """Fetch the board and save the raw response. Returns (path, sha256)."""
    url = board_url(board)
    data = fetch_bytes(url, opener=opener)
    return save_raw(data, raw_dir, timestamp, board)
