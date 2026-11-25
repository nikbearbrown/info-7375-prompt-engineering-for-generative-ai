"""Compare two results files from run_filter.py. Usage: python scripts/diff_runs.py results/a.json results/b.json"""
import collections
import json
import sys

a = {(r["board"], r["id"]): r for r in json.load(open(sys.argv[1], encoding="utf-8"))}
b = {(r["board"], r["id"]): r for r in json.load(open(sys.argv[2], encoding="utf-8"))}
moved = [(k, a[k], b[k]) for k in a if (a[k]["verdict"], a[k]["failed_check"]) != (b[k]["verdict"], b[k]["failed_check"])]
print(f"{len(moved)} of {len(a)} postings changed verdict")
print(collections.Counter(f"{x['verdict']}/{x['failed_check']} -> {y['verdict']}/{y['failed_check']}" for _, x, y in moved))
for k, x, y in moved[:12]:
    print(f"  {k[0]} {x['title'][:60]!r}: {x['failed_check']} -> {y['failed_check']} {y['verdict']}")
