"""The bounded loop (GATE.md §1–§4).

Shape of one run: for each board in the plan, attempt it; classify any failure
by exception class; retry only where §4 says a retry is sound; stop the moment
a budget is reached; record every attempt in the trace; and let the exit status
be *derived* from that trace afterwards.

What this module is careful never to do: turn a failure into a number. A board
that failed contributes no postings and appears in the report as failed. The
tempting one-liner that makes it appear as `{"new": 0}` is wrong version W1.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from . import providers
from .errors import (
    AgentError,
    BudgetExhausted,
    PermanentFailure,
    PolicyRefusal,
    SchemaFailure,
    TransientFailure,
)
from .http import fetch as http_fetch
from .http import parse_json, sha256, utc_stamp
from .policy import Policy
from .trace import Trace

LOOP_VERSION = "L-v1"

#: GATE.md §4: backoff for the `transient` class only.
BACKOFF_SECONDS = (1.0, 3.0)


@dataclass(frozen=True)
class Budget:
    """GATE.md §2. Read from config/budget.json; never widened at runtime."""

    boards: int
    requests: int
    seconds: float
    retries_per_board: int

    @classmethod
    def from_file(cls, path: str | Path) -> "Budget":
        import json

        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            boards=int(data["boards"]),
            requests=int(data["requests"]),
            seconds=float(data["seconds"]),
            retries_per_board=int(data["retries_per_board"]),
        )

    def as_dict(self) -> dict:
        return {
            "boards": self.boards,
            "requests": self.requests,
            "seconds": self.seconds,
            "retries_per_board": self.retries_per_board,
        }


@dataclass
class BoardOutcome:
    board: str
    provider: str
    token: str
    status: str                  # ok | transient | permanent | schema | policy
    attempts: int
    postings: list = field(default_factory=list)
    raw: dict | None = None
    error_class: str | None = None
    error: str | None = None
    deliberate: bool = False
    note: str | None = None

    @property
    def observed(self) -> bool:
        return self.status == "ok"


@dataclass
class RunResult:
    outcomes: list[BoardOutcome]
    trace: Trace
    planned: int
    budget: Budget
    budget_hit: str | None
    seconds_used: float
    started_at: str
    skipped: list[str] = field(default_factory=list)


def _save_raw(policy: Policy, raw_dir: Path, board: str, body: bytes) -> dict:
    """Write the response bytes as evidence, through the write policy."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    safe = board.replace(":", "-").replace("/", "-")
    path = raw_dir / f"{utc_stamp()}-{safe}.json"
    policy.check_write(path)
    path.write_bytes(body)
    return {"path": str(path), "bytes": len(body), "sha256": sha256(body)}


def run(
    plan: list[dict],
    *,
    policy: Policy,
    budget: Budget,
    raw_dir: Path,
    trace: Trace,
    fetcher=http_fetch,
    timeout: float = 20.0,
    sleep=time.sleep,
    clock=time.monotonic,
) -> RunResult:
    """Run the loop once. Raises nothing for board faults; only for `error`.

    A `PolicyRefusal` is re-raised: GATE.md §4 says a policy refusal aborts the
    run, because it means the plan or the code is wrong, not the world.
    """
    from .http import utc_now

    started_at = utc_now()
    t0 = clock()
    outcomes: list[BoardOutcome] = []
    skipped: list[str] = []
    budget_hit: str | None = None
    requests_used = 0

    for index, entry in enumerate(plan):
        board = entry["board"]
        token = entry["token"]
        provider_name = entry["provider"]
        deliberate = bool(entry.get("deliberate_failure"))

        # --- budgets are checked before each board, and before each retry ---
        if index >= budget.boards:
            budget_hit = "boards"
            skipped.extend(e["board"] for e in plan[index:])
            trace.record(
                board=board, provider=provider_name, attempt=0, method="GET",
                url="", elapsed_ms=0, outcome="budget",
                note=f"board budget {budget.boards} reached before this board",
            )
            break
        if clock() - t0 >= budget.seconds:
            budget_hit = "seconds"
            skipped.extend(e["board"] for e in plan[index:])
            trace.record(
                board=board, provider=provider_name, attempt=0, method="GET",
                url="", elapsed_ms=0, outcome="budget",
                note=f"second budget {budget.seconds}s reached before this board",
            )
            break

        provider = providers.get(provider_name)
        url = provider.url_for(token)

        # GATE.md §3: one note per action, before the first attempt. Retries do
        # not re-notify, which is how "a retry is the one exception" is
        # implemented rather than merely asserted.
        try:
            policy.note_action("GET", url)
        except PolicyRefusal:
            trace.record(
                board=board, provider=provider_name, attempt=0, method="GET",
                url=url, elapsed_ms=0, outcome="policy",
                error_class="RepeatedAction",
            )
            raise

        attempt = 0
        outcome: BoardOutcome | None = None

        while True:
            attempt += 1
            if requests_used >= budget.requests:
                budget_hit = "requests"
                skipped.extend(e["board"] for e in plan[index:])
                trace.record(
                    board=board, provider=provider_name, attempt=attempt,
                    method="GET", url=url, elapsed_ms=0, outcome="budget",
                    note=f"request budget {budget.requests} reached",
                )
                break

            a0 = clock()
            try:
                body, status = fetcher(policy, url, timeout=timeout)
                requests_used += 1
                payload = parse_json(board, body)
                postings = provider.parse(board, payload)
                raw = _save_raw(policy, raw_dir, board, body)
                trace.record(
                    board=board, provider=provider_name, attempt=attempt,
                    method="GET", url=url,
                    elapsed_ms=int((clock() - a0) * 1000), outcome="ok",
                    http_status=status, postings=len(postings),
                    raw_path=raw["path"], raw_sha256=raw["sha256"],
                )
                outcome = BoardOutcome(
                    board=board, provider=provider_name, token=token, status="ok",
                    attempts=attempt, postings=postings, raw=raw,
                    deliberate=deliberate,
                )
                break

            except PolicyRefusal:
                # GATE.md §4: abort the run. Record it first so the trace shows
                # why, then let it out of the loop.
                requests_used += 1
                trace.record(
                    board=board, provider=provider_name, attempt=attempt,
                    method="GET", url=url,
                    elapsed_ms=int((clock() - a0) * 1000), outcome="policy",
                    error_class="PolicyRefusal",
                )
                raise

            except (TransientFailure, PermanentFailure, SchemaFailure) as exc:
                requests_used += 1
                kind = exc.classification
                may_retry = (
                    kind == "transient"
                    and (attempt - 1) < budget.retries_per_board
                    and requests_used < budget.requests
                )
                trace.record(
                    board=board, provider=provider_name, attempt=attempt,
                    method="GET", url=url,
                    elapsed_ms=int((clock() - a0) * 1000), outcome=kind,
                    error_class=type(exc).__name__, error=str(exc),
                    retry_scheduled=may_retry,
                )
                if may_retry:
                    sleep(BACKOFF_SECONDS[min(attempt - 1, len(BACKOFF_SECONDS) - 1)])
                    continue
                outcome = BoardOutcome(
                    board=board, provider=provider_name, token=token, status=kind,
                    attempts=attempt, error_class=type(exc).__name__, error=str(exc),
                    deliberate=deliberate,
                )
                break

        if outcome is not None:
            outcomes.append(outcome)
        if budget_hit:
            break

    return RunResult(
        outcomes=outcomes,
        trace=trace,
        planned=len(plan),
        budget=budget,
        budget_hit=budget_hit,
        seconds_used=round(clock() - t0, 3),
        started_at=started_at,
        skipped=skipped,
    )


def replay_fetcher(raw_dir: Path):
    """A fetcher that reads saved responses instead of the network.

    Replay is a first-class mode, not a test hook: a TA has to be able to
    reproduce the run, the deliberate failure and the finished-wrong-answer
    demonstration from a fresh clone with no network at all. Every run report
    records which mode produced it.
    """
    raw_dir = Path(raw_dir)

    def fetch(policy: Policy, url: str, *, timeout: float = 20.0):
        policy.check_request("GET", url)
        name = _replay_name(url)
        path = raw_dir / name
        if not path.exists():
            raise PermanentFailure(
                f"replay: no saved response at {path} for {url}"
            )
        return path.read_bytes(), 200

    return fetch


def _replay_name(url: str) -> str:
    """Map a board URL to its fixture filename, deterministically."""
    from urllib.parse import urlsplit

    parts = urlsplit(url)
    host = parts.hostname or ""
    token = parts.path.rstrip("/").split("/")[-1]
    if host.endswith("greenhouse.io"):
        token = parts.path.rstrip("/").split("/")[-2]
        return f"greenhouse-{token}.json"
    if host.endswith("lever.co"):
        return f"lever-{token}.json"
    if host.endswith("ashbyhq.com"):
        return f"ashby-{token}.json"
    return f"{host}-{token}.json"
