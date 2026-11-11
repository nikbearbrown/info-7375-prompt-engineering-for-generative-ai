"""Shared fakes and CONSTRUCTED fixtures for the JS2 tests. No test touches the network.

The interface these tests assume, taken from GATE.md (written before any agent2 code):

agent2.policy
    Policy(root)                       root = the output root ("out")
      .authorize(operation, target, method="GET", approved=False, old_ids=None, new_ids=None)
                                       fetch -> host; file operations -> resolved Path;
                                       anything refused -> PolicyRefused (a PermissionError)
      .read_file / .write_run_file / .update_state / .reset_state / .read_state
agent2.providers
    url_for(system, board), parse(system, board, body) -> postings, key(system, board, id),
    http_get(url, policy, opener=..., timeout=...) -> (status, body, final_url),
    Transient (timeout / connection error), BadResponse
agent2.loop
    PROFILES {"full": boards 1-5, "demo": boards 1-4}, Loop(boards, policy=, client=, clock=,
    sleep=, budgets=).run() -> report; client(url, timeout) -> (status, body) or raises Transient
agent2.check
    check_run(run_dir) -> {"flags": [...], "boards": [...]}, reading only the saved raw responses

Every board body below is CONSTRUCTED for the tests (marked "_constructed": true); none is a
saved live response.
"""
import json
import urllib.error


def gh_body(jobs):
    """A CONSTRUCTED Greenhouse-shaped board response."""
    return json.dumps({"_constructed": True, "jobs": jobs, "meta": {"total": len(jobs)}}).encode()


def gh_job(i, title="Data Analyst", location="New York City, NY", content="Python and SQL"):
    return {"id": i, "title": title, "location": {"name": location}, "content": content,
            "absolute_url": f"https://example.com/{i}"}


def ashby_body(jobs):
    """A CONSTRUCTED Ashby-shaped board response."""
    return json.dumps({"_constructed": True, "apiVersion": "1", "jobs": jobs}).encode()


def ashby_job(i, title="Staff Engineer, Machine Learning", location="San Francisco, CA"):
    return {"id": f"00000000-0000-0000-0000-{i:012d}", "title": title, "location": location,
            "descriptionHtml": "<p>Python</p>", "descriptionPlain": "Python", "isListed": True}


GH = "https://boards-api.greenhouse.io/v1/boards/{}/jobs?content=true"
ASHBY = "https://api.ashbyhq.com/posting-api/job-board/{}"
URLS = {
    "faire": GH.format("faire"),
    "instacart": GH.format("instacart"),
    "ashby_poshmark": ASHBY.format("poshmark"),
    "gh_poshmark": GH.format("poshmark"),
    "bad": GH.format("no-such-board-js2-test"),
}
NOT_FOUND = b'{"status":404,"error":"Job not found"}'


def ok_responses():
    """Constructed responses for all five planned boards; the failing board returns 404."""
    return {
        URLS["faire"]: [(200, gh_body([gh_job(1), gh_job(2)]))],
        URLS["instacart"]: [(200, gh_body([gh_job(3)]))],
        URLS["ashby_poshmark"]: [(200, ashby_body([ashby_job(n) for n in range(1, 23)]))],
        URLS["gh_poshmark"]: [(200, b'{"jobs":[],"meta":{"total":0}}')],
        URLS["bad"]: [(404, NOT_FOUND)],
    }


class FakeClock:
    def __init__(self):
        self.t = 0.0
        self.sleeps = []

    def __call__(self):
        return self.t

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.t += seconds


class FakeClient:
    """client(url, timeout) -> (status, body). Each url has a queue of responses; an item that
    is an exception is raised. advance= seconds added to the clock per call."""

    def __init__(self, responses, clock=None, advance=0.0):
        self.responses = {u: list(v) for u, v in responses.items()}
        self.calls = []
        self.clock = clock
        self.advance = advance

    def __call__(self, url, timeout=None):
        self.calls.append(url)
        if self.clock is not None:
            self.clock.t += self.advance
        queue = self.responses.get(url)
        if not queue:
            raise AssertionError(f"unexpected request to {url}")
        item = queue.pop(0) if len(queue) > 1 else queue[0]
        if isinstance(item, BaseException):
            raise item
        return item


class FakeResponse:
    def __init__(self, status, body):
        self.status, self._body = status, body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class SpyOpener:
    """An opener for providers.http_get: records every request; a url may map to a redirect."""

    def __init__(self, redirects=None, body=b'{"jobs":[]}'):
        self.redirects = redirects or {}
        self.calls = []
        self.body = body

    def __call__(self, request, timeout=None):
        url = request.full_url
        self.calls.append((request.get_method(), url))
        if url in self.redirects:
            raise urllib.error.HTTPError(url, 302, "Found", {"Location": self.redirects[url]}, None)
        return FakeResponse(200, self.body)


def board(system, name, company=None):
    url = (GH if system == "greenhouse" else ASHBY).format(name)
    return {"system": system, "board": name, "company": company or name, "url": url}
