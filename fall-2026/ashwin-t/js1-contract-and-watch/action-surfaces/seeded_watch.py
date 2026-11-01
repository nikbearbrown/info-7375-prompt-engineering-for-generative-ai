"""Action surface 3, run on the same posting: a SEEDED REPLAY through the real watch.

The live runs found no new posting, so the watch never judged 7855793003. This replays run 2's saved,
real board response against a scratch copy of the state with that one id removed, so the watch treats it as
new. It goes through the normal path: persona check, parse, new-since-last by id, rule record, one real
`claude -p` call with revision-v2, validation, report, then the scratch state update.

The committed `state/seen_ids.json` and `runs/` are only read, never written. Every output is under
`action-surfaces/3-watch-seeded/`, and the report is labeled SEEDED REPLAY.

    python3 action-surfaces/seeded_watch.py
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTING_ID = "7855793003"
RAW = "runs/2026-10-31T16-09-43Z/raw-response.json"      # run 2, live, unchanged
COLLECTED_AT = "2026-10-31T16:09:43Z"
OUT = Path("action-surfaces/3-watch-seeded")


def main() -> int:
    if (ROOT / OUT / "runs").exists():
        print(f"{OUT}/runs already exists; this replay is run once", file=sys.stderr)
        return 1
    state = json.loads((ROOT / "state/seen_ids.json").read_text(encoding="utf-8"))
    if POSTING_ID not in state["seen_ids"]:
        print(f"{POSTING_ID} is not in the committed state", file=sys.stderr)
        return 1
    state["seen_ids"] = [i for i in state["seen_ids"] if i != POSTING_ID]
    seeded = json.dumps(state, indent=2) + "\n"
    (ROOT / OUT / "state").mkdir(parents=True)
    (ROOT / OUT / "state-before-seeded.json").write_text(seeded, encoding="utf-8")   # kept as evidence
    (ROOT / OUT / "state" / "seen_ids.json").write_text(seeded, encoding="utf-8")    # the watch updates this
    cmd = [sys.executable, "-m", "jobwatch", "--fixture", RAW, "--collected-at", COLLECTED_AT, "--seeded",
           "--state", str(OUT / "state" / "seen_ids.json"), "--runs", str(OUT / "runs"),
           "--judge", "claude", "--prompt", "prompts/revision-v2.md"]
    (ROOT / OUT / "command.txt").write_text(" ".join(cmd[1:]) + "\n", encoding="utf-8")
    return subprocess.run(cmd, cwd=ROOT).returncode


if __name__ == "__main__":
    sys.exit(main())
