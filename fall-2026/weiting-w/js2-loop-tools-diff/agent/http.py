"""The only outbound call in the package, and it goes through the policy.

Every HTTP failure is translated into one of GATE.md §4's classifications here,
at the point where the HTTP facts are still visible. Nothing downstream
inspects an error message to decide what to do.
"""

from __future__ import annotations

import hashlib
import urllib.error
import urllib.request
from datetime import datetime, timezone

from .errors import PermanentFailure, SchemaFailure, TransientFailure
from .policy import Policy

USER_AGENT = (
    "INFO7375-JS2-job-search-agent/2.0 (coursework; read-only; "
    "contact via GitHub course repo)"
)

RETRYABLE_STATUS = frozenset({408, 425, 429, 500, 502, 503, 504})


class _NoRedirects(urllib.request.HTTPRedirectHandler):
    """A redirect is a failed observation, not a thing to follow.

    The allow-list was checked against the URL this agent was told to fetch;
    following a 302 would mean fetching a URL nobody checked.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise TransientFailure(
            f"refusing to follow a redirect ({code}) to {newurl!r}"
        )


_OPENER = urllib.request.build_opener(_NoRedirects)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(policy: Policy, url: str, *, method: str = "GET", timeout: float = 20.0):
    """Return `(body_bytes, http_status)`.

    Raises a `PolicyRefusal` subclass before opening a socket if the request is
    not permitted, `TransientFailure` for faults worth one more try, and
    `PermanentFailure` for faults that a retry cannot fix.
    """
    # The allow-list is enforced here, at the socket boundary. The repeat rule
    # is NOT enforced here: it is a rule about the actions the loop issues, and
    # GATE.md §3 makes an authorised retry its one exception. A retry re-issues
    # the same (method, url) by design, so counting it as a repeat would make
    # the error policy's retries impossible. See FRICTIONAL.md, 2026-11-09.
    policy.check_request(method, url)
    request = urllib.request.Request(
        url,
        method=method,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with _OPENER.open(request, timeout=timeout) as response:
            return response.read(), response.status
    except urllib.error.HTTPError as exc:
        if exc.code in RETRYABLE_STATUS:
            raise TransientFailure(f"HTTP {exc.code} from {url}") from exc
        raise PermanentFailure(f"HTTP {exc.code} from {url}") from exc
    except TimeoutError as exc:
        raise TransientFailure(f"timeout after {timeout}s on {url}") from exc
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        if isinstance(reason, TimeoutError):
            raise TransientFailure(f"timeout on {url}") from exc
        raise TransientFailure(f"could not reach {url}: {reason}") from exc


def parse_json(board: str, raw: bytes):
    """Decode a response body, mapping every decode failure to `schema`."""
    import json

    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SchemaFailure(f"{board}: response was not JSON: {exc}") from exc
