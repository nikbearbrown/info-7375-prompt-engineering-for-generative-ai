"""State file: load, integrity, cumulative seen set, pending queue (CONTRACT §10)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from job_search_agent.errors import StateCorrupt
from job_search_agent.fsio import OutputRoot
from job_search_agent.models import (
    JudgmentDiagnostic,
    JudgmentOutcome,
    JudgmentStatus,
    ModelEvidence,
    ModelJudgment,
    RawRef,
    SeenState,
)
from job_search_agent.privacy import scan_text, sensitive_values
from job_search_agent.state import (
    advance,
    drop_pending,
    parse_state,
    read_state_rel,
    sort_ids,
    state_to_bytes,
)
from tests.tools.builders import fixture_resume

T0 = datetime(2026, 10, 30, 0, 0, 0, tzinfo=UTC)
T1 = datetime(2026, 10, 31, 0, 5, 0, tzinfo=UTC)
RUN0 = "2026-10-30T00-00-00Z"
RUN1 = "2026-10-31T00-05-00Z"
RUN2 = "2026-11-01T00-05-00Z"
RAW = RawRef(path="data/live/runs/x/raw/greenhouse-stripe.json", sha256="a" * 64)


def ref(index: int) -> RawRef:
    return RawRef(path=RAW.path, sha256=RAW.sha256, index=index)


def outcome(pid: str, status: JudgmentStatus) -> JudgmentOutcome:
    if status is JudgmentStatus.VALID:
        judgment = ModelJudgment(
            status=status,
            label="RELEVANT",
            summary="s",
            evidence=[ModelEvidence(resume_path="$.a", posting_path="$.b", reason="r")],
        )
    else:
        judgment = ModelJudgment(
            status=status, diagnostic=JudgmentDiagnostic(unavailable_reason="x")
        )
    return JudgmentOutcome(pid, judgment)


def step(
    prior: SeenState | None,
    ids: set[str],
    run_id: str = RUN1,
    outcomes: dict[str, JudgmentOutcome] | None = None,
    sources: dict[str, RawRef] | None = None,
) -> SeenState:
    return advance(
        prior,
        valid_ids=ids,
        run_id=run_id,
        fetched_at=T1,
        run_started_at=T1,
        outcomes=outcomes or {},
        pending_sources=sources or {},
        provider="greenhouse",
        board="stripe",
        seeded=False,
    )


@pytest.fixture
def baseline() -> SeenState:
    return advance(
        None,
        valid_ids={"10", "2", "3"},
        run_id=RUN0,
        fetched_at=T0,
        run_started_at=T0,
        outcomes={},
        pending_sources={},
        provider="greenhouse",
        board="stripe",
        seeded=False,
    )


def test_absent_state_is_none(tmp_path: Path) -> None:
    assert read_state_rel("live/state.json", OutputRoot(tmp_path).read_bytes) is None


@pytest.mark.parametrize(
    ("content", "reason"),
    [
        (b"{not json", "not_json"),
        (b"\xff\xfe", "not_json"),
        (b"[]", "not_object"),
        (b"", "not_json"),
    ],
)
def test_corrupt_state_raises_not_baseline(
    tmp_path: Path, content: bytes, reason: str
) -> None:
    path = tmp_path / "state.json"
    path.write_bytes(content)
    with pytest.raises(StateCorrupt) as info:
        parse_state(path.read_bytes())
    assert info.value.reason == reason
    assert path.read_bytes() == content


def test_integrity_failure_raises(baseline: SeenState) -> None:
    obj = json.loads(state_to_bytes(baseline))
    obj["seen_ids"].append(obj["seen_ids"][0])
    with pytest.raises(StateCorrupt) as info:
        parse_state(json.dumps(obj).encode())
    assert info.value.reason == "integrity"


@pytest.mark.parametrize("version", [2, 0, "1", True, None])
def test_schema_version_mismatch_raises(baseline: SeenState, version: object) -> None:
    obj = json.loads(state_to_bytes(baseline))
    obj["schema_version"] = version
    with pytest.raises(StateCorrupt) as info:
        parse_state(json.dumps(obj).encode())
    assert info.value.reason == "schema_version"


def test_round_trip(baseline: SeenState) -> None:
    assert parse_state(state_to_bytes(baseline)) == baseline


def test_advance_unions_ids_cumulatively(baseline: SeenState) -> None:
    after = step(baseline, {"3", "4"})
    assert after.seen_ids == ["2", "3", "4", "10"]
    assert after.last_successful_run_id == RUN1
    assert after.last_successful_fetch_utc == T1


def test_disappeared_id_retained(baseline: SeenState) -> None:
    after = step(baseline, {"99"})
    assert {"2", "3", "10"} <= set(after.seen_ids)


def test_reappearing_id_not_new(baseline: SeenState) -> None:
    gone = step(baseline, {"3"})
    back = step(gone, {"2", "3", "10"}, run_id=RUN2)
    new = {"2", "3", "10"} - set(gone.seen_ids)
    assert new == set()
    assert back.seen_ids == gone.seen_ids


@pytest.mark.parametrize(
    "status",
    [JudgmentStatus.ERROR, JudgmentStatus.INVALID_OUTPUT, JudgmentStatus.UNAVAILABLE],
)
def test_pending_added_on(baseline: SeenState, status: JudgmentStatus) -> None:
    after = step(
        baseline, {"4"}, outcomes={"4": outcome("4", status)}, sources={"4": ref(0)}
    )
    assert [p.posting_id for p in after.pending] == ["4"]
    pending = after.pending[0]
    assert pending.last_status is status
    assert pending.attempts == 1
    assert pending.queued_run_id == RUN1
    assert pending.source == ref(0)


def test_pending_removed_only_on_valid(baseline: SeenState) -> None:
    queued = step(
        baseline,
        {"4"},
        outcomes={"4": outcome("4", JudgmentStatus.ERROR)},
        sources={"4": ref(5)},
    )
    still = step(
        queued, set(), run_id=RUN2, outcomes={"4": outcome("4", JudgmentStatus.ERROR)}
    )
    assert still.pending[0].attempts == 2
    assert still.pending[0].queued_run_id == RUN1
    assert still.pending[0].last_attempt_run_id == RUN2
    assert still.pending[0].source == ref(5)
    untouched = step(still, set(), run_id=RUN2)
    assert untouched.pending == still.pending
    done = step(
        still, set(), run_id=RUN2, outcomes={"4": outcome("4", JudgmentStatus.VALID)}
    )
    assert done.pending == []
    assert "4" in done.seen_ids


def test_new_pending_without_source_rejected(baseline: SeenState) -> None:
    with pytest.raises(ValueError):
        step(baseline, {"4"}, outcomes={"4": outcome("4", JudgmentStatus.ERROR)})


def test_outcome_for_unseen_id_rejected(baseline: SeenState) -> None:
    with pytest.raises(ValueError):
        step(baseline, set(), outcomes={"77": outcome("77", JudgmentStatus.VALID)})


def test_pending_drop_requires_reason_and_records_decision(baseline: SeenState) -> None:
    queued = step(
        baseline,
        {"4"},
        outcomes={"4": outcome("4", JudgmentStatus.UNAVAILABLE)},
        sources={"4": ref(1)},
    )
    with pytest.raises(ValueError):
        drop_pending(queued, "4", reason="   ", dropped_at=T1)
    with pytest.raises(KeyError):
        drop_pending(queued, "2", reason="not pending", dropped_at=T1)
    dropped = drop_pending(queued, "4", reason="posting withdrawn", dropped_at=T1)
    assert dropped.pending == []
    assert dropped.abandoned[0].posting_id == "4"
    assert dropped.abandoned[0].reason == "posting withdrawn"
    assert dropped.abandoned[0].last_status is JudgmentStatus.UNAVAILABLE
    assert "4" in dropped.seen_ids
    # an abandoned ID is not re-queued by later runs that do not judge it
    later = step(dropped, {"4"}, run_id=RUN2)
    assert later.pending == [] and later.abandoned == dropped.abandoned


def test_serialisation_deterministic(baseline: SeenState) -> None:
    a = step(baseline, {"5", "4", "11"})
    b = step(baseline, {"11", "5", "4"})
    assert state_to_bytes(a) == state_to_bytes(b)
    assert state_to_bytes(a).endswith(b"\n")
    assert sort_ids(["10", "9", "100", "9"]) == ["9", "10", "100"]


def test_state_contains_no_credentials_or_resume(
    baseline: SeenState, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-SECRET-0001")
    text = state_to_bytes(
        step(
            baseline,
            {"4"},
            outcomes={"4": outcome("4", JudgmentStatus.ERROR)},
            sources={"4": ref(0)},
        )
    ).decode()
    assert "sk-ant-test" not in text
    assert scan_text(text, sensitive_values(fixture_resume())) == []
    assert "/Users/" not in text
    assert set(json.loads(text)) == set(SeenState.model_fields)
