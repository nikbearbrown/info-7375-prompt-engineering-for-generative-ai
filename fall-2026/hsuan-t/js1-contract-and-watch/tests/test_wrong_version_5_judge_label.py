"""CONTRACT Wrong version 5 — a verdict with the wrong judge label.

A rule verdict labelled "claude" (or the reverse) is perfectly formatted, so nothing else would
catch it; and a record mistaken for a judgment (or a judgment for a record) is exactly what
CONTRACT Refuses #3 forbids. The label comes from code in verdict.py, so that is what is tested.
"""

import pytest
from fakes import GOOD, SENIOR, FakeClaude, board, good_answer, job, run_once

from job_agent.common.posting import Posting
from job_agent.judges import claude, verdict

PROMPT = claude.Prompt("test", "judge this")


def test_every_verdict_in_a_run_carries_its_own_judges_label(paths):
    run_once(paths, board(job(1)), n=0)
    doc = run_once(paths, board(job(1), job(2, **GOOD), job(3, **SENIOR), job(4, content="")), n=1)
    rule_v = [v for v in doc["verdicts"] if v["judge"] == "rule"]
    claude_v = [v for v in doc["verdicts"] if v["judge"] == "claude"]
    assert len(rule_v) == len(claude_v) == 3              # each posting judged once by each judge
    assert {v["kind"] for v in rule_v} == {"record"}       # ok relevant, ok not_relevant, error
    assert {v["kind"] for v in claude_v} == {"judgment"}


@pytest.mark.parametrize("judge, kind", [("rule", "record"), ("claude", "judgment")])
def test_kind_is_set_by_code_from_the_judge(judge, kind):
    assert verdict.ok(judge, 1, verdict.RELEVANT, [])["kind"] == kind
    assert verdict.error(judge, 1, "x")["kind"] == kind


def test_unknown_judge_or_verdict_is_refused():
    with pytest.raises(ValueError):
        verdict.ok("gpt", 1, verdict.RELEVANT, [])
    with pytest.raises(ValueError):
        verdict.ok("rule", 1, "maybe", [])


def test_claude_cannot_label_itself(criteria):
    """Even a reply that tries to say it is the rule is rejected (extra keys break validator row 2),
    and an accepted reply is labelled by code: claude + judgment."""
    posting = Posting(7, GOOD["title"], GOOD["location"], GOOD["content"])
    sneaky = FakeClaude(lambda p: {**good_answer(p), "judge": "rule", "kind": "record"})
    v = claude.judge(posting, criteria, sneaky, PROMPT).verdict
    assert (v["status"], v["judge"], v["kind"]) == ("error", "claude", "judgment")
    v = claude.judge(posting, criteria, FakeClaude(), PROMPT).verdict
    assert (v["status"], v["judge"], v["kind"]) == ("ok", "claude", "judgment")
