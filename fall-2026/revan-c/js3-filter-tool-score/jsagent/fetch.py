"""Allow-listed, read-only fetch of one Greenhouse board (CONTRACT.md, In and Refuses)."""
import urllib.parse
import urllib.request

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io"})
ALLOWED_SLUG = "klaviyo"
_PATH = f"/v1/boards/{ALLOWED_SLUG}/jobs"
_QUERY = "content=true"
USER_AGENT = "js1-contract-and-watch/1.0 (INFO7375 course project; read-only)"


class FetchRefused(Exception):
    """The request would leave the contract's allow-list."""


def board_url(slug):
    if slug != ALLOWED_SLUG:
        raise FetchRefused(f"board slug {slug!r} is not allowed; only {ALLOWED_SLUG!r}")
    url = f"https://boards-api.greenhouse.io{_PATH}?{_QUERY}"
    check_url(url)
    return url


def check_url(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https":
        raise FetchRefused(f"scheme {parts.scheme!r} refused; https only")
    if parts.hostname not in ALLOWED_HOSTS or parts.port is not None or parts.username:
        raise FetchRefused(f"host {parts.netloc!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}")
    if parts.path != _PATH or parts.query != _QUERY or parts.fragment:
        raise FetchRefused(f"endpoint {parts.path}?{parts.query} refused; only {_PATH}?{_QUERY}")


def check_redirect(new_url):
    # A redirect is held to the same rule as the first request, so it can never leave the host.
    check_url(new_url)


class _AllowListRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_redirect(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_board(url, timeout=30):
    """GET the board and return the raw response bytes, unparsed."""
    check_url(url)
    opener = urllib.request.build_opener(_AllowListRedirects)
    request = urllib.request.Request(
        url, method="GET", headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    with opener.open(request, timeout=timeout) as response:
        check_url(response.geturl())
        return response.read()
