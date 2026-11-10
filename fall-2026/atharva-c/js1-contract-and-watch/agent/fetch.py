"""Allow-listed fetch. CONTRACT.md > Refuses: only boards-api.greenhouse.io."""
import urllib.request
from urllib.parse import urlparse

ALLOWED_HOSTS = {"boards-api.greenhouse.io"}
BOARD = "stripe"
BOARD_URL = f"https://boards-api.greenhouse.io/v1/boards/{BOARD}/jobs?content=true"


class HostNotAllowed(Exception):
    pass


def check_allowed(url):
    u = urlparse(url)
    if u.scheme != "https" or u.hostname not in ALLOWED_HOSTS:
        raise HostNotAllowed(f"refusing to fetch {url!r}: host not on allow-list {sorted(ALLOWED_HOSTS)}")


class _NoOffListRedirects(urllib.request.HTTPRedirectHandler):
    # A redirect to another host would bypass the allow-list, so check it too.
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_allowed(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def get(url=BOARD_URL, timeout=60):
    check_allowed(url)
    opener = urllib.request.build_opener(_NoOffListRedirects)
    req = urllib.request.Request(url, headers={"User-Agent": "js1-contract-and-watch (course project)"})
    with opener.open(req, timeout=timeout) as resp:
        return resp.read()
