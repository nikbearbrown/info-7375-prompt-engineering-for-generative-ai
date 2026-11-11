"""A record of every observation, written as it happens.

GATE.md §1 E2 says the exit status is *derived from the trace*, not asserted by
the code that wanted to succeed. That only works if the trace is the primary
record, so every attempt — including the ones that failed, including the
retries — appends a line here before the loop decides anything.

The format is JSON Lines, one observation per line, so a truncated run still
leaves a readable trace.

The trace is a file the agent creates, so it goes through `Policy.check_write`
like every other one (GATE.md §5.2, amendment A3). It did not, until
2026-11-09; `tests/test_all_writes_go_through_the_policy.py` is what found that
and is what keeps it true. `policy` is optional only so that a Trace can be
used in-memory with no path at all.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .http import utc_now


@dataclass
class Observation:
    seq: int
    board: str
    provider: str
    attempt: int
    method: str
    url: str
    at: str
    elapsed_ms: int
    outcome: str                      # ok | transient | permanent | schema | policy | budget
    http_status: int | None = None
    postings: int | None = None
    raw_path: str | None = None
    raw_sha256: str | None = None
    error_class: str | None = None
    error: str | None = None
    retry_scheduled: bool = False
    note: str | None = None


@dataclass
class Trace:
    path: Path | None = None
    observations: list[Observation] = field(default_factory=list)
    policy: object | None = None

    def record(self, **kwargs) -> Observation:
        obs = Observation(seq=len(self.observations) + 1, at=utc_now(), **kwargs)
        if self.path is not None:
            # Checked before the observation is kept, so a refused trace path
            # cannot leave the in-memory trace and the file disagreeing.
            if self.policy is not None:
                self.policy.check_write(self.path)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(asdict(obs), ensure_ascii=False) + "\n")
        self.observations.append(obs)
        return obs

    # --- what the exit status is derived from -------------------------------

    def boards_attempted(self) -> list[str]:
        seen = []
        for obs in self.observations:
            if obs.board not in seen:
                seen.append(obs.board)
        return seen

    def final_outcome_per_board(self) -> dict[str, str]:
        """The last recorded outcome for each board, which is its verdict."""
        out: dict[str, str] = {}
        for obs in self.observations:
            out[obs.board] = obs.outcome
        return out

    def requests_used(self) -> int:
        """Every outbound attempt, retries included (GATE.md §2)."""
        return sum(1 for obs in self.observations if obs.outcome != "budget")

    def as_dicts(self) -> list[dict]:
        return [asdict(obs) for obs in self.observations]
