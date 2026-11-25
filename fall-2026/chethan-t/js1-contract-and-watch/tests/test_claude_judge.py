import json

from agent import claude_judge


def test_18_reply_missing_verdict_is_rejected():
    reply = json.dumps({
        "resume_fields": ["target.roles"],
        "posting_fields": ["title"],
        "reason": "The title matches a target role.",
    })
    assert claude_judge.validate(reply) is None


def test_18b_complete_reply_is_accepted():
    fields = {
        "verdict": "relevant",
        "resume_fields": ["target.roles"],
        "posting_fields": ["title"],
        "reason": "The title matches a target role.",
    }
    result = claude_judge.validate(json.dumps(fields))
    assert result is not None
    assert result["verdict"] == "relevant"
