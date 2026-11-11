"""The independent check (GATE.md §6).

This program **never reads a run report**. It reads the saved raw responses in
`evidence/raw/` and the floors I wrote by hand in `config/boards.json`, parses
the responses with the provider adapters, and compares each board's latest
count against its own previous count on disk. That is what makes it
independent: the agent's own account of the run has no way to influence it.

It exists for one specific failure the loop cannot see. A board that answers
HTTP 200 with an empty postings array gives the loop nothing to complain about:
the request succeeded, the schema parsed, zero postings were found, so zero are
new, and `finished` is the honest status for what the loop knows. It is still
wrong when the board has jobs and the token now points at a retired board, or
when the provider renamed a field.

    python3 tools/crosscheck.py
    python3 tools/crosscheck.py --raw-dir evidence/seeded/wrong-answer --boards config/boards-wronganswer.json

Exit codes: 0 nothing flagged, 1 at least one flag. A flag is not proof of a
bug; it is a place I have to look myself.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent import providers  # noqa: E402
from agent.errors import SchemaFailure  # noqa: E402

#: raw files are named <utc-stamp>-<provider>-<token>.json by agent.loop
NAME = re.compile(r"^(?P<stamp>\d{8}T\d{6}Z)-(?P<board>.+)\.json$")

DROP_RATIO = 0.5


def group_by_board(raw_dir: Path) -> dict[str, list[Path]]:
    groups: dict[str, list[Path]] = defaultdict(list)
    for path in sorted(raw_dir.glob("*.json")):
        m = NAME.match(path.name)
        if not m:
            continue
        groups[m.group("board")].append(path)
    return {b: sorted(p) for b, p in groups.items()}


def count_postings(board_key: str, path: Path) -> int | None:
    """Parse one saved response with its own provider adapter."""
    provider_name = board_key.split("-", 1)[0]
    try:
        provider = providers.get(provider_name)
    except KeyError:
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return len(provider.parse(board_key, payload))
    except (json.JSONDecodeError, SchemaFailure):
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--raw-dir", default="evidence/raw")
    ap.add_argument("--boards", default="config/boards.json")
    ap.add_argument("--state", default="evidence/state/seen.json")
    args = ap.parse_args(argv)

    raw_dir = Path(args.raw_dir)
    plan = json.loads(Path(args.boards).read_text(encoding="utf-8"))["boards"]
    floors = {e["board"].replace(":", "-"): e.get("expect_at_least", 0) for e in plan}

    state_counts = {}
    state_path = Path(args.state)
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state_counts = {
            b.replace(":", "-"): v.get("last_count")
            for b, v in (state.get("boards") or {}).items()
        }

    groups = group_by_board(raw_dir)
    if not groups:
        print(f"crosscheck: no saved responses in {raw_dir}")
        return 1

    flags: list[tuple[str, str]] = []
    print(f"crosscheck: reading {raw_dir} (never the run report)\n")
    print(f"{'board':30s} {'latest':>7s} {'previous':>9s} {'floor':>6s} {'state':>6s}  flags")
    totals_latest = totals_previous = 0

    for board, paths in sorted(groups.items()):
        latest = count_postings(board, paths[-1])
        previous = count_postings(board, paths[-2]) if len(paths) > 1 else None
        floor = floors.get(board)
        st = state_counts.get(board)
        row_flags = []

        if latest is None:
            row_flags.append("UNPARSEABLE")
        else:
            totals_latest += latest
            if previous is not None:
                totals_previous += previous
            if floor is not None and latest < floor:
                row_flags.append("BELOW_FLOOR")
            if previous is not None and latest == 0 and previous > 0:
                row_flags.append("SUSPECT_EMPTY")
            if previous and previous > 0 and latest < previous * DROP_RATIO:
                row_flags.append("SUSPECT_DROP")
        if board not in floors:
            row_flags.append("NOT_IN_PLAN")

        print(
            f"{board:30s} {str(latest):>7s} {str(previous):>9s} "
            f"{str(floor):>6s} {str(st):>6s}  {','.join(row_flags) or '-'}"
        )
        flags.extend((board, f) for f in row_flags)

    if totals_previous and totals_latest < totals_previous * DROP_RATIO:
        flags.append(("<run total>", "SUSPECT_TOTAL"))
        print(
            f"\n{'<run total>':30s} {totals_latest:>7d} {totals_previous:>9d} "
            f"{'-':>6s} {'-':>6s}  SUSPECT_TOTAL"
        )

    print()
    if not flags:
        print("crosscheck: nothing flagged.")
        return 0
    for board, flag in flags:
        print(f"FLAG {flag:14s} {board}")
    print(
        f"\ncrosscheck: {len(flags)} flag(s). A flag is not proof of a bug; it is a "
        "place I have to look myself."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
