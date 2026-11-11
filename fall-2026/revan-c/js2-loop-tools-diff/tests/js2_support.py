"""Helpers for the Job-Search Agent 2 tests.

Every board body built here is a CONSTRUCTED test fixture, not a board result.
The fetcher and clock are fakes, so no test touches the network or waits on real time.
"""
import json
import pathlib
import shutil

from jsloop.fetch import FetchResult

ROOT = pathlib.Path(__file__).resolve().parent.parent
RESUME = ROOT / "resumes" / "aarav-patel.json"

KLAVIYO = "https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true"
DUOLINGO = "https://boards-api.greenhouse.io/v1/boards/duolingo/jobs?content=true"
PATCHMYPC = "https://api.lever.co/v0/postings/patchmypc?mode=json"
MISSING = "https://boards-api.greenhouse.io/v1/boards/js2-deliberate-missing-board/jobs?content=true"


def _escape(html):
    # Greenhouse sends `content` as entity-escaped HTML.
    return html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def gh_job(job_id, title="Software Engineer", location="Boston, MA",
           content="<p>Python, SQL and Docker on AWS.</p>"):
    return {"id": job_id, "title": title, "location": {"name": location},
            "content": _escape(content), "absolute_url": f"https://example.invalid/gh/{job_id}"}


def gh_body(*jobs):
    return json.dumps({"jobs": list(jobs), "meta": {"total": len(jobs)}}).encode()


def lever_posting(posting_id, text="Software Engineer, Backend", location="United States",
                  description="<div>Python and PostgreSQL services.</div>"):
    return {"id": posting_id, "text": text,
            "categories": {"location": location, "team": "Engineering"},
            "description": description, "lists": [], "additional": "",
            "hostedUrl": f"https://example.invalid/lever/{posting_id}", "workplaceType": "remote"}


def lever_body(*postings):
    return json.dumps(list(postings)).encode()


def ok(body):
    return FetchResult(status=200, body=body, error=None)


def good_responses():
    """One valid, nonempty response per normal board."""
    return {
        KLAVIYO: ok(gh_body(gh_job(1), gh_job(2, "Account Executive", "London, UK"))),
        DUOLINGO: ok(gh_body(gh_job(10, "Backend Engineer"), gh_job(11, "Designer", "Pittsburgh, PA"))),
        PATCHMYPC: ok(lever_body(lever_posting("aaa-1"), lever_posting("bbb-2", "Finance Analyst"))),
    }


class FakeFetcher:
    """Serves canned FetchResults by URL and records every call it receives."""

    def __init__(self, responses, clock=None, advance_by=None):
        self.responses = dict(responses)
        self.calls = []
        self.clock = clock
        self.advance_by = advance_by or {}

    def __call__(self, url, timeout):
        self.calls.append((url, timeout))
        if self.clock is not None and url in self.advance_by:
            self.clock.advance(self.advance_by[url])
        if url not in self.responses:
            raise AssertionError(f"test fetcher has no response for {url}")
        return self.responses[url]


class FakeClock:
    """A monotonic clock that moves only when a test moves it."""

    def __init__(self, start=0.0):
        self.now = float(start)

    def advance(self, seconds):
        self.now += seconds

    def __call__(self):
        return self.now


def make_workspace(tmp_path):
    """A fresh repository-shaped folder: the fictional résumé plus an empty fixtures folder."""
    base = tmp_path / "repo"
    (base / "resumes").mkdir(parents=True)
    shutil.copy(RESUME, base / "resumes" / "aarav-patel.json")
    (base / "fixtures" / "js2").mkdir(parents=True)
    return base


def file_bytes(path):
    path = pathlib.Path(path)
    return path.read_bytes() if path.exists() else None
