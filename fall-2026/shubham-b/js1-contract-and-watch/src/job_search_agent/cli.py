"""``jsa`` command-line entry point (PLAN §1.5).

Every command builds its collaborators from the real modules, inside the command:

* ``resume.load_verified_resume``: the §12 résumé gate.
* ``fsio.OutputRoot`` (the only write root) and ``fsio.ReadPolicy`` (read roots).
* ``http.build_fetcher_from_settings``: the allow-listed fetcher (live runs only).
* ``providers.get_provider``: the configured board provider.
* ``rule.verdict.evaluate`` and ``evidence_validator.validate_rule_evidence``.
* ``judge.judge.build_judge`` with ``judge.prompt.load_prompt`` (``jsa run``), and
  ``judge.judge.build_backend`` with ``judge.judge.probe_model``
  (``jsa doctor --probe-model``). Backend ``none`` builds no judge, so every
  judgment is an honest ``UNAVAILABLE`` and the run is PARTIAL_FAILURE.
* ``privacy.sensitive_values`` and ``privacy.scan_tree``: ``jsa audit-privacy``.
* ``experiments.cli.register``: the ``jsa exp ...`` group.

Exit codes follow PLAN §1.4: 0 BASELINE/SUCCESS_*, 1 PARTIAL_FAILURE, 2 fetch or
response failure, 3 résumé refused, 4 state corrupt, 5 configuration error; 6 is the
experiments CLI's refused gate; 7 (``LOCKED``) means another ``jsa run`` or ``jsa
pending drop`` holds ``data/<live|seeded>/.lock`` (or a run already used this
second's run ID), so nothing was done and the command can be retried. Nothing
printed here contains résumé values, credentials or absolute paths.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from job_search_agent.clock import SystemClock
from job_search_agent.config import (
    DEFAULT_CONFIG_PATH,
    AgentConfig,
    ConfigOverrides,
    ModelBackendKind,
    load_config,
)
from job_search_agent.errors import (
    AgentError,
    ConfigError,
    PathRejected,
    ResumeRefused,
    StateCorrupt,
)
from job_search_agent.events import EventLog
from job_search_agent.evidence_validator import validate_rule_evidence
from job_search_agent.experiments.cli import register as register_experiments
from job_search_agent.fsio import (
    OutputRoot,
    ReadPolicy,
    create_output_root,
    relative_within,
)
from job_search_agent.http import build_fetcher_from_settings
from job_search_agent.judge.judge import build_backend, build_judge, probe_model
from job_search_agent.judge.prompt import load_prompt
from job_search_agent.models import (
    ExitCode,
    RunReport,
    SeenState,
    VerifiedResume,
    exit_code_for_status,
)
from job_search_agent.pipeline import (
    RunDeps,
    load_report,
    lock_rel,
    run_once,
)
from job_search_agent.ports import (
    Clock,
    CommandRunner,
    Judge,
    RawSource,
)
from job_search_agent.privacy import scan_tree, sensitive_values
from job_search_agent.providers import get_provider
from job_search_agent.report import render_runs_markdown
from job_search_agent.resume import load_verified_resume
from job_search_agent.rule.verdict import evaluate
from job_search_agent.sources import (
    EvidenceStatus,
    LiveSource,
    ReplaySource,
    verify_saved_evidence,
)
from job_search_agent.state import (
    drop_pending,
    parse_state,
    read_state_rel,
    state_to_bytes,
)
from job_search_agent.sysio import SubprocessGit, SubprocessRunner, minimal_env

Handler = Callable[[argparse.Namespace], int]
"""A subcommand handler: receives parsed arguments, returns the exit code."""

type Subparsers = argparse._SubParsersAction[argparse.ArgumentParser]
"""The object returned by ``add_subparsers``; registrars add commands to it."""

GITIGNORE_REQUIRED = (
    "private/",
    "*.resume.json",
    "!*.resume.example.json",
    "data/tmp/",
)
"""``.gitignore`` lines ``jsa doctor`` requires (CONTRACT §12, PLAN §4)."""

DATA_DIR_HELP = (
    "override [data].dir (relative to the project root; must stay inside it), "
    "e.g. data/scratch for trial runs that must not touch data/live or data/seeded"
)

CLAUDE_VERSION_TIMEOUT_S = 15.0

PROBE_FACTS = (
    "available",
    "unavailable_reason",
    "claude_version",
    "model_requested",
    "model_served",
    "session_id",
    "is_error",
    "backend_error",
    "reply_is_ok",
)
"""Probe report fields ``jsa doctor --probe-model`` prints (never reply text)."""


# --- components -----------------------------------------------------------------


def _load_resume(cfg: AgentConfig) -> VerifiedResume:
    """Runs the §12 résumé gate on the configured fixture.

    The fixture is read through ``fsio.ReadPolicy``, so a path outside the read
    roots (``persona/``, ``evidence/``, ...) is refused.

    Raises:
        ResumeRefused: Any §12 check failed.
        ConfigError: The fixture path is outside the project root or the read roots.
    """
    return load_verified_resume(
        cfg.resume_path,
        cfg.resume.pinned_sha256,
        read_bytes=ReadPolicy(cfg.project_root).read_bytes,
        project_root=cfg.project_root,
    )


def _judge(
    cfg: AgentConfig,
    out: OutputRoot,
    clock: Clock,
    runner: CommandRunner,
    *,
    seeded: bool,
    read: Callable[[Path], bytes],
    events: EventLog | None = None,
) -> tuple[Judge | None, str | None]:
    """Builds the Claude judge, or explains why judgments will be ``UNAVAILABLE``.

    Args:
        cfg: The configuration; ``[model]`` selects the backend and prompt.
        out: The data-root writer (raw-reply logs, per-call empty directories).
        clock: The clock.
        runner: Runs ``claude``.
        seeded: Written into every raw-reply log (``True`` for replay runs).
        read: Reads the prompt file through the read policy.
        events: The run's event log (backend cleanup events).

    Returns:
        ``(judge, unavailable_reason)``. Backend ``none`` gives ``(None,
        "backend_none")`` (never a silent fallback: the records say UNAVAILABLE with
        this reason and the run is PARTIAL_FAILURE); a real judge gives
        ``(judge, None)``.
    """
    if cfg.model.backend == "none":
        return None, "backend_none"
    prompt = load_prompt(cfg.project_root, cfg.model.prompt_version, read_bytes=read)
    judge = build_judge(
        cfg.model,
        prompt,
        runner=runner,
        writer=out,
        make_empty_dir=out.make_empty_dir,
        clock=clock,
        repo_rel=cfg.repo_rel,
        seeded=seeded,
        events=events,
    )
    return judge, None


def _repo_rel(cfg: AgentConfig, path: Path) -> str:
    """Returns ``path`` (relative to the cwd) relative to the project root.

    Raises:
        ConfigError: The path is outside the project root (``fsio.relative_within``).
    """
    try:
        return relative_within(path.absolute(), cfg.project_root, allow_root=True)
    except PathRejected:
        raise ConfigError("path must be inside the project root") from None


# --- run ------------------------------------------------------------------------


def build_run_deps(
    cfg: AgentConfig,
    replay: Path | None,
    *,
    clock: Clock | None = None,
    runner: CommandRunner | None = None,
    transport: httpx.BaseTransport | None = None,
) -> RunDeps:
    """Wires the real collaborators for ``jsa run``.

    Args:
        cfg: The configuration (with any CLI overrides applied).
        replay: A saved raw response to replay (seeded run), or ``None`` for live.
        clock: The clock; defaults to ``SystemClock``.
        runner: Runs ``git`` and ``claude``; defaults to ``SubprocessRunner``.
        transport: The fetcher's inner transport; defaults to TLS-verifying HTTPS.

    Returns:
        The run dependencies.

    Raises:
        ConfigError: The provider is unknown or the replay path is outside the
            project.
    """
    clock = clock or SystemClock()
    runner = runner or SubprocessRunner()
    events = EventLog(clock)
    out = create_output_root(cfg.data_dir)
    read = ReadPolicy(cfg.project_root).read_bytes
    provider = get_provider(cfg.board.provider)
    source: RawSource
    if replay is not None:
        source = ReplaySource(
            cfg.project_root / _repo_rel(cfg, replay),
            _repo_rel(cfg, replay),
            read_bytes=read,
        )
    else:
        url = provider.jobs_url(cfg.board.token)
        fetcher = build_fetcher_from_settings(cfg.http, inner=transport, events=events)
        source = LiveSource(fetcher, url)
    judge, reason = _judge(
        cfg, out, clock, runner, seeded=replay is not None, read=read, events=events
    )
    return RunDeps(
        config=cfg,
        clock=clock,
        source=source,
        provider=provider,
        load_resume=lambda: _load_resume(cfg),
        evaluate=evaluate,
        validate_evidence=validate_rule_evidence,
        judge=judge,
        out=out,
        git=SubprocessGit(cfg.project_root, runner=runner),
        events=events,
        seeded=replay is not None,
        read_repo_file=lambda rel: read(cfg.project_root / rel),
        unavailable_reason=reason,
        terminal=lambda text: print(text, end=""),
    )


def _config(
    args: argparse.Namespace, *, model_backend: ModelBackendKind | None = None
) -> AgentConfig:
    overrides = ConfigOverrides(data_dir=args.data_dir, model_backend=model_backend)
    return load_config(args.config, overrides=overrides)


def cmd_run(args: argparse.Namespace) -> int:
    """``jsa run [--replay RAW] [--model-backend claude-cli|none]``."""
    cfg = _config(args, model_backend=args.model_backend)
    report: RunReport = run_once(build_run_deps(cfg, args.replay))
    return int(exit_code_for_status(report.status))


# --- doctor ---------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Check:
    """One ``jsa doctor`` line."""

    name: str
    level: str
    """``OK``, ``WARN``, ``SKIP`` or ``FAIL``."""
    detail: str
    refused: bool = False
    """True only when the résumé gate refused the fixture (exit 3)."""


def _check_claude(cfg: AgentConfig, runner: CommandRunner) -> Check:
    if cfg.model.backend == "none":
        return Check("claude", "SKIP", "model backend is 'none'")
    found = shutil.which(cfg.model.executable)
    if found is None:
        return Check(
            "claude", "WARN", "executable not on PATH; judgments will be UNAVAILABLE"
        )
    try:
        done = runner.run(
            [found, "--version"],
            cwd=cfg.project_root,
            env=minimal_env(),
            stdin="",
            timeout_s=CLAUDE_VERSION_TIMEOUT_S,
        )
    except OSError:
        return Check("claude", "WARN", "found on PATH but could not be started")
    version = (done.stdout.strip().splitlines() or ["?"])[0][:80]
    if done.returncode != 0:
        return Check("claude", "WARN", "found on PATH; --version failed")
    return Check("claude", "OK", f"found on PATH, version {version}")


def _check_resume(cfg: AgentConfig) -> Check:
    try:
        _load_resume(cfg)
    except ResumeRefused as exc:
        codes = ", ".join(sorted(exc.codes))
        return Check("resume", "FAIL", f"refused: {codes}", refused=True)
    except ConfigError as exc:
        return Check("resume", "FAIL", str(exc))
    return Check(
        "resume",
        "OK",
        f"{cfg.resume.path} passed every check (pinned digest, fictional persona)",
    )


def _check_gitignore(cfg: AgentConfig) -> Check:
    path = cfg.project_root / ".gitignore"
    try:
        lines = {line.strip() for line in path.read_text(encoding="utf-8").splitlines()}
    except OSError:
        return Check("gitignore", "FAIL", ".gitignore not readable")
    missing = [rule for rule in GITIGNORE_REQUIRED if rule not in lines]
    if missing:
        return Check("gitignore", "FAIL", "missing rules: " + ", ".join(missing))
    return Check("gitignore", "OK", "required rules present")


def _read_state(cfg: AgentConfig, rel: str) -> SeenState | None:
    """Reads a state file through ``OutputRoot`` (a symlink is refused, not followed).

    Returns:
        The state, or ``None`` when it (or the data directory) is absent.

    Raises:
        PathRejected: The path violates the file policy (e.g. a symlink).
        StateCorrupt: The file exists but is not a valid state.
    """
    if not cfg.data_dir.is_dir():
        return None
    data = read_state_rel(rel, OutputRoot(cfg.data_dir).read_bytes)
    return None if data is None else parse_state(data)


def _check_state(cfg: AgentConfig, *, seeded: bool) -> Check:
    rel = cfg.state_rel(seeded=seeded)
    name = "seeded state" if seeded else "live state"
    try:
        state = _read_state(cfg, rel)
    except StateCorrupt as exc:
        return Check(name, "FAIL", f"{rel}: corrupt ({exc.reason})")
    except PathRejected as exc:
        return Check(name, "FAIL", f"{rel}: refused ({exc.reason})")
    if state is None:
        return Check(name, "OK", f"{rel}: absent (next run is a baseline)")
    return Check(
        name,
        "OK",
        f"{rel}: seen={len(state.seen_ids)} pending={len(state.pending)}",
    )


def doctor_checks(cfg: AgentConfig, runner: CommandRunner) -> list[Check]:
    """Runs every offline doctor check (no network, no model call).

    Args:
        cfg: The configuration.
        runner: Used only for ``claude --version``.

    Returns:
        The checks, in display order.
    """
    py = sys.version_info
    checks = [
        Check(
            "python",
            "OK" if py >= (3, 12) else "FAIL",
            f"{py.major}.{py.minor}.{py.micro}",
        ),
        Check("config", "OK", "loaded and validated"),
        _check_claude(cfg, runner),
        _check_resume(cfg),
        _check_gitignore(cfg),
        Check("allow-list", "OK", ", ".join(cfg.http.allowed_hosts)),
    ]
    data_rel = cfg.data_dir.relative_to(cfg.project_root.resolve()).as_posix()
    if cfg.data_dir.is_dir():
        writable = os.access(cfg.data_dir, os.W_OK)
        checks.append(
            Check(
                "data dir",
                "OK" if writable else "FAIL",
                f"{data_rel}/ {'writable' if writable else 'not writable'}",
            )
        )
    else:
        checks.append(Check("data dir", "WARN", f"{data_rel}/ absent; created on run"))
    checks += [_check_state(cfg, seeded=False), _check_state(cfg, seeded=True)]
    return checks


def _probe_model(cfg: AgentConfig) -> int:
    """Makes the one-call model probe and records it under ``data/doctor/``.

    Returns:
        ``OK``; a probe that could not call the model or got an unexpected reply is
        printed as ``WARN`` with the recorded facts.
    """
    clock = SystemClock()
    out = create_output_root(cfg.data_dir)
    backend = build_backend(
        cfg.model,
        runner=SubprocessRunner(),
        make_empty_dir=out.make_empty_dir,
        clock=clock,
    )
    result = probe_model(
        backend, model_requested=cfg.model.model_id, clock=clock, writer=out
    )
    report = result.report
    level = "OK" if report.reply_is_ok and report.backend_error is None else "WARN"
    where = cfg.repo_rel(result.data_rel) if result.data_rel else "nowhere"
    print(f"[{level}] probe-model: facts recorded in {where}")
    facts = report.model_dump(mode="json")
    for key in PROBE_FACTS:
        print(f"  {key}: {json.dumps(facts[key])}")
    return int(ExitCode.OK)


def cmd_doctor(args: argparse.Namespace) -> int:
    """``jsa doctor [--probe-model]``."""
    cfg = _config(args)
    checks = doctor_checks(cfg, SubprocessRunner())
    for check in checks:
        print(f"[{check.level}] {check.name}: {check.detail}")
    if any(c.refused for c in checks):
        return int(ExitCode.RESUME_REFUSED)
    if any(c.level == "FAIL" for c in checks):
        return int(ExitCode.CONFIG_ERROR)
    if args.probe_model:
        return _probe_model(cfg)
    return int(ExitCode.OK)


# --- pending ----------------------------------------------------------------------


def cmd_pending_list(args: argparse.Namespace) -> int:
    """``jsa pending list [--data live|seeded]``."""
    cfg = _config(args)
    rel = cfg.state_rel(seeded=args.data == "seeded")
    state = _read_state(cfg, rel)
    if state is None:
        print(f"{rel}: absent (no baseline yet)")
        return int(ExitCode.OK)
    print(f"{rel}: {len(state.pending)} pending, {len(state.abandoned)} abandoned")
    for p in state.pending:
        print(
            f"  {p.posting_id} last_status={p.last_status.value} "
            f"attempts={p.attempts} queued={p.queued_run_id} "
            f"last_attempt={p.last_attempt_run_id}"
        )
    for a in state.abandoned:
        print(f"  [abandoned] {a.posting_id} dropped={a.dropped_at_utc.isoformat()}")
    return int(ExitCode.OK)


def cmd_pending_drop(args: argparse.Namespace) -> int:
    """``jsa pending drop <posting_id> --reason TEXT [--data live|seeded]``."""
    cfg = _config(args)
    seeded = args.data == "seeded"
    rel = cfg.state_rel(seeded=seeded)
    out = create_output_root(cfg.data_dir)
    with out.lock(lock_rel(seeded=seeded)):
        data = read_state_rel(rel, out.read_bytes)
        if data is None:
            raise ConfigError("no state file; nothing is pending")
        state = parse_state(data)
        try:
            dropped = drop_pending(
                state,
                args.posting_id,
                reason=args.reason,
                dropped_at=SystemClock().now_utc(),
            )
        except KeyError as exc:
            raise ConfigError("posting is not pending") from exc
        except ValueError as exc:
            raise ConfigError("a non-empty --reason is required") from exc
        out.write_bytes_atomic(rel, state_to_bytes(dropped))
    print(f"dropped {args.posting_id} from pending in {rel} (decision recorded)")
    return int(ExitCode.OK)


# --- rule ---------------------------------------------------------------------------


def cmd_rule(args: argparse.Namespace) -> int:
    """``jsa rule --raw RAW --id ID``: print one posting's rule record (pure)."""
    cfg = _config(args)
    resume = _load_resume(cfg)
    read = ReadPolicy(cfg.project_root).read_bytes
    provider = get_provider(cfg.board.provider)
    board = provider.parse(read(cfg.project_root / _repo_rel(cfg, args.raw)))
    matches = [p for p in board.postings if p.posting_id == args.posting_id]
    if not matches:
        raise ConfigError("posting id not found in the raw file")
    posting = matches[0]
    verdict = evaluate(posting, resume)
    errors = validate_rule_evidence(verdict, posting.raw, resume.to_dict())
    record: dict[str, Any] = {
        "posting_id": posting.posting_id,
        "title": posting.title,
        "location": posting.location_name,
        "updated_at": posting.updated_at,
        "rule_verdict": verdict.model_dump(mode="json"),
        "rule_evidence_errors": errors,
    }
    print(json.dumps(record, indent=2, ensure_ascii=False))
    return int(ExitCode.OK if not errors else ExitCode.PARTIAL_FAILURE)


# --- verify-evidence / audit-privacy / docs --------------------------------------


def cmd_verify_evidence(args: argparse.Namespace) -> int:
    """``jsa verify-evidence``: re-hash every saved raw file against its meta."""
    cfg = _config(args)
    checks = verify_saved_evidence(cfg.project_root.resolve())
    if not checks:
        print("no saved raw evidence found")
    for c in checks:
        print(f"[{c.status.value}] {c.descriptor} -> {c.raw or '<invalid pointer>'}")
    bad = [c for c in checks if c.status is not EvidenceStatus.OK]
    return int(ExitCode.OK if not bad else ExitCode.PARTIAL_FAILURE)


def cmd_audit_privacy(args: argparse.Namespace) -> int:
    """``jsa audit-privacy [PATH]``: scan outputs with the privacy scanner."""
    cfg = _config(args)
    target_rel = _repo_rel(cfg, args.path)
    values = sensitive_values(_load_resume(cfg))
    findings = scan_tree(cfg.project_root / target_rel, values)
    for finding in findings:
        print(f"[FINDING] {finding.describe()}")
    print(f"audit-privacy {target_rel}: {len(findings)} finding(s)")
    return int(ExitCode.OK if not findings else ExitCode.PARTIAL_FAILURE)


def collect_reports(data_dir: Path) -> list[RunReport]:
    """Loads every ``runs/*/report.json`` under the data directory.

    Args:
        data_dir: The data directory.

    Returns:
        The reports (unparseable files are skipped).
    """
    reports: list[RunReport] = []
    for path in sorted(data_dir.glob("*/runs/*/report.json")):
        try:
            reports.append(load_report(path.read_bytes()))
        except (OSError, ValueError):
            continue
    return reports


def cmd_docs_render(args: argparse.Namespace) -> int:
    """``jsa docs render``: print ``docs/RUNS.md`` (live and seeded tables)."""
    cfg = _config(args)
    print(render_runs_markdown(collect_reports(cfg.data_dir)), end="")
    return int(ExitCode.OK)


# --- parser -----------------------------------------------------------------------


def _add_run(sub: Subparsers) -> None:
    parser = sub.add_parser("run", help="fetch the board once, apply the rule, judge")
    parser.add_argument(
        "--replay",
        type=Path,
        metavar="RAW_JSON",
        help="replay a saved raw response instead of fetching (seeded run)",
    )
    parser.add_argument(
        "--model-backend",
        choices=("claude-cli", "none"),
        help="override [model].backend; 'none' marks every judgment UNAVAILABLE",
    )
    parser.set_defaults(handler=cmd_run)


def _add_doctor(sub: Subparsers) -> None:
    parser = sub.add_parser("doctor", help="offline environment and fixture checks")
    parser.add_argument(
        "--probe-model",
        action="store_true",
        help="make one tiny real model call and record the facts in data/doctor/",
    )
    parser.set_defaults(handler=cmd_doctor)


def _add_pending(sub: Subparsers) -> None:
    parser = sub.add_parser("pending", help="inspect or drop pending judgments")
    actions = parser.add_subparsers(dest="pending_action", required=True)
    list_parser = actions.add_parser("list", help="list pending judgments")
    list_parser.add_argument("--data", choices=("live", "seeded"), default="live")
    list_parser.set_defaults(handler=cmd_pending_list)
    drop_parser = actions.add_parser("drop", help="stop retrying one posting")
    drop_parser.add_argument("posting_id")
    drop_parser.add_argument("--reason", required=True, help="documented reason")
    drop_parser.add_argument("--data", choices=("live", "seeded"), default="live")
    drop_parser.set_defaults(handler=cmd_pending_drop)


def _add_rule(sub: Subparsers) -> None:
    parser = sub.add_parser("rule", help="print the rule record for one posting")
    parser.add_argument("--raw", type=Path, required=True, metavar="RAW_JSON")
    parser.add_argument("--id", dest="posting_id", required=True)
    parser.set_defaults(handler=cmd_rule)


def _add_verify_evidence(sub: Subparsers) -> None:
    parser = sub.add_parser(
        "verify-evidence", help="recompute every saved raw sha256 against its meta"
    )
    parser.set_defaults(handler=cmd_verify_evidence)


def _add_audit_privacy(sub: Subparsers) -> None:
    parser = sub.add_parser(
        "audit-privacy", help="scan outputs for résumé values, credentials, abs paths"
    )
    parser.add_argument("path", type=Path, nargs="?", default=Path("data"))
    parser.set_defaults(handler=cmd_audit_privacy)


def _add_docs(sub: Subparsers) -> None:
    parser = sub.add_parser("docs", help="render generated documentation to stdout")
    actions = parser.add_subparsers(dest="docs_action", required=True)
    render = actions.add_parser("render", help="print docs/RUNS.md from report.json")
    render.set_defaults(handler=cmd_docs_render)


_REGISTRY: tuple[Callable[[Subparsers], None], ...] = (
    _add_run,
    _add_doctor,
    _add_pending,
    _add_rule,
    _add_verify_evidence,
    _add_audit_privacy,
    _add_docs,
    register_experiments,
)


def build_parser() -> argparse.ArgumentParser:
    """Builds the full ``jsa`` argument parser.

    Returns:
        The parser; every subcommand sets a ``handler`` default.
    """
    parser = argparse.ArgumentParser(
        prog="jsa",
        description=(
            "Job-Search Agent: discovery only. Watches one public job board, applies a "
            "deterministic rule and records a separate Claude opinion."
        ),
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"configuration file (default: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument("--data-dir", default=None, help=DATA_DIR_HELP)
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    for register in _REGISTRY:
        register(sub)
    _accept_data_dir_everywhere(parser)
    return parser


def _accept_data_dir_everywhere(parser: argparse.ArgumentParser) -> None:
    """Lets ``--data-dir`` follow any subcommand (``jsa run --data-dir X``).

    Subcommands use ``default=SUPPRESS`` so they never overwrite a value given
    before the subcommand.
    """
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for child in action.choices.values():
                child.add_argument(
                    "--data-dir", default=argparse.SUPPRESS, help=DATA_DIR_HELP
                )
                _accept_data_dir_everywhere(child)


def main(argv: Sequence[str] | None = None) -> int:
    """Runs ``jsa``.

    Args:
        argv: Arguments without the program name; defaults to ``sys.argv[1:]``.

    Returns:
        The process exit code. Deliberate failures (``AgentError``) print their
        content-free message and return their own exit code; an unexpected I/O
        error prints its error text (never a path) and returns 5.
    """
    args = build_parser().parse_args(argv)
    handler: Handler = args.handler
    try:
        return handler(args)
    except AgentError as exc:
        print(f"jsa: {exc}", file=sys.stderr)
        return int(exc.exit_code)
    except OSError as exc:
        print(f"jsa: I/O error: {exc.strerror or type(exc).__name__}", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)


if __name__ == "__main__":
    sys.exit(main())
