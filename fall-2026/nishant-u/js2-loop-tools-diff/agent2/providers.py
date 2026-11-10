"""Greenhouse and Ashby: the board URL, one GET through the policy, and parsing into
{system, board, id, title, location, content} with ids keyed "system:board:id"."""
import json
import socket
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "info7375-js2-coursework (GET only)"
MAX_REDIRECTS = 3


class Transient(Exception):
    """A timeout or connection error: the error policy may retry it once."""

    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


class BadResponse(ValueError):
    """HTTP 200 whose body is not valid JSON or not the board shape."""


def url_for(system, board):
    if system == "greenhouse":
        return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
    if system == "ashby":
        return f"https://api.ashbyhq.com/posting-api/job-board/{urllib.parse.quote(board)}"
    raise ValueError(f"unknown system {system!r}")


def key(system, board, raw_id):
    return f"{system}:{board}:{raw_id}"


# --- network ---------------------------------------------------------------------------------
class _NoFollow(urllib.request.HTTPRedirectHandler):
    # Redirects surface as HTTPError so http_get can check the new host before following it.
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoFollow)


def _default_open(request, timeout):
    return _OPENER.open(request, timeout=timeout)


def http_get(url, policy, opener=None, timeout=20, method="GET"):
    """(status, body, final_url). Every hop is authorized before its request is made.
    HTTP error statuses are returned, not raised; timeouts and connection errors raise Transient."""
    opener = opener or _default_open
    policy.authorize("fetch", url, method=method)
    for _ in range(MAX_REDIRECTS + 1):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
        try:
            with opener(request, timeout) as response:
                return response.status, response.read(), url
        except urllib.error.HTTPError as exc:
            if exc.code in (301, 302, 303, 307, 308):
                location = exc.headers.get("Location") if exc.headers else None
                if not location:
                    return exc.code, b"", url
                url = urllib.parse.urljoin(url, location)
                policy.check_redirect(url)  # raises PolicyRefused before any request to a new host
                continue
            body = exc.read() if exc.fp is not None else b""
            return exc.code, body, url
        except (socket.timeout, TimeoutError) as exc:
            raise Transient("timeout") from exc
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, (socket.timeout, TimeoutError)):
                raise Transient("timeout") from exc
            raise Transient("connection-error") from exc
        except ConnectionError as exc:
            raise Transient("connection-error") from exc
    raise Transient("connection-error")  # too many redirects: treated as a failed connection


# --- parsing ---------------------------------------------------------------------------------
def _load(body):
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise BadResponse(f"not valid JSON: {exc.__class__.__name__}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise BadResponse("wrong shape: expected an object with a 'jobs' list")
    return data["jobs"]


def parse(system, board, body):
    jobs = _load(body)
    out = []
    for job in jobs:
        if not isinstance(job, dict) or not isinstance(job.get("title"), str):
            raise BadResponse("wrong shape: every posting needs a string title")
        raw_id = job.get("id")
        if system == "greenhouse":
            if type(raw_id) is not int:
                raise BadResponse("wrong shape: Greenhouse ids are integers")
            location = (job.get("location") or {}).get("name") or ""
            content = job.get("content") or ""
        elif system == "ashby":
            if not isinstance(raw_id, str) or not raw_id:
                raise BadResponse("wrong shape: Ashby ids are non-empty strings")
            location = job.get("location") or ""
            content = job.get("descriptionHtml") or job.get("descriptionPlain") or ""
        else:
            raise ValueError(f"unknown system {system!r}")
        out.append({"system": system, "board": board, "id": key(system, board, raw_id),
                    "title": job["title"], "location": location, "content": content})
    return out


def judge_view(posting):
    """The Greenhouse-shaped view the JS1 rule judge and support check read."""
    return {"id": posting["id"], "title": posting["title"],
            "location": {"name": posting["location"]}, "content": posting["content"]}
