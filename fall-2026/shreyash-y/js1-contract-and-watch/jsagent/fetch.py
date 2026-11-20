"""The only network code in the agent. HTTPS GET to one allow-listed host; every redirect is
checked against the same list (CONTRACT.md section 4)."""
import re
import urllib.parse
import urllib.request

ALLOWED_HOSTS = {"boards-api.greenhouse.io"}
TOKEN_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
USER_AGENT = "INFO7375-JS1-student-agent (read-only; one request per run)"


class HostNotAllowed(Exception):
    pass


def check_url(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https":
        raise HostNotAllowed(f"refused non-https url: {url}")
    if parts.username or parts.password or parts.hostname not in ALLOWED_HOSTS or parts.port:
        raise HostNotAllowed(f"refused host {parts.hostname!r}: not on the allow-list {sorted(ALLOWED_HOSTS)}")
    return url


def board_url(token):
    if not TOKEN_RE.match(token or ""):
        raise ValueError(f"bad board token {token!r}")
    return check_url(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true")


class AllowListRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(urllib.parse.urljoin(req.full_url, newurl))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def get(url, timeout=30):
    """Returns the raw response bytes. Nothing is parsed here."""
    check_url(url)
    opener = urllib.request.build_opener(AllowListRedirectHandler())
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with opener.open(req, timeout=timeout) as resp:
        check_url(resp.geturl())
        return resp.read()
