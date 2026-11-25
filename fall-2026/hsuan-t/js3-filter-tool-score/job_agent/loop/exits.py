"""The run's exit (GATE §1): finished, incomplete, budget-exhausted or error.

A pure function of the board results, so the precedence rule can be tested row by row without
running anything. "A loop that stops is not a loop that succeeded" (JS2 D3): finished needs every
board ok.
"""

from .results import FAILED, OK, BoardResult

FINISHED, INCOMPLETE, BUDGET_EXHAUSTED, ERROR = "finished", "incomplete", "budget-exhausted", "error"


def decide(results: list[BoardResult], shared_error: str | None = None,
           other_budgets: tuple[str, ...] = ()) -> tuple[str, str]:
    """(exit, reason). GATE §1 order, first match wins: error for a shared failure, then
    budget-exhausted, then error when no board ended ok, then incomplete, then finished.

    other_budgets: budgets that stopped work outside the boards, e.g. "claude seconds" when a
    selected Claude call could not start (GATE §2: scheduled work a budget kept from finishing)."""
    if shared_error:
        return ERROR, shared_error
    stopped_by = sorted({r.budget for r in results if r.budget} | set(other_budgets))
    if stopped_by:
        return BUDGET_EXHAUSTED, f"budget used up: {', '.join(stopped_by)}"
    if not any(r.status == OK for r in results):
        return ERROR, "no board ended ok"
    not_ok = [r for r in results if r.status != OK]
    if not_ok:
        failed = sum(r.status == FAILED for r in not_ok)
        return INCOMPLETE, f"{len(not_ok)} of {len(results)} boards not ok ({failed} failed, {len(not_ok) - failed} skipped)"
    return FINISHED, f"all {len(results)} boards ok"
