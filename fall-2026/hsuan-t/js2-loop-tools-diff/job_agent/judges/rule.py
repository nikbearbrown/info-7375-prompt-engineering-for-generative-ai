"""The rule judge: runs the CHECKS in order and turns them into a 'record' verdict (R17).

It never guesses: each justification line names the posting field, what it was compared to, and
the result, so a TA can redo it by hand. The checks themselves live in checks.py.
"""

from dataclasses import dataclass

from . import verdict
from ..common.posting import Posting
from .checks import CHECKS, Criteria, PostingText

JUDGE = "rule"


@dataclass(frozen=True)
class RuleResult:
    verdict: dict
    failed_check: str | None   # id of the check that cut it; for the summary counts only, not saved


def judge(posting: Posting, criteria: Criteria) -> RuleResult:
    text = PostingText.of(posting)
    # Checked first: with no JD, checks 3-6 can't run, and "relevant" from the title alone would
    # look right while being unsupported (Wrong version 2). HTML with no text ("<p></p>") is empty too.
    if not text.jd.strip():
        return RuleResult(verdict.error(JUDGE, posting.id, "posting.content is empty, skills check cannot run"), None)

    lines = []
    for check in CHECKS:
        result = check.run(text, criteria)
        lines.append(result.line)
        if not result.passed:
            # The justification stops here, so its last line is the reason (CONTRACT Out).
            return RuleResult(verdict.ok(JUDGE, posting.id, verdict.NOT_RELEVANT, lines), check.id)
    return RuleResult(verdict.ok(JUDGE, posting.id, verdict.RELEVANT, lines), None)
