"""Finished-wrong demo (JS2 Step 7, R20, D6): one run of the real agent that ends `finished` and is wrong.

The setup is seeded, not observed: Greenhouse has never been seen to do this (11/07: Stripe 765 = 765).
Starting from the real Stripe response saved in Step 6 (766 jobs, `meta.total` 766), the 86
postings that were new since the 10/31 state are taken out of the list, and `meta.total` is left
as the board sent it. That is a board answering 200 with valid JSON and a list that is complete in
form but missing postings. The agent replays it against the 10/31 state and reports 0 new jobs,
although 86 were posted.

Why the output goes to demo/finished_wrong/out/ and not the repo's runs/ and state/: those hold
the real runs (Step 6). Paths(out=...) moves the whole run record, the same way the tests do.
Why it calls job_agent.__main__.main: that is the command a person runs, so the demo shows what
the real agent prints, exit status included.

Usage (from the repo root): .venv/bin/python demo/finished_wrong/run_demo.py
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))   # run as a script from anywhere, without installing the package

from job_agent import __main__ as cli            # noqa: E402
from job_agent.common.paths import Paths          # noqa: E402

REAL_RAW = REPO / "evidence" / "raw" / "2026-11-08T234257Z" / "stripe_content.json"   # Step 6, committed
OLD_STATE = HERE / "input" / "stripe.state.2026-10-31.json"                            # 757 ids, from git 08e3c9d
OUT = HERE / "out"
# Under out/evidence/raw/ because the run's policy only reads saved responses from there (GATE §5).
SEEDED = OUT / "evidence" / "raw" / "seeded" / "stripe_missing_new_postings.json"


def build() -> tuple[int, int, int]:
    """Write the seeded response and the 10/31 state; return (jobs in the real list, jobs kept, meta.total)."""
    real = json.loads(REAL_RAW.read_text())
    seen = set(json.loads(OLD_STATE.read_text())["seen_ids"])
    kept = [j for j in real["jobs"] if j["id"] in seen]
    seeded = {**real, "jobs": kept}            # meta (total 766) stays as the board sent it
    SEEDED.parent.mkdir(parents=True)
    SEEDED.write_text(json.dumps(seeded))
    (OUT / "state").mkdir(parents=True)
    (OUT / "state" / "stripe.state.json").write_text(OLD_STATE.read_text())
    return len(real["jobs"]), len(kept), real["meta"]["total"]


def main() -> int:
    if OUT.exists():
        # The run record is evidence; refuse instead of silently mixing a second run into it.
        print(f"{OUT.relative_to(REPO)}/ already exists: delete it to run the demo again.", file=sys.stderr)
        return 2
    real, kept, total = build()
    print(f"Seeded: {SEEDED.relative_to(REPO)} · {kept} of {real} real jobs kept · meta.total still {total}")
    print(f"State: 10/31 ({OLD_STATE.relative_to(REPO)}), so the {real - kept} removed postings were the new ones\n")
    return cli.main(["--board", "stripe", "--from-raw", str(SEEDED)], paths=Paths(out=OUT))


if __name__ == "__main__":
    sys.exit(main())
