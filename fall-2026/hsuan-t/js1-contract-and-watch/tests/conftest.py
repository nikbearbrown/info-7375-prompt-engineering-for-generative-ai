"""Fixtures every test file uses: a temp output folder and the demo job seeker's criteria.

Paths(out=tmp_path) is what keeps tests from writing into the repo's submitted state/ runs/
evidence/ (they must contain only Isaac's two real runs); inputs still come from the repo.
"""

import pytest

from job_agent import inputs
from job_agent.common.paths import Paths
from job_agent.judges import claude_cli


@pytest.fixture(autouse=True)
def no_real_claude(monkeypatch):
    """Every test runs as if Claude Code isn't installed and no API key exists, so a test that
    forgets to pass a fake Claude gets an error verdict instead of a real (paid, slow) call."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(claude_cli, "find_claude", lambda: None)


@pytest.fixture
def paths(tmp_path) -> Paths:
    return Paths(out=tmp_path)


@pytest.fixture
def criteria(paths):
    """The shipped Aarav résumé + profile + built-in lists — the same inputs Run 1 and Run 2 use."""
    return inputs.load_criteria(paths.default_resume, paths.default_profile, paths)
