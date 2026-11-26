"""Swaps in one GATE §8 wrong version when ``JSA_JS2_WRONG`` names it (meta-test)."""

from __future__ import annotations

import importlib
import os
from pathlib import Path

import pytest

from tests.watch.harness import Project
from tests.wrong_versions.js2 import WRONG_VERSIONS


@pytest.fixture(autouse=True)
def _js2_wrong_version(monkeypatch: pytest.MonkeyPatch) -> None:
    name = os.environ.get("JSA_JS2_WRONG")
    if name:
        target, attr, replacement = WRONG_VERSIONS[name]
        owner = importlib.import_module(target) if isinstance(target, str) else target
        monkeypatch.setattr(owner, attr, replacement)


@pytest.fixture
def p(tmp_path: Path) -> Project:
    """A temporary project for one loop test."""
    return Project(tmp_path / "project")
