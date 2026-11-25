"""Fake board data, a fake network and a fake Claude for the tests, so no test ever touches the real
Stripe board, the Claude API, the repo's state/ runs/ evidence/ folders, or the internet.

Shared here (not copied into each test file) so every Wrong-version test builds postings the same
way the real Greenhouse API sends them: HTML escaped once inside "content", location under "name".
"""

import html
import json
from datetime import datetime, timedelta, timezone

from job_agent.common.paths import Paths
from job_agent.loop import runner
from job_agent.loop.budget import Budget
from job_agent.loop.trace import Trace
from job_agent.judges.claude import Reply
from job_agent.pipeline import run

# A posting the demo profile accepts at every check: target role, US location, a résumé skill
# (Java), 2 years (≤ 2 + 2), no "no sponsorship" phrase, no salary. Tests change one field at a
# time from here, so the check that cuts it is the one the test is about.
GOOD = {
    "title": "Backend Engineer, Payments",
    "location": "US-Remote",
    "content": "<p>You will build APIs in Java.</p><p>2+ years of experience.</p>",
}

# Cut at check 1a ("senior" is an exclude word) — the opposite verdict of GOOD.
SENIOR = {**GOOD, "title": "Senior Backend Engineer, Payments"}

START = datetime(2026, 10, 31, 12, 0, 0, tzinfo=timezone.utc)


def job(posting_id: int, title: str = GOOD["title"], location: str = GOOD["location"],
        content: str = GOOD["content"], offices: tuple[str, ...] = ()) -> dict:
    """One job as Greenhouse sends it: the JD's HTML arrives escaped (&lt;p&gt;), which strip_html must undo.
    offices: each office's full "location" text, as Greenhouse lists them under offices[] (JS2 D7)."""
    j = {"id": posting_id, "title": title, "location": {"name": location}, "content": html.escape(content)}
    if offices:
        j["offices"] = [{"id": i, "name": o.split(",")[0], "location": o} for i, o in enumerate(offices)]
    return j


def board(*jobs: dict) -> bytes:
    return json.dumps({"jobs": list(jobs), "meta": {"total": len(jobs)}}).encode()


def ashby_job(posting_id: str, title: str = GOOD["title"], location: str = GOOD["location"],
              content: str = GOOD["content"], secondary: tuple[str, ...] = (), country: str = "") -> dict:
    """One job as Ashby sends it (checked on openai, 2026-11-07): a UUID-style string id, a plain
    location string plus "secondaryLocations", and the JD as unescaped HTML in "descriptionHtml"."""
    j = {"id": posting_id, "title": title, "location": location,
         "secondaryLocations": [{"location": s} for s in secondary], "descriptionHtml": content}
    if country:
        j["address"] = {"postalAddress": {"addressLocality": location, "addressCountry": country}}
    return j


def ashby_board(*jobs: dict) -> bytes:
    """Ashby's envelope has no total count (unlike Greenhouse's meta.total)."""
    return json.dumps({"jobs": list(jobs), "apiVersion": "1"}).encode()


class FakeFetcher:
    """Stands in for net.http_get: returns a given body and remembers every URL it was asked for,
    so a test can prove a run stopped *before* fetching."""

    def __init__(self, body: bytes = b'{"jobs": []}'):
        self.body = body
        self.urls: list[str] = []

    def __call__(self, url: str) -> tuple[bytes, str]:
        self.urls.append(url)
        return self.body, "HTTP 200\nContent-Type: application/json\n"


def good_answer(posting: dict) -> dict:
    """A reply that passes every validator row: it quotes the title Claude was shown."""
    return {"posting_id": posting["posting_id"], "verdict": "relevant", "justification": [
        {"posting_field": "title", "compared_to": "profile.target_roles[]",
         "result": "a backend role", "quote": posting["title"]}]}


class FakeClaude:
    """Stands in for claude_api.make_ask(): answer(posting) builds the reply, so each test decides
    what "Claude" says; it also remembers which postings were sent (to check the test cap)."""

    def __init__(self, answer=good_answer, stop_reason: str = "end_turn"):
        self.answer = answer
        self.stop_reason = stop_reason
        self.sent: list[int] = []

    def __call__(self, system: str, user: str) -> Reply:
        posting = json.loads(user)["posting"]
        self.sent.append(posting["posting_id"])
        reply = self.answer(posting)
        text = reply if isinstance(reply, str) else json.dumps(reply)
        return Reply(text, self.stop_reason, {"model": "fake"})


def run_once(paths: Paths, body: bytes, n: int = 0, resume=None, profile=None, ask=None,
             board_name: str = "stripe", use_claude: bool = False) -> dict:
    """One full pipeline run on a fake board; returns the verdicts.json it wrote. Claude is off
    unless use_claude (the JS2 default, D1); when on, the fake Claude answers.

    n shifts the clock by n seconds because run folders are named by the second and the pipeline
    refuses two runs in the same second.
    """
    outcome = run(board_name, resume or paths.default_resume, profile or paths.default_profile, paths,
                  now=START + timedelta(seconds=n), fetcher=FakeFetcher(body), ask=ask or FakeClaude(),
                  use_claude=use_claude)
    return json.loads((outcome.folder / "verdicts.json").read_text())


def by_id(doc: dict, judge: str = "rule") -> dict[int, dict]:
    """One judge's verdicts by posting id; verdicts.json holds both judges' verdicts for each posting."""
    return {v["posting_id"]: v for v in doc["verdicts"] if v["judge"] == judge}


def one_board(paths: Paths, policy, board, fetcher, criteria=None, clock=None):
    """Run the loop on a single Board that need not be in data/boards.json (another slug, a fake
    adapter), and return its BoardResult plus the trace; for tests about one board's handling."""
    from job_agent import inputs
    clock = clock or (lambda: 0.0)
    criteria = criteria or inputs.load_criteria(paths.default_resume, paths.default_profile, paths)
    ctx = runner.Context(paths, policy, criteria, START, paths.raw("x"), Budget(clock=clock), Trace(clock),
                         fetcher=fetcher, clock=clock)
    [result], shared = runner.run_boards([board], ctx)
    assert shared is None
    return result, ctx.trace


def board_row(doc: dict, name: str = "stripe") -> dict:
    """One board's line from verdicts.json["boards"]."""
    return next(b for b in doc["boards"] if b["board"] == name)


class Clock:
    """A test clock: time moves only when a test (or a fetcher) says so."""

    def __init__(self):
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


class ScriptedFetcher:
    """A fake network with one script per URL: each request takes the next item (bytes = an HTTP
    200 body, an exception = that failure); the last item repeats. step advances the clock per
    request, so time budgets can be reached without waiting."""

    def __init__(self, script: dict, clock: Clock | None = None, step: float = 0.0):
        self.script = {url: list(items) for url, items in script.items()}
        self.clock, self.step = clock, step
        self.urls: list[str] = []

    def __call__(self, url: str) -> tuple[bytes, str]:
        self.urls.append(url)
        if self.clock:
            self.clock.now += self.step
        items = self.script[url]
        item = items.pop(0) if len(items) > 1 else items[0]
        if isinstance(item, BaseException):
            raise item
        return item, "HTTP 200\nContent-Type: application/json\n"
