"""The board loop (GATE "Loop, budgets, and exits", "Board failure policy"; F3–F15, F17, F20).

Boards are visited in config order. For each board: permission check, budget check, fetch,
save the raw bytes, validate, compare with that board's saved IDs, and record the result.
Timeouts and HTTP 5xx get one retry after a 1-second wait when F11 allows it; everything
else is a board failure with no retry (F9). The exit follows the precedence
error > budget-exhausted > incomplete > finished.
"""

import os
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from . import config as board_config
from . import limits, providers, state
from .budget import Budget
from .errors import (ConfigError, EvidenceError, MalformedResponse, PermissionDenied,
                     RequestDenied, StateError, TransportError, TransportTimeout)
from .fsio import STATE_NAME, FileGate
from .policy import check_request
from .trace import TRACE_NAME, Trace
from .transport import UrllibTransport, send

FINISHED = "finished"
ERROR = "error"
INCOMPLETE = "incomplete"
BUDGET_EXHAUSTED = "budget-exhausted"
EXIT_CODES = {FINISHED: 0, ERROR: 2, INCOMPLETE: 3, BUDGET_EXHAUSTED: 4}  # F15

NEXT_BOARD = "record failure; next board"


def resolve_exit(*, fatal: bool, budget_limit: str | None, any_failed: bool) -> str:
    """GATE precedence: error > budget-exhausted > incomplete > finished."""
    if fatal:
        return ERROR
    if budget_limit:
        return BUDGET_EXHAUSTED
    if any_failed:
        return INCOMPLETE
    return FINISHED


def new_run_id() -> str:
    return datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ-") + secrets.token_hex(3)


@dataclass
class BoardResult:
    board: providers.Board
    status: str = "pending"  # pending | succeeded | failed
    fetched: int | None = None
    new: int | None = None
    new_ids: list | None = None
    jobs_in_response: int | None = None
    duplicates_removed: int | None = None
    baseline: bool | None = None
    attempts: int = 0
    raw_paths: list = field(default_factory=list)
    failure: dict | None = None
    retry_pending: bool = False

    def fail(self, kind: str, detail: str, *, status=None, first_failure=None, retry_pending=False):
        self.status = "failed"
        self.fetched = self.new = self.new_ids = None  # F15: unset counts are null
        self.failure = {"kind": kind, "detail": detail, "status": status}
        if first_failure is not None:
            self.failure["first_failure"] = first_failure
        self.retry_pending = retry_pending

    def as_dict(self) -> dict:
        return {
            "board": self.board.key,
            "provider": self.board.provider,
            "token": self.board.token,
            "status": self.status,
            "fetched": self.fetched,
            "new": self.new,
            "new_ids": self.new_ids,
            "jobs_in_response": self.jobs_in_response,
            "duplicates_removed": self.duplicates_removed,
            "baseline": self.baseline,
            "attempts": self.attempts,
            "raw_paths": self.raw_paths,
            "failure": self.failure,
            "retry_pending": self.retry_pending,
        }


@dataclass
class Outcome:
    kind: str
    status: int | None = None
    error: str | None = None
    raw_path: str | None = None
    parsed: providers.ParsedJobs | None = None
    retryable: bool = False
    timeout: float | None = None

    def brief(self) -> dict:
        return {"kind": self.kind, "status": self.status, "error": self.error, "raw_path": self.raw_path}


@dataclass
class RunResult:
    exit: str
    code: int
    summary: dict
    summary_path: str | None  # relative to the output root; None if it could not be written
    output_root: str | None
    message: str | None = None


class Runner:
    def __init__(self, config_path, out_dir, *, transport, clock, sleep, run_id, mode):
        self.budget = Budget(clock, sleep)  # the run clock starts here
        self.config_path = config_path
        self.out_dir = out_dir
        self.transport = transport
        self.run_id = run_id
        self.mode = mode
        self.gate = None
        self.trace = None
        self.store = None
        self.results: list[BoardResult] = []
        self.duplicates: list[dict] = []
        self.limit_hit: str | None = None
        self.fatal: dict | None = None
        self.snapshot_path: str | None = None
        self.state_written = False

    # ---------- run ----------

    def run(self) -> RunResult:
        try:
            self.gate = FileGate(self.out_dir, self.run_id, config_path=self.config_path)
        except (PermissionDenied, OSError) as err:
            return self._unavailable(f"output folder unavailable: {err}")
        self.run_dir = self.gate.root / "runs" / self.run_id
        if os.path.lexists(self.run_dir):
            return self._unavailable(f"run folder {self.run_dir} already exists")
        self.trace = Trace(self.gate, self.run_dir, self.budget.elapsed)
        try:
            self._execute()
        except EvidenceError as err:
            self.fatal = {"stage": "evidence", "message": str(err)}
        except Exception as err:  # safety net: an unexpected failure still ends as exit error
            self.fatal = {"stage": "internal", "message": f"{type(err).__name__}: {err}"}
        return self._finalize()

    def _execute(self) -> None:
        self.trace.event("run-start", "load config", run_id=self.run_id, mode=self.mode)
        try:
            cfg = board_config.load_config(self.gate, self.config_path)
        except ConfigError as err:
            self.fatal = {"stage": "config", "message": str(err)}
            self.trace.event("config", "stop: exit error before any transport call", error=str(err))
            return
        self.results = [BoardResult(board) for board in cfg.boards]
        self.trace.event("config", "load state", status="valid", boards=[b.key for b in cfg.boards])
        for dup in cfg.duplicates:
            entry = {"board": dup.board.key, "config_index": dup.index, "kept_index": dup.first_index}
            self.duplicates.append(entry)
            self.trace.event("config-duplicate", "skip duplicate", board=dup.board.key,
                             config_index=dup.index, kept_index=dup.first_index)

        try:
            loaded = state.load_state(self.gate)
        except StateError as err:
            self.fatal = {"stage": "state", "message": str(err)}
            self.trace.event("state-load", "stop: exit error before any transport call", error=str(err))
            return
        self.snapshot_path = state.write_snapshot(self.gate, self.run_dir, loaded)
        self.store = state.StateStore(loaded)
        self.trace.event(
            "state-load", "visit boards in config order",
            status="no state file" if loaded.entries is None else f"{len(loaded.entries)} board entries",
            snapshot=self.snapshot_path,
        )
        for result in self.results:
            if not self._visit(result):
                break

    # ---------- one board ----------

    def _visit(self, result: BoardResult) -> bool:
        """Process one board. Returns False when a budget limit stops the loop."""
        board, key = result.board, result.board.key
        url = providers.listing_url(board)
        try:
            check_request("GET", url, board)
        except RequestDenied as err:  # F7: a denial during the run is a board failure
            result.fail("permission-denied", str(err))
            self.trace.event("permission-check", NEXT_BOARD, board=key, error=str(err))
            return True
        self.trace.event("permission-check", "budget check", board=key, status="allowed")

        limit = self.budget.check_attempt()
        if limit:
            self.limit_hit = limit
            self.trace.event("budget-check", "stop: this and later boards pending", board=key,
                             error=f"{limit} limit reached")
            return False

        first = self._attempt(result, url, 1)
        if first.kind == "ok":
            return self._succeed(result, first, 1)
        if not first.retryable:
            self._trace_attempt(key, 1, first, NEXT_BOARD)
            result.fail(first.kind, first.error, status=first.status)
            return True

        # F11: a timeout or 5xx gets one retry if the budget allows the wait and an attempt.
        limit = self.budget.check_retry_before_wait()
        if limit:
            return self._retry_pending(result, first, limit, "before the wait", attempt=1)
        self._trace_attempt(key, 1, first, f"wait {limits.RETRY_WAIT_SECONDS} s, then retry")
        self.budget.wait_for_retry()
        limit = self.budget.check_retry_after_wait()
        if limit:
            return self._retry_pending(result, first, limit, "after the wait", attempt=None)
        self.trace.event("retry-wait", "retry", board=key, attempt=2, status="budget ok")

        second = self._attempt(result, url, 2)
        if second.kind == "ok":
            return self._succeed(result, second, 2)
        self._trace_attempt(key, 2, second, NEXT_BOARD + " (no second retry)")
        result.fail(second.kind, second.error, status=second.status, first_failure=first.brief())
        return True

    def _retry_pending(self, result, first: Outcome, limit: str, when: str, attempt) -> bool:
        """F13: keep the original failure in the trace, report the retry pending, stop."""
        self.limit_hit = limit
        next_step = f"retry pending ({limit} limit {when}); stop"
        if attempt is not None:
            self._trace_attempt(result.board.key, attempt, first, next_step)
        else:
            self.trace.event("retry-wait", next_step, board=result.board.key, error=f"{limit} limit reached")
        result.fail(first.kind, first.error, status=first.status, retry_pending=True)
        return False

    def _trace_attempt(self, key, attempt: int, outcome: Outcome, next_step: str) -> None:
        self.trace.event("fetch", next_step, board=key, attempt=attempt, status=outcome.status,
                         error=outcome.error, raw_path=outcome.raw_path, outcome=outcome.kind,
                         timeout_s=outcome.timeout)

    def _attempt(self, result: BoardResult, url: str, attempt: int) -> Outcome:
        board = result.board
        timeout = self.budget.attempt_timeout()

        def counted(method, request_url, request_timeout):
            self.budget.record_attempt()  # F8: every transport call counts, even if it fails
            result.attempts += 1
            return self.transport(method, request_url, request_timeout)

        try:
            response = send(board, "GET", url, transport=counted, timeout=timeout)
        except RequestDenied as err:
            return Outcome("permission-denied", error=str(err), timeout=timeout)
        except TransportTimeout as err:
            return Outcome("timeout", error=str(err), retryable=True, timeout=timeout)
        except TransportError as err:
            return Outcome("transport-error", error=str(err), timeout=timeout)

        raw_path = None
        if response.body:  # save the bytes before anything parses them
            try:
                raw_path = self.trace.save_raw(board, attempt, response.body)
            except EvidenceError as err:
                result.fail("evidence-not-saved", str(err), status=response.status)
                raise
            result.raw_paths.append(raw_path)

        status = response.status
        found = dict(status=status, raw_path=raw_path, timeout=timeout)
        if status == 200:
            try:
                parsed = providers.parse_ids(board.provider, response.body)
            except MalformedResponse as err:
                return Outcome("malformed", error=str(err), **found)
            return Outcome("ok", parsed=parsed, **found)
        if 500 <= status <= 599:
            return Outcome("http-5xx", error=f"HTTP {status}", retryable=True, **found)
        if 300 <= status <= 399:
            return Outcome("redirect", error=f"HTTP {status} redirect to {response.location!r} refused; not followed", **found)
        if status == 404:
            return Outcome("http-404", error="HTTP 404", **found)
        if 400 <= status <= 499:
            return Outcome("http-4xx", error=f"HTTP {status}", **found)
        return Outcome("unexpected-status", error=f"HTTP {status}", **found)

    def _succeed(self, result: BoardResult, outcome: Outcome, attempt: int) -> bool:
        board, key, parsed = result.board, result.board.key, outcome.parsed
        self._trace_attempt(key, attempt, outcome, "validate response")
        self.trace.event("validate", "compare with this board's saved IDs", board=key, attempt=attempt,
                         status="valid", raw_path=outcome.raw_path, jobs_in_response=parsed.jobs_in_response,
                         unique_ids=len(parsed.ids), duplicates_removed=parsed.duplicates_removed)
        seen = self.store.seen(board)
        fresh = state.new_ids(seen, parsed.ids)
        self.store.stage(board, parsed.ids)  # only after the raw response is saved and valid
        result.status = "succeeded"
        result.fetched = len(parsed.ids)
        result.new = len(fresh)
        result.new_ids = list(fresh)
        result.jobs_in_response = parsed.jobs_in_response
        result.duplicates_removed = parsed.duplicates_removed
        result.baseline = seen is None
        self.trace.event("diff", "stage seen IDs; next board", board=key, baseline=seen is None,
                         fetched=result.fetched, new=result.new)
        return True

    # ---------- finish ----------

    def _pending(self) -> list[dict]:
        pending = [{"board": r.board.key, "pending": "retry"} for r in self.results if r.retry_pending]
        pending += [{"board": r.board.key, "pending": "board"} for r in self.results if r.status == "pending"]
        return pending

    def _summary(self, exit_name: str) -> dict:
        return {
            "run_id": self.run_id,
            "mode": self.mode,
            "exit": exit_name,
            "exit_code": EXIT_CODES[exit_name],
            "config": str(self.config_path),
            "output_root": str(self.gate.root) if self.gate else str(self.out_dir),
            "limits": {
                "max_distinct_boards": limits.MAX_DISTINCT_BOARDS,
                "max_http_attempts": limits.MAX_HTTP_ATTEMPTS,
                "run_seconds": limits.RUN_SECONDS,
                "network_window_seconds": limits.NETWORK_WINDOW_SECONDS,
                "attempt_cap_seconds": limits.ATTEMPT_CAP_SECONDS,
                "retry_wait_seconds": limits.RETRY_WAIT_SECONDS,
            },
            "attempts_used": self.budget.attempts_used,
            "elapsed_s": round(self.budget.elapsed(), 3),
            "budget_limit_hit": self.limit_hit,
            "boards": [r.as_dict() for r in self.results],
            "duplicates_skipped": self.duplicates,
            "pending": self._pending(),
            "error": self.fatal,
            "state": {
                "path": STATE_NAME,
                "pre_run_snapshot": self.snapshot_path,
                "staged_boards": sorted(self.store.staged) if self.store else [],
                "written": self.state_written,
            },
            "trace": str((self.run_dir / TRACE_NAME).relative_to(self.gate.root)) if self.trace else None,
        }

    def _finalize(self) -> RunResult:
        any_failed = any(r.status == "failed" for r in self.results)
        exit_name = resolve_exit(fatal=self.fatal is not None, budget_limit=self.limit_hit, any_failed=any_failed)
        summary_path, message = None, None
        try:
            next_step = "stop: state.json left unchanged" if exit_name == ERROR else "write summary, then state.json"
            self.trace.event("exit", next_step, status=exit_name, error=(self.fatal or {}).get("message"))
            summary_path = self.trace.write_summary(self._summary(exit_name))
        except EvidenceError as err:
            self.fatal = self.fatal or {"stage": "evidence", "message": str(err)}
            exit_name = ERROR
        if exit_name != ERROR:
            # F5: evidence first, then one atomic replace of state.json.
            try:
                state.commit(self.gate, self.store)
            except EvidenceError as err:
                self.fatal = {"stage": "evidence", "message": str(err)}
                exit_name = ERROR
            else:
                self.state_written = True
            try:
                self.trace.event("state-write", "done" if self.state_written else "stop: state.json left unchanged",
                                 status="written" if self.state_written else "not written",
                                 error=(self.fatal or {}).get("message"))
                summary_path = self.trace.write_summary(self._summary(exit_name))
            except EvidenceError as err:
                # The state write already happened (or failed atomically); keep the exit it earned.
                message = f"could not update the summary after the state write: {err}"
        if self.fatal:
            message = self.fatal["message"]
        summary = self._summary(exit_name)
        return RunResult(exit_name, EXIT_CODES[exit_name], summary, summary_path, str(self.gate.root), message)

    def _unavailable(self, message: str) -> RunResult:
        self.fatal = {"stage": "output", "message": message}
        summary = {
            "run_id": self.run_id, "mode": self.mode, "exit": ERROR, "exit_code": EXIT_CODES[ERROR],
            "config": str(self.config_path), "output_root": str(self.out_dir),
            "boards": [], "duplicates_skipped": [], "pending": [], "error": self.fatal,
            "state": {"written": False},
        }
        return RunResult(ERROR, EXIT_CODES[ERROR], summary, None, None, message)


def run(config_path, out_dir, *, transport=None, clock=time.monotonic, sleep=time.sleep, run_id=None) -> RunResult:
    """Run the agent once. With no transport given, it uses the live urllib transport."""
    mode = "live" if transport is None else "injected-transport"
    if transport is None:
        transport = UrllibTransport(clock=clock)
    return Runner(config_path, out_dir, transport=transport, clock=clock, sleep=sleep,
                  run_id=run_id or new_run_id(), mode=mode).run()
