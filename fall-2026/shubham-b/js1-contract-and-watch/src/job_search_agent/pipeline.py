"""One agent run: ``run_once(deps)`` (PLAN §1.3).

Everything the run touches arrives through ``RunDeps``: the rule, provider, résumé
gate, HTTP source and judge are injected, and every file is written through the one
``fsio.OutputRoot``. The CLI does the real wiring.

Order of work and why:

1. Verify the résumé (refusal aborts before any fetch or model call, exit 3).
2. Load the state (corrupt aborts before fetching, exit 4; the file is untouched).
3. Create the run folder; copy the prior state to ``state.before.json``.
4. Obtain the raw response once; save it byte-for-byte with its sha256 whenever a
   body exists, even for an unsuccessful HTTP status (replay: a pointer file).
5. A fetch failure, an invalid response or an empty response writes the report only;
   the state file is never touched (§10, §15).
6. Baseline (no prior state): store every valid ID, judge nothing, ``new_count`` 0.
7. Otherwise judge new postings (rule, evidence validation, Claude), then retry every
   pending judgment, re-reading a posting from its saved raw file if it left the
   board (A26).
8. Write order is records -> state -> report. The state is written atomically, and
   only after the records are safely on disk, so a crash re-reports instead of losing
   postings.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from job_search_agent import __version__
from job_search_agent.clock import format_run_id, to_eastern
from job_search_agent.config import AgentConfig
from job_search_agent.errors import (
    AgentError,
    ConfigError,
    InvalidResponse,
    PathRejected,
    RunIdTaken,
    StateCorrupt,
)
from job_search_agent.events import EventLog
from job_search_agent.fsio import OutputRoot
from job_search_agent.models import (
    FetchKind,
    JudgmentDiagnostic,
    JudgmentOutcome,
    JudgmentStatus,
    ModelJudgment,
    OutputRecord,
    ParsedBoard,
    PendingJudgment,
    Posting,
    RawRef,
    RuleVerdict,
    RunMode,
    RunReport,
    RunStatus,
    SeenState,
    SourceKind,
    SourceResult,
    VerifiedResume,
)
from job_search_agent.ports import BoardProvider, Clock, GitInspector, Judge, RawSource
from job_search_agent.report import render_markdown, render_terminal
from job_search_agent.sources import REPLAYED_FROM_NAME, sha256_hex
from job_search_agent.state import (
    advance,
    parse_state,
    read_state_rel,
    state_to_bytes,
)
from job_search_agent.status import explain_status

LIVE_DIR = "live"
SEEDED_DIR = "seeded"
LOCK_NAME = ".lock"
"""Lock file inside ``data/<live|seeded>/``; held for the whole of a run."""

NOTE_SEEDED = "seeded_replay_no_network"
NOTE_PENDING_SOURCE_UNAVAILABLE = "pending_source_unavailable"
NOTE_JUDGE_UNAVAILABLE = "judge_unavailable"

# --- seams --------------------------------------------------------------------

EvaluateFn = Callable[[Posting, VerifiedResume], RuleVerdict]
"""``rule.verdict.evaluate(posting, resume) -> RuleVerdict``."""

EvidenceValidatorFn = Callable[
    [RuleVerdict, Mapping[str, Any], Mapping[str, Any]], list[str]
]
"""``evidence_validator.validate_rule_evidence(verdict, raw_posting, resume_data)``;
an empty list means valid."""

ResumeLoader = Callable[[], VerifiedResume]
"""Runs the résumé gate; raises ``ResumeRefused`` on any failed check."""

RepoReader = Callable[[str], bytes]
"""Reads a repo-relative file (through the read policy) for pending retries (A26)."""


def lock_rel(*, seeded: bool) -> str:
    """Returns the data-root-relative lock file for a mode, e.g. ``"live/.lock"``.

    Args:
        seeded: The seeded (replay) mode instead of live.

    Returns:
        The lock path; ``jsa run`` and ``jsa pending drop`` hold it while they work.
    """
    return f"{SEEDED_DIR if seeded else LIVE_DIR}/{LOCK_NAME}"


@dataclass(frozen=True)
class RunDeps:
    """Everything one run needs, injected.

    Attributes:
        config: Validated configuration (board, model settings, state paths).
        clock: Time source; the first reading becomes the run ID.
        source: Live fetch or seeded replay, called exactly once.
        provider: Board provider (shape validation, normalisation).
        load_resume: The résumé gate; called first, before anything else.
        evaluate: The deterministic rule.
        validate_evidence: The §7 rule-evidence validator.
        judge: Claude's judge, or ``None`` for honest ``UNAVAILABLE`` judgments.
        out: The data-root writer (``fsio.OutputRoot`` on ``config.data_dir``).
        git: Repository inspector for ``code_commit``/``code_dirty``, or ``None``.
        events: The run's event log; attached to ``events.jsonl`` by the run.
        seeded: True for a replay; the run then uses ``data/seeded`` only.
        read_repo_file: Reads a saved raw file by repo-relative path (A26 retries).
        unavailable_reason: ``unavailable_reason`` recorded when ``judge`` is None;
            ``None`` when a real judge is wired.
        terminal: Receives the privacy-safe terminal summary, if given.
    """

    config: AgentConfig
    clock: Clock
    source: RawSource
    provider: BoardProvider
    load_resume: ResumeLoader
    evaluate: EvaluateFn
    validate_evidence: EvidenceValidatorFn
    judge: Judge | None
    out: OutputRoot
    git: GitInspector | None
    events: EventLog
    seeded: bool
    read_repo_file: RepoReader
    unavailable_reason: str | None = "backend_none"
    terminal: Callable[[str], None] | None = None


# --- helpers ------------------------------------------------------------------


@dataclass
class _Run:
    """Mutable bookkeeping for one run (private to this module)."""

    run_id: str
    run_rel: str
    started_at: datetime
    prior: SeenState | None
    code_commit: str | None
    code_dirty: bool | None
    notes: list[str] = field(default_factory=list)


@dataclass
class _Judged:
    """Records and outcomes produced by one run's judging pass."""

    records: list[OutputRecord] = field(default_factory=list)
    retried: list[OutputRecord] = field(default_factory=list)
    outcomes: dict[str, JudgmentOutcome] = field(default_factory=dict)
    pending_sources: dict[str, RawRef] = field(default_factory=dict)
    new_ids: list[str] = field(default_factory=list)
    retried_ids: list[str] = field(default_factory=list)


def _note_once(run: _Run, note: str) -> None:
    if note not in run.notes:
        run.notes.append(note)


def _is_valid(record: OutputRecord) -> bool:
    return record.model_judgment.status is JudgmentStatus.VALID


def _record_dump(records: Sequence[OutputRecord]) -> list[dict[str, Any]]:
    return [r.model_dump(mode="json") for r in records]


def _git_facts(git: GitInspector | None) -> tuple[str | None, bool | None]:
    if git is None:
        return None, None
    try:
        return git.head(), git.is_dirty()
    except (OSError, RuntimeError):
        return None, None


def _unavailable(reason: str) -> ModelJudgment:
    return ModelJudgment(
        status=JudgmentStatus.UNAVAILABLE,
        diagnostic=JudgmentDiagnostic(unavailable_reason=reason),
    )


def _crashed(exc: BaseException) -> ModelJudgment:
    """An ``ERROR`` judgment for a judge that raised; the reason names the type only."""
    return ModelJudgment(
        status=JudgmentStatus.ERROR,
        diagnostic=JudgmentDiagnostic(
            error_reason=f"judge_raised:{type(exc).__name__}"
        ),
    )


def _try_write(write: Callable[[], object]) -> bool:
    """Runs one write; returns False on an I/O or path-policy failure."""
    try:
        write()
    except (OSError, PathRejected):
        return False
    return True


class _Pipeline:
    """Runs the steps of ``run_once``; one instance per run."""

    def __init__(self, deps: RunDeps) -> None:
        self.d = deps
        self.cfg = deps.config
        self.base = SEEDED_DIR if deps.seeded else LIVE_DIR
        self.state_rel = self.cfg.state_rel(seeded=deps.seeded)
        self._saved_boards: dict[str, ParsedBoard | None] = {}

    # -- steps --

    def run(self) -> RunReport:
        resume = self.d.load_resume()
        with self.d.out.lock(lock_rel(seeded=self.d.seeded)):
            return self._run_locked(resume)

    def _start_run(self) -> _Run:
        """Loads the prior state, claims the run folder and saves ``state.before``.

        Raises:
            StateCorrupt: The state file is invalid (nothing is written).
            RunIdTaken: This second's run folder already exists.
        """
        prior_bytes, prior = self._load_prior()
        started = self.d.clock.now_utc()
        run_id = format_run_id(started, seeded=self.d.seeded)
        run_rel = f"{self.base}/runs/{run_id}"
        if self.d.out.exists(run_rel):
            raise RunIdTaken(run_id)
        commit, dirty = _git_facts(self.d.git)
        run = _Run(run_id, run_rel, started, prior, commit, dirty)
        if self.d.seeded:
            run.notes.append(NOTE_SEEDED)
        self.d.out.make_empty_dir(run_rel)
        self.d.events.attach(self.d.out, f"{run_rel}/events.jsonl")
        self.d.events.emit(
            "run.started",
            {
                "run_id": run_id,
                "mode": (RunMode.REPLAY if self.d.seeded else RunMode.LIVE).value,
                "seeded": self.d.seeded,
                "baseline": prior is None,
            },
        )
        before_rel = f"{run_rel}/state.before.json"
        if prior_bytes is None:
            self.d.out.write_json_atomic(before_rel, None)
        else:
            self.d.out.write_bytes_atomic(before_rel, prior_bytes)
        return run

    def _run_locked(self, resume: VerifiedResume) -> RunReport:
        run = self._start_run()
        fetched_at = self.d.clock.now_utc()
        src = self.d.source.obtain()
        self._emit_source(src)
        if (src.kind is SourceKind.REPLAY) is not self.d.seeded:
            raise ConfigError("source kind does not match the seeded flag")
        raw_ref = self._save_raw(run, src, fetched_at)

        if not src.ok or src.body is None:
            return self._finish(run, src, raw_ref, FetchKind.FAILED, board=None)
        try:
            board = self.d.provider.parse(src.body)
        except InvalidResponse as exc:
            self.d.events.emit("board.invalid", {"code": exc.code})
            return self._finish(run, src, raw_ref, FetchKind.INVALID, board=None)
        self.d.events.emit(
            "board.parsed",
            {
                "fetched_count": board.fetched_count,
                "valid_ids": len(board.postings),
                "data_quality_errors": board.error_count,
                "data_quality_issues": len(board.data_quality),
            },
        )
        if board.is_empty:
            return self._finish(run, src, raw_ref, FetchKind.EMPTY, board=board)
        if raw_ref is None:
            raise ConfigError("source returned a body without a raw reference")
        return self._process(run, src, raw_ref, board, resume, fetched_at)

    def _load_prior(self) -> tuple[bytes | None, SeenState | None]:
        data = read_state_rel(self.state_rel, self.d.out.read_bytes)
        if data is None:
            return None, None
        state = parse_state(data)
        if state.seeded is not self.d.seeded:
            raise StateCorrupt("seeded_flag")
        if (
            state.provider != self.d.provider.name
            or state.board != self.cfg.board.token
        ):
            raise StateCorrupt("board_mismatch")
        return data, state

    def _emit_source(self, src: SourceResult) -> None:
        fetch = src.fetch
        self.d.events.emit(
            "source.obtained",
            {
                "kind": src.kind.value,
                "http_status": fetch.status_code if fetch else None,
                "bytes": len(src.body) if src.body is not None else None,
                "sha256": src.sha256,
                "error": src.error.value if src.error else None,
                "replayed_from": src.replayed_from.path if src.replayed_from else None,
            },
        )

    def _save_raw(
        self, run: _Run, src: SourceResult, fetched_at: datetime
    ) -> RawRef | None:
        raw_dir = f"{run.run_rel}/raw"
        if src.kind is SourceKind.REPLAY:
            ref = src.replayed_from
            if ref is None:
                return None
            pointer: dict[str, Any] = {
                "path": ref.path,
                "sha256": ref.sha256,
                "original_fetched_at_utc": (
                    src.original_fetched_at_utc.isoformat()
                    if src.original_fetched_at_utc
                    else None
                ),
                "verified": src.ok,
                "seeded": True,
                "source": SourceKind.REPLAY.value,
                "provider": self.d.provider.name,
                "board": self.cfg.board.token,
                "agent_version": __version__,
                "code_commit": run.code_commit,
                "code_dirty": run.code_dirty,
            }
            self.d.out.write_json_atomic(
                f"{raw_dir}/{REPLAYED_FROM_NAME}", pointer, sort_keys=False
            )
            self.d.events.emit("raw.pointer_saved", {"path": ref.path})
            return ref
        if src.body is None:
            return None
        name = f"{self.d.provider.name}-{self.cfg.board.token}"
        raw_rel = f"{raw_dir}/{name}.json"
        digest = sha256_hex(src.body)
        self.d.out.write_bytes_atomic(raw_rel, src.body)
        fetch = src.fetch
        headers = dict(fetch.headers) if fetch else {}
        meta: dict[str, Any] = {
            "url": fetch.requested_url if fetch else None,
            "final_url": fetch.final_url if fetch else None,
            "redirect_chain": list(fetch.redirect_chain) if fetch else [],
            "fetched_at_utc": fetched_at.isoformat(),
            "fetched_at_et": to_eastern(fetched_at).isoformat(),
            "http_status": fetch.status_code if fetch else None,
            "headers": {
                k: headers[k] for k in ("content-type", "etag", "date") if k in headers
            },
            "bytes": len(src.body),
            "sha256": digest,
            "fetch_error": src.error.value if src.error else None,
            "seeded": False,
            "source": SourceKind.NETWORK.value,
            "provider": self.d.provider.name,
            "board": self.cfg.board.token,
            "agent_version": __version__,
            "code_commit": run.code_commit,
            "code_dirty": run.code_dirty,
        }
        self.d.out.write_json_atomic(
            f"{raw_dir}/{name}.meta.json", meta, sort_keys=False
        )
        ref = RawRef(path=self.cfg.repo_rel(raw_rel), sha256=digest)
        self.d.events.emit(
            "raw.saved", {"path": ref.path, "bytes": len(src.body), "sha256": digest}
        )
        return ref

    def _judge(
        self, run: _Run, posting: Posting, resume: VerifiedResume
    ) -> JudgmentOutcome:
        if self.d.judge is None:
            outcome = JudgmentOutcome(
                posting.posting_id,
                _unavailable(self.d.unavailable_reason or "unavailable"),
            )
        else:
            outcome = self._call_judge(self.d.judge, run, posting, resume)
        self.d.events.emit(
            "judgment.completed",
            {
                "posting_id": posting.posting_id,
                "status": outcome.status.value,
                "label": outcome.judgment.label,
            },
        )
        return outcome

    def _call_judge(
        self, judge: Judge, run: _Run, posting: Posting, resume: VerifiedResume
    ) -> JudgmentOutcome:
        """Calls the judge; an exception it raises becomes an ``ERROR`` judgment.

        ``ports.Judge`` implementations must not raise, but a failed raw-log write
        (``OSError``/``PathRejected``) or a payload bug (``PayloadError``, a
        ``ValueError``) must not abort the run either: the posting then goes
        pending through the normal path, and records, state and report are written.
        """
        log_dir = f"{run.run_rel}/model/{posting.posting_id}"
        try:
            outcome = judge.judge(posting, resume, log_dir=log_dir)
        except (AgentError, OSError, ValueError) as exc:
            judgment = _crashed(exc)
            self.d.events.emit(
                "judgment.crashed",
                {
                    "posting_id": posting.posting_id,
                    "reason": judgment.diagnostic.error_reason,
                },
            )
            return JudgmentOutcome(posting.posting_id, judgment)
        if outcome.posting_id != posting.posting_id:
            raise ValueError("judge returned an outcome for another posting")
        return outcome

    def _record(
        self,
        run: _Run,
        posting: Posting,
        resume: VerifiedResume,
        resume_data: Mapping[str, Any],
    ) -> tuple[OutputRecord, JudgmentOutcome]:
        verdict = self.d.evaluate(posting, resume)
        errors = self.d.validate_evidence(verdict, posting.raw, resume_data)
        self.d.events.emit(
            "rule.evaluated",
            {
                "posting_id": posting.posting_id,
                "label": verdict.label.value,
                "failed_gates": [g.value for g in verdict.failed_gates],
                "evidence_errors": len(errors),
            },
        )
        outcome = self._judge(run, posting, resume)
        record = OutputRecord(
            posting_id=posting.posting_id,
            title=posting.title,
            location=posting.location_name,
            updated_at=posting.updated_at,
            rule_verdict=verdict,
            model_judgment=outcome.judgment,
            rule_evidence_errors=list(errors),
        )
        return record, outcome

    def _saved_board(self, ref: RawRef) -> ParsedBoard | None:
        if ref.path in self._saved_boards:
            return self._saved_boards[ref.path]
        board: ParsedBoard | None = None
        try:
            data = self.d.read_repo_file(ref.path)
            if sha256_hex(data) == ref.sha256:
                board = self.d.provider.parse(data)
        except (OSError, PathRejected, InvalidResponse):
            board = None
        self._saved_boards[ref.path] = board
        return board

    def _pending_posting(
        self, pending: PendingJudgment, current: Mapping[str, Posting]
    ) -> tuple[Posting | None, str]:
        posting = current.get(pending.posting_id)
        if posting is not None:
            return posting, "board"
        saved = self._saved_board(pending.source)
        if saved is not None:
            for candidate in saved.postings:
                if (
                    candidate.index == pending.source.index
                    and candidate.posting_id == pending.posting_id
                ):
                    return candidate, "saved_raw"
        return None, "unavailable"

    def _process(
        self,
        run: _Run,
        src: SourceResult,
        raw_ref: RawRef,
        board: ParsedBoard,
        resume: VerifiedResume,
        fetched_at: datetime,
    ) -> RunReport:
        judged = _Judged()
        if run.prior is not None:
            resume_data = resume.to_dict()
            self._judge_new(run, run.prior, board, raw_ref, resume, resume_data, judged)
            self._retry_pending(run, run.prior, board, resume, resume_data, judged)
        records_saved = self._save_records(run, judged)
        new_state = self._advance(run, src, board, judged, fetched_at)
        state_saved = self._save_state(run, new_state, records_saved=records_saved)
        return self._finish(
            run,
            src,
            raw_ref,
            FetchKind.OK,
            board=board,
            judged=judged,
            unresolved=[p.posting_id for p in new_state.pending],
            records_saved=records_saved,
            state_saved=state_saved,
        )

    def _judge_new(
        self,
        run: _Run,
        prior: SeenState,
        board: ParsedBoard,
        raw_ref: RawRef,
        resume: VerifiedResume,
        resume_data: Mapping[str, Any],
        judged: _Judged,
    ) -> None:
        """Judges every posting not in ``prior.seen_ids``, in board order."""
        seen = set(prior.seen_ids)
        for posting in board.postings:
            if posting.posting_id in seen:
                continue
            judged.new_ids.append(posting.posting_id)
            record, outcome = self._record(run, posting, resume, resume_data)
            judged.records.append(record)
            judged.outcomes[posting.posting_id] = outcome
            judged.pending_sources[posting.posting_id] = RawRef(
                path=raw_ref.path, sha256=raw_ref.sha256, index=posting.index
            )

    def _retry_pending(
        self,
        run: _Run,
        prior: SeenState,
        board: ParsedBoard,
        resume: VerifiedResume,
        resume_data: Mapping[str, Any],
        judged: _Judged,
    ) -> None:
        """Retries every pending judgment, from the board or its saved raw (A26)."""
        current = {p.posting_id: p for p in board.postings}
        for pending in prior.pending:
            found, origin = self._pending_posting(pending, current)
            self.d.events.emit(
                "pending.retry",
                {"posting_id": pending.posting_id, "posting_from": origin},
            )
            if found is None:
                _note_once(run, NOTE_PENDING_SOURCE_UNAVAILABLE)
                continue
            judged.retried_ids.append(pending.posting_id)
            record, outcome = self._record(run, found, resume, resume_data)
            judged.retried.append(record)
            judged.outcomes[pending.posting_id] = outcome

    def _save_records(self, run: _Run, judged: _Judged) -> bool:
        """Writes ``records.json`` then ``retried.json``; False if either failed."""
        records_saved = _try_write(
            lambda: self.d.out.write_json_atomic(
                f"{run.run_rel}/records.json",
                _record_dump(judged.records),
                sort_keys=False,
            )
        ) and _try_write(
            lambda: self.d.out.write_json_atomic(
                f"{run.run_rel}/retried.json",
                _record_dump(judged.retried),
                sort_keys=False,
            )
        )
        self.d.events.emit(
            "records.saved",
            {
                "ok": records_saved,
                "new": len(judged.records),
                "retried": len(judged.retried),
            },
        )
        return records_saved

    def _advance(
        self,
        run: _Run,
        src: SourceResult,
        board: ParsedBoard,
        judged: _Judged,
        fetched_at: datetime,
    ) -> SeenState:
        """Computes the next state (pure ``state.advance``)."""
        original = src.original_fetched_at_utc
        return advance(
            run.prior,
            valid_ids=set(board.valid_ids),
            run_id=run.run_id,
            fetched_at=original if (self.d.seeded and original) else fetched_at,
            run_started_at=run.started_at,
            outcomes=judged.outcomes,
            pending_sources=judged.pending_sources,
            provider=self.d.provider.name,
            board=self.cfg.board.token,
            seeded=self.d.seeded,
        )

    def _save_state(
        self, run: _Run, new_state: SeenState, *, records_saved: bool
    ) -> bool:
        """Writes the state, only after the records are on disk (crash-safe order)."""
        state_saved = False
        if records_saved:
            data = state_to_bytes(new_state)
            state_saved = _try_write(
                lambda: self.d.out.write_bytes_atomic(self.state_rel, data)
            )
            if state_saved:
                _try_write(
                    lambda: self.d.out.write_bytes_atomic(
                        f"{run.run_rel}/state.after.json", data
                    )
                )
        self.d.events.emit(
            "state.saved",
            {
                "ok": state_saved,
                "seen_ids": len(new_state.seen_ids),
                "pending": len(new_state.pending),
            },
        )
        return state_saved

    def _finish(
        self,
        run: _Run,
        src: SourceResult,
        raw_ref: RawRef | None,
        fetch_kind: FetchKind,
        *,
        board: ParsedBoard | None,
        judged: _Judged | None = None,
        unresolved: Sequence[str] | None = None,
        records_saved: bool = False,
        state_saved: bool = False,
    ) -> RunReport:
        judged = judged if judged is not None else _Judged()
        if unresolved is None:
            unresolved = [p.posting_id for p in run.prior.pending] if run.prior else []
        all_records = [*judged.records, *judged.retried]
        decision = explain_status(
            fetch=fetch_kind,
            is_baseline=run.prior is None,
            new_count=len(judged.new_ids),
            failed_judgments=sum(1 for r in all_records if not _is_valid(r)),
            unresolved_pending=len(unresolved),
            data_quality_errors=board.error_count if board else 0,
            records_saved=records_saved,
            state_saved=state_saved,
            rule_evidence_errors=sum(1 for r in all_records if r.rule_evidence_errors),
        )
        if self.d.judge is None and all_records:
            _note_once(run, NOTE_JUDGE_UNAVAILABLE)
        report = _build_run_report(
            _ReportInputs(
                run=run,
                src=src,
                raw_ref=raw_ref,
                fetch_kind=fetch_kind,
                board=board,
                judged=judged,
                unresolved=list(unresolved),
                records_saved=records_saved,
                state_saved=state_saved,
                status=decision.status,
                notes=[*run.notes, *decision.notes],
            ),
            config=self.cfg,
            provider=self.d.provider.name,
            seeded=self.d.seeded,
            finished=self.d.clock.now_utc(),
        )
        self._write_report(run, report, judged)
        return report

    def _write_report(self, run: _Run, report: RunReport, judged: _Judged) -> None:
        """Writes ``report.json`` and ``report.md`` and prints the terminal summary."""
        self.d.out.write_json_atomic(
            f"{run.run_rel}/report.json",
            report.model_dump(mode="json"),
            sort_keys=False,
        )
        self.d.out.write_bytes_atomic(
            f"{run.run_rel}/report.md",
            render_markdown(report, judged.records, judged.retried).encode("utf-8"),
        )
        self.d.events.emit(
            "run.finished",
            {"status": report.status.value, "state_saved": report.state_saved},
        )
        if self.d.terminal is not None:
            self.d.terminal(render_terminal(report, judged.records, judged.retried))


@dataclass(frozen=True)
class _ReportInputs:
    """Everything one run decided, gathered for ``_build_run_report``."""

    run: _Run
    src: SourceResult
    raw_ref: RawRef | None
    fetch_kind: FetchKind
    board: ParsedBoard | None
    judged: _Judged
    unresolved: list[str]
    records_saved: bool
    state_saved: bool
    status: RunStatus
    notes: list[str]


def _build_run_report(
    facts: _ReportInputs,
    *,
    config: AgentConfig,
    provider: str,
    seeded: bool,
    finished: datetime,
) -> RunReport:
    """Builds the ``report.json`` model from what a run decided (no I/O).

    Args:
        facts: The run's bookkeeping, status and notes.
        config: The configuration (board, model settings).
        provider: The provider's registry name.
        seeded: True for a replay run.
        finished: When the run finished.

    Returns:
        The report.
    """
    run, src, board = facts.run, facts.src, facts.board
    fetch = src.fetch
    parsed = facts.fetch_kind in (FetchKind.OK, FetchKind.EMPTY) and board is not None
    counts: dict[JudgmentStatus, int] = {}
    for record in [*facts.judged.records, *facts.judged.retried]:
        status = record.model_judgment.status
        counts[status] = counts.get(status, 0) + 1
    backend = config.model.backend
    return RunReport(
        run_id=run.run_id,
        mode=RunMode.REPLAY if seeded else RunMode.LIVE,
        seeded=seeded,
        provider=provider,
        board=config.board.token,
        code_commit=run.code_commit,
        code_dirty=run.code_dirty,
        started_at_utc=run.started_at,
        started_at_et=to_eastern(run.started_at),
        finished_at_utc=finished,
        finished_at_et=to_eastern(finished),
        status=facts.status,
        fetched_count=board.fetched_count if parsed and board else None,
        unique_valid_ids=len(board.postings) if parsed and board else None,
        new_count=len(facts.judged.new_ids),
        new_ids=list(facts.judged.new_ids),
        retried_pending_ids=list(facts.judged.retried_ids),
        unresolved_pending_ids=facts.unresolved,
        judgment_counts=counts,
        data_quality_issues=list(board.data_quality) if board else [],
        records_saved=facts.records_saved,
        state_saved=facts.state_saved,
        raw_evidence=facts.raw_ref,
        original_fetched_at_utc=src.original_fetched_at_utc,
        fetch_error=src.error,
        http_status=fetch.status_code if fetch else None,
        model_backend=backend,
        model_id=config.model.model_id if backend != "none" else None,
        prompt_version=config.model.prompt_version if backend != "none" else None,
        notes=facts.notes,
    )


def run_once(deps: RunDeps) -> RunReport:
    """Runs the agent once (PLAN §1.3).

    Args:
        deps: Every collaborator, injected.

    Returns:
        The run report (also written to ``runs/<run_id>/report.json``).

    Raises:
        ResumeRefused: The résumé gate refused the fixture; nothing was fetched.
        RunLocked: Another process holds ``data/<live|seeded>/.lock``; nothing was
            fetched or written.
        RunIdTaken: A run with the same one-second run ID exists; nothing was
            fetched or written.
        StateCorrupt: The state file exists but is invalid; nothing was fetched and
            the file is untouched.
        ConfigError: The source kind contradicts ``deps.seeded``.
    """
    return _Pipeline(deps).run()


def load_report(data: bytes) -> RunReport:
    """Parses a ``report.json`` file.

    Args:
        data: The file's bytes.

    Returns:
        The report.
    """
    return RunReport.model_validate(json.loads(data))


__all__ = [
    "EvaluateFn",
    "EvidenceValidatorFn",
    "RepoReader",
    "ResumeLoader",
    "RunDeps",
    "load_report",
    "lock_rel",
    "run_once",
]
