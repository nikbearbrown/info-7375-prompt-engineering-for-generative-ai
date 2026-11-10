"""One-time step, run before JS2's first live run: start the Anthropic board from JS1's state.

    python3 scripts/import_js1_state.py

Reads JS1's state file and the two raw responses it was built from (read only), checks
that the state's 675 seen ids are exactly the ids in those responses, and writes
jobs/state/greenhouse-anthropic.json with both JS1 runs as the board's history, so
check_run.py can recompute "new since 2026-10-31" from JS1's saved bytes.
This is not the agent and does not go through its policy; it refuses to overwrite.
"""

import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
JS1 = HERE.parent / "js1-contract-and-watch"
JS1_STATE = JS1 / "state" / "anthropic.state.json"
TARGET = HERE / "jobs" / "state" / "greenhouse-anthropic.json"


def main():
    if TARGET.exists():
        print("refused: %s exists; not overwriting it" % TARGET.relative_to(HERE), file=sys.stderr)
        return 1
    state_bytes = JS1_STATE.read_bytes()
    state = json.loads(state_bytes)
    seen = sorted(str(i) for i in state["seen_ids"])
    runs, from_raw = [], set()
    for js1_run in state["runs"]:
        raw = gzip.decompress((JS1 / js1_run["raw_file"]).read_bytes())
        ids = {str(job["id"]) for job in json.loads(raw)["jobs"]}
        from_raw |= ids
        runs.append({"run_id": "js1-run-%d" % js1_run["run_number"], "source": "live (JS1)",
                     "postings": len(ids), "new": js1_run["new"],
                     "raw_file": "../js1-contract-and-watch/" + js1_run["raw_file"],
                     "raw_sha256": hashlib.sha256(raw).hexdigest(), "started_at": js1_run["started_at"]})
    if from_raw != set(seen):
        print("refused: JS1's seen ids are not the ids in its raw responses", file=sys.stderr)
        return 1
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps({
        "system": "greenhouse", "board": "anthropic", "seen_ids": seen, "runs": runs,
        "imported_from": {"file": "../js1-contract-and-watch/state/anthropic.state.json",
                          "sha256": hashlib.sha256(state_bytes).hexdigest(),
                          "note": "JS1's state, converted to JS2's format (ids as strings); 675 ids, "
                                  "equal to the ids in JS1's two raw responses"},
    }, indent=2) + "\n", encoding="utf-8")
    print("wrote %s: %d seen ids from %d JS1 runs" % (TARGET.relative_to(HERE), len(seen), len(runs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
