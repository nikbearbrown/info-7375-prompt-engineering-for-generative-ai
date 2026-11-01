"""Make a SEEDED 'earlier' board response from a real saved one.

It removes every posting whose `first_published` is on or after a cutoff, so the result
looks like the board before those postings appeared. Everything else is byte-for-byte
the same JSON objects. The output is labeled seeded wherever it is used.

    python scripts/make_seeded_earlier.py runs/<live run>/raw.json.gz 2026-10-30 evidence/seeded/earlier.json.gz
"""
import gzip
import json
import sys

src, cutoff, dst = sys.argv[1], sys.argv[2], sys.argv[3]
data = json.loads(gzip.decompress(open(src, "rb").read()))
removed = [j for j in data["jobs"] if (j.get("first_published") or "")[:10] >= cutoff]
data["jobs"] = [j for j in data["jobs"] if (j.get("first_published") or "")[:10] < cutoff]
data["_seeded"] = {"from": src, "removed_first_published_on_or_after": cutoff,
                   "removed_ids": [j["id"] for j in removed]}
with gzip.open(dst, "wt") as f:
    json.dump(data, f)
print(f"kept {len(data['jobs'])}, removed {len(removed)}: " + ", ".join(f"{j['id']} {j['title'].strip()!r}" for j in removed))
