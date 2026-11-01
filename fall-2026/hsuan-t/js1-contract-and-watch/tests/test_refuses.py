"""CONTRACT Refuses #1 and #2 — the allow-list and the real-résumé guard.

Both must stop the run before anything leaves the machine or lands on disk, so each test checks
not only that an error is raised but that no request was made and no state/raw file was written.
(Refuses #3, judgment vs record, is Wrong version 5.)
"""

import json
import urllib.request
from datetime import datetime, timezone

import pytest
from fakes import FakeFetcher, START, board, job

from job_agent import inputs
from job_agent.common import net
from job_agent.common.errors import InputError, WatchError
from job_agent.pipeline import run
from job_agent.watch import watch
from job_agent.watch.boards import greenhouse


# ---- Refuses #1: hosts outside the allow-list -------------------------------------------------

@pytest.mark.parametrize("url", [
    "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true",
    "https://api.anthropic.com/v1/messages",
])
def test_allowed_hosts_pass(url):
    net.check_host(url)


@pytest.mark.parametrize("url", [
    "https://example.com/jobs",
    "https://boards-api.greenhouse.io.evil.com/v1/boards/stripe/jobs",   # look-alike suffix
    "https://boards-api.greenhouse.io@evil.com/v1/boards/stripe/jobs",   # host hidden as user name
    "https://evil.com/boards-api.greenhouse.io/",                        # allowed name only in the path
    "https://api.lever.co/v0/postings/stripe",                           # a real board, but not allowed
])
def test_refused_host_never_gets_a_request(url, monkeypatch):
    def no_network(*_, **__):
        raise AssertionError("urlopen was called for a refused host")
    monkeypatch.setattr(urllib.request, "urlopen", no_network)
    with pytest.raises(WatchError, match="not on allow-list"):
        net.http_get(url)


def test_watch_with_a_refused_board_url_writes_nothing(paths, monkeypatch):
    class EvilAdapter:
        board_url = staticmethod(lambda board: "https://evil.com/jobs")
        parse = staticmethod(greenhouse.parse)
    with pytest.raises(WatchError):
        watch("stripe", paths.state("stripe"), paths.raw("x"), datetime.now(timezone.utc), adapter=EvilAdapter)
    assert not paths.raw("x").exists() and not paths.state("stripe").exists()


# ---- Refuses #2: never a real résumé ----------------------------------------------------------

def _resume_with_email(paths, tmp_path, email):
    r = json.loads(paths.default_resume.read_text())
    r["basics"]["email"] = email
    p = tmp_path / "resume.json"
    p.write_text(json.dumps(r))
    return p


def test_shipped_persona_passes_the_guard(paths):
    assert inputs.load_resume(paths.default_resume)["basics"]["email"].endswith("@example.com")


@pytest.mark.parametrize("email", ["aarav.patel@gmail.com", "someone@northeastern.edu", "x@example.com.evil.io"])
def test_non_example_email_stops_before_fetching(paths, tmp_path, email):
    fetcher = FakeFetcher(board(job(1)))
    with pytest.raises(InputError, match="@example.com"):
        run("stripe", _resume_with_email(paths, tmp_path, email), paths.default_profile, paths,
            now=START, fetcher=fetcher)
    assert fetcher.urls == [] and not paths.state("stripe").exists()


def test_guard_ignores_email_case(paths, tmp_path):
    inputs.load_resume(_resume_with_email(paths, tmp_path, "Aarav.Patel@EXAMPLE.COM"))


def test_summary_never_prints_resume_contact_details(paths):
    basics = json.loads(paths.default_resume.read_text())["basics"]
    run("stripe", paths.default_resume, paths.default_profile, paths, now=START, fetcher=FakeFetcher(board(job(1))))
    outcome = run("stripe", paths.default_resume, paths.default_profile, paths,
                  now=START.replace(second=1), fetcher=FakeFetcher(board(job(1), job(2))))
    written = outcome.summary + (outcome.folder / "verdicts.json").read_text()
    for value in (basics["name"], basics["email"], basics["phone"]):
        assert value not in written


def test_gitignore_blocks_real_resume_files(paths):
    rules = {line.strip() for line in (paths.repo / ".gitignore").read_text().splitlines()}
    assert {"my_resume/", "*.pdf", ".env"} <= rules
