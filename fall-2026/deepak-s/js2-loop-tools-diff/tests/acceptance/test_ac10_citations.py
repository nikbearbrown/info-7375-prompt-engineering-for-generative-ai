"""Case 10. Cases and expected verdicts drafted with Claude (chat), hand-checked and adopted by Deepak on 2026-10-29; code typed by Claude Code from his answers on 2026-10-29, before any implementation."""
import json
from datetime import timedelta

import pytest

from conftest import BOARD_URL, FIXED_NOW, FakeClient, FakeOpener, board_body, job, latest_report, run_args, run_cli

# A constructed prompt in the CONTRACT.md Interfaces format; its wording doesn't matter to the fake.
PROMPT = (
    "## System\nConstructed test prompt.\n\n"
    "## User\nRésumé: {{RESUME_JSON}}\nPosting id: {{POSTING_ID}}\nPosting: {{POSTING_JSON}}\n"
)
POSTING = job(1001, "Machine Learning Engineer, Payments", "Boston, MA")  # constructed

GOOD_RESUME = {"source": "resume", "path": "/targets/roles/0", "value": "Machine Learning Engineer"}
GOOD_POSTING = {"source": "posting", "path": "/title", "value": "Machine Learning Engineer"}

BAD = {
    "no_citations_at_all": [],
    "zero_resume_citations": [GOOD_POSTING],
    "zero_posting_citations": [GOOD_RESUME],
    "posting_path_not_in_document": [
        GOOD_RESUME,
        {"source": "posting", "path": "/salary", "value": "Engineer"},
    ],
    "posting_value_not_at_path": [
        GOOD_RESUME,
        {"source": "posting", "path": "/title", "value": "Kubernetes"},
    ],
    "resume_path_not_in_document": [
        {"source": "resume", "path": "/targets/roles/99", "value": "Machine Learning Engineer"},
        GOOD_POSTING,
    ],
    "resume_value_not_at_path": [
        {"source": "resume", "path": "/targets/roles/0", "value": "Data Scientist"},
        GOOD_POSTING,
    ],
}


def _judge_once(workdir, monkeypatch, citations):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    (workdir / "prompt_case10.md").write_text(PROMPT, encoding="utf-8")
    args = run_args(extra=("--prompt", "prompt_case10.md"))

    def responder(kwargs):
        out = {"posting_id": "1001", "verdict": "relevant", "citations": citations,
               "reason": "Constructed test response."}
        return json.dumps(out), "end_turn"

    client = FakeClient(responder)
    for jobs, now in (([], FIXED_NOW), ([POSTING], FIXED_NOW + timedelta(minutes=1))):
        opener = FakeOpener({BOARD_URL: (200, board_body(jobs), {"Content-Type": "application/json"})})
        assert run_cli(args, opener=opener, client=client, now=now) == 0
    assert len(client.calls) == 1
    records = latest_report(workdir)["records"]
    assert [r["posting_id"] for r in records] == ["1001"]
    return records[0]


def test_ac10_valid_citations_are_accepted(workdir, monkeypatch):
    rec = _judge_once(workdir, monkeypatch, [GOOD_RESUME, GOOD_POSTING])
    assert rec["judgment"]["status"] == "accepted"
    assert rec["judgment"]["verdict"] == "relevant"


@pytest.mark.parametrize("citations", list(BAD.values()), ids=list(BAD))
def test_ac10_uncited_or_miscited_verdict_is_rejected(workdir, monkeypatch, citations):
    rec = _judge_once(workdir, monkeypatch, citations)
    assert rec["judgment"]["status"] == "rejected"
    assert rec["judgment"]["verdict"] is None
    assert isinstance(rec["judgment"]["reason"], str) and rec["judgment"]["reason"]
    assert rec["agreement"] == "n/a"
