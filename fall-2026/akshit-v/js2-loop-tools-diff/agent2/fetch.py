"""HTTP transports. Every request passes the permission policy first.

LiveTransport talks to the network. ReplayTransport serves saved files and is used only
for runs labeled REPLAY or SEEDED.
"""
import json
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from agent2 import policy

USER_AGENT = "INFO7375-js2-student-agent (read-only)"


@dataclass
class Response:
    kind: str                 # "ok" | "http_error" | "transient"
    status: int | None
    body: bytes | None
    detail: str = ""


class AllowListRedirects(urllib.request.HTTPRedirectHandler):
    """A redirect is a new request, so it must pass the policy too."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        policy.check_request("GET", newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class LiveTransport:
    label = "LIVE"

    def __init__(self):
        self.opener = urllib.request.build_opener(AllowListRedirects)

    def get(self, url: str, timeout: float) -> Response:
        policy.check_request("GET", url)
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with self.opener.open(req, timeout=timeout) as resp:
                policy.check_request("GET", resp.geturl())
                return Response("ok", resp.status, resp.read())
        except urllib.error.HTTPError as e:
            body = e.read()
            kind = "transient" if e.code >= 500 else "http_error"
            return Response(kind, e.code, body, f"HTTP {e.code}")
        except (urllib.error.URLError, TimeoutError, socket.timeout, ConnectionError) as e:
            return Response("transient", None, None, f"{type(e).__name__}: {e}")


class ReplayTransport:
    """Serves saved responses from a manifest {url: {"file": path, "status": n}}."""

    def __init__(self, manifest_path: Path, label: str):
        self.manifest_path = Path(manifest_path)
        self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.label = label

    def get(self, url: str, timeout: float) -> Response:
        policy.check_request("GET", url)
        entry = self.manifest.get(url)
        if entry is None:
            return Response("transient", None, None, "replay: no saved response for this URL")
        body = (self.manifest_path.parent / entry["file"]).read_bytes()
        status = entry.get("status", 200)
        kind = "ok" if status < 400 else ("transient" if status >= 500 else "http_error")
        return Response(kind, status, body, "" if kind == "ok" else f"HTTP {status}")
