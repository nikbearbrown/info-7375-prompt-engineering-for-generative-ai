"""One run, end to end: inputs -> boards (the loop) -> judges -> output -> state. The CLI and the tests both call run().

The order is the contract's safety net, so it lives in exactly one place: inputs are checked
before any board is touched, and state is written last, after verdicts are on disk, and only for
boards that ended `ok` (GATE WV2) — a crash or a failed board can never mark new postings as seen
without them being judged.
"""

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from . import inputs, report
from .common.errors import AgentError, InputError, MissingInputError
from .common.paths import Paths, stamp
from .common.policy import Confirm, Policy, PolicyError, refuse
from .judges import claude, claude_api, claude_cli
from .loop import claude_step, exits, runner
from .loop.budget import LIMITS, Budget, Limits
from .loop.results import OK
from .loop.trace import Trace
from .watch import board_list
from .watch import state as state_file


DEFAULT_PROMPT = "claude_judge.v1"
# How the real Claude is reached. "cli" (Claude Code subscription) is the default since D18;
# "api" needs ANTHROPIC_API_KEY and API credits. Both give the judge the same ask().
CLAUDE_LINES = {"cli": claude_cli, "api": claude_api}
DEFAULT_VIA = "cli"


@dataclass(frozen=True)
class RunOutcome:
    folder: Path
    summary: str
    exit: str


def run(board: str | None, resume_path: Path, profile_path: Path, paths: Paths,
        from_raw: Path | None = None, now: datetime | None = None, fetcher=None,
        ask: claude.Ask | None = None, prompt_name: str = DEFAULT_PROMPT, via: str = DEFAULT_VIA,
        confirm: Confirm = refuse, clock=time.monotonic, limits: Limits = LIMITS,
        use_claude: bool = False) -> RunOutcome:
    """board None runs every board in data/boards.json (JS2 D17); a name runs only that one.

    use_claude is off by default (D1): only the rule judges, Claude is never built, prompts/ and
    api.anthropic.com stay closed. When on, every new posting goes to Claude until its
    budget (30 calls, 300 s in total) runs out (GATE §2, D20, loop/claude_step.py).

    ask is the Claude call; None means "build the real one through `via`". Tests pass a fake so
    they never reach Claude, whatever is installed or exported on the machine. confirm answers
    "overwrite this existing run record?"; the default refuses (GATE §5). clock and limits let
    tests make time pass and reach a budget's edge; the real limits are fixed (GATE §2)."""
    now = now or datetime.now(timezone.utc)
    st = stamp(now)
    if via not in CLAUDE_LINES:
        raise InputError(f"--claude-via must be one of {sorted(CLAUDE_LINES)}, got {via!r}")
    if from_raw is not None and board is None:
        raise InputError("--from-raw replays one board's saved response: name the board with --board")
    policy = Policy.for_run(paths, claude_via=via if use_claude else None, confirm=confirm)
    # Folders are named by the second, so a second run in the same second would overwrite the
    # first one's record: ask (JS2 D15) before doing anything, not halfway through.
    policy.check_write(paths.run(st))
    policy.check_write(paths.raw(st))

    for path in (paths.boards, resume_path, profile_path, paths.skill_aliases, paths.no_sponsorship_phrases):
        _check_read_if_present(policy, path)
    listed = board_list.load(paths.boards)
    targets = [board_list.find(listed, board)] if board else listed
    criteria = inputs.load_criteria(resume_path, profile_path, paths)
    prompt = _load_prompt(paths, prompt_name, policy) if use_claude else None

    budget, trace = Budget(limits, clock), Trace(clock)
    ctx = runner.Context(paths, policy, criteria, now, paths.raw(st), budget, trace,
                         fetcher=fetcher, from_raw=from_raw, clock=clock)
    results, shared = runner.run_boards(targets, ctx)
    ok = [r for r in results if r.status == OK]

    c = claude_step.ClaudeOutcome()
    if use_claude:
        make_ask = (lambda timeout_s: ask) if ask else (
            lambda timeout_s: CLAUDE_LINES[via].make_ask(policy, timeout_s=timeout_s))
        c = claude_step.run_claude(ok, criteria, make_ask, prompt, budget, trace)
    # Each verdict names its board: the same job id on two boards is two postings (GATE WV1).
    verdicts = [{**r.verdict, "board": b.board} for b in ok for r in b.rule_results]
    verdicts += [{**v, "board": name} for name, vs in c.by_board.items() for v in vs]

    exit_, reason = exits.decide(results, shared, (c.budget_stop,) if c.budget_stop else ())
    trace.run_end(exit_, reason, budget.snapshot())
    info = report.ClaudeInfo(prompt.name if prompt else "", claude.MODEL,
                             via if ask is None else "injected", on=use_claude)
    run_info = report.RunInfo(now.strftime("%Y-%m-%dT%H:%M:%SZ"), exit_, reason, budget.snapshot())
    folder = paths.run(st)
    summary = report.summary_text(run_info, results, c.by_board, paths, profile_path, info, folder / "trace.jsonl")
    try:
        report.write_run(folder, run_info, report.board_rows(results, paths), verdicts, summary,
                         trace.jsonl(), policy, c.raw)
    except (PolicyError, OSError) as e:
        # Code 401 (GATE §4): without the record, saving state would hide these postings for good.
        raise AgentError(f"could not write the run record: {e}") from e
    for r in ok:
        state_file.save(policy.check_write(paths.state(r.board)), r.watch.next_state)
    return RunOutcome(folder, summary, exit_)


def _check_read_if_present(policy: Policy, path: Path) -> None:
    """A missing file keeps its own clear "not found" message from the loader; the policy only
    rules on files that exist (a missing file outside the folders can't be read anyway)."""
    if Path(path).exists():
        policy.check_read(path)


def _load_prompt(paths: Paths, name: str, policy: Policy) -> claude.Prompt:
    """Checked with the other inputs, before the board is touched: a typo in --prompt must not cost a run."""
    path = paths.prompt(name)
    _check_read_if_present(policy, path)   # also stops --prompt ../something
    if not path.exists():
        raise MissingInputError(f"prompt file not found: {paths.show(path)}")
    return claude.Prompt.load(path)

