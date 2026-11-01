"""Build a SEEDED "earlier" response for the baseline run (assignment Step 2 allows this, clearly labeled).

    python3 seed.py --published-before 2026-10-29

Fetches the live board once (allow-listed), saves that raw response as evidence, then writes
evidence/seeded/earlier-response-before-<date>.json.gz: the same response with every posting whose
first_published is on or after the cutoff removed, plus a top-level "_SEEDED" note saying so.

Limit: postings that closed before today are absent from both files, so the seeded file is only an
approximation of what the board looked like before the cutoff.
"""

import argparse
import gzip
import datetime as dt
import json
from pathlib import Path

from jsagent.fetch import board_url, fetch
from jsagent.watch import parse_jobs, save_raw

HERE = Path(__file__).resolve().parent


def seed(raw, cutoff):
    data = json.loads(raw)
    kept = [j for j in data["jobs"] if j["first_published"][:10] < cutoff]
    removed = [str(j["id"]) for j in data["jobs"] if j["first_published"][:10] >= cutoff]
    data["jobs"] = kept
    data["meta"] = {"total": len(kept)}
    data["_SEEDED"] = (f"Constructed, not fetched: the live response minus the {len(removed)} postings with "
                       f"first_published >= {cutoff}. Removed ids: {', '.join(removed)}")
    return data, removed


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--board", default="stripe")
    p.add_argument("--published-before", required=True, help="YYYY-MM-DD; postings first published on/after this are removed")
    args = p.parse_args()
    dt.date.fromisoformat(args.published_before)

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw = fetch(board_url(args.board))
    parse_jobs(raw)
    record = save_raw(raw, HERE / "evidence" / "raw", stamp, "live-seed-source")
    data, removed = seed(raw, args.published_before)
    out = HERE / "evidence" / "seeded" / f"earlier-response-before-{args.published_before}.json.gz"
    out.parent.mkdir(parents=True, exist_ok=True)
    data["_SEEDED"] += f". Source: evidence/raw/{record['file']} (sha256 {record['sha256_of_raw']})."
    out.write_bytes(gzip.compress(json.dumps(data, ensure_ascii=False).encode(), mtime=0))
    print(f"live source saved: evidence/raw/{record['file']}")
    print(f"seeded file: {out.relative_to(HERE)} — kept {len(data['jobs'])}, removed {len(removed)}")


if __name__ == "__main__":
    main()
