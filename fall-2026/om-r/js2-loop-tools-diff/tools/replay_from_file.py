"""Replay one saved board response through the REAL, unmodified loop - no
network, and the project's real state is never written.

JS1 had `--from-file` on its watch command. JS2's loop CLI deliberately has
no such flag: replaying into a scratch state would need a CLI override of
the write root, which GATE.md's permission policy does not allow. So the
replay lives here instead, outside the agent:

  1. create a fresh scratch root in the system temp directory;
  2. copy the board's REAL state file (state/<board>_seen.json) into it, so
     the replay is judged against the real seen-ids (not a baseline);
  3. call agent.loop.run() with root=<scratch> and a fetch that returns the
     saved file's bytes for exactly that board's URL (anything else raises);
  4. print agent.loop.format_report() exactly as the loop produces it;
  5. hash the real state file before and after to show it is untouched.

Greenhouse boards only (one request per board). Files with SEEDED in their
name are labeled as constructed input in this output.

Both of these work, from any directory:

    python3 tools/replay_from_file.py --board stripe --from-file evidence/stripe_SEEDED_empty_<ts>.json
    python3 -m tools.replay_from_file --board stripe --from-file evidence/stripe_SEEDED_empty_<ts>.json
"""
import argparse
import hashlib
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Run as a script (python3 tools/replay_from_file.py), Python puts tools/ - not
# the project root - first on sys.path, so `import agent` would fail. Put the
# project root there explicitly so script mode and -m mode behave the same.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent import boards as boards_mod  # noqa: E402
from agent import loop  # noqa: E402


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", required=True, choices=sorted(boards_mod.BOARDS))
    ap.add_argument("--from-file", required=True, type=Path)
    ap.add_argument("--keep-scratch", action="store_true", help="do not delete the scratch root afterwards")
    args = ap.parse_args(argv)

    if boards_mod.ats_of(args.board) != "greenhouse":
        ap.error("replay supports single-request Greenhouse boards only")
    real_state = ROOT / "state" / f"{args.board}_seen.json"
    if not real_state.exists():
        ap.error(f"{real_state} does not exist; a replay is judged against the real state")

    raw = args.from_file.read_bytes()
    url = boards_mod.page_url(args.board, 0)
    seeded = "SEEDED" in args.from_file.name

    def replay_fetch(requested, timeout=None):
        if requested != url:
            raise AssertionError(f"replay fetch asked for {requested}, only {url} is replayed")
        return raw

    scratch = Path(tempfile.mkdtemp(prefix="js2_replay_"))
    (scratch / "state").mkdir()
    shutil.copy2(real_state, scratch / "state" / real_state.name)
    before = sha256(real_state)

    print("=" * 72)
    if seeded:
        print("SEEDED REPLAY - constructed input, NOT live board data")
    else:
        print("REPLAY of a saved real response - no network")
    print(f"board:        {args.board}")
    print(f"replayed:     {args.from_file}  ({len(raw)} bytes, sha256 {sha256(args.from_file)[:16]})")
    print(f"state copied: {real_state.relative_to(ROOT)} -> <scratch>/state/{real_state.name}")
    print(f"scratch root: {scratch}")
    print("=" * 72)

    report = loop.run([args.board], root=scratch, fetch=replay_fetch, approved_new_boards=set())

    print("----- loop's own report (agent.loop.format_report, unmodified) -----")
    print(loop.format_report(report))
    print("----- end of loop's own report -----")
    print("note: paths in the loop's report (evidence, run log) are inside the scratch root, "
          "not the project" + ("" if args.keep_scratch else "; the scratch root is deleted below"))
    print(f"real {real_state.relative_to(ROOT)} unchanged: {sha256(real_state) == before}")
    if args.keep_scratch:
        print(f"scratch kept at {scratch}")
    else:
        shutil.rmtree(scratch)
    return loop.EXIT_CODES[report["exit"]]


if __name__ == "__main__":
    sys.exit(main())
