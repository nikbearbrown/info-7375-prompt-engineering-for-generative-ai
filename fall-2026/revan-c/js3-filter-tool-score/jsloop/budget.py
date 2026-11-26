"""Run limits (GATE.md, Budgets). Only a new written decision in GATE.md changes PRODUCTION_BUDGET."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Budget:
    max_boards: int
    max_requests: int
    max_seconds: float        # deadline for the whole run, including saving the trace
    request_timeout: float    # upper bound for one request
    finalize_reserve: float   # kept back so the trace can always be saved

    @property
    def min_seconds_to_start_request(self):
        return self.request_timeout + self.finalize_reserve


PRODUCTION_BUDGET = Budget(max_boards=4, max_requests=4, max_seconds=45.0,
                           request_timeout=8.0, finalize_reserve=2.0)
