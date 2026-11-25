"""Recompute "new since the last run" from two saved responses, without the agent's code.

It checks the contract's failure sentence by recomputation: run 2's new ids must be exactly the ids
in run 2's response that were not in run 1's. This holds when run 1 was the baseline and there was
no run in between (otherwise "seen" includes those runs' ids too).

Usage:  python3 tools/recompute_new.py runs/<run 1>/response.json runs/<run 2>/response.json [runs/<run 2>/report.json]
With a report, exit 1 if the report's new ids differ from the recomputed ones.
"""

import hashlib
import json
import sys


def ids(path):
    raw = open(path, "rb").read()
    jobs = json.loads(raw.decode("utf-8"))["jobs"]
    return {job["id"]: job["title"] for job in jobs}, hashlib.sha256(raw).hexdigest()


def main(argv):
    if len(argv) not in (2, 3):
        print(__doc__)
        return 2
    (first, sha1), (second, sha2) = ids(argv[0]), ids(argv[1])
    new = sorted(set(second) - set(first))
    gone = sorted(set(first) - set(second))
    print(f"run 1: {len(first)} postings, SHA-256 {sha1}")
    print(f"run 2: {len(second)} postings, SHA-256 {sha2}")
    print(f"new in run 2 (recomputed): {len(new)}")
    for posting_id in new:
        print(f"  {posting_id}  {second[posting_id]}")
    print(f"gone in run 2 (recomputed): {len(gone)}")
    if len(argv) == 3:
        report = json.load(open(argv[2], encoding="utf-8"))
        reported = sorted(item["id"] for item in report["new"])
        reported_gone = sorted(item["id"] for item in report["gone"])
        same = reported == new and reported_gone == gone
        print(f"report says {len(reported)} new and {len(reported_gone)} gone: {'MATCH' if same else 'MISMATCH'}")
        return 0 if same else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
