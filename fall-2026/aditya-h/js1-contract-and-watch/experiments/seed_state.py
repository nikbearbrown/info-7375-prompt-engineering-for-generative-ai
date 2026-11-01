"""SEEDED second run helper. Builds a state file representing the board as it stood before a cutoff,
using only a real saved response: every posting whose own `first_published` is before the cutoff
counts as already seen. Nothing is invented; this is a reconstruction, labeled SEEDED everywhere.

Limits: postings removed from the board before the saved response are not in it, and a posting
re-published under the same id keeps its original first_published.

Usage: python3 experiments/seed_state.py RAW_JSON CUTOFF_ISO OUT_STATE
"""
import datetime as dt
import json
import pathlib
import sys

raw, cutoff, out = sys.argv[1], dt.datetime.fromisoformat(sys.argv[2]), pathlib.Path(sys.argv[3])
jobs = json.loads(pathlib.Path(raw).read_text())["jobs"]
seen = sorted(j["id"] for j in jobs if dt.datetime.fromisoformat(j["first_published"]) < cutoff)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({"board": "stripe", "last_run": cutoff.isoformat(), "seen_ids": seen,
                           "SEEDED": f"reconstructed from {raw}: postings first_published before {cutoff.isoformat()}"},
                          indent=1) + "\n")
print(f"seeded {len(seen)} of {len(jobs)} ids as seen; {len(jobs) - len(seen)} will be new")
