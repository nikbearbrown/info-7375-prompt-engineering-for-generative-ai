"""Shared fixtures.

The provider payloads in this file are **CONSTRUCTED EXAMPLES**, written by
hand to exercise one adapter behaviour each. They are not real responses, they
are not used in any run report, any count, or any evidence file, and they are
labelled here so nothing in the test suite can be mistaken for evidence about a
real board. The real saved responses live in `evidence/raw/`, with their
provenance in `evidence/PROVENANCE.md`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent import resume as resume_mod  # noqa: E402
from agent.policy import Policy  # noqa: E402


# --- CONSTRUCTED provider payloads -------------------------------------------

GREENHOUSE_OK = {
    "jobs": [
        {
            "id": 1001,
            "title": "Software Engineer, Ads Formats",
            "location": {"name": "Remote - United States"},
            "metadata": [
                {"name": "Position ID", "value": "P-1001"},
                {"name": "Job Family", "value": "Software Engineering"},
                {"name": "Management Level", "value": "IC3"},
            ],
            "absolute_url": "https://job-boards.greenhouse.io/constructed/jobs/1001",
        },
        {
            "id": 1002,
            "title": "Senior Software Engineer, Ads",
            "location": {"name": "Remote - United States"},
            "metadata": [{"name": "Job Family", "value": "Software Engineering"}],
            "absolute_url": "https://job-boards.greenhouse.io/constructed/jobs/1002",
        },
        {
            "id": 1003,
            "title": "Software Engineer, Data Platform",
            "location": {"name": "Remote - United States"},
            "metadata": [{"name": "Job Family", "value": None}],
            "absolute_url": "https://job-boards.greenhouse.io/constructed/jobs/1003",
        },
    ],
    "meta": {"total": 3},
}

LEVER_OK = [
    {
        "id": "lev-aaa",
        "text": "Software Engineer, Platform",
        "categories": {
            "location": "New York City, NY",
            "team": "Software Engineering",
            "department": "Engineering",
            "commitment": "Full time",
        },
        "hostedUrl": "https://jobs.lever.co/constructed/lev-aaa",
    },
    {
        "id": "lev-bbb",
        "text": "Account Executive, EMEA",
        "categories": {"location": "Amsterdam, Netherlands", "department": "Sales"},
        "hostedUrl": "https://jobs.lever.co/constructed/lev-bbb",
    },
    {
        "id": "lev-ccc",
        "text": "Software Engineer, Nothing Known",
        "categories": {"location": "Remote - United States"},
        "hostedUrl": "https://jobs.lever.co/constructed/lev-ccc",
    },
]

ASHBY_OK = {
    "jobs": [
        {
            "id": "ash-111",
            "title": "Machine Learning Engineer",
            "location": "Remote - United States",
            "department": "Machine Learning",
            "team": "Ranking",
            "isListed": True,
            "jobUrl": "https://jobs.ashbyhq.com/constructed/ash-111",
        },
        {
            "id": "ash-222",
            "title": "Software Engineer, Billing",
            "location": "Remote - Ontario, Canada",
            "department": "Software Engineering",
            "isListed": True,
            "jobUrl": "https://jobs.ashbyhq.com/constructed/ash-222",
        },
        {
            "id": "ash-333",
            "title": "Software Engineer, Hidden",
            "location": "New York City, NY",
            "department": "Software Engineering",
            "isListed": False,
            "jobUrl": "https://jobs.ashbyhq.com/constructed/ash-333",
        },
    ]
}

GREENHOUSE_EMPTY = {"jobs": [], "meta": {"total": 0}}


@pytest.fixture(scope="session")
def persona():
    return resume_mod.load(ROOT / "data" / "resume.persona.json")


@pytest.fixture
def project(tmp_path):
    """A throwaway project tree with the same shape as the real one."""
    (tmp_path / "config").mkdir()
    (tmp_path / "data").mkdir()
    (tmp_path / "evidence" / "raw").mkdir(parents=True)
    (tmp_path / "evidence" / "runs").mkdir(parents=True)
    (tmp_path / "evidence" / "state").mkdir(parents=True)
    (tmp_path / "evidence-evil").mkdir()  # the prefix trick's sibling
    (tmp_path / "data" / "resume.persona.json").write_text(
        (ROOT / "data" / "resume.persona.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / "config" / "budget.json").write_text(
        json.dumps({"boards": 6, "requests": 12, "seconds": 90, "retries_per_board": 2}),
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def policy(project):
    return Policy(
        project_root=project,
        output_root=(project / "evidence").resolve(),
    )


def write_plan(project, boards, name="boards.json"):
    path = project / "config" / name
    path.write_text(json.dumps({"plan_version": 1, "boards": boards}), encoding="utf-8")
    return path


def fetcher_from(mapping, *, failures=None):
    """A constructed fetcher: url -> payload, or url -> exception to raise.

    `failures` maps a url to a callable that raises; it is consulted first and
    may be stateful, which is how the flapping-board tests work.
    """
    failures = failures or {}

    def fetch(policy, url, *, timeout=20.0):
        policy.check_request("GET", url)
        if url in failures:
            failures[url]()
        if url not in mapping:
            from agent.errors import PermanentFailure

            raise PermanentFailure(f"constructed fetcher: HTTP 404 from {url}")
        return json.dumps(mapping[url]).encode("utf-8"), 200

    return fetch
