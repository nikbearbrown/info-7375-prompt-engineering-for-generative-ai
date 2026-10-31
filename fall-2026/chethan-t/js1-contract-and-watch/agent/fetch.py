"""Greenhouse board fetch. Only boards-api.greenhouse.io is allowed."""

import urllib.parse
import urllib.request

ALLOWED_HOST = "boards-api.greenhouse.io"


def board_url(board):
    return f"https://{ALLOWED_HOST}/v1/boards/{board}/jobs?content=true"


def fetch_board(url):
    """Fetch a board; raise ValueError for any other host before any request.

    Returns the raw response bytes, untouched.
    """
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname != ALLOWED_HOST:
        raise ValueError(f"refusing to fetch {url!r}: only https://{ALLOWED_HOST} is allowed")
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()
