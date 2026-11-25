"""The gate's numbers (GATE.md, Exits and Budgets). They live here and nowhere else in the code.

A budget changes only by a new version of GATE.md: tests/test_gate.py fails if a number here and
the GATE.md table disagree. A command-line flag may lower a budget for one run, never raise it.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .errors import Refused

GATE_VERSION = "1.0"

MAX_BOARDS = 5
MAX_REQUESTS = 10
MAX_CLAUDE_CALLS = 20
MAX_SECONDS = 600
REQUEST_TIMEOUT = 30  # seconds for one request
RETRY_WAIT = 5  # seconds before the one retry a transient failure gets

FINISHED = "finished"
INCOMPLETE = "incomplete"
BUDGET_EXHAUSTED = "budget-exhausted"
ERROR = "error"
EXIT_CODES = {FINISHED: 0, INCOMPLETE: 1, BUDGET_EXHAUSTED: 4}
BROKEN_INPUT_CODE = 2
REFUSED_CODE = 3
# When more than one applies, the first in this order wins (GATE.md, Exits).
ORDER = (ERROR, BUDGET_EXHAUSTED, INCOMPLETE, FINISHED)


@dataclass(frozen=True)
class Budgets:
    boards: int = MAX_BOARDS
    requests: int = MAX_REQUESTS
    claude_calls: int = MAX_CLAUDE_CALLS
    seconds: int = MAX_SECONDS

    def lowered(self, **asked) -> "Budgets":
        """This run's budgets. Each value asked for must be a whole number from 0 up to the gate's limit."""
        changes = {}
        for name, value in asked.items():
            if value is None:
                continue
            flag = "--max-" + name.replace("_", "-")
            limit = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise Refused(f"refused: {flag} must be a whole number from 0 to {limit}")
            if value > limit:
                raise Refused(f"refused: {flag} {value} would raise the budget above {limit}; "
                              "a budget changes only by a new version of GATE.md")
            changes[name] = value
        return replace(self, **changes)

    def as_dict(self) -> dict:
        return {"boards": self.boards, "requests": self.requests, "claude_calls": self.claude_calls,
                "seconds": self.seconds}
