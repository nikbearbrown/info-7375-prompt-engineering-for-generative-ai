"""Unit tests for whole runs through the seam: seeded runs, files written, failures and judge outcomes. Written by Claude Code on 2026-10-29. All postings and responses are constructed."""
import json
import os
import socket
import urllib.error
from datetime import timedelta

import pytest

from conftest import (BOARD_URL, FIXED_NOW, FakeClient, FakeOpener, board_body, job, latest_report,
                      run_args, run_cli)

PROMPT = "## System\nS\n## User\n{{RESUME_JSON}}\n{{POSTING_ID}}\n{{POSTING_JSON}}\n"
GOOD = {"source": "resume", "path": "/targets/roles/0", "value": "Machine Learning Engineer"}


def _serve(jobs, status=200):
    return FakeOpener({BOARD_URL: (status, board_body(jobs), {})})


def _baseline(workdir):
    assert run_cli(run_args(), opener=_serve([])) == 0


def _runs(workdir):
    return sorted((workdir / "evidence" / "runs").iterdir())


def _with_key(workdir, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    (workdir / "p.md").write_text(PROMPT, encoding="utf-8")
    return ("--prompt", "p.md")


def test_baseline_writes_raw_manifest_report_and_state(workdir, capsys):
    assert run_cli(run_args(), opener=_serve([job(1, "AI Engineer")])) == 0
    (run_dir,) = _runs(workdir)
    assert run_dir.name == "20261029T180000Z_acme"
    raw = workdir / "evidence" / "raw" / "20261029T180000Z_acme.raw"
    assert raw.read_bytes() == board_body([job(1, "AI Engineer")])
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["label"] == "baseline" and manifest["source"] == "network"
    assert manifest["url"] == BOARD_URL and manifest["http_status"] == 200
    assert manifest["raw_path"] == "evidence/raw/20261029T180000Z_acme.raw"
    assert manifest["state_before_sha256"] is None and manifest["prompt_path"] is None
    assert "location_header" not in manifest
    assert not (run_dir / "state_before.json").exists()
    out = capsys.readouterr().out
    assert out == (run_dir / "report.txt").read_text()
    assert out.splitlines()[1] == "source network"
    assert "Baseline run: no posting is reported as new" in out
    report = json.loads((run_dir / "report.json").read_text())
    assert (report["source"], report["from_file"], report["from_file_sha256"]) == ("network", None, None)
    state = json.loads((workdir / "state" / "acme.json").read_text())
    assert state == {"schema_version": 1, "board": "acme", "seen_ids": ["1"],
                     "updated_at": "2026-10-29T18:00:00Z", "last_run_id": "20261029T180000Z_acme"}


def test_run_id_collision_gets_a_suffix(workdir):
    _baseline(workdir)
    assert run_cli(run_args(), opener=_serve([])) == 0
    assert [p.name for p in _runs(workdir)] == ["20261029T180000Z_acme", "20261029T180000Z_acme-2"]


def test_seeded_run_reads_the_file_and_never_calls_the_opener(workdir):
    _baseline(workdir)
    saved = workdir / "saved.raw"
    saved.write_bytes(board_body([job(5, "Data Scientist", "Seattle, WA")]))
    opener = FakeOpener({})
    later = FIXED_NOW + timedelta(minutes=1)
    assert run_cli(run_args(extra=("--from-file", "saved.raw")), opener=opener, now=later) == 0
    assert opener.requests == []
    report = latest_report(workdir)
    assert report["label"] == "seeded" and [r["posting_id"] for r in report["records"]] == ["5"]
    assert report["records"][0]["record"]["verdict"] == "relevant"
    run_dir = _runs(workdir)[-1]
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["url"] is None and manifest["http_status"] is None and manifest["source"] == "file"
    assert manifest["from_file"] == "saved.raw" and manifest["from_file_sha256"] == manifest["sha256"]
    assert (report["source"], report["from_file"], report["from_file_sha256"]) == ("file", "saved.raw", manifest["sha256"])
    header = (run_dir / "report.txt").read_text().splitlines()[1]
    assert header == f"source file saved.raw (sha256 {manifest['sha256']})"


def test_from_file_without_state_is_a_baseline(workdir):
    saved = workdir / "saved.raw"
    saved.write_bytes(board_body([job(5, "Data Scientist", "Seattle, WA")]))
    opener = FakeOpener({})
    assert run_cli(run_args(extra=("--from-file", "saved.raw")), opener=opener) == 0
    assert opener.requests == []
    report = latest_report(workdir)
    assert report["label"] == "baseline" and report["source"] == "file"
    assert report["records"] == [] and report["counts"]["new"] == 0
    assert json.loads((workdir / "state" / "acme.json").read_text())["seen_ids"] == ["5"]


@pytest.mark.skipif(not hasattr(os, "geteuid") or os.geteuid() == 0, reason="root can read a chmod 000 file")
def test_unreadable_state_file_is_corrupt(workdir):
    _baseline(workdir)
    state = workdir / "state" / "acme.json"
    before = state.read_bytes()
    state.chmod(0)
    try:
        opener = _serve([job(1, "AI Engineer")])
        assert run_cli(run_args(), opener=opener, now=FIXED_NOW + timedelta(minutes=1)) == 4
        assert opener.requests == []
        assert len(_runs(workdir)) == 1  # nothing written for the refused run
    finally:
        state.chmod(0o644)
    assert state.read_bytes() == before


def test_state_before_is_a_byte_copy(workdir):
    _baseline(workdir)
    before = (workdir / "state" / "acme.json").read_bytes()
    assert run_cli(run_args(), opener=_serve([]), now=FIXED_NOW + timedelta(minutes=1)) == 0
    assert (_runs(workdir)[-1] / "state_before.json").read_bytes() == before


def test_bad_title_is_listed_every_run_not_judged_but_remembered(workdir):
    jobs = [job(1, "AI Engineer"), job(2, "  "), job(3, "Data Scientist")]
    assert run_cli(run_args(), opener=_serve(jobs)) == 0
    assert latest_report(workdir)["skipped_bad_title"] == ["2"]
    jobs.append(job(4, None))
    assert run_cli(run_args(), opener=_serve(jobs), now=FIXED_NOW + timedelta(minutes=1)) == 0
    report = latest_report(workdir)
    assert report["skipped_bad_title"] == ["2", "4"]
    assert report["records"] == []
    assert report["counts"] == {"postings": 4, "unique": 4, "previously_seen": 3, "new": 0, "agree": 0, "disagree": 0}
    assert json.loads((workdir / "state" / "acme.json").read_text())["seen_ids"] == ["1", "2", "3", "4"]


def test_counts_with_bad_ids_and_duplicates(workdir):
    _baseline(workdir)
    jobs = [job(1, "AI Engineer"), job(1, "AI Engineer"), job("x", "AI Engineer"), job(2, "Recruiter")]
    assert run_cli(run_args(), opener=_serve(jobs), now=FIXED_NOW + timedelta(minutes=1)) == 0
    report = latest_report(workdir)
    assert report["counts"]["postings"] == 4 and report["counts"]["unique"] == 2 and report["counts"]["new"] == 2
    assert report["skipped_bad_id"] == ["x"] and report["duplicates_dropped"] == 1


@pytest.mark.parametrize("status", [204, 404, 500])
def test_non_200_saves_bytes_and_stops_with_state_unchanged(workdir, status):
    _baseline(workdir)
    before = (workdir / "state" / "acme.json").read_bytes()
    opener = FakeOpener({BOARD_URL: (status, b"oops", {})})
    assert run_cli(run_args(), opener=opener, now=FIXED_NOW + timedelta(minutes=1)) == 3
    assert (workdir / "state" / "acme.json").read_bytes() == before
    run_dir = _runs(workdir)[-1]
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["http_status"] == status
    assert (workdir / manifest["raw_path"]).read_bytes() == b"oops"
    assert not (run_dir / "report.json").exists() and not (run_dir / "report.txt").exists()


class _FailingOpener:
    def __init__(self, exc):
        self.exc = exc

    def open(self, request, timeout=None):
        raise self.exc


@pytest.mark.parametrize("exc,kind", [
    (socket.timeout(), "timeout"),
    (urllib.error.URLError(ConnectionRefusedError()), "url_error:ConnectionRefusedError"),
])
def test_network_failure_exits_3_and_records_why(workdir, exc, kind):
    assert run_cli(run_args(), opener=_FailingOpener(exc)) == 3
    (run_dir,) = _runs(workdir)
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["error"] == kind
    assert manifest["raw_path"] is None and manifest["sha256"] is None and manifest["byte_length"] is None
    assert not (workdir / "evidence" / "raw").exists()
    assert not (run_dir / "report.json").exists()
    assert not (workdir / "state").exists()


@pytest.mark.parametrize("body", [b"not json", b"[]", b'{"jobs": {}}'])
def test_body_that_is_not_a_jobs_list_stops_with_exit_1(workdir, body):
    assert run_cli(run_args(), opener=FakeOpener({BOARD_URL: (200, body, {})})) == 1
    (run_dir,) = _runs(workdir)
    assert (run_dir / "manifest.json").exists() and not (run_dir / "report.json").exists()
    assert (workdir / "evidence" / "raw" / f"{run_dir.name}.raw").read_bytes() == body
    assert not (workdir / "state").exists()


def test_invalid_rule_verdict_exits_5_and_leaves_state(workdir, monkeypatch):
    import jobwatch.run

    _baseline(workdir)
    before = (workdir / "state" / "acme.json").read_bytes()
    monkeypatch.setattr(jobwatch.run, "apply_rule", lambda resume, j: {"verdict": "relevant", "citations": []})
    assert run_cli(run_args(), opener=_serve([job(9, "AI Engineer")]), now=FIXED_NOW + timedelta(minutes=1)) == 5
    assert (workdir / "state" / "acme.json").read_bytes() == before
    run_dir = _runs(workdir)[-1]
    assert (run_dir / "manifest.json").exists() and not (run_dir / "report.json").exists()


def test_key_set_and_prompt_missing_is_refused_before_any_request(workdir, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    opener = _serve([])
    assert run_cli(run_args(extra=("--prompt", "absent.md")), opener=opener) == 2
    assert opener.requests == []


def test_request_file_records_model_and_settings(workdir, monkeypatch):
    extra = _with_key(workdir, monkeypatch)
    answer = {"posting_id": "9", "verdict": "not_relevant", "reason": "r",
              "citations": [GOOD, {"source": "posting", "path": "/title", "value": "Recruiter"}]}
    client = FakeClient(lambda kw: (json.dumps(answer), "end_turn"))
    assert run_cli(run_args(extra=extra), opener=_serve([]), client=client) == 0
    later = FIXED_NOW + timedelta(minutes=1)
    assert run_cli(run_args(extra=extra), opener=_serve([job(9, "Recruiter")]), client=client, now=later) == 0
    (call,) = client.calls
    assert call["model"] == "claude-sonnet-5-5" and call["temperature"] == 1.0 and call["max_tokens"] == 600
    assert "tools" not in call and call["system"] == "S"
    assert call["messages"][0]["role"] == "user" and '"content_text"' in call["messages"][0]["content"]
    run_dir = _runs(workdir)[-1]
    assert json.loads((run_dir / "claude" / "9.request.json").read_text()) == call
    meta = json.loads((run_dir / "claude" / "9.response.meta.json").read_text())
    assert meta == {"id": "msg_fake_1", "model": "claude-sonnet-5-5", "stop_reason": "end_turn",
                    "called_at": "2026-10-29T18:01:00Z"}
    report = latest_report(workdir)
    assert report["records"][0]["agreement"] == "agree" and report["counts"]["agree"] == 1
    assert report["judge"]["status"] == "run" and report["judge"]["prompt_sha256"]


def test_disagreement_is_shown_and_not_resolved(workdir, monkeypatch, capsys):
    extra = _with_key(workdir, monkeypatch)
    answer = {"posting_id": "9", "verdict": "relevant", "reason": "Claims a fit.",
              "citations": [GOOD, {"source": "posting", "path": "/title", "value": "Recruiter"}]}
    client = FakeClient(lambda kw: (json.dumps(answer), "end_turn"))
    assert run_cli(run_args(extra=extra), opener=_serve([]), client=client) == 0
    capsys.readouterr()
    later = FIXED_NOW + timedelta(minutes=1)
    assert run_cli(run_args(extra=extra), opener=_serve([job(9, "Recruiter")]), client=client, now=later) == 0
    rec = latest_report(workdir)["records"][0]
    assert rec["record"]["verdict"] == "not_relevant" and rec["judgment"]["verdict"] == "relevant"
    assert rec["agreement"] == "disagree"
    out = capsys.readouterr().out
    assert "  RECORD (rule): not_relevant" in out
    assert "  JUDGMENT (claude-sonnet-5-5, 2026-10-29): relevant" in out
    assert "\n  DISAGREE\n" in out


def test_truncated_response_is_rejected_and_kept(workdir, monkeypatch):
    extra = _with_key(workdir, monkeypatch)
    client = FakeClient(lambda kw: ('{"posting_id": "9", "verd', "max_tokens"))
    assert run_cli(run_args(extra=extra), opener=_serve([]), client=client) == 0
    later = FIXED_NOW + timedelta(minutes=1)
    assert run_cli(run_args(extra=extra), opener=_serve([job(9, "AI Engineer")]), client=client, now=later) == 0
    j = latest_report(workdir)["records"][0]["judgment"]
    assert j["status"] == "rejected" and j["reason"] == "truncated"
    assert (workdir / j["raw_path"]).read_text() == '{"posting_id": "9", "verd'


def test_api_error_is_reported_and_posting_still_marked_seen(workdir, monkeypatch):
    extra = _with_key(workdir, monkeypatch)

    def boom(kw):
        raise RuntimeError("simulated failure")

    client = FakeClient(boom)
    assert run_cli(run_args(extra=extra), opener=_serve([]), client=client) == 0
    later = FIXED_NOW + timedelta(minutes=1)
    assert run_cli(run_args(extra=extra), opener=_serve([job(9, "AI Engineer")]), client=client, now=later) == 0
    j = latest_report(workdir)["records"][0]["judgment"]
    assert j["status"] == "error" and j["reason"] == "api_error:other" and j["raw_path"] is None
    assert json.loads((workdir / "state" / "acme.json").read_text())["seen_ids"] == ["9"]


def test_judge_client_has_60s_timeout_and_no_retries(monkeypatch):
    from jobwatch.judge import make_client

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    client = make_client()  # constructing the client sends nothing
    assert client.timeout == 60.0 and client.max_retries == 0


def test_bad_title_posting_gets_no_record_even_when_new(workdir):
    _baseline(workdir)
    jobs = [job(1, "AI Engineer"), job(2, "—")]
    assert run_cli(run_args(), opener=_serve(jobs), now=FIXED_NOW + timedelta(minutes=1)) == 0
    report = latest_report(workdir)
    assert [r["posting_id"] for r in report["records"]] == ["1"]
    assert report["counts"]["new"] == 1 and report["skipped_bad_title"] == ["2"]


def test_unknown_subcommand_is_an_argument_error(workdir):
    assert run_cli(["no-such-command", "x"]) == 2
