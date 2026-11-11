"""HTTP transports for the loop. The loop takes any callable

    transport(method, url, headers, timeout) -> Response

and never follows redirects itself: a 3xx comes back as a Response so the
loop can check the target against the policy first.

  UrllibTransport   the real network (GET only, redirects NOT followed).
  ReplayTransport   serves saved response files for --replay; no network.

Tests pass their own fake transport, so no test touches the network.
"""

import http.client
import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from agent import policy

USER_AGENT = "js2-job-search-agent/2.0"
MANIFEST_NAME = "replay.json"


@dataclass
class Response:
    status: int
    body: bytes = b""
    headers: dict = field(default_factory=dict)  # lower-cased names
    url: str = ""


class TransportTimeout(Exception):
    """The request timed out (retryable once under GATE section 4)."""


class TransportConnectionError(Exception):
    """The connection failed (retryable once under GATE section 4)."""


class ReplayMissing(Exception):
    """--replay has no saved response for this URL. Never retried."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Hand every 3xx back to the caller instead of following it."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _lower(headers):
    return {str(k).lower(): str(v) for k, v in (headers or {}).items()}


class UrllibTransport:
    """The only code that opens a network connection."""

    def __init__(self):
        self._opener = urllib.request.build_opener(_NoRedirect())

    def __call__(self, method, url, headers, timeout):
        policy.check_request(method, url, headers)  # checked again, here
        request = urllib.request.Request(url, headers=dict(headers),
                                         method=method)
        try:
            with self._opener.open(request, timeout=timeout) as response:
                return Response(response.status, response.read(),
                                _lower(response.headers), url)
        except urllib.error.HTTPError as exc:  # 3xx, 4xx, 5xx
            try:
                body = exc.read()
            except (OSError, http.client.HTTPException):
                body = b""
            return Response(exc.code, body, _lower(exc.headers), url)
        except TimeoutError as exc:
            raise TransportTimeout(str(exc)) from None
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, TimeoutError):
                raise TransportTimeout(str(exc.reason)) from None
            raise TransportConnectionError(str(exc.reason)) from None
        except (OSError, http.client.HTTPException) as exc:
            raise TransportConnectionError(
                f"{exc.__class__.__name__}: {exc}") from None


class ReplayTransport:
    """Serve saved responses from DIR instead of the network.

    DIR is read through the policy, so it must be inside data/, config/ or
    out/. Two layouts are accepted:

    1. DIR/replay.json (written by every run into out/runs/<run_id>/):
         {"responses": {"<url>": [<entry>, ...]}}
       where <entry> is {"status": 200, "file": "<path relative to DIR>",
       "headers": {...}} or {"error": "timeout" | "connection"}.
       The n-th request for a URL gets the n-th entry (the last one repeats).
    2. Otherwise DIR/<board>.json is served as a 200 for that board's URL.
    """

    def __init__(self, replay_dir, board_urls, root=policy.ROOT):
        self.root = root
        self.dir = policy.check_read(replay_dir, root)
        self.board_urls = dict(board_urls)  # url -> board name
        self.calls = {}
        manifest = self.dir / MANIFEST_NAME
        if manifest.is_file():
            data = json.loads(policy.read_bytes(manifest, root))
            self.responses = data.get("responses", {}) \
                if isinstance(data, dict) else None
            if not isinstance(self.responses, dict):
                raise ValueError(f"{manifest}: 'responses' is not an object")
        else:
            self.responses = None

    def __call__(self, method, url, headers, timeout):
        policy.check_request(method, url, headers)
        count = self.calls.get(url, 0)
        self.calls[url] = count + 1
        if self.responses is None:
            board = self.board_urls.get(url)
            path = self.dir / f"{board}.json"
            if board is None or not path.is_file():
                raise ReplayMissing(f"no saved response for {url}")
            return Response(200, policy.read_bytes(path, self.root), {}, url)
        entries = self.responses.get(url)
        if not entries:
            raise ReplayMissing(f"no saved response for {url}")
        entry = entries[min(count, len(entries) - 1)]
        if not isinstance(entry, dict) or not (
                entry.get("error") or isinstance(entry.get("status"), int)):
            raise ReplayMissing(f"unusable replay entry for {url}")
        if entry.get("error") == "timeout":
            raise TransportTimeout("replayed timeout")
        if entry.get("error"):
            raise TransportConnectionError("replayed connection error")
        body = b""
        if entry.get("file"):
            path = Path(self.dir) / entry["file"]
            if not path.is_file():
                raise ReplayMissing(f"saved file {entry['file']} not found")
            body = policy.read_bytes(path, self.root)
        return Response(int(entry["status"]), body,
                        _lower(entry.get("headers")), url)
