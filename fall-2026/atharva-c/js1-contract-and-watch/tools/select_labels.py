"""Pick 20 real postings for hand-labeling from the committed baseline response.

Pool: every posting whose title contains "engineer" or "developer" (any case,
any seniority), so the set holds real near-misses rather than 738 obvious
non-matches. Twenty are drawn with a fixed seed and split 10 dev / 10 held-out
by the same seed. The sheet is blind: no rule or Claude verdict is shown.

    python3 -m tools.select_labels runs/2026-10-30T063746Z/raw.json
"""
import csv
import json
import random
import sys
from pathlib import Path

from agent import rule

SEED = 7375
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "labels"


def main(raw_path):
    jobs = json.loads(Path(raw_path).read_text())["jobs"]
    pool = sorted((j for j in jobs if any(w in j["title"].lower() for w in rule.TITLE_WORDS)),
                  key=lambda j: j["id"])
    rng = random.Random(SEED)
    picked = rng.sample(pool, 20)
    sets = ["dev"] * 10 + ["held-out"] * 10
    rng.shuffle(sets)

    (OUT / "postings").mkdir(parents=True, exist_ok=True)
    with open(OUT / "sheet.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["posting_id", "set", "title", "location", "url", "my_label", "my_reason"])
        for j, s in sorted(zip(picked, sets), key=lambda x: (x[1] != "dev", x[0]["id"])):
            w.writerow([j["id"], s, j["title"].strip(), j["location"]["name"].strip(),
                        j["absolute_url"], "", ""])
            text = rule.posting_text(j)
            (OUT / "postings" / f"{j['id']}.txt").write_text(
                f"{j['title'].strip()}\nLocation: {j['location']['name'].strip()}\n"
                f"URL: {j['absolute_url']}\n\n" + " ".join(text.split()) + "\n")
    (OUT / "selection.json").write_text(json.dumps(
        {"source": str(raw_path), "seed": SEED, "pool_rule": "title contains engineer or developer",
         "pool_size": len(pool), "picked": [{"posting_id": j["id"], "set": s} for j, s in zip(picked, sets)]},
        indent=2))
    print(f"pool {len(pool)} postings; wrote labels/sheet.csv and labels/postings/*.txt (20)")


if __name__ == "__main__":
    main(sys.argv[1])
