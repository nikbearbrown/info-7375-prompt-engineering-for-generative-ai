"""The loop's budgets (GATE §2): how many boards, how many board requests, how many seconds.

Why the limits are constants and not command-line options: GATE says only Isaac may change a
budget, after a written decision in DECISIONS.md. An option would let anyone (or an agent) raise
them at run time. Tests pass their own Limits to the loop in code to reach the edges quickly.
"""

import time
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Limits:
    boards: int = 4                 # three normal boards + the one that fails on purpose
    requests: int = 10              # every outgoing board request, retries included
    seconds: float = 120.0          # whole board phase, Claude off
    request_seconds: float = 10.0   # one request: a slow board can't eat the whole run
    # Claude, only with --claude (D1, D20): 120 s boards + 300 s Claude in total + 60 s reporting.
    claude_calls: int = 30          # = at most 30 new postings sent, whatever the rule said (D20)
    claude_seconds: float = 300.0   # all Claude calls together, not each one (Isaac: 300 s already costs tokens)
    seconds_with_claude: float = 480.0
    report_reserve_seconds: float = 60.0


# GATE §2, 2026-11-08. Change only with a DECISIONS.md entry signed by Isaac.
LIMITS = Limits()


class Budget:
    """Counts what one run has used. clock is injectable so tests can make time pass without waiting."""

    def __init__(self, limits: Limits = LIMITS, clock=time.monotonic):
        self.limits, self.clock = limits, clock
        self.started_at = clock()
        self.boards_used = 0
        self.requests_used = 0
        self.claude_calls_used = 0
        self.claude_seconds_used = 0.0

    def seconds_used(self) -> float:
        return self.clock() - self.started_at

    def seconds_left(self) -> float:
        return self.limits.seconds - self.seconds_used()

    def stops_board(self) -> str | None:
        """The name of the budget that forbids starting another board, or None. Requests are
        checked here too: a board that can't make even one request would only fail."""
        if self.boards_used >= self.limits.boards:
            return "boards"
        return self.stops_request()

    def stops_request(self) -> str | None:
        if self.requests_used >= self.limits.requests:
            return "requests"
        if self.seconds_left() <= 0:
            return "seconds"
        return None

    def start_board(self) -> None:
        self.boards_used += 1

    def start_request(self) -> float:
        """Count the request and return its timeout: 10 s or the board time left, whichever is lower."""
        self.requests_used += 1
        return min(self.limits.request_seconds, self.seconds_left())

    def claude_seconds_left(self) -> float:
        """Claude time left: the 300 s shared by all calls, and never past the reporting reserve, so
        the record is still written even if the board phase ran long."""
        to_reserve = self.limits.seconds_with_claude - self.limits.report_reserve_seconds - self.seconds_used()
        return min(self.limits.claude_seconds - self.claude_seconds_used, to_reserve)

    def stops_claude(self) -> str | None:
        """GATE §2 (D20): another call may start while calls and Claude time are left. There is no
        per-call cap, so the last call may be cut short (D20 (4), accepted for a 300 s total)."""
        if self.claude_calls_used >= self.limits.claude_calls:
            return "claude calls"
        if self.claude_seconds_left() <= 0:
            return "claude seconds"
        return None

    def start_claude(self) -> float:
        """Count the call and return its timeout: all the Claude time that is left."""
        self.claude_calls_used += 1
        return self.claude_seconds_left()

    def end_claude(self, seconds: float) -> None:
        """Charge a finished call's real duration to the shared Claude time."""
        self.claude_seconds_used += seconds

    def snapshot(self) -> dict:
        """Used and left for each budget; written into the trace and the summary."""
        return {
            "limits": asdict(self.limits),
            "boards_used": self.boards_used,
            "requests_used": self.requests_used,
            "requests_left": self.limits.requests - self.requests_used,
            "seconds_used": round(self.seconds_used(), 3),
            "seconds_left": round(max(self.seconds_left(), 0.0), 3),
            "claude_calls_used": self.claude_calls_used,
            "claude_seconds_used": round(self.claude_seconds_used, 3),
        }
