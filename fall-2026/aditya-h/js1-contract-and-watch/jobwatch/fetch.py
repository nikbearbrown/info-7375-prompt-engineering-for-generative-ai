"""Allow-listed fetch of one public Greenhouse board (CONTRACT: Refuses 1, 4)."""
import json
import os
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io"})
_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class HostNotAllowed(Exception):
    pass


class FetchError(Exception):
    pass


def board_url(slug):
    if not _SLUG.match(slug or ""):
        raise ValueError(f"invalid board slug: {slug!r}")
    return f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"


def check_url(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS:
        raise HostNotAllowed(f"refusing to fetch {url!r}: host not on allow-list {sorted(ALLOWED_HOSTS)}")


def _tls_context():
    """Verified TLS. python.org macOS builds ship no CA bundle, so fall back to the system one."""
    ctx = ssl.create_default_context()
    if not ctx.get_ca_certs() and os.path.exists("/etc/ssl/cert.pem"):
        ctx = ssl.create_default_context(cafile="/etc/ssl/cert.pem")
    return ctx


def http_get(url, timeout=30):
    """Default fetcher: one GET request to an allow-listed URL, returns the raw body bytes."""
    check_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": "info7375-js1-jobwatch (student project)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_tls_context()) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        raise FetchError(f"HTTP {e.code} from {url}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise FetchError(f"request to {url} failed: {e}") from e


def parse_jobs(raw):
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as e:
        raise FetchError("response body is not JSON") from e
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise FetchError("response has no 'jobs' list")
    return data["jobs"]
