"""Shared fixtures. The corpus is real; the constructed payloads say so."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inherited import resume as resume_mod  # noqa: E402
from jobfilter import corpus as corpus_mod  # noqa: E402
from jobfilter import pipeline  # noqa: E402


@pytest.fixture(scope="session")
def persona():
    return resume_mod.load(ROOT / "data" / "resume.persona.json")


@pytest.fixture(scope="session")
def postings():
    """The 452 real postings JS2 captured on 2026-11-11T00:18Z."""
    return corpus_mod.load()


@pytest.fixture(scope="session")
def decisions(postings, persona):
    return pipeline.run(postings, persona)


def make_posting(**kw):
    """A CONSTRUCTED posting. Never evidence about a real board."""
    base = dict(
        identity="constructed:1", board="ashby:constructed", provider="ashby",
        posting_id="1", title="Software Engineer, Backend",
        location="New York, NY", job_family="Engineering",
        url="https://example.com/1", body="We build APIs in Python.",
        body_fields=("descriptionPlain",), raw={},
    )
    base.update(kw)
    return corpus_mod.Posting(**base)
