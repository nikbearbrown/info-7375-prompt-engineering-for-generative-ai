"""Pick the 20 real postings for hand labeling: 10 development, 10 held-out.

Sampled from the live baseline response with a fixed seed. To make sure both sets contain
postings that could plausibly be relevant, each set gets 6 postings whose TITLE passes the
title test and has no management word, and 4 others. Only the title is used to stratify;
the skills test (which needs the description) is not computed here. The sheet shows the
labeler only id, title, location and link, never a verdict.

    python scripts/select_postings.py runs/<live baseline>/raw.json.gz experiment/labels.csv
"""
import csv
import gzip
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jsagent import rule  # noqa: E402

SEED = 20261031
src, out = sys.argv[1], sys.argv[2]
jobs = json.loads(gzip.decompress(open(src, "rb").read()))["jobs"]
jobs = sorted(jobs, key=lambda j: j["id"])
title_ok = [j for j in jobs if rule.find_words(j["title"], ["AI", "Engineer", "Engineering"])
            and not rule.find_words(j["title"], rule.MANAGEMENT_WORDS)]
others = [j for j in jobs if j not in title_ok]
rng = random.Random(SEED)
a, b = rng.sample(title_ok, 12), rng.sample(others, 8)
dev, held = a[:6] + b[:4], a[6:] + b[4:]
rng.shuffle(dev); rng.shuffle(held)
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["set", "id", "title", "location", "url", "hand_label", "skills_found_by_hand", "note"])
    for name, group in (("dev", dev), ("heldout", held)):
        for j in group:
            w.writerow([name, j["id"], j["title"].strip(), j["location"]["name"], j["absolute_url"], "", "", ""])
print(f"title-ok pool {len(title_ok)}, others {len(others)}; wrote {out}")
