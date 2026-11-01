"""Pick the 20 postings for the prompt experiment from the saved baseline response, then split them
10 development / 10 held-out. Deterministic (fixed seed) so anyone can recompute the selection.

Selection is stratified by title text so the set is not ~95% "not relevant", and each stratum is
split evenly between dev and held-out:
  A. 8 titles containing a CONTRACT Check-1 phrase (product manager/analyst/strategy/operations/owner)
     -> 4 dev, 4 held-out. Location is NOT used, so these can still be not_relevant.
  B. 6 other titles containing the word "product" (near-misses) -> 3 dev, 3 held-out.
  C. 6 titles from everything else -> 3 dev, 3 held-out.
No full rule verdict and no Claude output is used to choose.

History (2026-10-31): a first draw (14 "product" titles + 6 others, unstratified split) put zero
PM-family titles in the dev set, which would make the dev comparison meaningless. It was discarded
before any labeling or Claude call, and replaced by this stratified version.

Usage: python3 experiments/select_postings.py runs/raw/stripe-20261101T024132Z.json
"""
import json
import random
import sys

SEED = 7375


def main(raw_path):
    jobs = json.load(open(raw_path))["jobs"]
    jobs = sorted(jobs, key=lambda j: j["id"])
    phrases = ("product manager", "product analyst", "product strategy", "product operations", "product owner")
    title = lambda j: " ".join(j["title"].lower().split())
    a = [j for j in jobs if any(p in title(j) for p in phrases)]
    b = [j for j in jobs if j not in a and "product" in title(j)]
    c = [j for j in jobs if j not in a and j not in b]
    rng = random.Random(SEED)
    picked = []
    for pool, n in ((a, 8), (b, 6), (c, 6)):
        draw = rng.sample(pool, n)
        picked += [("dev", j) for j in draw[: n // 2]] + [("heldout", j) for j in draw[n // 2:]]
    rng.shuffle(picked)
    picked.sort(key=lambda sj: sj[0])  # dev rows first, order within each set shuffled
    rows = []
    for split, j in picked:
        rows.append({
            "set": split,
            "id": j["id"],
            "title": j["title"].strip(),
            "location_name": j["location"]["name"],
            "offices": [o["name"] for o in j.get("offices", [])],
            "url": j.get("absolute_url"),
        })
    json.dump({"source": raw_path, "seed": SEED, "postings": rows}, open("experiments/prompt/selection.json", "w"),
              indent=1, ensure_ascii=False)
    with open("experiments/prompt/labels.csv", "w") as f:
        f.write("set,id,title,location_name,offices,hand_label,note\n")
        for r in rows:
            cells = [r["set"], str(r["id"]), r["title"], r["location_name"], " | ".join(r["offices"]), "", ""]
            f.write(",".join('"' + c.replace('"', '""') + '"' for c in cells) + "\n")
    print(f"wrote {len(rows)} postings")


if __name__ == "__main__":
    main(sys.argv[1])
