"""Command line entry: `python -m job_agent` runs one full watch + judge, so a TA can reproduce a run with one command (R33).

Only argument parsing and printing live here; the run itself is pipeline.run(), which tests call directly.
"""

import argparse
import sys
from pathlib import Path

from .common.errors import AgentError
from .common.paths import Paths
from .pipeline import CLAUDE_LINES, DEFAULT_PROMPT, DEFAULT_VIA, run


def main(argv: list[str] | None = None, paths: Paths | None = None) -> int:
    paths = paths or Paths()
    p = argparse.ArgumentParser(prog="python -m job_agent", description="Watch one Greenhouse board and judge new postings.")
    p.add_argument("--board", default="stripe", help="Greenhouse board slug (default: stripe)")
    p.add_argument("--resume", type=Path, default=paths.default_resume)
    p.add_argument("--profile", type=Path, default=paths.default_profile)
    p.add_argument("--from-raw", type=Path, help="replay a saved raw response instead of fetching (a 'seeded' run)")
    # The Step 9 experiment runs the same postings under two prompt files; this picks which one.
    p.add_argument("--claude-via", choices=sorted(CLAUDE_LINES), default=DEFAULT_VIA,
                   help="cli = Claude Code subscription (claude -p); api = ANTHROPIC_API_KEY + API credits (default: %(default)s)")
    p.add_argument("--prompt", default=DEFAULT_PROMPT, help=f"Claude prompt file in prompts/, without .md (default: {DEFAULT_PROMPT})")
    args = p.parse_args(argv)

    try:
        outcome = run(args.board, args.resume, args.profile, paths, from_raw=args.from_raw, prompt_name=args.prompt, via=args.claude_via)
    except AgentError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(outcome.summary, end="")
    print(f"Run output: {paths.show(outcome.folder)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
