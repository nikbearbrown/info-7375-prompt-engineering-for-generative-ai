"""Fakes and fixtures for the JS2 tests.

Every board response in this file is CONSTRUCTED:
- Greenhouse jobs come from tests/helpers.job (JS1's fixture, whose keys and value
  types were checked against a live Greenhouse response on 2026-10-28).
- Ashby jobs copy the field set and value types of a live Ashby job (Linear's board,
  fetched 2026-11-08).
Nothing here sends a request. Every Approval passed to the code under test is a
SIMULATED approval fixture, not a decision by a person.
"""

import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from jobwatch import net
from tests.helpers import PERSONA_PATH, board_bytes, job

# Literal endpoints, written out by hand (not computed by the code under test).
ANTHROPIC_URL = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true"
DATABRICKS_URL = "https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true"
LINEAR_URL = "https://api.ashbyhq.com/posting-api/job-board/linear"
BAD_SLUG_URL = "https://boards-api.greenhouse.io/v1/boards/jobwatch-no-such-board-js2/jobs?content=true"

NORMAL = ["greenhouse/anthropic", "greenhouse/databricks", "ashby/linear"]
WITH_FAILURE_CONTROL = NORMAL + ["greenhouse/jobwatch-no-such-board-js2"]

GH_404_BODY = b'{"status":404,"error":"Job not found"}'
ASHBY_404_BODY = b"Not Found"


def greenhouse(*jobs):
    return board_bytes(*jobs)


def gh_job(job_id, title="Recruiting Coordinator", location="Dublin, IE",
           content="<p>Scheduling.</p>"):
    return job(job_id, title, location, content)


def ashby_job(uuid, title="Account Executive", location="Europe",
              html="<p>Sell things.</p>", board="linear"):
    """Same keys and value types as a live Ashby job (2026-11-08)."""
    return {
        "id": uuid,
        "title": title,
        "department": "Constructed",
        "team": "Constructed",
        "employmentType": "FullTime",
        "location": location,
        "secondaryLocations": [],
        "publishedAt": "2026-11-01T12:00:00.000+00:00",
        "isListed": True,
        "isRemote": False,
        "workplaceType": "Hybrid",
        "address": {"postalAddress": {"addressCountry": "Constructed"}},
        "jobUrl": f"https://jobs.ashbyhq.com/{board}/{uuid}",
        "applyUrl": f"https://jobs.ashbyhq.com/{board}/{uuid}/application",
        "descriptionHtml": html,
        "descriptionPlain": "Constructed.",
    }


def ashby(*jobs):
    return json.dumps({"apiVersion": "1", "jobs": list(jobs)}).encode("utf-8")


def ashby_url_key(uuid, board="linear"):
    return f"https://jobs.ashbyhq.com/{board}/{uuid}"


class FakeClock:
    """A monotonic clock that moves only when a fake request takes time."""

    def __init__(self, start=1000.0):
        self.t = start

    def __call__(self):
        return self.t

    def advance(self, seconds):
        self.t += seconds


@dataclass
class Reply:
    status: int = 200
    body: bytes = b""
    seconds: float = 0.25
    location: str | None = None
    content_type: str = "application/json; charset=utf-8"


@dataclass
class Fail:
    error: type = net.ConnectionFailed
    seconds: float = 0.25
    message: str = "connection reset (simulated)"


class FakeTransport:
    """Stands in for net.https_get, with the same contract: the whole response if it
    ends by the deadline; otherwise the clock reaches the deadline and net.Timeout is
    raised. Records every call. An unscripted URL fails the test."""

    def __init__(self, clock, script):
        self.clock = clock
        self.script = {url: (list(v) if isinstance(v, list) else [v]) for url, v in script.items()}
        self.calls = []

    def __call__(self, url, deadline):
        self.calls.append({"url": url, "deadline": deadline, "started": self.clock()})
        outcomes = self.script.get(url)
        if not outcomes:
            raise AssertionError(f"unscripted request to {url}")
        outcome = outcomes.pop(0) if len(outcomes) > 1 else outcomes[0]
        if self.clock() + outcome.seconds > deadline:
            self.clock.t = deadline
            raise net.Timeout("no complete response by the deadline (simulated)")
        self.clock.advance(outcome.seconds)
        if isinstance(outcome, Fail):
            raise outcome.error(outcome.message)
        return net.Response(outcome.status, outcome.body, outcome.content_type, outcome.location)

    def urls(self):
        return [c["url"] for c in self.calls]


class Project:
    """A disposable project folder laid out like the real one (persona/, later runs/ and
    state/). Its path is resolved, so macOS's /var -> /private/var link is not inside it."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name).resolve()
        self.root = self.base / "project"
        (self.root / "persona").mkdir(parents=True)
        shutil.copy(PERSONA_PATH, self.root / "persona" / "alex_morgan.json")

    def cleanup(self):
        self._tmp.cleanup()

    @property
    def state_path(self):
        return self.root / "state" / "state.json"

    def state_bytes(self):
        return self.state_path.read_bytes() if self.state_path.exists() else None

    def state(self):
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def run_dir(self, run_id):
        return self.root / "runs" / run_id

    def results(self, run_id):
        return json.loads((self.run_dir(run_id) / "results.json").read_text(encoding="utf-8"))

    def trace(self, run_id):
        return json.loads((self.run_dir(run_id) / "trace.json").read_text(encoding="utf-8"))
