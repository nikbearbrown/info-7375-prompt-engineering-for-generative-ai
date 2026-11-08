"""Independent check: what can the saved raw responses actually support?

It imports nothing from the agent and reads no trace or report; its only
inputs are raw response files for ONE board, given in time order:

    python3 independent_check.py EARLIER_RAW.json ... LATER_RAW.json

Rules (Swathi's decisions, 2026-11-05):
  UNREADABLE         the file is not JSON, or has no "jobs" list (e.g. a 404 body).
  EMPTY, UNVERIFIED  no body, or a "jobs" list with 0 postings: it cannot support
                     any "N new" or "finished" claim.
  DROP TO ZERO       an EMPTY response whose latest earlier readable response had
                     more than 0 postings (both counts are printed).
Not checked: partial drops (e.g. 923 -> 40) and meta.total.
Exit code 1 if any file is flagged, else 0.
"""
import hashlib
import json
from pathlib import Path
import sys

UNREADABLE = "UNREADABLE"
EMPTY = "EMPTY, UNVERIFIED"
DROP = "DROP TO ZERO"


def _count(body):
    if not body.strip():
        return 0, None
    try:
        data = json.loads(body)
    except ValueError:
        return None, UNREADABLE
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        return None, UNREADABLE
    return len(data["jobs"]), None


def check_files(paths):
    results, previous = [], None
    for path in paths:
        body = Path(path).read_bytes()
        postings, problem = _count(body)
        flags, drop_from = [], None
        if problem:
            flags.append(problem)
        elif postings == 0:
            flags.append(EMPTY)
            if previous:
                flags.append(DROP)
                drop_from = previous
        if postings is not None:
            previous = postings
        results.append({"path": str(path), "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                        "postings": postings, "flags": flags, "drop_from": drop_from})
    return results


def main(argv=None, out=sys.stdout):
    paths = sys.argv[1:] if argv is None else argv
    if not paths:
        print(__doc__, file=out)
        return 2
    results = check_files(paths)
    for r in results:
        count = "-" if r["postings"] is None else r["postings"]
        flags = "; ".join(f"{DROP} ({r['drop_from']} -> 0)" if f == DROP else f for f in r["flags"]) or "ok"
        print(f"{r['path']}\n  sha256 {r['sha256']}  bytes {r['bytes']}  postings {count}  -> {flags}", file=out)
    flagged = sum(1 for r in results if r["flags"])
    print(f"{flagged} of {len(results)} responses flagged" + (": no 'N new' or 'finished' claim is supported by "
          "a flagged response" if flagged else ""), file=out)
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
