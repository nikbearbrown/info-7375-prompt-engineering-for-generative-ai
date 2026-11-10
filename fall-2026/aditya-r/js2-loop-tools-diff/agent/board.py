"""Allow-listed fetch of one public Greenhouse board, and board-response parsing.

CONTRACT.md §3: only HTTPS on boards-api.greenhouse.io, including after redirects.
"""
import gzip
import json
import re
import urllib.error
import urllib.request
from urllib.parse import urlsplit

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io"})
BOARD_TOKEN_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
USER_AGENT = "js1-contract-and-watch/1.0 (INFO 7375 coursework; read-only)"


class RefusedError(Exception):
    """A prohibited operation (CONTRACT.md §3). Nothing was fetched."""


class BoardError(ValueError):
    """The board response is unusable; state must not change."""


def board_url(board):
    if not isinstance(board, str) or not BOARD_TOKEN_RE.match(board):
        raise RefusedError(f"refused: invalid board token {board!r}")
    return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"


def check_allowed(url):
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise RefusedError(f"refused: non-HTTPS URL scheme {parts.scheme!r}")
    host = (parts.hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        raise RefusedError(f"refused: host {host!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}")
    if parts.username or parts.password or (parts.port not in (None, 443)):
        raise RefusedError("refused: credentials or non-default port in URL")
    return url


class _AllowListRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_allowed(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, timeout=60):
    """GET an allow-listed URL. Returns (body bytes exactly as received, info dict)."""
    check_allowed(url)
    opener = urllib.request.build_opener(_AllowListRedirects())
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with opener.open(req, timeout=timeout) as resp:
            body = resp.read()
            final_url = resp.geturl()
            check_allowed(final_url)
            return body, {"status": resp.status, "final_url": final_url, "headers": dict(resp.headers.items())}
    except urllib.error.HTTPError as e:
        raise BoardError(f"fetch failed: HTTP {e.code} from {url}") from None
    except urllib.error.URLError as e:
        if isinstance(e.reason, RefusedError):
            raise e.reason from None
        raise BoardError(f"fetch failed: {e.reason}") from None


def decode_body(body):
    """Raw bytes -> parsed JSON. Accepts gzip bytes (the archived capture is stored as served)."""
    if body[:2] == b"\x1f\x8b":
        body = gzip.decompress(body)
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise BoardError(f"board response is not valid JSON: {e}") from None


def parse_jobs(data):
    """Validate the board response shape and ids; return the jobs list."""
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise BoardError("board response has no 'jobs' array")
    seen = set()
    for i, job in enumerate(data["jobs"]):
        if not isinstance(job, dict):
            raise BoardError(f"jobs[{i}] is not an object")
        job_id = job.get("id")
        if not isinstance(job_id, int) or isinstance(job_id, bool):
            raise BoardError(f"jobs[{i}] has a missing or non-integer id")
        if job_id in seen:
            raise BoardError(f"duplicate posting id {job_id}")
        seen.add(job_id)
    return data["jobs"]


def load_jobs_file(path):
    with open(path, "rb") as f:
        return parse_jobs(decode_body(f.read()))
