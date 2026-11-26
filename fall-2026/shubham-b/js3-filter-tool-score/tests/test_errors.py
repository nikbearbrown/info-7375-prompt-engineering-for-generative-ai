"""The exception hierarchy and exit codes."""

from __future__ import annotations

import pytest

from job_search_agent.errors import (
    AgentError,
    ConfigError,
    HostNotAllowed,
    InvalidResponse,
    PathRejected,
    ResumeRefused,
    RunIdTaken,
    RunLocked,
    StateCorrupt,
)
from job_search_agent.models import ExitCode, RefusalCode


def test_resume_refused_lists_codes_only() -> None:
    exc = ResumeRefused([RefusalCode.EMAIL_DOMAIN, RefusalCode.DIGEST_MISMATCH])
    assert exc.codes == {RefusalCode.EMAIL_DOMAIN, RefusalCode.DIGEST_MISMATCH}
    assert str(exc) == "resume refused: DIGEST_MISMATCH, EMAIL_DOMAIN"
    assert exc.exit_code == ExitCode.RESUME_REFUSED


def test_resume_refused_requires_a_code() -> None:
    with pytest.raises(ValueError, match="at least one"):
        ResumeRefused([])


def test_path_rejected_message_omits_path() -> None:
    exc = PathRejected("absolute", "/Users/someone/secret")
    assert "/Users" not in str(exc)
    assert exc.path == "/Users/someone/secret"


def test_host_not_allowed_message_omits_url() -> None:
    exc = HostNotAllowed("evil.example", "host")
    assert "evil.example" in str(exc)
    assert "://" not in str(exc)


@pytest.mark.parametrize(
    ("exc", "code"),
    [
        (ConfigError("x"), ExitCode.CONFIG_ERROR),
        (StateCorrupt("not_json"), ExitCode.STATE_CORRUPT),
        (InvalidResponse("not_json"), ExitCode.FETCH_OR_RESPONSE),
        (HostNotAllowed("h", "scheme"), ExitCode.FETCH_OR_RESPONSE),
        (RunLocked("live/.lock"), ExitCode.LOCKED),
        (RunIdTaken("2026-10-30T02-11-07Z"), ExitCode.LOCKED),
    ],
)
def test_exit_codes(exc: AgentError, code: ExitCode) -> None:
    assert isinstance(exc, AgentError)
    assert exc.exit_code == code
