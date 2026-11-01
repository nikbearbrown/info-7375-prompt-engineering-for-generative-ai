"""Allow-listed fetch of one public Greenhouse board (CONTRACT.md, Refuses 1).

Only https://boards-api.greenhouse.io is reachable. Redirects are refused, so a
302 to another host can't take the request off the allow-list.
"""
import os
import re
import ssl
import urllib.request
from urllib.parse import urlsplit

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io"})
BOARD_TOKEN = re.compile(r"^[a-z0-9-]+$")
USER_AGENT = "js1-contract-and-watch/1.0 (INFO 7375 coursework; read-only)"


class RefusedFetch(Exception):
    """Raised for anything the contract says the agent must not fetch."""


def board_url(board):
    if not BOARD_TOKEN.match(board or ""):
        raise RefusedFetch(f"board token {board!r} is not [a-z0-9-]+")
    return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"


def check_allowed(url):
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise RefusedFetch(f"scheme {parts.scheme!r} refused; https only")
    if parts.username or parts.password or "@" in parts.netloc:
        raise RefusedFetch("credentials in the URL are refused")
    if parts.port not in (None, 443):
        raise RefusedFetch(f"port {parts.port} refused")
    host = (parts.hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        raise RefusedFetch(f"host {host!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}")
    return host


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RefusedFetch(f"redirect {code} to {newurl!r} refused")


def _tls_context():
    """Certificate verification always stays ON. The python.org macOS build ships without a
    CA bundle (first live run failed CERTIFICATE_VERIFY_FAILED, 2026-10-25), so fall back to
    the OS bundle when Python's own default file is missing."""
    ctx = ssl.create_default_context()
    paths = ssl.get_default_verify_paths()
    if not (paths.cafile or paths.capath) and not os.environ.get("SSL_CERT_FILE"):
        for bundle in ("/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt"):
            if os.path.exists(bundle):
                ctx.load_verify_locations(cafile=bundle)
                break
    return ctx


def fetch(url, timeout=30):
    """Return (raw_bytes, http_status). Raises RefusedFetch before any network I/O."""
    check_allowed(url)
    opener = urllib.request.build_opener(_NoRedirect, urllib.request.HTTPSHandler(context=_tls_context()))
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with opener.open(req, timeout=timeout) as resp:
        return resp.read(), resp.status
