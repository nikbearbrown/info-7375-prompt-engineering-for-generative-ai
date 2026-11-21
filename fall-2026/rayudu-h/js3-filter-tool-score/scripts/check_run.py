"""Independent check of a finished run: it does not read the agent's report or verdicts.

For each board in a run it reads the saved raw response itself (plain json, not the agent's
parser) and compares the number of postings with the count from the state file the run
started from. A board whose raw response holds 0 postings, when the earlier state had some,
is flagged: "no new jobs" cannot be trusted for it.

    python scripts/check_run.py runs/<run id> <state file the run started from>
Exit 1 if anything is flagged.
"""
import gzip
import json
import sys
from pathlib import Path

run_dir, before = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text())
flags = []
for raw in sorted((run_dir / "raw").glob("*.json.gz")):
    system, board = raw.name[: -len(".json.gz")].split("-", 1)
    data = json.loads(gzip.decompress(raw.read_bytes()))
    n = len(data.get("jobs", [])) if isinstance(data, dict) else 0
    prev = (before["boards"].get(f"{system}:{board}") or {}).get("last_good_count")
    line = f"{system}:{board}: raw holds {n} postings; state before the run said {prev}"
    if prev and n == 0:
        flags.append(line + "  <-- EMPTY BOARD: 'no new jobs' here is not evidence")
    print(line)
print()
print("\n".join(flags) if flags else "no board flagged")
sys.exit(1 if flags else 0)
