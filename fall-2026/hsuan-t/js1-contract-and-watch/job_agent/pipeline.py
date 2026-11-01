"""One run, end to end: inputs -> watch -> judges -> output -> state. The CLI and the tests both call run().

The order is the contract's safety net, so it lives in exactly one place: inputs are checked
before the board is touched, and the state is written last, after verdicts are on disk — a crash
while judging can never mark new postings as seen without them being judged.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from . import inputs, report
from .common.errors import ClaudeCallError, InputError, WatchError
from .common.paths import Paths, stamp
from .judges import claude, claude_api, claude_cli, rule
from .watch import state as state_file
from .watch import watch


DEFAULT_PROMPT = "claude_judge.v1"
# How the real Claude is reached. "cli" (Claude Code subscription) is the default since D18;
# "api" needs ANTHROPIC_API_KEY and API credits. Both give the judge the same ask().
CLAUDE_LINES = {"cli": claude_cli, "api": claude_api}
DEFAULT_VIA = "cli"


@dataclass(frozen=True)
class RunOutcome:
    folder: Path
    summary: str


def run(board: str, resume_path: Path, profile_path: Path, paths: Paths,
        from_raw: Path | None = None, now: datetime | None = None, fetcher=None,
        ask: claude.Ask | None = None, prompt_name: str = DEFAULT_PROMPT, via: str = DEFAULT_VIA) -> RunOutcome:
    """ask is the Claude call; None means "build the real one through `via`". Tests pass a fake so
    they never reach Claude, whatever is installed or exported on the machine."""
    now = now or datetime.now(timezone.utc)
    st = stamp(now)
    # Folders are named by the second; a second run in the same second would crash halfway
    # (raw saved, verdicts not), so refuse before doing anything.
    if paths.run(st).exists() or paths.raw(st).exists():
        raise WatchError(f"a run already used the time {st}; run again in a second")

    criteria = inputs.load_criteria(resume_path, profile_path, paths)
    prompt = _load_prompt(paths, prompt_name)
    if via not in CLAUDE_LINES:
        raise InputError(f"--claude-via must be one of {sorted(CLAUDE_LINES)}, got {via!r}")
    w = watch(board, paths.state(board), paths.raw(st), now, from_raw=from_raw,
              **({"fetcher": fetcher} if fetcher else {}))

    rule_results = [rule.judge(p, criteria) for p in w.new]
    claude_results = _claude(w.new, criteria, ask, prompt, via)
    claude_verdicts = [r.verdict for r in claude_results]
    verdicts = [r.verdict for r in rule_results] + claude_verdicts

    info = report.ClaudeInfo(prompt.name, claude.MODEL, via if ask is None else "injected")
    summary = report.summary_text(w, rule_results, claude_verdicts, paths, profile_path, info)
    report.write_run(paths.run(st), w, verdicts, summary, paths, [r.raw for r in claude_results])
    state_file.save(paths.state(board), w.next_state)
    return RunOutcome(paths.run(st), summary)


def _load_prompt(paths: Paths, name: str) -> claude.Prompt:
    """Checked with the other inputs, before the board is touched: a typo in --prompt must not cost a run."""
    path = paths.prompt(name)
    if not path.exists():
        raise InputError(f"prompt file not found: {paths.show(path)}")
    return claude.Prompt.load(path)


def _claude(new, criteria, ask, prompt, via) -> list[claude.ClaudeResult]:
    """Build the real Claude call only when there is something to judge, and turn "can't call
    Claude" (CLI missing, no key, SDK missing) into per-posting errors: the rule's verdicts still
    count (CONTRACT In)."""
    reason = ""
    if new and ask is None:
        try:
            ask = CLAUDE_LINES[via].make_ask()
        except ClaudeCallError as e:
            reason = str(e)
        except ImportError:
            reason = "the anthropic package is not installed (pip install -r requirements.txt)"
    return claude.judge_new(new, criteria, ask, prompt, no_ask_reason=reason)
