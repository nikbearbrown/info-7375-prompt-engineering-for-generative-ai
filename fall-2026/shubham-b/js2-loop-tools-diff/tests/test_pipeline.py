"""Orchestration: ``pipeline.run_once`` end to end (PLAN §3.4).

Every collaborator is the real module (``tests/pipeline_harness.py``): provider, rule,
evidence validator, résumé gate, ``OutputRoot``, allow-listed fetcher and judge; only
the model replies (``FakeBackend``) and git are scripted. Response variants are built
in memory from the committed hand-check bytes; every such variant is CONSTRUCTED and
is never written to ``evidence/``.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from job_search_agent.errors import (
    ConfigError,
    PathRejected,
    ResumeRefused,
    RunIdTaken,
    RunLocked,
    StateCorrupt,
)
from job_search_agent.fsio import OutputRoot
from job_search_agent.judge.payload import PayloadError
from job_search_agent.judge.validator import RejectionCode
from job_search_agent.models import (
    BackendErrorKind,
    ExitCode,
    FetchErrorKind,
    JudgmentOutcome,
    JudgmentStatus,
    OutputRecord,
    Posting,
    RefusalCode,
    RunReport,
    RunStatus,
    SeenState,
    SourceKind,
    SourceResult,
    VerifiedResume,
)
from job_search_agent.pipeline import run_once
from job_search_agent.report import render_runs_markdown
from job_search_agent.state import parse_state
from tests.conftest import FIXED_START, HANDCHECK_RAW_REL
from tests.fakes import FakeBackend, FixedClock, Reply
from tests.pipeline_harness import (
    CONSTRUCTED_ID,
    JOBS_URL,
    VALID_REPLY,
    Harness,
    InjectingRoot,
    constructed_with_added_posting,
    constructed_without,
    handcheck_body,
)

BODY = handcheck_body()
NEW_ID = str(CONSTRUCTED_ID)
LIVE_STATE = "live/state.json"
SEEDED_STATE = "seeded/state.json"


@pytest.fixture
def h(tmp_path: Path) -> Harness:
    return Harness.create(tmp_path)


def live(h: Harness, body: bytes = BODY, status: int = 200) -> RunReport:
    reply = Reply(
        status=status, body=body, headers={"content-type": "application/json"}
    )
    return run_once(h.deps(h.live_source(reply)))


def added(title: str = "Software Engineer, Constructed") -> bytes:
    return constructed_with_added_posting(BODY, title=title)


def records(h: Harness, report: RunReport, name: str = "records.json") -> list[Any]:
    path = h.run_dir(report.run_id, seeded=report.seeded) / name
    data: list[Any] = json.loads(path.read_text())
    return data


def state(h: Harness, rel: str = LIVE_STATE) -> SeenState:
    return parse_state(h.data(rel).read_bytes())


def valid_ids(body: bytes) -> list[str]:
    return [str(j["id"]) for j in json.loads(body)["jobs"]]


# --- baseline -------------------------------------------------------------------


def test_first_run_is_baseline_with_new_count_zero_and_no_judgments(h: Harness) -> None:
    report = live(h)
    assert report.status is RunStatus.BASELINE
    assert report.new_count == 0 and report.new_ids == []
    assert h.backend.calls == 0
    assert report.judgment_counts == {}
    assert records(h, report) == []
    assert records(h, report, "retried.json") == []
    assert not (h.run_dir(report.run_id) / "model").exists()


def test_baseline_reports_fetched_unique_and_state_saved(h: Harness) -> None:
    report = live(h)
    ids = valid_ids(BODY)
    assert report.fetched_count == len(json.loads(BODY)["jobs"])
    assert report.unique_valid_ids == len(set(ids))
    assert report.state_saved is True
    saved = state(h)
    assert set(saved.seen_ids) == set(ids)
    assert saved.pending == [] and saved.seeded is False
    run = h.run_dir(report.run_id)
    assert json.loads((run / "state.before.json").read_text()) is None
    assert (run / "state.after.json").read_bytes() == h.data(LIVE_STATE).read_bytes()
    assert "baseline" in (run / "report.md").read_text().lower()


# --- later runs -----------------------------------------------------------------


def test_second_run_same_response_success_no_new(h: Harness) -> None:
    live(h)
    before = h.data(LIVE_STATE).read_bytes()
    report = live(h)
    assert report.status is RunStatus.SUCCESS_NO_NEW
    assert report.new_count == 0
    assert h.backend.calls == 0
    run = h.run_dir(report.run_id)
    assert (run / "state.before.json").read_bytes() == before
    assert state(h).seen_ids == parse_state(before).seen_ids


def test_second_run_with_added_posting_success_with_new_judges_only_new(
    h: Harness,
) -> None:
    live(h)
    h.set_backend(FakeBackend([VALID_REPLY]))
    report = live(h, added())
    assert report.status is RunStatus.SUCCESS_WITH_NEW
    assert report.new_ids == [NEW_ID]
    assert h.backend.calls == 1
    assert "Software Engineer, Constructed" in h.backend.prompts[0]
    (record,) = records(h, report)
    assert record["posting_id"] == NEW_ID
    assert record["model_judgment"]["status"] == "VALID"
    assert list(record) == [
        "posting_id",
        "title",
        "location",
        "updated_at",
        "rule_verdict",
        "model_judgment",
        "rule_evidence_errors",
    ]
    assert list(record["rule_verdict"])[:4] == [
        "label",
        "location_check",
        "evidence",
        "reason",
    ]
    assert state(h).pending == []
    assert NEW_ID in state(h).seen_ids


# --- failures keep state --------------------------------------------------------


def test_fetch_failed_preserves_state_bytes(h: Harness) -> None:
    live(h)
    before = h.data(LIVE_STATE).read_bytes()
    report = run_once(h.deps(h.failing_source()))
    assert report.status is RunStatus.FETCH_FAILED
    assert report.fetch_error is FetchErrorKind.TRANSPORT
    assert report.fetched_count is None and report.raw_evidence is None
    assert h.data(LIVE_STATE).read_bytes() == before
    run = h.run_dir(report.run_id)
    assert not (run / "state.after.json").exists()
    assert not (run / "records.json").exists()
    assert (run / "report.json").exists()
    for status in (404, 429, 500):
        report = live(h, b"error page", status=status)
        assert report.status is RunStatus.FETCH_FAILED
        assert report.http_status == status
        assert h.data(LIVE_STATE).read_bytes() == before


def test_empty_response_preserves_state_and_is_not_success_no_new(h: Harness) -> None:
    live(h)
    before = h.data(LIVE_STATE).read_bytes()
    report = live(h, b'{"jobs": [], "meta": {"total": 0}}')
    assert report.status is RunStatus.EMPTY_RESPONSE
    assert report.fetched_count == 0
    assert h.data(LIVE_STATE).read_bytes() == before


@pytest.mark.parametrize(
    "body",
    [
        b"<html>not json</html>",
        b'{"jobs": {}}',
        b"[]",
        b'{"jobs": [{}], "meta": {"total": 1}}',
    ],
)
def test_invalid_response_preserves_state(h: Harness, body: bytes) -> None:
    live(h)
    before = h.data(LIVE_STATE).read_bytes()
    report = live(h, body)
    assert report.status is RunStatus.INVALID_RESPONSE
    assert report.fetched_count is None
    assert h.data(LIVE_STATE).read_bytes() == before


def test_empty_first_run_creates_no_baseline(h: Harness) -> None:
    report = live(h, b'{"jobs": [], "meta": {"total": 0}}')
    assert report.status is RunStatus.EMPTY_RESPONSE
    assert not h.data(LIVE_STATE).exists()
    report = live(h, b"not json")
    assert report.status is RunStatus.INVALID_RESPONSE
    assert not h.data(LIVE_STATE).exists()
    assert live(h).status is RunStatus.BASELINE


# --- judgment failures ----------------------------------------------------------


def test_model_error_partial_failure_and_pending(h: Harness) -> None:
    live(h)
    h.set_backend(FakeBackend([BackendErrorKind.TIMEOUT]))
    report = live(h, added())
    assert report.status is RunStatus.PARTIAL_FAILURE
    assert report.judgment_counts == {JudgmentStatus.ERROR: 1}
    assert report.unresolved_pending_ids == [NEW_ID]
    (pending,) = state(h).pending
    assert pending.posting_id == NEW_ID
    assert pending.last_status is JudgmentStatus.ERROR
    assert pending.source.index == len(json.loads(added())["jobs"]) - 1
    (record,) = records(h, report)
    assert record["rule_verdict"]["label"] in ("MATCH", "NO_MATCH")
    assert h.backend.calls == 1  # ERROR is not retried within the run


@pytest.mark.parametrize("judge_none", [False, True])
def test_model_unavailable_partial_failure_and_pending(
    h: Harness, judge_none: bool
) -> None:
    live(h)
    h.set_backend(FakeBackend(available=False, unavailable_reason="cli_not_found"))
    report = run_once(
        h.deps(h.live_source(Reply(body=added())), use_judge=not judge_none)
    )
    assert report.status is RunStatus.PARTIAL_FAILURE
    assert report.judgment_counts == {JudgmentStatus.UNAVAILABLE: 1}
    (record,) = records(h, report)
    judgment = record["model_judgment"]
    assert judgment["status"] == "UNAVAILABLE" and judgment["label"] is None
    expected = "backend_none" if judge_none else "cli_not_found"
    assert judgment["diagnostic"]["unavailable_reason"] == expected
    assert state(h).pending[0].last_status is JudgmentStatus.UNAVAILABLE
    assert h.backend.calls == 0


def test_invalid_output_twice_recorded_and_raw_kept_separately(h: Harness) -> None:
    live(h)
    marker1 = "RAW-REPLY-ONE prose before {"
    marker2 = '```json\n{"label": "RELEVANT"}\n``` RAW-REPLY-TWO'
    h.set_backend(FakeBackend([marker1, marker2]))
    report = live(h, added())
    assert report.status is RunStatus.PARTIAL_FAILURE
    (record,) = records(h, report)
    judgment = record["model_judgment"]
    assert judgment["status"] == "INVALID_OUTPUT"
    assert judgment["label"] is None and judgment["summary"] is None
    text = (h.run_dir(report.run_id) / "records.json").read_text()
    assert "RAW-REPLY-ONE" not in text and "RAW-REPLY-TWO" not in text
    model_dir = h.run_dir(report.run_id) / "model" / NEW_ID
    assert "RAW-REPLY-ONE" in (model_dir / "attempt-1.json").read_text()
    assert "RAW-REPLY-TWO" in (model_dir / "attempt-2.json").read_text()
    refs = [a["raw_log_ref"] for a in judgment["diagnostic"]["attempts"]]
    assert refs == [
        f"data/live/runs/{report.run_id}/model/{NEW_ID}/attempt-1.json",
        f"data/live/runs/{report.run_id}/model/{NEW_ID}/attempt-2.json",
    ]
    assert state(h).pending[0].last_status is JudgmentStatus.INVALID_OUTPUT


# --- pending retries ------------------------------------------------------------


def queue_pending(h: Harness) -> RunReport:
    live(h)
    h.set_backend(FakeBackend([BackendErrorKind.NONZERO_EXIT]))
    report = live(h, added())
    assert state(h).pending[0].posting_id == NEW_ID
    return report


def test_pending_retried_next_run_even_when_not_new(h: Harness) -> None:
    queue_pending(h)
    h.set_backend(FakeBackend([VALID_REPLY]))
    report = live(h, added())
    assert report.new_count == 0
    assert report.retried_pending_ids == [NEW_ID]
    assert report.status is RunStatus.SUCCESS_NO_NEW
    assert state(h).pending == []
    (retried,) = records(h, report, "retried.json")
    assert retried["model_judgment"]["status"] == "VALID"
    assert records(h, report) == []


def test_pending_retry_failure_with_no_new_is_partial_failure(h: Harness) -> None:
    queue_pending(h)
    h.set_backend(FakeBackend([BackendErrorKind.IS_ERROR]))
    report = live(h, added())
    assert report.new_count == 0
    assert report.status is RunStatus.PARTIAL_FAILURE
    (pending,) = state(h).pending
    assert pending.attempts == 2
    assert pending.last_attempt_run_id == report.run_id


def test_pending_posting_missing_from_board_uses_saved_raw(h: Harness) -> None:
    queued = queue_pending(h)
    h.set_backend(FakeBackend([VALID_REPLY]))
    report = live(h, BODY)  # the constructed posting is gone from the board
    assert report.retried_pending_ids == [NEW_ID]
    assert report.status is RunStatus.SUCCESS_NO_NEW
    (retried,) = records(h, report, "retried.json")
    assert retried["posting_id"] == NEW_ID
    assert retried["title"] == "Software Engineer, Constructed"
    retry_events = [e for e in h.events[-1].events if e["event"] == "pending.retry"]
    assert retry_events == [
        {
            "seq": retry_events[0]["seq"],
            "event": "pending.retry",
            "posting_id": NEW_ID,
            "posting_from": "saved_raw",
        }
    ]
    assert queued.raw_evidence is not None


def test_pending_saved_raw_tampered_stays_pending(h: Harness) -> None:
    queued = queue_pending(h)
    assert queued.raw_evidence is not None
    raw = h.root / queued.raw_evidence.path
    raw.write_bytes(raw.read_bytes() + b" ")
    report = live(h, BODY)
    assert report.retried_pending_ids == []
    assert report.unresolved_pending_ids == [NEW_ID]
    assert report.status is RunStatus.PARTIAL_FAILURE
    assert "pending_source_unavailable" in report.notes


# --- aborts and write failures --------------------------------------------------


def test_state_save_failure_reports_state_saved_false(h: Harness) -> None:
    live(h)
    before = h.data(LIVE_STATE).read_bytes()
    failing = InjectingRoot(h.config.data_dir, fail_writes={LIVE_STATE})
    h.set_backend(FakeBackend([VALID_REPLY]))
    report = run_once(h.deps(h.live_source(Reply(body=added())), out=failing))
    assert report.state_saved is False
    assert report.status is RunStatus.PARTIAL_FAILURE
    assert "state_not_saved" in report.notes
    assert h.data(LIVE_STATE).read_bytes() == before
    assert not (h.run_dir(report.run_id) / "state.after.json").exists()


def test_baseline_state_save_failure_is_partial(tmp_path: Path) -> None:
    h = Harness.create(tmp_path)
    failing = InjectingRoot(h.config.data_dir, fail_writes={LIVE_STATE})
    report = run_once(h.deps(h.live_source(Reply(body=BODY)), out=failing))
    assert report.status is RunStatus.PARTIAL_FAILURE
    assert "baseline_state_not_saved" in report.notes
    assert not h.data(LIVE_STATE).exists()


def test_records_write_failure_skips_state_save(h: Harness) -> None:
    live(h)
    before = h.data(LIVE_STATE).read_bytes()
    h.set_backend(FakeBackend([VALID_REPLY]))
    failing = InjectingRoot(h.config.data_dir, fail_writes={"records.json"})
    report = run_once(h.deps(h.live_source(Reply(body=added())), out=failing))
    assert report.records_saved is False and report.state_saved is False
    assert report.status is RunStatus.PARTIAL_FAILURE
    assert h.data(LIVE_STATE).read_bytes() == before  # next run re-reports


def test_write_order_records_state_report(h: Harness) -> None:
    live(h)
    recorder = InjectingRoot(h.config.data_dir)
    h.set_backend(FakeBackend([VALID_REPLY]))
    run_once(h.deps(h.live_source(Reply(body=added())), out=recorder))
    order = [rel.rsplit("/", 1)[-1] for rel in recorder.writes]
    assert order.index("records.json") < order.index("state.json")
    assert order.index("retried.json") < order.index("state.json")
    assert order.index("state.json") < order.index("report.json")


def test_corrupt_state_aborts_before_fetch(h: Harness) -> None:
    path = h.data(LIVE_STATE)
    path.parent.mkdir(parents=True)
    path.write_bytes(b'{"schema_version": 1, "seen_ids": "oops"}')
    source = h.live_source(Reply(body=BODY))
    with pytest.raises(StateCorrupt):
        run_once(h.deps(source))
    assert h.transports[-1].requests == []
    assert path.read_bytes() == b'{"schema_version": 1, "seen_ids": "oops"}'
    assert not h.data("live/runs").exists()


def test_refused_resume_aborts_before_fetch_and_model(h: Harness) -> None:
    def refuse() -> VerifiedResume:
        raise ResumeRefused([RefusalCode.DIGEST_MISMATCH])

    h.set_backend(FakeBackend([VALID_REPLY]))
    source = h.live_source(Reply(body=BODY))
    with pytest.raises(ResumeRefused):
        run_once(h.deps(source, load_resume=refuse))
    assert h.transports[-1].requests == []
    assert h.backend.calls == 0
    assert list(h.config.data_dir.iterdir()) == []


# --- replay (seeded) ------------------------------------------------------------


def test_replay_labels_seeded_everywhere(h: Harness) -> None:
    report = run_once(h.deps(h.replay_source(), seeded=True))
    assert report.status is RunStatus.BASELINE
    # 1. folder and 2. run-id suffix
    assert report.run_id.endswith("-SEEDED")
    run = h.run_dir(report.run_id, seeded=True)
    assert run.is_dir() and run.parent.parent.name == "seeded"
    # 3. seeded/source in the meta pointer and report.json
    pointer = json.loads((run / "raw" / "REPLAYED_FROM.json").read_text())
    assert pointer["seeded"] is True and pointer["source"] == "replay"
    assert pointer["path"] == HANDCHECK_RAW_REL
    assert pointer["sha256"] == hashlib.sha256(BODY).hexdigest()
    assert pointer["original_fetched_at_utc"] == "2026-10-29T22:41:31+00:00"
    report_json = json.loads((run / "report.json").read_text())
    assert report_json["seeded"] is True and report_json["mode"] == "replay"
    assert "seeded_replay_no_network" in report_json["notes"]
    # 4. report.md banner and 5. terminal banner
    banner = (
        f"> SEEDED RUN — replayed from saved file {HANDCHECK_RAW_REL} "
        f"(sha256 {hashlib.sha256(BODY).hexdigest()}, originally fetched "
        "2026-10-29T22:41:31+00:00). No network request was made."
    )
    assert (run / "report.md").read_text().splitlines()[0] == banner
    assert h.terminal_lines[-1].splitlines()[0] == banner
    # 6. RUNS.md has a separate seeded table
    runs_md = render_runs_markdown([report])
    seeded_part = runs_md.split("## Seeded runs")[1]
    assert report.run_id in seeded_part
    assert report.run_id not in runs_md.split("## Seeded runs")[0]
    # the seeded state records the original fetch time
    seeded = state(h, SEEDED_STATE)
    assert seeded.seeded is True
    assert seeded.last_successful_fetch_utc.isoformat() == "2026-10-29T22:41:31+00:00"
    assert seeded.run_started_at_utc == report.started_at_utc
    assert not (run / "raw" / "greenhouse-stripe.json").exists()


def test_replay_makes_no_network_request(h: Harness) -> None:
    report = run_once(h.deps(h.replay_source(), seeded=True))
    assert report.status is RunStatus.BASELINE
    assert h.transports == []
    names = [e["event"] for e in h.events[-1].events]
    assert not any(str(n).startswith("http.") for n in names)
    second = run_once(h.deps(h.replay_source(), seeded=True))
    assert second.status is RunStatus.SUCCESS_NO_NEW


def test_replay_verifies_sha256(h: Harness) -> None:
    raw = h.root / HANDCHECK_RAW_REL
    raw.write_bytes(raw.read_bytes().replace(b"Stripe", b"Strype", 1))
    report = run_once(h.deps(h.replay_source(), seeded=True))
    assert report.status is RunStatus.FETCH_FAILED
    assert report.fetch_error is FetchErrorKind.REPLAY_DIGEST_MISMATCH
    assert not h.data(SEEDED_STATE).exists()
    pointer = json.loads(
        (
            h.run_dir(report.run_id, seeded=True) / "raw" / "REPLAYED_FROM.json"
        ).read_text()
    )
    assert pointer["verified"] is False


def test_live_and_seeded_state_are_separate(h: Harness) -> None:
    live(h)
    live_before = h.data(LIVE_STATE).read_bytes()
    seeded_report = run_once(h.deps(h.replay_source(), seeded=True))
    assert seeded_report.status is RunStatus.BASELINE  # its own baseline
    assert h.data(LIVE_STATE).read_bytes() == live_before
    seeded_before = h.data(SEEDED_STATE).read_bytes()
    h.set_backend(FakeBackend([VALID_REPLY]))
    assert live(h, added()).status is RunStatus.SUCCESS_WITH_NEW
    assert h.data(SEEDED_STATE).read_bytes() == seeded_before
    assert not list(h.data("live/runs").glob("*-SEEDED"))
    assert all(p.name.endswith("-SEEDED") for p in h.data("seeded/runs").iterdir())


def test_seeded_flag_mismatch_in_state_is_corrupt(h: Harness) -> None:
    live(h)
    target = h.data(SEEDED_STATE)
    target.parent.mkdir(parents=True)
    target.write_bytes(h.data(LIVE_STATE).read_bytes())
    with pytest.raises(StateCorrupt):
        run_once(h.deps(h.replay_source(), seeded=True))


def test_replay_source_with_live_flag_refused(h: Harness) -> None:
    with pytest.raises(ConfigError):
        run_once(h.deps(h.replay_source(), seeded=False))
    assert not h.data(LIVE_STATE).exists()


# --- evidence and output hygiene ------------------------------------------------


def test_raw_saved_byte_for_byte_with_sha256(h: Harness) -> None:
    report = live(h)
    run = h.run_dir(report.run_id)
    raw = run / "raw" / "greenhouse-stripe.json"
    assert raw.read_bytes() == BODY
    meta = json.loads((run / "raw" / "greenhouse-stripe.meta.json").read_text())
    digest = hashlib.sha256(BODY).hexdigest()
    assert meta["sha256"] == digest and meta["bytes"] == len(BODY)
    assert meta["seeded"] is False and meta["source"] == "network"
    assert meta["url"] == JOBS_URL and meta["http_status"] == 200
    assert meta["code_commit"] == "a" * 40
    assert report.raw_evidence is not None
    assert report.raw_evidence.sha256 == digest
    assert report.raw_evidence.path == (
        f"data/live/runs/{report.run_id}/raw/greenhouse-stripe.json"
    )
    # an HTTP error body is evidence too
    error_body = b"<html>503 Service Unavailable</html>"
    failed = live(h, error_body, status=503)
    assert failed.status is RunStatus.FETCH_FAILED
    frun = h.run_dir(failed.run_id)
    assert (frun / "raw" / "greenhouse-stripe.json").read_bytes() == error_body
    fmeta = json.loads((frun / "raw" / "greenhouse-stripe.meta.json").read_text())
    assert fmeta["sha256"] == hashlib.sha256(error_body).hexdigest()
    assert fmeta["http_status"] == 503
    assert fmeta["fetch_error"] == "HTTP_STATUS"


def full_cycle(h: Harness) -> None:
    live(h)
    h.set_backend(FakeBackend([VALID_REPLY]))
    live(h, added())
    run_once(h.deps(h.replay_source(), seeded=True))


def test_outputs_contain_no_resume_content(h: Harness) -> None:
    full_cycle(h)
    assert h.privacy_findings() == []
    assert "Kiran" not in h.all_output_text()


def test_outputs_contain_no_absolute_paths(h: Harness) -> None:
    full_cycle(h)
    text = h.all_output_text()
    assert str(h.root) not in text
    assert "/Users/" not in text and "/home/" not in text


def test_outputs_contain_no_credentials(
    h: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    secret = "sk-ant-test-0123456789-SECRET"  # noqa: S105 - fake credential
    monkeypatch.setenv("ANTHROPIC_API_KEY", secret)
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", secret + "-auth")
    full_cycle(h)
    assert "sk-ant-test" not in h.all_output_text()


def test_every_record_passes_evidence_validator(h: Harness) -> None:
    live(h)
    h.set_backend(FakeBackend([VALID_REPLY]))
    report = live(h, added())
    recs = [OutputRecord.model_validate(r) for r in records(h, report)]
    assert recs and all(r.rule_evidence_errors == [] for r in recs)
    assert recs[0].rule_verdict.evidence  # the constructed posting has skills


def test_rule_evidence_failure_flags_record_and_partial(h: Harness) -> None:
    live(h)
    h.set_backend(FakeBackend([VALID_REPLY]))
    report = run_once(
        h.deps(
            h.live_source(Reply(body=added())),
            validate=lambda verdict, raw, resume: ["constructed_failure"],
        )
    )
    assert report.status is RunStatus.PARTIAL_FAILURE
    assert "rule_evidence_errors" in report.notes
    (record,) = records(h, report)
    assert record["rule_evidence_errors"] == ["constructed_failure"]


def test_data_quality_errors_partial_on_later_runs_only(h: Harness) -> None:
    obj = json.loads(BODY)
    obj["jobs"].append({"id": "not-an-int", "title": "x"})
    bad = json.dumps(obj).encode()
    first = live(h, bad)
    assert first.status is RunStatus.BASELINE
    assert first.data_quality_issues
    second = live(h, bad)
    assert second.status is RunStatus.PARTIAL_FAILURE
    assert "data_quality_errors" in second.notes


def test_duplicate_id_is_a_data_quality_error(h: Harness) -> None:
    obj = json.loads(BODY)
    obj["jobs"].append(dict(obj["jobs"][0]))  # the same posting ID twice
    obj["meta"]["total"] = len(obj["jobs"])
    doubled = json.dumps(obj).encode()
    first = live(h, doubled)
    assert first.status is RunStatus.BASELINE
    assert [i.code.value for i in first.data_quality_issues] == ["DUPLICATE_ID"]
    assert first.unique_valid_ids == len(set(valid_ids(BODY)))
    second = live(h, doubled)
    assert second.status is RunStatus.PARTIAL_FAILURE
    assert "data_quality_errors" in second.notes
    assert second.new_count == 0  # the duplicate is not a new posting


def test_reply_echoing_a_resume_value_is_rejected_r10(h: Harness) -> None:
    live(h)
    bullet = h.resume().to_dict()["experience"][0]["bullets"][0]
    echo = json.dumps({**json.loads(VALID_REPLY), "summary": f"Fits: {bullet}"})
    h.set_backend(FakeBackend([echo, echo]))
    report = live(h, added())
    assert report.status is RunStatus.PARTIAL_FAILURE
    (record,) = records(h, report)
    judgment = record["model_judgment"]
    assert judgment["status"] == "INVALID_OUTPUT"
    assert judgment["summary"] is None and judgment["evidence"] == []
    codes = [a["validation_codes"] for a in judgment["diagnostic"]["attempts"]]
    assert codes == [[RejectionCode.RESUME_VALUE_ECHO.value]] * 2
    assert bullet not in (h.run_dir(report.run_id) / "records.json").read_text()
    assert state(h).pending[0].last_status is JudgmentStatus.INVALID_OUTPUT


def test_event_trace_one_event_per_observation(h: Harness) -> None:
    live(h)
    h.set_backend(FakeBackend([VALID_REPLY]))
    report = live(h, added())
    log = h.events[-1]
    path = h.run_dir(report.run_id) / "events.jsonl"
    lines = [json.loads(line) for line in path.read_text().splitlines()]
    assert lines == log.events
    assert [e["seq"] for e in lines] == list(range(1, len(lines) + 1))
    names = [e["event"] for e in lines]
    for once in (
        "run.started",
        "source.obtained",
        "raw.saved",
        "board.parsed",
        "records.saved",
        "state.saved",
        "run.finished",
    ):
        assert names.count(once) == 1, once
    assert names.count("rule.evaluated") == len(records(h, report)) == 1
    assert names.count("judgment.completed") == h.backend.calls == 1
    assert names[0] == "run.started" and names[-1] == "run.finished"


def test_pipeline_issues_exactly_one_request(h: Harness) -> None:
    live(h)
    h.set_backend(FakeBackend([VALID_REPLY]))
    live(h, added())
    assert [len(t.requests) for t in h.transports] == [1, 1]
    assert all(str(t.requests[0].url) == JOBS_URL for t in h.transports)


def test_constructed_variant_removing_posting_is_no_new(h: Harness) -> None:
    live(h)
    first_id = json.loads(BODY)["jobs"][0]["id"]
    report = live(h, constructed_without(BODY, first_id))
    assert report.status is RunStatus.SUCCESS_NO_NEW
    assert str(first_id) in state(h).seen_ids  # cumulative
    report = live(h, BODY)  # it reappears: still not new
    assert report.new_count == 0


# --- review fix 1: a raising judge never aborts the run ---------------------------


class _RaisingJudge:
    """A ``ports.Judge`` that breaks its no-raise contract (failure injection)."""

    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    def judge(
        self, posting: Posting, resume: VerifiedResume, *, log_dir: str
    ) -> JudgmentOutcome:
        raise self.exc


@pytest.mark.parametrize(
    ("exc", "code"),
    [
        (PathRejected("not_empty", "tmp/claude-x"), "judge_raised:PathRejected"),
        (OSError("disk full"), "judge_raised:OSError"),
        (PayloadError("skills.backend must be a list"), "judge_raised:PayloadError"),
    ],
)
def test_raising_judge_gives_error_judgment_and_partial_failure(
    h: Harness, exc: Exception, code: str
) -> None:
    live(h)
    out = InjectingRoot(h.config.data_dir)
    deps = dataclasses.replace(
        h.deps(h.live_source(Reply(status=200, body=added())), out=out),
        judge=_RaisingJudge(exc),
    )
    report = run_once(deps)
    assert report.status is RunStatus.PARTIAL_FAILURE
    assert report.unresolved_pending_ids == [NEW_ID]
    assert [p.posting_id for p in state(h).pending] == [NEW_ID]
    (record,) = records(h, report)
    judgment = record["model_judgment"]
    assert judgment["status"] == "ERROR"
    assert judgment["diagnostic"]["error_reason"] == code
    assert str(exc) not in json.dumps(record)
    run_rel = f"live/runs/{report.run_id}"
    order = [
        out.writes.index(f"{run_rel}/records.json"),
        out.writes.index(LIVE_STATE),
        out.writes.index(f"{run_rel}/report.json"),
    ]
    assert order == sorted(order)
    crashed = [e for e in h.events[-1].events if e["event"] == "judgment.crashed"]
    assert len(crashed) == 1
    assert crashed[0]["posting_id"] == NEW_ID
    assert crashed[0]["reason"] == code


# --- review fix 3: one run at a time per data mode --------------------------------


def test_run_fails_fast_while_another_process_holds_the_lock(h: Harness) -> None:
    live(h)
    before = h.data(LIVE_STATE).read_bytes()
    runs_before = sorted(p.name for p in h.data("live/runs").iterdir())
    out = OutputRoot(h.config.data_dir)
    with out.lock("live/.lock"), pytest.raises(RunLocked) as info:
        run_once(h.deps(h.live_source(Reply(body=added())), out=out))
    assert info.value.exit_code is ExitCode.LOCKED
    assert h.data(LIVE_STATE).read_bytes() == before
    assert sorted(p.name for p in h.data("live/runs").iterdir()) == runs_before
    assert h.transports[-1].requests == []
    assert h.backend.calls == 0
    report = run_once(h.deps(h.live_source(Reply(body=BODY)), out=out))
    assert report.status is RunStatus.SUCCESS_NO_NEW  # the lock was released


def test_same_second_run_id_is_a_clear_error_not_path_rejected(h: Harness) -> None:
    clock = FixedClock(FIXED_START, step=timedelta(0))
    out = OutputRoot(h.config.data_dir)
    first = dataclasses.replace(
        h.deps(h.live_source(Reply(body=BODY)), out=out), clock=clock
    )
    run_once(first)
    before = h.data(LIVE_STATE).read_bytes()
    second = dataclasses.replace(
        h.deps(h.live_source(Reply(body=BODY)), out=out), clock=clock
    )
    with pytest.raises(RunIdTaken) as info:
        run_once(second)
    assert not isinstance(info.value, PathRejected)
    assert info.value.exit_code is ExitCode.LOCKED
    assert h.data(LIVE_STATE).read_bytes() == before
    assert h.transports[-1].requests == []


# --- review fix 4: the state is read through the write root's path policy ----------


def test_state_is_read_through_the_output_writer(h: Harness) -> None:
    live(h)
    h.data(LIVE_STATE).write_bytes(b"not json")
    out = InjectingRoot(h.config.data_dir)
    with pytest.raises(StateCorrupt):
        run_once(h.deps(h.live_source(Reply(body=BODY)), out=out))
    assert out.reads == [LIVE_STATE]


def test_symlinked_state_file_is_refused(h: Harness, tmp_path: Path) -> None:
    live(h)
    outside = tmp_path / "outside-state.json"
    outside.write_bytes(h.data(LIVE_STATE).read_bytes())
    h.data(LIVE_STATE).unlink()
    h.data(LIVE_STATE).symlink_to(outside)
    before = outside.read_bytes()
    with pytest.raises(PathRejected) as info:
        run_once(
            h.deps(
                h.live_source(Reply(body=added())), out=OutputRoot(h.config.data_dir)
            )
        )
    assert info.value.reason == "symlink"
    assert outside.read_bytes() == before
    assert h.transports[-1].requests == []


# --- review nit: a body without provenance is an explicit error ------------------


class _NoProvenanceReplay:
    def obtain(self) -> SourceResult:
        return SourceResult(kind=SourceKind.REPLAY, body=BODY, sha256=None, error=None)


def test_body_without_raw_ref_is_a_config_error_not_an_assert(h: Harness) -> None:
    live(h)
    with pytest.raises(ConfigError, match="raw"):
        run_once(h.deps(_NoProvenanceReplay(), seeded=True))
