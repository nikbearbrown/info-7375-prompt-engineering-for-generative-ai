"""Greenhouse board fetch. Only boards-api.greenhouse.io is allowed."""

import urllib.parse
import urllib.request

ALLOWED_HOST = "boards-api.greenhouse.io"


def board_url(board):
    return f"https://{ALLOWED_HOST}/v1/boards/{board}/jobs?content=true"


def check_url(url):
    """Raise ValueError unless url is https on the allowed host."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname != ALLOWED_HOST:
        raise ValueError(f"refusing to fetch {url!r}: only https://{ALLOWED_HOST} is allowed")


class RefuseOffHostRedirect(urllib.request.HTTPRedirectHandler):
    """Check every redirect target before urllib requests it."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        try:
            check_url(newurl)
        except ValueError:
            fp.close()
            raise
        return super().redirect_request(req, fp, code, msg, headers, newurl)


# urllib.request.urlopen with the redirect check installed for this module only.
urlopen = urllib.request.build_opener(RefuseOffHostRedirect).open


def fetch_board(url):
    """Fetch a board; raise ValueError for any other host, including redirects,
    before any request to it.

    Returns the raw response bytes, untouched.
    """
    check_url(url)
    with urlopen(url, timeout=30) as response:
        return response.read()
