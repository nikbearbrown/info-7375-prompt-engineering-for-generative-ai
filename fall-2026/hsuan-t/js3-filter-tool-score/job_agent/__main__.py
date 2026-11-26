"""Command line entry: `python -m job_agent` runs one bounded loop over every board in data/boards.json
(JS2 D17), so a TA can reproduce a run with one command (R33). `--board NAME` runs a single board.

Only argument parsing and printing live here; the run itself is pipeline.run(), which tests call directly.
"""

import argparse
import sys
from pathlib import Path

from .common.errors import AgentError
from .common.paths import Paths
from .common.policy import ask_terminal, refuse
from .loop import codes, exits
from .pipeline import CLAUDE_LINES, DEFAULT_PROMPT, DEFAULT_VIA, run

# Process exit status, so a script or scheduler can tell the run's exit without reading files:
# only `finished` is success; a run that stopped early is not (JS2 D3).
STATUS = {exits.FINISHED: 0, exits.ERROR: 1, exits.INCOMPLETE: 2, exits.BUDGET_EXHAUSTED: 2}


def main(argv: list[str] | None = None, paths: Paths | None = None) -> int:
    paths = paths or Paths()
    p = argparse.ArgumentParser(prog="python -m job_agent",
                                description="Watch every board in data/boards.json (Greenhouse or Ashby) and judge new postings.")
    p.add_argument("--board", help="run only this board name from data/boards.json (default: every board)")
    p.add_argument("--resume", type=Path, default=paths.default_resume)
    p.add_argument("--profile", type=Path, default=paths.default_profile)
    p.add_argument("--from-raw", type=Path, help="replay a saved raw response instead of fetching (a 'seeded' run; needs --board)")
    p.add_argument("--claude", action="store_true",
                   help="also ask Claude about every new posting, until 30 calls or 300 s of Claude time are used (off by default)")
    # The Step 9 experiment runs the same postings under two prompt files; this picks which one.
    p.add_argument("--claude-via", choices=sorted(CLAUDE_LINES), default=DEFAULT_VIA,
                   help="cli = Claude Code subscription (claude -p); api = ANTHROPIC_API_KEY + API credits (default: %(default)s)")
    p.add_argument("--prompt", default=DEFAULT_PROMPT, help=f"Claude prompt file in prompts/, without .md (default: {DEFAULT_PROMPT})")
    args = p.parse_args(argv)

    try:
        # GATE §5: ask only when a person is at the terminal; piped or scheduled runs refuse.
        confirm = ask_terminal if sys.stdin.isatty() else refuse
        outcome = run(args.board, args.resume, args.profile, paths, from_raw=args.from_raw,
                      prompt_name=args.prompt, via=args.claude_via, confirm=confirm, use_claude=args.claude)
    except AgentError as e:
        # Before or after the loop (inputs, run folders, writing the record): the run is `error`.
        print(f"ERROR {codes.describe(codes.for_setup(e))}: {e}", file=sys.stderr)
        return 1
    print(outcome.summary, end="")
    print(f"Run output: {paths.show(outcome.folder)}/ · exit: {outcome.exit}")
    return STATUS[outcome.exit]


if __name__ == "__main__":
    sys.exit(main())
