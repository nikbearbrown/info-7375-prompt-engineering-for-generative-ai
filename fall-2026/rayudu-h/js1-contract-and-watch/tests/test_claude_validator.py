"""The Claude judge's fixed output format: the validator accepts exactly one shape and rejects anything else.

No Claude calls here: a fake caller returns CONSTRUCTED answers.
"""
import json

from conftest import posting
from jsagent import claude_judge

GOOD = {"verdict": "relevant", "confidence": "high", "resume_fields": ["skills", "experience[].title"],
        "posting_fields": ["title", "content"], "justification": 'Title "AI Engineer" and content names "Python".'}


def test_accepts_the_contract_shape():
    parsed, errors = claude_judge.validate(json.dumps(GOOD))
    assert errors == [] and parsed == GOOD


def test_rejects_everything_else():
    bad = [
        "```json\n" + json.dumps(GOOD) + "\n```",            # code fence
        "Sure! " + json.dumps(GOOD),                          # prose
        json.dumps(dict(GOOD, extra=1)),                      # extra key
        json.dumps({k: v for k, v in GOOD.items() if k != "confidence"}),
        json.dumps(dict(GOOD, verdict="maybe")),
        json.dumps(dict(GOOD, verdict="Relevant")),           # case matters
        json.dumps(dict(GOOD, confidence="0.9")),
        json.dumps(dict(GOOD, resume_fields=[])),             # cites nothing
        json.dumps(dict(GOOD, posting_fields=["salary"])),    # cites a field that doesn't exist
        json.dumps(dict(GOOD, justification="")),
        json.dumps(dict(GOOD, justification="x" * 801)),
        json.dumps([GOOD]),
        "",
    ]
    for text in bad:
        parsed, errors = claude_judge.validate(text)
        assert parsed is None and errors, text[:60]


def test_judge_labels_a_judgment_and_flags_ungrounded_quotes(resume):
    answer = dict(GOOD, justification='Title "AI Engineer" and content names "Kubernetes at scale".')

    def fake_caller(prompt, model):
        return {"started_at": "constructed", "exit_code": 0, "model_requested": model, "models_used": ["fake"],
                "duration_ms": 0, "is_error": False, "result": json.dumps(answer)}

    rec = claude_judge.judge(posting(1, "AI Engineer", "<p>Python</p>"), resume, caller=fake_caller)
    assert rec["kind"].startswith("judgment") and rec["valid"]
    assert rec["ungrounded_quotes"] == ["Kubernetes at scale"]


def test_rejected_answer_is_recorded_not_used(resume):
    def fake_caller(prompt, model):
        return {"started_at": "constructed", "exit_code": 0, "model_requested": model, "models_used": [],
                "duration_ms": 0, "is_error": False, "result": "I think it's relevant."}

    rec = claude_judge.judge(posting(1, "AI Engineer"), resume, caller=fake_caller)
    assert rec["valid"] is False and rec["judgment"] is None and rec["errors"]


def test_one_change_between_prompt_versions():
    v1, v2 = claude_judge.load_prompt("v1"), claude_judge.load_prompt("v2")
    added = [line for line in v2.splitlines() if line not in v1.splitlines()]
    removed = [line for line in v1.splitlines() if line not in v2.splitlines()]
    assert removed == []
    assert added[0].startswith("Apply this rule.")   # the one change: the written rule is added
