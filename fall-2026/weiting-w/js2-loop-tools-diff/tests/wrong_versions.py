"""The plausible-but-wrong implementations from GATE.md §7.

Real code, not descriptions of code. The contract tests are run against these
as well as against the real implementation, and a test that passes on one of
these is a test that proves nothing.
"""

from __future__ import annotations

from pathlib import Path

from agent.errors import NeedsApproval, PathEscapes, TransientFailure
from agent.policy import Policy


class PrefixPathPolicy(Policy):
    """W2 — the write boundary as a string prefix test.

    Plausible because it is the obvious one-liner, it reads correctly, and it
    passes every test that only tries `..`. It admits `evidence-evil/x.json`,
    because that string really does start with the output root's string.
    """

    def check_write(self, path):
        path = Path(path)
        if not str(path.resolve()).startswith(str(self.output_root.resolve())):
            raise PathEscapes(f"{path} is outside {self.output_root}")
        if (
            self.output_root / "raw"
        ).resolve() in path.resolve().parents and path.exists():
            if not self.approve_overwrite:
                raise NeedsApproval(f"{path} exists")
        return path


class NoRepeatPolicy(Policy):
    """W4 — no repeat rule: the same (method, url) may be issued twice."""

    def note_action(self, method: str, url: str) -> None:
        return None


def report_failure_as_zero(result, *, policy, resume) -> dict:
    """W1 — fold a failed board into the report as `{"postings_seen": 0}`.

    Plausible because a failed board and an empty board look alike at the point
    where you build the summary row, and the row needs a number. Every count
    here is defensible on its own. The run claims `finished` while a board was
    never observed, which is the part no count-based test can see.
    """
    boards = []
    for outcome in result.outcomes:
        boards.append(
            {
                "board": outcome.board,
                "provider": outcome.provider,
                "token": outcome.token,
                "status": outcome.status,
                "attempts": outcome.attempts,
                "deliberate_failure": outcome.deliberate,
                # the bug: a number where there is no observation
                "postings_seen": len(outcome.postings),
            }
        )
    return {
        "exit_status": "finished",      # the other half of the bug
        "complete": True,
        "boards": boards,
        "usage": {
            "boards_planned": result.planned,
            "boards_attempted": len(result.outcomes),
            "boards_observed": len(result.outcomes),
            "boards_failed": 0,
            "boards_skipped": result.skipped,
            "requests_used": result.trace.requests_used(),
            "requests_limit": result.budget.requests,
            "seconds_used": result.seconds_used,
            "seconds_limit": result.budget.seconds,
        },
    }


def flap_without_counting_requests(fetcher, policy, url, *, max_attempts=50) -> int:
    """W3 — retry a transient failure without counting it against the budget.

    Plausible because the retry loop and the budget check live in different
    parts of the function, and the retry is "the same request, just again".
    Returns the number of attempts made, which on a permanently flapping board
    is `max_attempts` rather than anything the budget chose.
    """
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        try:
            return fetcher(policy, url)
        except TransientFailure:
            continue
    return attempts
