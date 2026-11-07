"""Pick the 20 real postings for hand labeling, from run 1's saved raw response.
Committed (with its output) before Shreyash labeled anything or saw the list.

Procedure, fixed in advance:
1. Pool = postings whose department is Engineering, Data, Product & Design or Security, or whose
   title contains engineer, software, developer, data, scien, machine learning, AI or ML.
   (A random draw from the whole board would be almost all claims, actuarial and clinical
   jobs, which every judge gets right and which teach nothing.)
2. One posting per distinct title (the same title in another city has the same ad text),
   choosing which city with random.Random(7375).
3. Draw 20 titles with the same generator, then the first 10 drawn are DEVELOPMENT and the
   last 10 are HELD-OUT.
No rule verdict, Claude verdict or content was looked at while choosing."""
import json
import pathlib
import random
import re
import sys

RAW = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "runs/raw/oscar-20261029T031015Z.json")
DEPTS = {"Engineering", "Data", "Product & Design", "Security"}
TITLE = re.compile(r"engineer|software|developer|data|scien|machine learning|\bAI\b|\bML\b", re.I)

jobs = json.loads(RAW.read_bytes())["jobs"]
pool = [j for j in jobs if {d["name"] for d in j["departments"]} & DEPTS or TITLE.search(j["title"])]
rng = random.Random(7375)
by_title = {}
for j in sorted(pool, key=lambda j: j["id"]):
    by_title.setdefault(j["title"].strip(), []).append(j)
one_each = [rng.choice(group) for _, group in sorted(by_title.items())]
drawn = rng.sample(one_each, 20)
out = {
    "raw_file": str(RAW),
    "procedure": __doc__.strip(),
    "pool_size": len(pool),
    "distinct_titles_in_pool": len(one_each),
    "development": [{"id": j["id"], "title": j["title"]} for j in drawn[:10]],
    "held_out": [{"id": j["id"], "title": j["title"]} for j in drawn[10:]],
}
pathlib.Path("experiments/selected_postings.json").write_text(json.dumps(out, indent=2) + "\n")
print(f"pool {len(pool)}, distinct titles {len(one_each)}; wrote experiments/selected_postings.json")
