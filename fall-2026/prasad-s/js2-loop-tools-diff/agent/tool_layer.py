"""The three tools: fetch, read, write (GATE.md v0.2 §4, §5).

Each one calls Policy.check first and acts only on what the Permit names.
This module is the only JS2 code meant to open the network or write a file;
the loop is wired to it in CP5b. There is no delete tool (§5 Never).
"""

import hashlib
import os
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass

from .policy import R_WRITE_APPROVAL, R_WRITE_FILE, PolicyRefusal

TIMEOUT_SECONDS = 10  # GATE.md §4, CONTRACT v0.5 item 6
# JS2-CP5c, 2026-11-06: api.ashbyhq.com (behind Cloudflare) answers urllib's default
# "Python-urllib/3.13" with 403, error 1010 "browser_signature_banned", for every board.
# Every request names this project honestly; it imitates no browser or other client.
# Not a config key: config.json's six keys are fixed (CONTRACT v0.7 E1).
USER_AGENT = "js2-loop-tools-diff/0.7 (INFO 7375 course project)"


class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """§4: a redirect is never followed; its status and Location are returned instead."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _send(request, timeout):
    """The one place a request leaves the process. Tests replace this function."""
    return urllib.request.build_opener(_RefuseRedirects).open(request, timeout=timeout)


@dataclass(frozen=True)
class FetchResult:
    """A response with a status, whatever the status. The caller decides what it means (§4)."""

    url: str
    status: int
    content_type: str
    location: str
    body: bytes


class FetchError(Exception):
    """No status came back. kind is "timeout" or "connection" (§4's two retryable rows)."""

    def __init__(self, kind, url, detail):
        self.kind = kind
        self.url = url
        super().__init__(f"{kind} fetching {url}: {detail}")


class ToolLayer:
    def __init__(self, policy, timeout=TIMEOUT_SECONDS):
        self.policy = policy
        self.timeout = timeout
        # GATE.md §3: a write already done with the same path and content is not re-run.
        self._written = {}  # resolved path -> (sha256 of content, permit)
        self.repeats = []  # report lines for repeats noticed
        self._temporaries = set()  # files this run wrote that move() may move

    def fetch(self, url):
        """One GET attempt. Retries belong to the loop, which counts each attempt (§2)."""
        permit = self.policy.check("fetch", url)
        request = urllib.request.Request(permit.url, headers={"Accept": "application/json", "User-Agent": USER_AGENT},
                                         method="GET")
        try:
            with _send(request, self.timeout) as response:
                status, headers, body = response.status, response.headers, response.read()
        except urllib.error.HTTPError as exc:  # 3xx (not followed), 4xx, 5xx all have a status
            status, headers, body = exc.code, exc.headers, exc.read()
        except (TimeoutError, socket.timeout) as exc:
            raise FetchError("timeout", permit.url, exc) from exc
        except urllib.error.URLError as exc:
            kind = "timeout" if isinstance(exc.reason, (TimeoutError, socket.timeout)) else "connection"
            raise FetchError(kind, permit.url, exc.reason) from exc
        except OSError as exc:
            raise FetchError("connection", permit.url, exc) from exc
        return FetchResult(
            url=permit.url,
            status=status,
            content_type=headers.get("Content-Type", "") if headers else "",
            location=headers.get("Location", "") if headers else "",
            body=body,
        )

    def read(self, path):
        permit = self.policy.check("read", path)
        return permit.path.read_bytes()

    def list_dir(self, path):
        """Names in a folder, sorted; [] when it does not exist. Checked as a read."""
        permit = self.policy.check("read", path)
        if not permit.path.is_dir():
            return []
        return sorted(entry.name for entry in permit.path.iterdir())

    def write(self, path, data):
        """Write bytes to the resolved path. A new file is created exclusively, so a
        file that appears after the check is never overwritten without approval."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        digest = hashlib.sha256(data).hexdigest()
        recorded = self._written.get(self.policy.resolve(path))
        if recorded and recorded[0] == digest:
            self.repeats.append({"tool": "write", "path": str(path), "note": "repeat — not re-run"})
            return recorded[1]
        permit = self.policy.check("write", path)
        permit.path.parent.mkdir(parents=True, exist_ok=True)
        with open(permit.path, "wb" if permit.overwrite else "xb") as fh:
            fh.write(data)
        self._written[permit.path] = (digest, permit)
        self._temporaries.add(permit.path)
        return permit

    def move(self, source, target):
        """Move a file this run wrote to a new path (v0.6 item 2). target passes the
        write check; a target that exists is refused, approval or not."""
        source_path = self.policy.resolve(source)
        if source_path not in self._temporaries:
            raise PolicyRefusal("write", target, [(R_WRITE_FILE, f"{source} was not written by this run")])
        permit = self.policy.check("write", target)
        if permit.overwrite:
            raise PolicyRefusal("write", target, [(R_WRITE_APPROVAL, f"{target} already exists; a move never overwrites")])
        os.rename(source_path, permit.path)
        self._temporaries.discard(source_path)
        self._written.pop(source_path, None)
        return permit
