"""Live HTTP (policy-checked, redirects re-checked) and a replay transport for SEEDED runs that
answers from saved files instead of the network."""
import json
import pathlib
import socket
import urllib.error
import urllib.request

from jsagent import policy

USER_AGENT = "INFO7375-JS2-student-agent (read-only)"


class _Redirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        policy.check_redirect(req.full_url, newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Live:
    def get(self, url, timeout=20):
        policy.check_request("GET", url)
        opener = urllib.request.build_opener(_Redirects())
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with opener.open(req, timeout=timeout) as resp:
                policy.check_request("GET", resp.geturl())
                return resp.status, resp.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()
        except (socket.timeout, TimeoutError):
            raise TimeoutError(f"no answer from {url} in {timeout}s")
        except urllib.error.URLError as e:
            if isinstance(e.reason, (socket.timeout, TimeoutError)):
                raise TimeoutError(f"no answer from {url} in {timeout}s")
            raise ConnectionError(str(e.reason))


class Replay:
    """SEEDED: map file {url: {"status": int, "file": path}}; nothing touches the network."""

    def __init__(self, map_path):
        self.base = pathlib.Path(map_path).resolve().parent
        self.map = json.loads(pathlib.Path(map_path).read_text())

    def get(self, url, timeout=20):
        policy.check_request("GET", url)
        entry = self.map.get(url)
        if entry is None:
            return 404, b'{"seeded": "no saved response for this url"}'
        return entry["status"], (self.base / entry["file"]).read_bytes()
