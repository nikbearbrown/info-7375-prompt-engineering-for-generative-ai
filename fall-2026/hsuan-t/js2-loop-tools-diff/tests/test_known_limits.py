"""Known limits, pinned as tests (JS2 D19): runs that end cleanly and are wrong, kept on purpose for now.

Why tests for behavior we don't want: a limit written only in prose is easy to forget, and easy to
"fix" by accident without anyone deciding to. Each test here asserts today's wrong outcome and says
so in its name. When a fix is decided (JS2 plan, "Later"), the test fails on purpose and is
rewritten to assert the right outcome, which is the point at which the limit is gone.
"""

from fakes import FakeClaude, board, board_row, by_id, job, run_once

from job_agent.loop import exits

# Seattle is in the US, so Aarav (profile: US locations) would want this posting. The rule reads
# the location literally and finds no "us" / "united states" in "Seattle, WA" (CONTRACT Known
# limits, "Location is read literally"), so check 2 cuts it. Everything else about it is GOOD.
MISSED = {"location": "Seattle, WA"}


def test_known_limit_with_claude_off_a_relevant_posting_the_rule_misses_is_not_flagged_and_the_run_finishes(paths):
    """With Claude off (the default, D1), nothing but the rule ever looks at the posting: it is on
    the report only as one not_relevant row, and like every handled posting it is not shown again."""
    claude = FakeClaude()   # would answer "relevant" if it were ever asked
    run_once(paths, board(job(1)), n=0, ask=claude)                                # baseline

    second = run_once(paths, board(job(1), job(2, **MISSED)), n=1, ask=claude)
    assert by_id(second)[2]["verdict"] == "not_relevant"                           # the rule misses it ...
    assert by_id(second)[2]["justification"][-1]["posting_field"] == "location.name"  # ... at check 2
    assert claude.sent == []                                                       # Claude never sees it
    assert second["exit"] == exits.FINISHED and board_row(second)["status"] == "ok"   # and nothing looks wrong

    third = run_once(paths, board(job(1), job(2, **MISSED)), n=2, ask=claude)
    assert third["verdicts"] == []                                                 # handled: not new any more


def test_with_claude_on_the_miss_is_flagged_as_a_disagreement(paths):
    """D20: with --claude and budget left, Claude sees the posting and its "relevant" stands next
    to the rule's "not_relevant" on the report, which is the flag. The id still goes into state like
    every handled posting: re-sending it would only get the same answer again (D19, reworded)."""
    claude = FakeClaude()
    run_once(paths, board(job(1)), n=0, ask=claude, use_claude=True)
    second = run_once(paths, board(job(1), job(2, **MISSED)), n=1, ask=claude, use_claude=True)
    assert claude.sent == [2]
    assert (by_id(second)[2]["verdict"], by_id(second, "claude")[2]["verdict"]) == ("not_relevant", "relevant")
    third = run_once(paths, board(job(1), job(2, **MISSED)), n=2, ask=claude, use_claude=True)
    assert third["verdicts"] == []
