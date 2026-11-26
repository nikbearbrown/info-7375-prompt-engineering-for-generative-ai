"""Claude judge plumbing with a fake client — no network, no API key.

Written AFTER jsagent/claude_judge.py (unlike test_contract.py). These check that the
judge records invalid/unavailable outcomes honestly; they say nothing about verdict quality.
"""
import json
from types import SimpleNamespace

import anthropic
import httpx2

from conftest import RELEVANT
from jsagent.claude_judge import make_claude_judge, resume_for_prompt, user_message


class FakeClient:
    def __init__(self, text=None, stop_reason="end_turn", error=None):
        self.calls = []
        self._text, self._stop, self._error = text, stop_reason, error
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        if self._error:
            raise self._error
        return SimpleNamespace(
            model=kwargs["model"], stop_reason=self._stop, _request_id="req_fake",
            content=[SimpleNamespace(type="text", text=self._text or "")],
        )


GOOD = json.dumps({"verdict": "relevant", "justification": [
    {"resume_field": "skills.devops_cicd", "resume_value": "Kubernetes",
     "posting_field": "content", "posting_value": "Kubernetes"}]})


def test_valid_output_is_accepted_and_labeled_metadata(resume):
    client = FakeClient(GOOD)
    out = make_claude_judge(client=client)(resume, RELEVANT)
    assert out["claude_verdict"] == "relevant"
    assert out["claude_model_served"] == "claude-opus-5-5"
    assert "temperature" not in client.calls[0]


def test_prose_wrapped_output_is_invalid_not_repaired(resume):
    client = FakeClient("Sure! " + GOOD)
    out = make_claude_judge(client=client)(resume, RELEVANT)
    assert out["claude_verdict"] == "invalid"
    assert out["claude_raw_text"].startswith("Sure!")
    assert len(client.calls) == 1  # no silent retry


def test_refusal_and_api_errors_are_unavailable(resume):
    out = make_claude_judge(client=FakeClient(GOOD, stop_reason="refusal"))(resume, RELEVANT)
    assert out["claude_verdict"] == "unavailable"

    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    err = anthropic.APIConnectionError(request=request)
    out = make_claude_judge(client=FakeClient(error=err))(resume, RELEVANT)
    assert out["claude_verdict"] == "unavailable" and "network" in out["claude_reason"]


def test_contact_details_never_sent(resume):
    sent = user_message(resume, RELEVANT)
    for secret in (resume["personal"]["name"], resume["personal"]["email"], resume["personal"]["phone"]):
        assert secret not in sent
    assert set(resume_for_prompt(resume)) == {
        "target_titles", "personal", "years_experience", "target_role", "skills"}
