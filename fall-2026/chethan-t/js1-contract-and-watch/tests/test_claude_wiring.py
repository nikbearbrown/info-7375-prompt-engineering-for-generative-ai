import json
import subprocess

import pytest

from agent import claude_judge, main

VALID = {
    "verdict": "relevant",
    "resume_fields": ["target.roles", "skills.frontend"],
    "posting_fields": ["title", "content"],
    "reason": "The title matches a target role and the posting's web work overlaps the résumé's frontend skills.",
}


@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    """No real subprocess calls; raw replies go to a temp folder."""
    def no_real_claude(*args, **kwargs):
        raise AssertionError("real subprocess call attempted")

    monkeypatch.setattr(subprocess, "run", no_real_claude)
    monkeypatch.setattr(claude_judge, "RESPONSES_DIR", tmp_path / "claude_responses", raising=False)
    return tmp_path / "claude_responses"


def fake_claude(monkeypatch, reply_text):
    """Mock `claude -p ... --output-format json` replying with reply_text; return the call log."""
    calls = []

    def run(args, **kwargs):
        calls.append((args, kwargs))
        envelope = {"type": "result", "subtype": "success", "is_error": False, "result": reply_text}
        return subprocess.CompletedProcess(args, 0, stdout=json.dumps(envelope), stderr="")

    monkeypatch.setattr(subprocess, "run", run)
    return calls


def test_19_prompt_sent_to_claude_has_no_personal_info(monkeypatch, postings, resume):
    calls = fake_claude(monkeypatch, json.dumps(VALID))
    posting = postings["swe_boston_us_citizen_escaped"]
    claude_judge.judge(posting, resume)

    (args, kwargs), = calls
    prompt = args[2]
    assert args == ["claude", "-p", prompt, "--output-format", "json"]
    assert kwargs["timeout"] == 120
    assert '"personal"' not in prompt
    for key in ("name", "email", "phone", "linkedin", "github"):
        assert resume["personal"][key] not in prompt
    # The posting's id, title, location, and HTML-free content are sent.
    assert str(posting["id"]) in prompt
    assert posting["title"] in prompt
    assert posting["location"]["name"] in prompt
    assert "U.S. citizen" in prompt
    assert "<strong>" not in prompt and "&lt;" not in prompt


def test_20_valid_reply_is_labeled_judgment(monkeypatch, postings, resume, isolated):
    fake_claude(monkeypatch, json.dumps(VALID))
    result = main.result_for(postings["swe_boston_plain"], resume, use_claude=True)

    judgment = result["judgment"]
    assert judgment["label"] == "judgment"
    assert {k: judgment[k] for k in VALID} == VALID
    assert result["record"]["verdict"] == "relevant"
    assert len(list(isolated.iterdir())) == 1  # raw reply saved


BAD_REPLIES = {
    "missing_key": json.dumps({k: v for k, v in VALID.items() if k != "reason"}),
    "extra_key": json.dumps({**VALID, "confidence": 0.9}),
    "extra_text": "Here is my verdict:\n" + json.dumps(VALID),
}


@pytest.mark.parametrize("reply", BAD_REPLIES.values(), ids=BAD_REPLIES.keys())
def test_21_bad_reply_is_recorded_as_no_claude_verdict(monkeypatch, postings, resume, isolated, reply):
    fake_claude(monkeypatch, reply)
    judgment = claude_judge.judge(postings["swe_boston_plain"], resume)

    assert judgment["label"] == "judgment"
    assert judgment["status"] == "no Claude verdict"
    assert "verdict" not in judgment
    saved = list(isolated.iterdir())
    assert len(saved) == 1 and reply in json.loads(saved[0].read_text())["result"]


def test_22_missing_claude_command_still_gives_rule_verdict(monkeypatch, postings, resume):
    def not_installed(*args, **kwargs):
        raise FileNotFoundError(2, "No such file or directory", "claude")

    monkeypatch.setattr(subprocess, "run", not_installed)
    result = main.result_for(postings["swe_boston_plain"], resume, use_claude=True)

    assert result["judgment"]["status"] == "Claude verdict: not run"
    assert result["record"]["verdict"] == "relevant"
