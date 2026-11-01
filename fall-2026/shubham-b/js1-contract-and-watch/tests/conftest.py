"""Shared pytest configuration: hermetic guards, options and fixtures (PLAN §3).

Guards (autouse):

* **No network.** ``socket.socket.connect``/``connect_ex``, ``socket.create_connection``
  and ``socket.getaddrinfo`` raise, in every test.
* **No subprocesses.** ``subprocess.Popen`` (and so ``run``/``check_output``),
  ``os.system``, ``os.posix_spawn[p]`` and ``os.fork`` raise. Lifted only for
  ``@pytest.mark.subprocess`` tests.

Option: ``--rule-impl={real,wrong_a,wrong_b}`` (the contract suite in
``tests/contract`` dispatches on the ``rule_impl`` fixture).
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, NoReturn

import pytest

from job_search_agent.fsio import OutputRoot
from job_search_agent.models import VerifiedResume
from job_search_agent.resume import load_verified_resume

REPO_ROOT = Path(__file__).resolve().parents[1]
RESUME_FIXTURE_REL = "persona/kiran-joshi.resume.example.json"
PINNED_RESUME_SHA256 = (
    "562a9d607213564c5291520f375ba69a7d407894c5803a995bad5b2d8f810532"
)
HANDCHECK_RAW_REL = "evidence/handcheck/stripe-jobs-2026-10-29T22-41-31Z.json"
HANDCHECK_META_REL = "evidence/handcheck/stripe-jobs-2026-10-29T22-41-31Z.meta.json"
FIXED_START = datetime(2026, 10, 30, 2, 11, 7, tzinfo=UTC)
RULE_IMPLS = ("real", "wrong_a", "wrong_b")


# --- options ----------------------------------------------------------------


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--rule-impl",
        choices=RULE_IMPLS,
        default="real",
        help="rule implementation the contract suite runs against",
    )


# --- guards -----------------------------------------------------------------


class NetworkBlockedError(RuntimeError):
    """Raised by the no-network guard."""


class SubprocessBlockedError(RuntimeError):
    """Raised by the no-subprocess guard."""


def _block_network(*_args: object, **_kwargs: object) -> NoReturn:
    raise NetworkBlockedError("network access is blocked in tests")


def _block_subprocess(*_args: object, **_kwargs: object) -> NoReturn:
    raise SubprocessBlockedError(
        "subprocesses are blocked in tests; mark the test @pytest.mark.subprocess"
    )


@pytest.fixture(autouse=True)
def _no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket.socket, "connect", _block_network)
    monkeypatch.setattr(socket.socket, "connect_ex", _block_network)
    monkeypatch.setattr(socket, "create_connection", _block_network)
    monkeypatch.setattr(socket, "getaddrinfo", _block_network)


@pytest.fixture(autouse=True)
def _no_subprocess(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    if request.node.get_closest_marker("subprocess"):
        return
    monkeypatch.setattr(subprocess, "Popen", _block_subprocess)
    for name in ("system", "posix_spawn", "posix_spawnp", "fork"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, _block_subprocess)


# --- fixtures ---------------------------------------------------------------


@dataclass(frozen=True)
class RawHandcheck:
    """The committed §13 raw response and its meta file."""

    rel_path: str
    body: bytes
    data: dict[str, Any]
    meta: dict[str, Any]


@pytest.fixture(scope="session")
def raw_handcheck() -> RawHandcheck:
    body = (REPO_ROOT / HANDCHECK_RAW_REL).read_bytes()
    meta = json.loads((REPO_ROOT / HANDCHECK_META_REL).read_text(encoding="utf-8"))
    return RawHandcheck(HANDCHECK_RAW_REL, body, json.loads(body), meta)


@pytest.fixture
def rule_impl(request: pytest.FixtureRequest) -> str:
    value: str = request.config.getoption("--rule-impl")
    return value


@pytest.fixture
def verified_resume() -> VerifiedResume:
    """The committed fixture, verified through the real résumé gate."""
    return load_verified_resume(
        REPO_ROOT / RESUME_FIXTURE_REL, PINNED_RESUME_SHA256, project_root=REPO_ROOT
    )


@pytest.fixture
def tmp_root(tmp_path: Path) -> OutputRoot:
    """An ``fsio.OutputRoot`` on ``tmp_path / "data"`` (created)."""
    root = tmp_path / "data"
    root.mkdir()
    return OutputRoot(root)
