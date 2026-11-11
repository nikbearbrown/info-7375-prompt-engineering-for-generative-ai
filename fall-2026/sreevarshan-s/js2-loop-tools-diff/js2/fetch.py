"""Fetch layer: one read-only request per call, one function per ATS.

Each fetch checks policy.allow_request before touching the network, sends a
single GET, and saves the raw body byte-for-byte under output/raw/ when
policy.write_bytes allows it. Failures raise BoardFetchError.
"""

import json
import os
import re
import socket
import time
import urllib.error
import urllib.request
from urllib.parse import quote

from js2 import policy

USER_AGENT = "INFO7375-JS2-student-agent"
REQUEST_TIMEOUT = 15

GREENHOUSE_URL = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
LEVER_URL = "https://api.lever.co/v0/postings/{token}?mode=json"


class BoardFetchError(Exception):
    """A board fetch failed.

    kind is one of: blocked, http, timeout, network, bad_json.
    status_code is None when no HTTP status was received.
    retriable is True only for 5xx and timeouts (GATE.md section 4).
    """

    def __init__(self, board, status_code, retriable, kind, message):
        super().__init__(message)
        self.board = board
        self.status_code = status_code
        self.retriable = retriable
        self.kind = kind


def greenhouse_url(token):
    return GREENHOUSE_URL.format(token=quote(token, safe=""))


def lever_url(token):
    return LEVER_URL.format(token=quote(token, safe=""))


URL_BUILDERS = {"greenhouse": greenhouse_url, "lever": lever_url}


def utc_stamp():
    t = time.time()
    return time.strftime("%Y%m%dT%H%M%S", time.gmtime(t)) + "%06dZ" % int((t % 1) * 1e6)


def _raw_path(ats, token, suffix=""):
    safe_token = re.sub(r"[^A-Za-z0-9_-]", "_", token)
    name = "%s-%s-%s%s.json" % (utc_stamp(), ats, safe_token, suffix)
    return os.path.join(policy.ALLOWED_OUTPUT, "raw", name)


def replay_from_file(path, ats, token):
    """Replay a saved raw response instead of fetching (no network).

    The bytes are copied into output/raw/ with a -SEEDED suffix so the
    trace and the independent check have evidence inside output/.
    """
    board = "%s:%s" % (ats, token)
    with open(path, "rb") as f:
        body = f.read()
    raw_path = _raw_path(ats, token, "-SEEDED")
    write_decision = policy.write_bytes(raw_path, body)
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise BoardFetchError(board, None, False, "bad_json", "replayed file %s is not JSON" % path)
    return {
        "ats": ats,
        "token": token,
        "url": URL_BUILDERS[ats](token),
        "status_code": None,
        "bytes": len(body),
        "data": data,
        "seeded_from": os.path.realpath(path),
        "raw_path": raw_path if write_decision is True else None,
        "raw_write_decision": write_decision,
    }


def _is_timeout(exc):
    if isinstance(exc, (socket.timeout, TimeoutError)):
        return True
    return isinstance(exc, urllib.error.URLError) and isinstance(
        exc.reason, (socket.timeout, TimeoutError)
    )


def _fetch(ats, token, url, timeout):
    board = "%s:%s" % (ats, token)
    if not policy.allow_request(url):
        raise BoardFetchError(board, None, False, "blocked", "request blocked by policy: %s" % url)

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            body = resp.read()
    except urllib.error.HTTPError as e:
        retriable = 500 <= e.code < 600
        raise BoardFetchError(board, e.code, retriable, "http", "HTTP %d from %s" % (e.code, url))
    except Exception as e:
        if _is_timeout(e):
            raise BoardFetchError(board, None, True, "timeout", "timed out after %ss: %s" % (timeout, url))
        if isinstance(e, (urllib.error.URLError, OSError)):
            raise BoardFetchError(board, None, False, "network", "network error for %s: %s" % (url, e))
        raise

    raw_path = _raw_path(ats, token)
    write_decision = policy.write_bytes(raw_path, body)

    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise BoardFetchError(board, status, False, "bad_json", "response from %s is not JSON" % url)

    return {
        "ats": ats,
        "token": token,
        "url": url,
        "status_code": status,
        "bytes": len(body),
        "data": data,
        "raw_path": raw_path if write_decision is True else None,
        "raw_write_decision": write_decision,
    }


def fetch_greenhouse(token, timeout=REQUEST_TIMEOUT):
    return _fetch("greenhouse", token, greenhouse_url(token), timeout)


def fetch_lever(token, timeout=REQUEST_TIMEOUT):
    return _fetch("lever", token, lever_url(token), timeout)
