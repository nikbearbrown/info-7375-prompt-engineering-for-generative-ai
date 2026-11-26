"""Wrong versions W1-W9 of the JS2 loop and policy (GATE §8), wrong on purpose.

Each one replaces exactly one GATE rule. ``tests/watch/conftest.py`` swaps one in
when ``JSA_JS2_WRONG`` names it, and ``tests/meta/test_js2_wrong_versions_caught.py``
requires ``tests/watch`` to fail for every one.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import httpx

from job_search_agent.models import FetchResult, RunReport, RunStatus
from job_search_agent.policy import Approver, Decision, Verdict
from job_search_agent.watch import BoardOutcome, BudgetMeter, LoopExit, board_ok


def w1_decide_exit(
    boards: Sequence[BoardOutcome], *, stopped_by: str | None
) -> LoopExit:
    """W1: a loop that stopped is reported as finished, failures or not."""
    return LoopExit.BUDGET_EXHAUSTED if stopped_by else LoopExit.FINISHED


def w2_board_ok(report: RunReport) -> tuple[bool, str]:
    """W2: an empty board counts as checked, with "no new jobs"."""
    if report.status is RunStatus.EMPTY_RESPONSE:
        return True, "SUCCESS_NO_NEW"
    return board_ok(report)


def w3_is_transient(result: FetchResult) -> bool:
    """W3: retries every failure, a 404 and a 429 included."""
    return result.error is not None


def w4_request_refusal(self: BudgetMeter) -> str | None:
    """W4: the request budget is checked one request too late."""
    if self.requests > self.budget.max_requests:
        return "max_requests"
    return None if self.seconds_left() > 0 else "max_seconds"


def w5_inside(path: Path, root: Path) -> bool:
    """W5: containment by string prefix, so ``watch-evil`` is inside ``watch``."""
    return str(path.resolve()).startswith(str(root.resolve()))


def w6_inside(path: Path, root: Path) -> bool:
    """W6: containment without resolving symlinks."""
    return Path(os.path.normpath(path)).is_relative_to(os.path.normpath(root))


def w7_host_refusal(url: httpx.URL, allowed_hosts: frozenset[str]) -> str | None:
    """W7: the host is matched by suffix or substring."""
    if url.scheme != "https":
        return "scheme"
    host = url.host.lower()
    if not any(host.endswith(h) or h in str(url) for h in allowed_hosts):
        return "host"
    return None


def w8_board_key(provider: str, token: str) -> tuple[str, str]:
    """W8: the repeat key is case-sensitive."""
    return provider.strip(), token.strip()


def w9_settle(verdict: Verdict, *, approver: Approver | None, question: str) -> Verdict:
    """W9: with nobody to ask, the delete goes ahead."""
    if verdict.decision is Decision.NEEDS_APPROVAL and approver is None:
        return Verdict(Decision.ALLOW, "approved")
    if verdict.decision is Decision.NEEDS_APPROVAL:
        return Verdict(Decision.ALLOW if approver(question) else Decision.DENY, "x")
    return verdict


WRONG_VERSIONS: dict[str, tuple[Any, str, Callable[..., Any]]] = {
    "W1": ("job_search_agent.watch", "decide_exit", w1_decide_exit),
    "W2": ("job_search_agent.watch", "board_ok", w2_board_ok),
    "W3": ("job_search_agent.watch", "is_transient", w3_is_transient),
    "W4": (BudgetMeter, "request_refusal", w4_request_refusal),
    "W5": ("job_search_agent.policy", "inside", w5_inside),
    "W6": ("job_search_agent.policy", "inside", w6_inside),
    "W7": ("job_search_agent.policy", "host_refusal", w7_host_refusal),
    "W8": ("job_search_agent.watch", "board_key", w8_board_key),
    "W9": ("job_search_agent.watch", "settle", w9_settle),
}
"""Name -> (module path or class, attribute, replacement)."""
