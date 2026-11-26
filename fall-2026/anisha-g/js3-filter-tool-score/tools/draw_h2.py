"""Second held-out set H2, drawn AFTER the first results showed H had only 1 'y' in 30 (WHAT_MOVES_THE_SCORE.md).
H2 = 24 postings drawn with seed 7376 from the UNJUDGED postings whose title passes R1 and fails no seniority rule
(the pool most likely to contain postings worth Nadia's time). Shuffled into its own blind sheet. Nothing in H2 was
looked at before this draw. Run:  python3 tools/draw_h2.py"""
import json, random
from pathlib import Path
seed = 7376; rng = random.Random(seed)
s = json.loads(Path("audit/sets.json").read_text()); used = {i for k, v in s.items() if k != "seed" for i in v}
d = [json.loads(l) for l in open("out/decisions_v1.0.jsonl")]
pool = sorted(x["id"] for x in d if x["r1"] and not x["r2_reject"] and x["id"] not in used)
H2 = rng.sample(pool, 24); order = H2[:]; rng.shuffle(order)
Path("audit/sets_h2.json").write_text(json.dumps({"seed": seed, "pool_size": len(pool), "H2_heldout": H2}, indent=1))
Path("audit/sheet_order_h2.json").write_text(json.dumps(order, indent=1))
print(f"H2: {len(H2)} drawn from a pool of {len(pool)}")
