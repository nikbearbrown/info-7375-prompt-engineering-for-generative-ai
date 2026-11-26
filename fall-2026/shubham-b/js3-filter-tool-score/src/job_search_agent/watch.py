"""The JS2 watch loop: several boards, one budget, one exit (GATE.md).

``run_loop`` reads a ``WatchPlan``, then for each planned board in order: checks the
budget, runs the JS1 one-board pass (``pipeline.run_once``) with a fetcher that asks
the permission policy before every request and retries a transient failure at most
once, and records the board's outcome. Every observation goes to
``data/watch/loops/<loop_id>/trace.jsonl``; the loop ends with exactly one
``LoopExit``, written to ``report.json`` and ``report.md`` beside the trace.

The functions ``board_key``, ``is_transient``, ``board_ok`` and ``decide_exit`` and the
method ``BudgetMeter.request_refusal`` hold the GATE rules; the wrong-version meta-test
swaps each one (GATE §8).
"""

from __future__ import annotations

import dataclasses
import time
import tomllib
from collections.abc import Callable, Sequence
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Final

import httpx
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError

from job_search_agent.clock import format_run_id
from job_search_agent.config import AgentConfig
from job_search_agent.errors import AgentError, ConfigError, InvalidResponse
from job_search_agent.events import EventLog
from job_search_agent.fsio import OutputRoot, create_output_root
from job_search_agent.http import build_fetcher_from_settings
from job_search_agent.models import (
    FetchErrorKind,
    FetchResult,
    JudgmentStatus,
    ParsedBoard,
    RunReport,
    RunStatus,
)
from job_search_agent.pipeline import NOTE_JUDGE_UNAVAILABLE, RunDeps, run_once
from job_search_agent.policy import (
    HOST_CEILING,
    WRITE_CEILING,
    Approver,
    PermissionPolicy,
    Verdict,
    inside,
    settle,
)
from job_search_agent.ports import BoardProvider, Clock, EventSink, HttpFetcher
from job_search_agent.providers import get_provider
from job_search_agent.sources import LiveSource, sha256_hex
from job_search_agent.status import NOTE_JUDGMENTS_FAILED, NOTE_PENDING_UNRESOLVED

DEFAULT_PLAN_PATH: Final = Path("config/watch.toml")
LOCK_REL: Final = ".lock"
"""Inside the write root; held for a whole loop and for a reset."""

_DEFERRED_NOTES: Final = frozenset(
    {NOTE_JUDGMENTS_FAILED, NOTE_PENDING_UNRESOLVED, NOTE_JUDGE_UNAVAILABLE}
)
_OK_STATUSES: Final = frozenset(
    {RunStatus.BASELINE, RunStatus.SUCCESS_WITH_NEW, RunStatus.SUCCESS_NO_NEW}
)
_NO_COUNT_STATUSES: Final = frozenset(
    {RunStatus.FETCH_FAILED, RunStatus.INVALID_RESPONSE, RunStatus.EMPTY_RESPONSE}
)
"""A failed fetch reports no posting, new or pending count: none is invented (§5)."""

# --- the plan (config/watch.toml) ---------------------------------------------

_Name = Annotated[str, StringConstraints(min_length=1)]


class _Section(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Budget(_Section):
    """GATE §3: per loop run."""

    max_boards: int = Field(ge=1)
    max_requests: int = Field(ge=1)
    max_seconds: float = Field(gt=0)


class RetrySettings(_Section):
    """GATE §5: how many retries of a transient failure, and when."""

    max_retries: int = Field(ge=0, le=1)
    pause_s: float = Field(ge=0)
    min_seconds_left: float = Field(ge=0)


class PolicySettings(_Section):
    """GATE §6: hosts and the write folder (relative to the project root)."""

    allowed_hosts: list[_Name] = Field(min_length=1)
    write_root: _Name


class BoardEntry(_Section):
    """One planned board, e.g. ``ashby`` / ``ramp``, with its GATE A2 floor if any."""

    provider: _Name
    token: _Name
    min_postings: int | None = Field(default=None, ge=1)


class WatchPlan(_Section):
    """The whole of ``config/watch.toml``."""

    budget: Budget
    retry: RetrySettings
    policy: PolicySettings
    boards: list[BoardEntry] = Field(min_length=1)


def load_plan(path: Path) -> WatchPlan:
    """Reads and validates a watch plan.

    Args:
        path: The TOML file.

    Returns:
        The plan.

    Raises:
        ConfigError: Missing file, bad TOML, or an unknown or invalid key.
    """
    try:
        with path.open("rb") as handle:
            raw = tomllib.load(handle)
        return WatchPlan.model_validate(raw)
    except FileNotFoundError as exc:
        raise ConfigError(f"watch plan not found: {path.name}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"watch plan is not valid TOML: {exc}") from exc
    except ValidationError as exc:
        errors = exc.errors(include_input=False, include_url=False)
        detail = "; ".join(
            f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in errors
        )
        raise ConfigError(f"invalid watch plan: {detail}") from exc


def board_key(provider: str, token: str) -> tuple[str, str]:
    """GATE §4: the same board is the same provider and token, trimmed and lowercased.

    Args:
        provider: Provider name as planned.
        token: Board token as planned.

    Returns:
        The normalised ``(provider, token)``.
    """
    return provider.strip().lower(), token.strip().lower()


def key_text(key: tuple[str, str]) -> str:
    """``("ashby", "ramp")`` -> ``"ashby/ramp"``."""
    return "/".join(key)


def board_dir_name(key: tuple[str, str]) -> str:
    """``("ashby", "ramp")`` -> ``"ashby-ramp"`` (the board's folder under boards/)."""
    return "-".join(key)


def build_policy(plan: WatchPlan, project_root: Path) -> PermissionPolicy:
    """Builds the permission policy from the plan, inside the code's ceilings (GATE §6).

    A plan may narrow the hosts and the write folder, never widen them: the ceilings
    are constants in ``policy``, so a plan file cannot grant itself more.

    Raises:
        ConfigError: A host outside ``HOST_CEILING``, or a write root outside
            ``WRITE_CEILING``.
    """
    extra = sorted(set(plan.policy.allowed_hosts) - HOST_CEILING)
    if extra:
        raise ConfigError(f"plan allows hosts outside GATE §6: {', '.join(extra)}")
    write_root = project_root / plan.policy.write_root
    if not inside(write_root, project_root / WRITE_CEILING):
        raise ConfigError(f"plan write_root must be inside {WRITE_CEILING}")
    return PermissionPolicy(
        project_root=project_root,
        write_root=write_root,
        allowed_hosts=plan.policy.allowed_hosts,
    )


def load_checked_plan(
    path: Path, project_root: Path
) -> tuple[WatchPlan, PermissionPolicy]:
    """Reads a plan only if the ceiling policy allows it, then builds its policy.

    The plan must be readable (not private, inside the project) and must not lie in a
    folder the agent can write, so the agent cannot rewrite its own plan.

    Args:
        path: The plan file.
        project_root: The project root.

    Returns:
        The plan and its permission policy.

    Raises:
        ConfigError: The plan is refused, invalid, or asks for more than the ceilings.
    """
    ceiling = PermissionPolicy(
        project_root=project_root,
        write_root=project_root / WRITE_CEILING,
        allowed_hosts=HOST_CEILING,
    )
    read = ceiling.check_read(path.resolve())
    if not read.allowed:
        raise ConfigError(f"policy refused reading the plan: {read.reason}")
    if ceiling.check_write(path.resolve()).allowed:
        raise ConfigError("the plan must not live where the agent can write")
    plan = load_plan(path)
    return plan, build_policy(plan, project_root)


# --- budget and the fetcher ---------------------------------------------------


@dataclasses.dataclass
class BudgetMeter:
    """What the loop has spent against its ``Budget``.

    Attributes:
        budget: The limits.
        monotonic: Seconds clock.
        started: ``monotonic()`` when the loop started.
        requests: GET attempts sent so far.
        boards: Boards started so far.
    """

    budget: Budget
    monotonic: Callable[[], float]
    started: float
    requests: int = 0
    boards: int = 0

    def seconds_used(self) -> float:
        """Wall time since the loop started."""
        return self.monotonic() - self.started

    def seconds_left(self) -> float:
        """Time left in ``max_seconds`` (may be negative)."""
        return self.budget.max_seconds - self.seconds_used()

    def request_refusal(self) -> str | None:
        """Returns the budget that forbids one more request, or ``None``."""
        if self.requests >= self.budget.max_requests:
            return "max_requests"
        if self.seconds_left() <= 0:
            return "max_seconds"
        return None

    def board_refusal(self) -> str | None:
        """Returns the budget that forbids starting one more board, or ``None``."""
        if self.boards >= self.budget.max_boards:
            return "max_boards"
        return self.request_refusal()


def is_transient(result: FetchResult) -> bool:
    """GATE §5: only a timeout, a connection error or a 5xx is worth one retry."""
    if result.error in (FetchErrorKind.TIMEOUT, FetchErrorKind.TRANSPORT):
        return True
    return (
        result.error is FetchErrorKind.HTTP_STATUS
        and result.status_code is not None
        and 500 <= result.status_code <= 599
    )


def _refused(url: str, kind: FetchErrorKind, detail: str) -> FetchResult:
    return FetchResult(
        requested_url=url,
        final_url=None,
        redirect_chain=(),
        status_code=None,
        headers={},
        body=None,
        error=kind,
        error_detail=detail,
    )


FetcherFactory = Callable[[float, EventSink], HttpFetcher]
"""Builds one allow-listed fetcher with a timeout; it emits ``http.*`` events."""


class LoopFetcher:
    """The loop's only network tool: policy, budget, repeat rule and retry (GATE §3-6).

    Args:
        policy: Asked before every request.
        meter: The loop's budget; charged one request per attempt.
        retry: Retry settings.
        trace: The loop trace.
        board: Board key text, written on every event.
        build: Builds the inner fetcher for one attempt.
        board_events: The board's own event log (``http.*`` events).
        timeout_cap: The configured per-request timeout.
        sleep: Pause before a retry.
        sent: GET attempts per URL in this loop run, shared by every board's
            fetcher so the repeat rule holds for the whole run (GATE §4).
    """

    def __init__(
        self,
        *,
        policy: PermissionPolicy,
        meter: BudgetMeter,
        retry: RetrySettings,
        trace: EventSink,
        board: str,
        build: FetcherFactory,
        board_events: EventSink,
        timeout_cap: float,
        sleep: Callable[[float], None] = time.sleep,
        sent: dict[str, int] | None = None,
    ) -> None:
        self._policy = policy
        self._meter = meter
        self._retry = retry
        self._trace = trace
        self._board = board
        self._build = build
        self._board_events = board_events
        self._timeout_cap = timeout_cap
        self._sleep = sleep
        self._sent = {} if sent is None else sent
        self.attempts = 0
        self.live_body: bytes | None = None
        """The body of the last result ``get`` returned: the board's live response."""

    def get(self, url: str) -> FetchResult:
        """One board request, with at most ``retry.max_retries`` retries.

        Args:
            url: The board URL.

        Returns:
            The last attempt's result, or a ``POLICY_REFUSED`` or
            ``BUDGET_EXHAUSTED`` result when no request was allowed.
        """
        verdict = self._policy.check_request("GET", url)
        if not verdict.allowed:
            self._trace.emit(
                "tool.fetch.refused", {"board": self._board, "reason": verdict.reason}
            )
            return _refused(url, FetchErrorKind.POLICY_REFUSED, verdict.reason)
        result = self._refusal(url) or self._attempt(url, 0)
        for attempt in range(1, self._retry.max_retries + 1):
            if result.ok or not is_transient(result):
                break
            skip = self._retry_refusal()
            if skip is not None:
                # The last real failure stays the board's result, with its saved body.
                self._trace.emit(
                    "tool.fetch.retry_skipped", {"board": self._board, "reason": skip}
                )
                break
            self._trace.emit(
                "tool.fetch.retry",
                {
                    "board": self._board,
                    "after": str(result.error),
                    "status_code": result.status_code,
                    "pause_s": self._retry.pause_s,
                },
            )
            self._sleep(self._retry.pause_s)
            result = self._refusal(url) or self._attempt(url, attempt)
        self.live_body = result.body
        return result

    def _retry_refusal(self) -> str | None:
        """Returns why a retry may not be sent now, or ``None`` (GATE §3, §5)."""
        budget = self._meter.request_refusal()
        if budget is not None:
            return budget
        if self._meter.seconds_left() < self._retry.min_seconds_left:
            return "max_seconds"
        return None

    def _refusal(self, url: str) -> FetchResult | None:
        if self._sent.get(url, 0) > self._retry.max_retries:
            self._trace.emit(
                "tool.fetch.refused", {"board": self._board, "reason": "repeat"}
            )
            return _refused(url, FetchErrorKind.POLICY_REFUSED, "repeat")
        budget = self._meter.request_refusal()
        if budget is not None:
            self._trace.emit("budget.stop", {"board": self._board, "budget": budget})
            return _refused(url, FetchErrorKind.BUDGET_EXHAUSTED, budget)
        return None

    def _attempt(self, url: str, attempt: int) -> FetchResult:
        timeout = max(0.001, min(self._timeout_cap, self._meter.seconds_left()))
        self._meter.requests += 1
        self._sent[url] = self._sent.get(url, 0) + 1
        self.attempts += 1
        self._trace.emit(
            "tool.fetch.attempt",
            {
                "board": self._board,
                "attempt": attempt + 1,
                "url": url,
                "timeout_s": round(timeout, 3),
                "requests_used": self._meter.requests,
            },
        )
        result = self._build(timeout, self._board_events).get(url)
        self._trace.emit(
            "tool.fetch.result",
            {
                "board": self._board,
                "attempt": attempt + 1,
                "status_code": result.status_code,
                "error": None if result.error is None else str(result.error),
                "bytes": None if result.body is None else len(result.body),
                "sha256": None if result.body is None else sha256_hex(result.body),
                "elapsed_ms": result.elapsed_ms,
                "redirects": len(result.redirect_chain),
            },
        )
        return result


# --- outcomes and the exit ----------------------------------------------------


class LoopExit(StrEnum):
    """GATE §2: every loop run ends in exactly one of these."""

    FINISHED = "FINISHED"
    INCOMPLETE = "INCOMPLETE"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    ERROR = "ERROR"


class BoardState(StrEnum):
    """What happened to one planned board."""

    OK = "OK"
    FAILED = "FAILED"
    SKIPPED_REPEAT = "SKIPPED_REPEAT"
    NOT_ATTEMPTED = "NOT_ATTEMPTED"


class BoardOutcome(_Section):
    """One planned board in the loop report. Counts are ``None`` when unknown."""

    board: str
    state: BoardState
    run_status: RunStatus | None = None
    run_folder: str | None = None
    fetched_count: int | None = None
    new_count: int | None = None
    pending_count: int | None = None
    http_status: int | None = None
    fetch_error: FetchErrorKind | None = None
    requests: int = 0
    note: str = ""


class LoopReport(_Section):
    """``report.json`` of one loop run."""

    loop_id: str
    started_at_utc: datetime
    finished_at_utc: datetime
    exit: LoopExit
    reason: str
    budget: Budget
    requests_used: int
    seconds_used: float
    boards: list[BoardOutcome]
    code_commit: str | None = None


def board_ok(report: RunReport) -> tuple[bool, str]:
    """GATE §2: whether one board's JS1 run counts as OK, and why.

    Args:
        report: The board's run report.

    Returns:
        ``(ok, note)``; the note is ``"judgments_deferred"`` for an OK
        ``PARTIAL_FAILURE`` and the status otherwise.
    """
    if report.status in _OK_STATUSES:
        return True, report.status.value
    deferred = (
        report.status is RunStatus.PARTIAL_FAILURE
        and report.model_backend == "none"
        and set(report.notes) <= _DEFERRED_NOTES
        and set(report.judgment_counts) <= {JudgmentStatus.UNAVAILABLE}
    )
    if deferred:
        return True, "judgments_deferred"
    return False, report.status.value


def decide_exit(boards: Sequence[BoardOutcome], *, stopped_by: str | None) -> LoopExit:
    """GATE §2 precedence: ERROR, BUDGET_EXHAUSTED, INCOMPLETE, FINISHED.

    Args:
        boards: Every planned board's outcome.
        stopped_by: The budget that stopped the loop early, or ``None``.

    Returns:
        The loop's exit.
    """
    attempted = [b for b in boards if b.state in (BoardState.OK, BoardState.FAILED)]
    ok = [b for b in attempted if b.state is BoardState.OK]
    if attempted and not ok:
        return LoopExit.ERROR
    if stopped_by is not None:
        return LoopExit.BUDGET_EXHAUSTED
    if not attempted:
        return LoopExit.ERROR
    if len(ok) < len(attempted):
        return LoopExit.INCOMPLETE
    return LoopExit.FINISHED


# --- the loop -----------------------------------------------------------------


BoardDepsFactory = Callable[[AgentConfig], RunDeps]
"""Wires one board's ``RunDeps``; the loop then replaces its source with the loop
fetcher, so every request goes through the policy and the budget."""


@dataclasses.dataclass(frozen=True)
class LoopDeps:
    """Everything one loop run needs, injected.

    Attributes:
        plan: The validated plan.
        base_config: ``config/agent.toml`` (résumé, HTTP limits, User-Agent).
        policy: The permission policy built from the plan.
        clock: Wall clock for IDs and timestamps.
        monotonic: Seconds clock for the time budget.
        board_deps: Wires one board's run.
        transport: Inner transport for the fetchers (tests); ``None`` is real HTTPS.
        sleep: Pause before a retry.
        code_commit: ``HEAD`` when the loop ran, if known.
    """

    plan: WatchPlan
    base_config: AgentConfig
    policy: PermissionPolicy
    clock: Clock
    monotonic: Callable[[], float]
    board_deps: BoardDepsFactory
    transport: httpx.BaseTransport | None = None
    sleep: Callable[[float], None] = time.sleep
    code_commit: str | None = None


def board_config(
    base: AgentConfig, policy: PermissionPolicy, key: tuple[str, str]
) -> AgentConfig:
    """One board's JS1 config: its own data folder, the policy's hosts, no model.

    Args:
        base: ``config/agent.toml``.
        policy: The permission policy (hosts and write root).
        key: The board key.

    Returns:
        The validated per-board configuration.
    """
    data_dir = policy.write_root / "boards" / board_dir_name(key)
    raw = base.model_dump()
    raw["data"] = {**raw["data"], "dir": str(data_dir.relative_to(base.project_root))}
    raw["board"] = {"provider": key[0], "token": key[1]}
    raw["http"] = {**raw["http"], "allowed_hosts": sorted(policy.allowed_hosts)}
    raw["model"] = {**raw["model"], "backend": "none"}
    return AgentConfig.model_validate(raw)


NOTE_BELOW_FLOOR: Final = "below_floor"


class FlooredProvider:
    """GATE A2: a live response listing 1 to ``floor - 1`` postings is invalid.

    Only the live response is floored, recognised by its bytes (``live_body``, from
    the loop's fetcher), so the order in which ``pipeline.run_once`` parses responses
    does not matter. Saved raws re-read for pending retries (A26) are never floored.

    Args:
        inner: The board's real provider.
        floor: The planned ``min_postings``.
        live_body: Returns the body the loop fetched for this board, or ``None``.
    """

    def __init__(
        self,
        inner: BoardProvider,
        floor: int,
        *,
        live_body: Callable[[], bytes | None],
    ) -> None:
        self._inner = inner
        self._floor = floor
        self._live_body = live_body
        self.below_floor = False

    @property
    def name(self) -> str:
        """The inner provider's name."""
        return self._inner.name

    def jobs_url(self, board_token: str) -> str:
        """The inner provider's URL."""
        return self._inner.jobs_url(board_token)

    def parse(self, body: bytes) -> ParsedBoard:
        """Parses with the inner provider, then floors the live response.

        Raises:
            InvalidResponse: The inner provider's, or ``below_floor``.
        """
        board = self._inner.parse(body)
        live = body == self._live_body()
        if live and not board.is_empty and board.fetched_count < self._floor:
            self.below_floor = True
            raise InvalidResponse(
                NOTE_BELOW_FLOOR, f"{board.fetched_count} < {self._floor}"
            )
        return board


class _Loop:
    """One loop run (private): planning, boards, report."""

    def __init__(self, deps: LoopDeps, out: OutputRoot, trace: EventLog) -> None:
        self.d = deps
        self.out = out
        self.trace = trace
        self.meter = BudgetMeter(deps.plan.budget, deps.monotonic, deps.monotonic())
        self.outcomes: dict[int, BoardOutcome] = {}
        self.sent: dict[str, int] = {}

    def plan_boards(self) -> list[tuple[int, tuple[str, str], str]] | str:
        """Applies the repeat rule and checks every URL; returns a refusal code.

        Every plan entry gets an outcome now (``SKIPPED_REPEAT`` or
        ``NOT_ATTEMPTED``), so an early stop never drops a planned board.
        """
        planned: list[tuple[int, tuple[str, str]]] = []
        seen: set[tuple[str, str]] = set()
        for index, entry in enumerate(self.d.plan.boards):
            key = board_key(entry.provider, entry.token)
            repeat = key in seen
            seen.add(key)
            state = BoardState.SKIPPED_REPEAT if repeat else BoardState.NOT_ATTEMPTED
            self.outcomes[index] = BoardOutcome(board=key_text(key), state=state)
            if repeat:
                self.trace.emit(
                    "plan.repeat_skipped", {"board": key_text(key), "index": index}
                )
            else:
                planned.append((index, key))
        checked: list[tuple[int, tuple[str, str], str]] = []
        for index, key in planned:
            try:
                url = get_provider(key[0]).jobs_url(key[1])
            except ConfigError:
                return f"plan_invalid:{key_text(key)}"
            verdict = self.d.policy.check_request("GET", url)
            folder = self.d.policy.check_write(
                self.d.policy.write_root / "boards" / board_dir_name(key)
            )
            if not verdict.allowed or not folder.allowed:
                return f"plan_refused:{key_text(key)}:{verdict.reason or folder.reason}"
            checked.append((index, key, url))
        return checked

    def run_board(
        self, key: tuple[str, str], url: str, floor: int | None = None
    ) -> BoardOutcome:
        name = key_text(key)
        cfg = board_config(self.d.base_config, self.d.policy, key)
        base_http = cfg.http
        deps = self.d.board_deps(cfg)

        def build(timeout: float, events: EventSink) -> HttpFetcher:
            settings = base_http.model_copy(update={"timeout_s": timeout})
            return build_fetcher_from_settings(
                settings, inner=self.d.transport, events=events
            )

        fetcher = LoopFetcher(
            policy=self.d.policy,
            meter=self.meter,
            retry=self.d.plan.retry,
            trace=self.trace,
            board=name,
            build=build,
            board_events=deps.events,
            timeout_cap=base_http.timeout_s,
            sleep=self.d.sleep,
            sent=self.sent,
        )
        floored = (
            None
            if floor is None
            else FlooredProvider(
                deps.provider, floor, live_body=lambda: fetcher.live_body
            )
        )
        deps = dataclasses.replace(
            deps,
            source=LiveSource(fetcher, url),
            provider=floored or deps.provider,
        )
        self.trace.emit("board.started", {"board": name, "url": url})
        report = run_once(deps)
        ok, note = board_ok(report)
        if floored is not None and floored.below_floor:
            note = NOTE_BELOW_FLOOR
        counted = report.status not in _NO_COUNT_STATUSES
        outcome = BoardOutcome(
            board=name,
            state=BoardState.OK if ok else BoardState.FAILED,
            run_status=report.status,
            run_folder=cfg.repo_rel(f"live/runs/{report.run_id}"),
            fetched_count=report.fetched_count if counted else None,
            new_count=report.new_count if counted else None,
            pending_count=len(report.unresolved_pending_ids) if counted else None,
            http_status=report.http_status,
            fetch_error=report.fetch_error,
            requests=fetcher.attempts,
            note=note,
        )
        self.trace.emit("board.finished", outcome.model_dump(mode="json"))
        return outcome

    def run(self) -> tuple[LoopExit, str]:
        resume = self.d.policy.check_read(self.d.base_config.resume_path)
        if not resume.allowed:
            return LoopExit.ERROR, f"resume_read_refused:{resume.reason}"
        planned = self.plan_boards()
        if isinstance(planned, str):
            return LoopExit.ERROR, planned
        stopped_by: str | None = None
        for index, key, url in planned:
            stopped_by = self.meter.board_refusal()
            if stopped_by is not None:
                self.trace.emit(
                    "budget.stop", {"board": key_text(key), "budget": stopped_by}
                )
                break
            self.meter.boards += 1
            requests_before = self.meter.requests
            try:
                floor = self.d.plan.boards[index].min_postings
                self.outcomes[index] = self.run_board(key, url, floor)
            except (AgentError, OSError) as exc:
                # GATE §2: even an I/O failure ends in one exit with a written report.
                error = type(exc).__name__
                self.trace.emit("board.error", {"board": key_text(key), "error": error})
                self.outcomes[index] = BoardOutcome(
                    board=key_text(key),
                    state=BoardState.FAILED,
                    requests=self.meter.requests - requests_before,
                    note=error,
                )
                return LoopExit.ERROR, f"{error}:{key_text(key)}"
        boards = self.boards()
        exit_ = decide_exit(boards, stopped_by=stopped_by)
        return exit_, stopped_by or _reason(exit_, boards)

    def boards(self) -> list[BoardOutcome]:
        """Every planned board's outcome, in plan order."""
        return [self.outcomes[i] for i in sorted(self.outcomes)]


def _reason(exit_: LoopExit, outcomes: Sequence[BoardOutcome]) -> str:
    failed = [o.board for o in outcomes if o.state is BoardState.FAILED]
    if exit_ is LoopExit.FINISHED:
        return "every planned board was checked"
    if exit_ is LoopExit.ERROR and not failed:
        return "no board was attempted"
    return "failed: " + ", ".join(failed)


def run_loop(deps: LoopDeps) -> LoopReport:
    """Runs the loop once and writes its trace and report (GATE §1-5).

    Args:
        deps: The loop's dependencies.

    Returns:
        The loop report (also written to ``loops/<loop_id>/report.json``).

    Raises:
        RunLocked: Another loop or reset holds ``data/watch/.lock``.
        ConfigError: The policy refuses the loop folder.
    """
    write = deps.policy.check_write(deps.policy.write_root / "loops")
    if not write.allowed:
        raise ConfigError(f"policy refused the loop folder: {write.reason}")
    out = create_output_root(deps.policy.write_root)
    started = deps.clock.now_utc()
    loop_id = format_run_id(started)
    loop_rel = f"loops/{loop_id}"
    with out.lock(LOCK_REL):
        out.make_empty_dir(loop_rel)
        trace = EventLog(deps.clock)
        trace.attach(out, f"{loop_rel}/trace.jsonl")
        trace.emit(
            "loop.started",
            {
                "loop_id": loop_id,
                "budget": deps.plan.budget.model_dump(),
                "planned": [f"{b.provider}/{b.token}" for b in deps.plan.boards],
                "allowed_hosts": sorted(deps.policy.allowed_hosts),
                "code_commit": deps.code_commit,
            },
        )
        loop = _Loop(deps, out, trace)
        exit_, reason = loop.run()
        report = LoopReport(
            loop_id=loop_id,
            started_at_utc=started,
            finished_at_utc=deps.clock.now_utc(),
            exit=exit_,
            reason=reason,
            budget=deps.plan.budget,
            requests_used=loop.meter.requests,
            seconds_used=round(loop.meter.seconds_used(), 3),
            boards=loop.boards(),
            code_commit=deps.code_commit,
        )
        trace.emit(
            "loop.finished",
            {
                "exit": exit_.value,
                "reason": reason,
                "requests_used": report.requests_used,
                "seconds_used": report.seconds_used,
            },
        )
        out.write_json_atomic(f"{loop_rel}/report.json", report.model_dump(mode="json"))
        out.write_bytes_atomic(f"{loop_rel}/report.md", render_report(report).encode())
    return report


def render_report(report: LoopReport) -> str:
    """Renders ``report.md``: the exit, one row per board, and what needs Shubham."""
    lines = [
        f"# Watch loop {report.loop_id}",
        "",
        f"**Exit:** `{report.exit.value}` — {report.reason}",
        "",
        f"Requests used: {report.requests_used} of {report.budget.max_requests}; "
        f"seconds used: {report.seconds_used} of {report.budget.max_seconds:g}; "
        f"boards attempted: "
        f"{sum(b.state in (BoardState.OK, BoardState.FAILED) for b in report.boards)} "
        f"of at most {report.budget.max_boards}.",
        "",
        "| board | state | run status | fetched | new | pending | HTTP | error "
        "| requests | note |",
        "|---|---|---|---:|---:|---:|---:|---|---:|---|",
    ]

    def cell(value: object) -> str:
        return "—" if value is None else str(value)

    for b in report.boards:
        lines.append(
            f"| {b.board} | {b.state.value} | {cell(b.run_status)} | "
            f"{cell(b.fetched_count)} | {cell(b.new_count)} | "
            f"{cell(b.pending_count)} | "
            f"{cell(b.http_status)} | {cell(b.fetch_error)} | {b.requests} | {b.note} |"
        )
    attention = [b for b in report.boards if b.state is not BoardState.OK]
    lines += ["", "## Needs your attention", ""]
    if not attention:
        lines.append("Nothing: every planned board was checked.")
    for b in attention:
        detail = [b.state.value, cell(b.run_status)]
        if b.http_status is not None:
            detail.append(f"HTTP {b.http_status}")
        if b.fetch_error is not None:
            detail.append(b.fetch_error.value)
        detail.append(f"{b.requests} request(s)")
        if b.note and b.note != cell(b.run_status):
            detail.append(b.note)
        lines.append(f"- `{b.board}`: " + ", ".join(detail))
    return "\n".join(lines) + "\n"


# --- reset (the one write that needs approval) --------------------------------


def reset_board(
    policy: PermissionPolicy,
    provider: str,
    token: str,
    *,
    approver: Approver | None,
) -> tuple[Verdict, bool]:
    """Deletes one board's saved state, only after Shubham approves (GATE §6).

    Args:
        policy: The permission policy.
        provider: Provider name.
        token: Board token.
        approver: Asks Shubham; ``None`` (no terminal) means no.

    Returns:
        The settled verdict, and whether a state file was deleted.

    Raises:
        ConfigError: Unknown provider or an unsafe token (nothing is asked).
        RunLocked: A loop is running.
    """
    key = board_key(provider, token)
    get_provider(key[0]).jobs_url(
        key[1]
    )  # same token check as the plan: no "/" or ".."
    state = policy.write_root / "boards" / board_dir_name(key) / "live" / "state.json"
    question = (
        f"Delete the saved state of {key_text(key)}? Its next run becomes a fresh "
        f"baseline. Type {key_text(key)} to approve: "
    )
    verdict = settle(policy.check_delete(state), approver=approver, question=question)
    if not verdict.allowed:
        return verdict, False
    with create_output_root(policy.write_root).lock(LOCK_REL):
        if not state.is_file():
            return verdict, False
        state.unlink()
    return verdict, True
