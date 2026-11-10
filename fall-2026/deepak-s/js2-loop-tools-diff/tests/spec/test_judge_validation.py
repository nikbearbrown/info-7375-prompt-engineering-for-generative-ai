"""Cases 11, 12 and 17 (Judges and validator). Written by Claude Code from tests/acceptance/ACCEPTANCE_CASES.md on 2026-10-29, before any implementation. All postings and Claude responses are constructed; the client is a fake."""
import json
from datetime import timedelta
from pathlib import Path

import pytest

from conftest import BOARD_URL, FIXED_NOW, FakeClient, FakeOpener, board_body, job, latest_report, run_args, run_cli

PROMPT = (
    "## System\nConstructed test prompt.\n\n"
    "## User\nRésumé: {{RESUME_JSON}}\nPosting id: {{POSTING_ID}}\nPosting: {{POSTING_JSON}}\n"
)
POSTING = job(
    1101,
    "Machine Learning Engineer, Payments",
    "Boston, MA",
    content="&lt;p&gt;You will train models with &lt;b&gt;PyTorch&lt;/b&gt;.&lt;/p&gt;",
    departments=["Applied ML"],
)
GOOD_RESUME = {"source": "resume", "path": "/targets/roles/0", "value": "Machine Learning Engineer"}
GOOD_POSTING = {"source": "posting", "path": "/title", "value": "Machine Learning Engineer"}


def _answer(**changes):
    out = {"posting_id": "1101", "verdict": "relevant", "citations": [GOOD_RESUME, GOOD_POSTING],
           "reason": "Constructed test response."}
    out.update(changes)
    return json.dumps(out)


def _judge(workdir, monkeypatch, text, stop_reason="end_turn"):
    """Baseline, then one run where POSTING is new and the fake client answers `text`."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    (workdir / "prompt_spec.md").write_text(PROMPT, encoding="utf-8")
    args = run_args(extra=("--prompt", "prompt_spec.md"))
    client = FakeClient(lambda kwargs: (text, stop_reason))
    for minute, jobs in ((0, []), (1, [POSTING])):
        opener = FakeOpener({BOARD_URL: (200, board_body(jobs), {})})
        assert run_cli(args, opener=opener, client=client, now=FIXED_NOW + timedelta(minutes=minute)) == 0
    assert len(client.calls) == 1
    (record,) = latest_report(workdir)["records"]
    return record


# Case 11 -------------------------------------------------------------------------------------

UNRESOLVED = {
    "field_outside_posting_document": {"source": "posting", "path": "/updated_at", "value": "2026"},
    "raw_content_not_citable": {"source": "posting", "path": "/content", "value": "PyTorch"},
    "index_out_of_range": {"source": "posting", "path": "/departments/3/name", "value": "Applied ML"},
    "resume_field_absent": {"source": "resume", "path": "/basics/nickname", "value": "Riley"},
}
NOT_PRESENT = {
    "posting_value_elsewhere": {"source": "posting", "path": "/title", "value": "Kubernetes"},
    "posting_substring_only": {"source": "posting", "path": "/title", "value": "Engine"},
    "resume_value_at_other_index": {"source": "resume", "path": "/targets/roles/0", "value": "Data Scientist"},
    "path_resolves_to_object": {"source": "posting", "path": "/location", "value": "Boston"},
}
RESOLVES = {
    "content_text": {"source": "posting", "path": "/content_text", "value": "PyTorch"},
    "number_as_decimal_string": {"source": "posting", "path": "/id", "value": "1101"},
    "department_name": {"source": "posting", "path": "/departments/0/name", "value": "Applied ML"},
}


def _with(citation):
    other = GOOD_POSTING if citation["source"] == "resume" else GOOD_RESUME
    return [other, citation]


@pytest.mark.parametrize("citation", list(UNRESOLVED.values()), ids=list(UNRESOLVED))
def test_ac11_citation_whose_path_does_not_resolve_is_rejected(workdir, monkeypatch, citation):
    rec = _judge(workdir, monkeypatch, _answer(citations=_with(citation)))
    assert rec["judgment"]["status"] == "rejected"
    assert rec["judgment"]["verdict"] is None


def test_ac11_field_outside_posting_document_is_path_unresolved(workdir, monkeypatch):
    rec = _judge(workdir, monkeypatch, _answer(citations=_with(UNRESOLVED["field_outside_posting_document"])))
    assert rec["judgment"]["reason"] == "path_unresolved"


@pytest.mark.parametrize("citation", list(NOT_PRESENT.values()), ids=list(NOT_PRESENT))
def test_ac11_citation_whose_value_is_not_at_its_path_is_rejected(workdir, monkeypatch, citation):
    rec = _judge(workdir, monkeypatch, _answer(citations=_with(citation)))
    assert rec["judgment"]["status"] == "rejected"
    assert rec["judgment"]["verdict"] is None


@pytest.mark.parametrize("citation", list(RESOLVES.values()), ids=list(RESOLVES))
def test_ac11_citation_that_resolves_is_accepted(workdir, monkeypatch, citation):
    rec = _judge(workdir, monkeypatch, _answer(citations=_with(citation)))
    assert rec["judgment"]["status"] == "accepted"


# Case 12 -------------------------------------------------------------------------------------

MALFORMED = {
    "json_code_fence": "```json\n" + _answer() + "\n```",
    "extra_key": _answer(confidence=0.9),
    "mismatched_posting_id": _answer(posting_id="9999"),
    "integer_posting_id": _answer(posting_id=1101),
    "verdict_maybe": _answer(verdict="maybe"),
}


def _saved_response(workdir, rec):
    run_dir = sorted((workdir / "evidence" / "runs").iterdir())[-1]
    by_name = (run_dir / "claude" / "1101.response.txt").read_text(encoding="utf-8")
    raw_path = Path(rec["judgment"]["raw_path"])
    by_path = (raw_path if raw_path.is_absolute() else workdir / raw_path).read_text(encoding="utf-8")
    return by_name, by_path


def test_ac12_well_formed_output_is_accepted(workdir, monkeypatch):
    rec = _judge(workdir, monkeypatch, _answer())
    assert rec["judgment"]["status"] == "accepted"
    assert rec["judgment"]["verdict"] == "relevant"


@pytest.mark.parametrize("text", list(MALFORMED.values()), ids=list(MALFORMED))
def test_ac12_malformed_output_is_rejected_and_raw_text_kept(workdir, monkeypatch, text):
    rec = _judge(workdir, monkeypatch, text)
    assert rec["judgment"]["status"] == "rejected"
    assert rec["judgment"]["verdict"] is None
    assert _saved_response(workdir, rec) == (text, text)


# Case 17 -------------------------------------------------------------------------------------

def test_ac17_no_api_key_means_not_run_and_client_never_called(workdir):
    def responder(kwargs):
        raise AssertionError("the client must not be called without an API key")

    client = FakeClient(responder)
    jobs = [job(1701, "Machine Learning Engineer"), job(1702, "Account Executive")]
    for minute, served in ((0, []), (1, jobs)):
        opener = FakeOpener({BOARD_URL: (200, board_body(served), {})})
        assert run_cli(run_args(), opener=opener, client=client, now=FIXED_NOW + timedelta(minutes=minute)) == 0

    report = latest_report(workdir)
    assert client.calls == []
    assert report["judge"]["status"] == "not_run"
    assert [r["posting_id"] for r in report["records"]] == ["1701", "1702"]
    for rec in report["records"]:
        assert rec["judgment"]["status"] == "not_run"
        assert rec["judgment"]["reason"] == "no_api_key"
        assert rec["judgment"]["verdict"] is None
        assert rec["agreement"] == "n/a"
