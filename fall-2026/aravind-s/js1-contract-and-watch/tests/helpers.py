"""Shared test doubles. Every board response built here is a CONSTRUCTED fixture, not real board data."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from job_agent.fetch import Response

REPO = Path(__file__).resolve().parent.parent
PERSONA = REPO / "persona" / "jane-doe.json"
BOARD = "https://api.ashbyhq.com/posting-api/job-board/openai"


def job(posting_id: str, title: str = "Software Engineer, Example Team", **extra) -> dict:
    data = {
        "id": posting_id,
        "title": title,
        "employmentType": "FullTime",
        "location": "San Francisco",
        "secondaryLocations": [],
        "address": {"postalAddress": {"addressCountry": "United States", "addressRegion": "California",
                                      "addressLocality": "San Francisco"}},
        "workplaceType": "Hybrid",
        "isListed": True,
        "jobUrl": f"https://jobs.ashbyhq.com/openai/{posting_id}",
        "descriptionPlain": "A constructed test posting.",
    }
    data.update(extra)
    return data


def board_bytes(jobs: list) -> bytes:
    return json.dumps({"_fixture": "CONSTRUCTED TEST FIXTURE, not a real board response", "apiVersion": "1",
                       "jobs": jobs}).encode("utf-8")


def response(body: bytes, status: int = 200) -> Response:
    return Response(url=BOARD, status=status, headers={"Content-Type": "application/json"}, body=body,
                    received_at="2026-10-30T00:00:00Z")


class FakeGet:
    """Stands in for fetch.get: hands out prepared responses and records every URL asked for."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.urls = []

    def __call__(self, url):
        self.urls.append(url)
        return self.responses.pop(0)


class Clock:
    """A clock that moves one hour per call, so every run gets its own run id."""

    def __init__(self, start=datetime(2026, 10, 30, 12, 0, 0, tzinfo=timezone.utc)):
        self.t = start

    def __call__(self):
        current = self.t
        self.t += timedelta(hours=1)
        return current


def stub_judge(job_data, resume, run_dir=None):
    """A judge double for watch tests: the real judges are tested on their own."""
    return {"rule": {"verdict": "relevant", "lines": ["stub rule verdict"]},
            "claude": {"verdict": "not_relevant", "lines": ["stub Claude verdict"]}}
