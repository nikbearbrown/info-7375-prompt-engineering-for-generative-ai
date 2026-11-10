"""How one board ended (GATE §1): ok, failed (with a code) or skipped (never attempted).

Its own module because three readers depend on the exact shape: the exit decision, the report,
and the pipeline, which saves state only for `ok` boards (GATE WV2).
"""

from dataclasses import dataclass, field

from ..judges.rule import RuleResult
from ..watch.watcher import WatchResult
from . import codes

OK, FAILED, SKIPPED = "ok", "failed", "skipped"


@dataclass
class BoardResult:
    board: str
    ats: str
    status: str
    code: str | None = None          # set when failed
    reason: str = ""                 # the error message, or why the board was skipped
    budget: str | None = None        # the budget that stopped this board's work, if one did
    attempts: int = 0
    watch: WatchResult | None = None             # only for ok boards
    rule_results: list[RuleResult] = field(default_factory=list)

    @property
    def fetched(self) -> int | None:
        """None, never 0, when the board did not succeed: a failed board has no job count (GATE WV4)."""
        return self.watch.fetched if self.watch else None

    def row(self) -> dict:
        """The board's line in verdicts.json and the trace."""
        w = self.watch
        return {
            "board": self.board, "ats": self.ats, "status": self.status,
            "code": self.code, "code_meaning": codes.describe(self.code) if self.code else None,
            "reason": self.reason, "budget": self.budget, "attempts": self.attempts,
            "fetched": self.fetched, "new": len(w.new) if w else None,
            "baseline": w.baseline if w else None, "source": w.source if w else None,
        }
