"""Constructed responses, a fake clock and a fake network for the tests.

None of these postings are real. Every test runs offline in a temporary folder
laid out like this one (config/, persona/, jobs/).
"""

import html
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from agent.tools import FetchError, Response

FOLDER = Path(__file__).resolve().parent.parent
PERSONA = FOLDER / "persona" / "aarav-patel.resume.example.json"
FIXED_NOW = datetime(2026, 11, 10, 12, 0, 0, tzinfo=timezone.utc)

GH = "https://boards-api.greenhouse.io/v1/boards/%s/jobs?content=true"
LEVER = "https://api.lever.co/v0/postings/%s?mode=json"
ASHBY = "https://api.ashbyhq.com/posting-api/job-board/%s"

ANTHROPIC = {"system": "greenhouse", "board": "anthropic", "company": "Anthropic"}
PALANTIR = {"system": "lever", "board": "palantir", "company": "Palantir"}
LINEAR = {"system": "ashby", "board": "linear", "company": "Linear"}
MISSING = {"system": "greenhouse", "board": "js2-deliberately-missing-board", "company": "(deliberate failure)"}
THREE = [ANTHROPIC, PALANTIR, LINEAR]


def gh_job(job_id, title="Software Engineer", location="San Francisco, CA", body=""):
    return {"id": job_id, "title": title, "location": {"name": location}, "content": html.escape(body),
            "absolute_url": "https://job-boards.greenhouse.io/anthropic/jobs/%s" % job_id,
            "company_name": "Anthropic", "first_published": "2026-11-01T10:00:00-04:00"}


def gh_body(*jobs):
    return json.dumps({"jobs": list(jobs), "meta": {"total": len(jobs)}}).encode("utf-8")


def lever_job(job_id, title="Software Engineer", location="Palo Alto, CA", description="", lists=()):
    return {"id": job_id, "text": title, "categories": {"location": location},
            "description": description, "descriptionPlain": description,
            "lists": [{"text": heading, "content": content} for heading, content in lists],
            "additional": "", "hostedUrl": "https://jobs.lever.co/palantir/%s" % job_id}


def lever_body(*jobs):
    return json.dumps(list(jobs)).encode("utf-8")


def ashby_job(job_id, title="Software Engineer", location="San Francisco, CA", description="", secondary=()):
    return {"id": job_id, "title": title, "location": location, "descriptionHtml": description,
            "secondaryLocations": [{"location": s} for s in secondary],
            "jobUrl": "https://jobs.ashbyhq.com/linear/%s" % job_id, "isListed": True}


def ashby_body(*jobs):
    return json.dumps({"apiVersion": "1", "jobs": list(jobs)}).encode("utf-8")


def ok(body, headers=None):
    return Response(200, headers or {}, body)


def status(code, body=b"", headers=None):
    return Response(code, headers or {}, body)


class FakeClock:
    """Seconds since the run started. sleep() moves time forward instead of waiting."""

    def __init__(self):
        self.t = 0.0
        self.sleeps = []

    def __call__(self):
        return self.t

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.t += seconds


class FakeNet:
    """script maps a URL to the list of answers it gives, in order.

    An answer is a Response, a FetchError (raised), or (seconds, answer) to make
    that request take that many seconds on the fake clock.
    """

    def __init__(self, clock, script):
        self.clock = clock
        self.script = {url: list(answers) for url, answers in script.items()}
        self.calls = []

    def __call__(self, url, timeout, max_bytes):
        self.calls.append({"url": url, "timeout": timeout, "max_bytes": max_bytes})
        answers = self.script.get(url)
        if not answers:
            raise AssertionError("unexpected request: %s" % url)
        answer = answers.pop(0)
        if isinstance(answer, tuple):
            seconds, answer = answer
            self.clock.t += seconds
        if isinstance(answer, FetchError):
            raise answer
        return answer

    def urls(self):
        return [c["url"] for c in self.calls]


def make_root(testcase, boards, persona=PERSONA):
    """A temporary copy of this folder's layout, removed after the test."""
    root = Path(os.path.realpath(tempfile.mkdtemp(prefix="js2-test-")))
    testcase.addCleanup(shutil.rmtree, root, True)
    (root / "config").mkdir()
    (root / "config" / "boards.json").write_text(json.dumps({"boards": boards}), encoding="utf-8")
    (root / "persona").mkdir()
    shutil.copy(persona, root / "persona" / "aarav-patel.resume.example.json")
    (root / "jobs").mkdir()
    return root


def run_loop(root, net, clock, run_id="run-1", **kwargs):
    from agent.loop import run
    return run(root, transport=net, clock=clock, sleep=clock.sleep, now=FIXED_NOW, run_id=run_id, **kwargs)


def load_persona():
    return json.loads(PERSONA.read_text(encoding="utf-8"))


def board(record, key):
    return next(b for b in record["boards"] if b["key"] == key)
