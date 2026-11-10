"""The agent's only tools: one network GET, file reads, and three kinds of write.

Every tool takes the policy and asks it first. On anything but "allow" the tool raises
Refused and does nothing. This is the only file in agent/ that touches the network or
the disk (tests/test_gate_matches_code.py checks that).
"""

import collections
import json
import os
import socket
import time
import urllib.error
import urllib.parse
import urllib.request

Response = collections.namedtuple("Response", "status headers body")
UrlParts = collections.namedtuple("UrlParts", "scheme username password hostname port path query_keys fragment")
USER_AGENT = "js2-loop-tools-diff (INFO 7375 coursework; read-only job board watch)"


class Refused(Exception):
    def __init__(self, decision):
        super().__init__("refused: %s (%s)" % (decision.reason, decision.target))
        self.decision = decision


class FetchError(Exception):
    """A request that got no HTTP answer: kind is timeout, connection or too_large."""

    def __init__(self, kind, detail):
        super().__init__("%s: %s" % (kind, detail))
        self.kind, self.detail = kind, detail


def split_url(url):
    parts = urllib.parse.urlsplit(url)
    try:
        port = parts.port
    except ValueError:
        port = -1
    keys = [key for key, _ in urllib.parse.parse_qsl(parts.query, keep_blank_values=True)]
    return UrlParts(parts.scheme.lower(), parts.username, parts.password, parts.hostname or "", port,
                    parts.path, keys, parts.fragment)


def normalize_url(url):
    """The repeat rule's "same fetch": lower-case scheme and host, no default port, sorted query."""
    parts = urllib.parse.urlsplit(url)
    host = parts.hostname or ""
    try:
        port = parts.port
    except ValueError:
        port = None
    netloc = host if port in (None, 443) else "%s:%d" % (host, port)
    query = urllib.parse.urlencode(sorted(urllib.parse.parse_qsl(parts.query, keep_blank_values=True)))
    return urllib.parse.urlunsplit((parts.scheme.lower(), netloc, parts.path, query, ""))


def join_url(base, location):
    return urllib.parse.urljoin(base, location or "")


class _NoRedirects(urllib.request.HTTPRedirectHandler):
    """urllib must not follow redirects by itself: the loop asks the policy first."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def http_transport(url, timeout, max_bytes):
    """GET the URL once, with no cookies or credentials. Any HTTP status comes back as a Response.

    The timeout covers the whole request, body included, and the body is not read past max_bytes.
    """
    deadline = time.monotonic() + timeout
    opener = urllib.request.build_opener(_NoRedirects)
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    try:
        response = opener.open(request, timeout=timeout)
        status = response.status
    except urllib.error.HTTPError as error:
        response, status = error, error.code
    except socket.timeout as error:
        raise FetchError("timeout", str(error) or "timed out")
    except urllib.error.URLError as error:
        if isinstance(error.reason, socket.timeout) or "timed out" in str(error.reason):
            raise FetchError("timeout", str(error.reason))
        raise FetchError("connection", str(error.reason))
    except OSError as error:
        raise FetchError("connection", str(error))
    with response:
        headers = {key.lower(): value for key, value in response.headers.items()}
        chunks, size = [], 0
        while True:
            if time.monotonic() > deadline:
                raise FetchError("timeout", "body not finished within %s s" % timeout)
            try:
                chunk = response.read(65536)
            except socket.timeout:
                raise FetchError("timeout", "timed out reading the body")
            except OSError as error:
                raise FetchError("connection", str(error))
            if not chunk:
                break
            size += len(chunk)
            if size > max_bytes:
                raise FetchError("too_large", "over %d bytes" % max_bytes)
            chunks.append(chunk)
    return Response(status, headers, b"".join(chunks))


def fetch(policy, url, transport, timeout, max_bytes, method="GET"):
    decision = policy.check_fetch(method, url)
    if not decision.allowed:
        raise Refused(decision)
    return transport(url, timeout, max_bytes)


def read_file(policy, path):
    decision = policy.check_read(path)
    if not decision.allowed:
        raise Refused(decision)
    with open(path, "rb") as handle:
        return handle.read()


def exists(policy, path):
    decision = policy.check_read(path)
    if not decision.allowed:
        raise Refused(decision)
    return os.path.lexists(path)


def write_new(policy, path, data):
    """Create a file that does not exist yet. Never follows a symbolic link, never overwrites."""
    decision = policy.check_write(path, "new")
    if not decision.allowed:
        raise Refused(decision)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    with os.fdopen(os.open(path, flags, 0o644), "wb") as handle:
        handle.write(data)
    policy.note_created(path)


def append_text(policy, path, text):
    decision = policy.check_write(path, "append")
    if not decision.allowed:
        raise Refused(decision)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(text)


def write_state(policy, path, state, board):
    """Replace a state file. A replacement that drops seen ids needs my approval (GATE.md section 5)."""
    old_ids = set()
    if exists(policy, path):
        old_ids = set(json.loads(read_file(policy, path).decode("utf-8")).get("seen_ids", []))
    drops = bool(old_ids - set(state["seen_ids"]))
    decision = policy.check_write(path, "state", board=board, drops_ids=drops)
    if not decision.allowed:
        raise Refused(decision)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    temp = str(path) + ".tmp"
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    with os.fdopen(os.open(temp, flags, 0o644), "w", encoding="utf-8") as handle:
        handle.write(json.dumps(state, indent=2, ensure_ascii=False) + "\n")
    os.replace(temp, path)
    return decision
