"""Collect postings by running JS2's loop UNCHANGED (agent/loop.py,
agent/boards.py, agent/permissions.py, agent/fetch.py are imported from the
JS2 project, not copied).

The only thing JS3 sets is root=<this project>, so JS2's WritePolicy confines
every write to this project's evidence/, state/, logs/ and JS2's own folder is
never touched. Budgets, retries, allow-list and the new-board approval gate
are JS2's, as-is.

    python3 -m js3.collect                       # later runs
    python3 -m js3.collect --approve-new-boards  # first run here (no state/ yet)

JS2's location: $JS2_ROOT, default ~/Desktop/js2-loop-tools-diff.
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS2_ROOT = Path(os.environ.get("JS2_ROOT", Path.home() / "Desktop" / "js2-loop-tools-diff")).resolve()
BOARDS = ["gitlab", "stripe", "palantir"]


def js2_loop():
    if str(JS2_ROOT) not in sys.path:
        sys.path.insert(0, str(JS2_ROOT))
    from agent import loop  # JS2's package
    assert Path(loop.__file__).resolve().is_relative_to(JS2_ROOT), loop.__file__
    return loop


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--approve-new-boards", action="store_true",
                    help="pass --approve-new-board for all three boards (first run in this project)")
    args = ap.parse_args(argv)
    loop = js2_loop()
    print(f"# JS2 loop imported from {loop.__file__}")
    print(f"# writing under {ROOT} (evidence/, state/, logs/ only - JS2 WritePolicy)")
    report = loop.run(BOARDS, root=ROOT, approved_new_boards=set(BOARDS) if args.approve_new_boards else ())
    print(loop.format_report(report))
    return loop.EXIT_CODES[report["exit"]]


if __name__ == "__main__":
    sys.exit(main())
