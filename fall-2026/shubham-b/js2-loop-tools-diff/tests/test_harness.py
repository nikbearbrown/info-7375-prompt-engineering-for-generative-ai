"""The hermetic guards and the shared options and fixtures (PLAN §3)."""

from __future__ import annotations

import socket
import subprocess
import sys

import pytest

from tests.conftest import (
    RULE_IMPLS,
    NetworkBlockedError,
    RawHandcheck,
    SubprocessBlockedError,
)


def test_network_is_blocked() -> None:
    with pytest.raises(NetworkBlockedError):
        socket.create_connection(("example.com", 443))
    with socket.socket() as sock, pytest.raises(NetworkBlockedError):
        sock.connect(("127.0.0.1", 9))
    with pytest.raises(NetworkBlockedError):
        socket.getaddrinfo("example.com", 443)


def test_subprocess_is_blocked() -> None:
    with pytest.raises(SubprocessBlockedError):
        subprocess.run([sys.executable, "-c", "pass"], check=False)  # noqa: S603


@pytest.mark.subprocess
def test_subprocess_marker_lifts_guard() -> None:
    done = subprocess.run(  # noqa: S603
        [sys.executable, "-c", "print('ok')"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert done.stdout.strip() == "ok"


def test_rule_impl_option(rule_impl: str, request: pytest.FixtureRequest) -> None:
    assert rule_impl in RULE_IMPLS
    assert rule_impl == request.config.getoption("--rule-impl")


def test_raw_handcheck_fixture(raw_handcheck: RawHandcheck) -> None:
    assert raw_handcheck.meta["bytes"] == len(raw_handcheck.body)
    assert isinstance(raw_handcheck.data["jobs"], list)
