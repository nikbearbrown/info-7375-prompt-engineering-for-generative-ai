"""Shared test fakes for JS1. Written with Claude in chat on 2026-10-29 (credited in SOURCES.md).

These fix the duck types behind the seam in CONTRACT.md Interfaces:
    cli.main(argv, *, opener=None, anthropic_client=None, now=None) -> int

- opener: has .open(request, timeout=...) like urllib's OpenerDirector. For a 2xx it returns a
  response with .status, .headers (.get) and .read(). For any other status it raises
  urllib.error.HTTPError, the way a real opener with redirects disabled does.
- anthropic_client: has .messages.create(**kwargs) returning an object with .id, .model,
  .stop_reason and .content = [obj with .type == "text" and .text].

No test touches the network. jobwatch is imported inside run_cli, so these tests are collected
and fail (red) until the implementation exists.
"""
import io
import json
import shutil
import urllib.error
from datetime import datetime, timezone
from email.message import Message
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
PERSONA = ROOT / "examples" / "persona_resume.json"
BOARD = "acme"
BOARD_URL = f"https://boards-api.greenhouse.io/v1/boards/{BOARD}/jobs?content=true"


def job(job_id, title, location="Boston, MA", content="", departments=()):
    """A constructed Greenhouse job object (fields as in the public Job Board API)."""
    return {
        "id": job_id,
        "title": title,
        "location": {"name": location} if location is not None else None,
        "absolute_url": f"https://job-boards.greenhouse.io/{BOARD}/jobs/{job_id}",
        "updated_at": "2026-10-29T12:00:00-04:00",
        "content": content,
        "departments": [{"id": i + 1, "name": d} for i, d in enumerate(departments)],
        "offices": [],
    }


def board_body(jobs):
    """Response body bytes for a board holding these jobs."""
    return json.dumps({"jobs": list(jobs), "meta": {"total": len(jobs)}}).encode("utf-8")


class FakeResponse:
    def __init__(self, status, body=b"", headers=None):
        self.status = status
        self._body = body
        msg = Message()
        for k, v in (headers or {}).items():
            msg[k] = v
        self.headers = msg

    def read(self):
        return self._body

    def getcode(self):
        return self.status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeOpener:
    """Serves responses by exact URL and records every request it receives."""

    def __init__(self, routes=None):
        self.routes = dict(routes or {})  # url -> (status, body_bytes, headers_dict)
        self.requests = []

    def open(self, request, timeout=None):
        url = request.full_url if hasattr(request, "full_url") else str(request)
        method = request.get_method() if hasattr(request, "get_method") else "GET"
        self.requests.append({"url": url, "method": method, "timeout": timeout})
        if url not in self.routes:
            raise AssertionError(f"unexpected request to {url}")
        status, body, headers = self.routes[url]
        if 200 <= status < 300:
            return FakeResponse(status, body, headers)
        hdrs = Message()
        for k, v in (headers or {}).items():
            hdrs[k] = v
        raise urllib.error.HTTPError(url, status, "fake", hdrs, io.BytesIO(body))


class FakeClient:
    """Stands in for anthropic.Anthropic(). `responder(kwargs) -> (text, stop_reason)`."""

    def __init__(self, responder, model="claude-sonnet-5-5"):
        self.calls = []
        self._responder = responder
        self._model = model
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        text, stop_reason = self._responder(kwargs)
        return SimpleNamespace(
            id=f"msg_fake_{len(self.calls)}",
            model=self._model,
            stop_reason=stop_reason,
            content=[SimpleNamespace(type="text", text=text)],
        )


FIXED_NOW = datetime(2026, 10, 29, 18, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    """A clean working directory holding a copy of the persona résumé and the prompts folder."""
    (tmp_path / "examples").mkdir()
    shutil.copy(PERSONA, tmp_path / "examples" / "persona_resume.json")
    if (ROOT / "prompts").is_dir():
        shutil.copytree(ROOT / "prompts", tmp_path / "prompts")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    return tmp_path


def run_cli(argv, opener=None, client=None, now=FIXED_NOW):
    """Call the seam. Returns the exit code."""
    from jobwatch import cli  # imported here so collection works before the code exists

    return cli.main(argv, opener=opener, anthropic_client=client, now=now)


def run_args(board=BOARD, resume="examples/persona_resume.json", extra=()):
    return ["run", "--board", board, "--resume", resume, *extra]


def latest_report(workdir):
    """The report.json of the most recent run under evidence/runs/."""
    runs = sorted((workdir / "evidence" / "runs").iterdir())
    return json.loads((runs[-1] / "report.json").read_text())
