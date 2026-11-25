"""Draw the audit and held-out sets from out/decisions_v1.0.jsonl with the seed in audit/SEED (committed before this ran).
A = 30 random rejects; B = 10 closest calls (rejected, exactly one rule failed, score 4-6, nearest to 5 first);
C = 6 random kept; H = held-out 30 (the other kept + R1-title rejects + others), never used to change anything.
All 76 are shuffled into one blind sheet: the sheet shows no filter verdict and no group.
Run:  python3 tools/draw_sets.py"""
import json, random
from pathlib import Path
seed = int(Path("audit/SEED").read_text()); rng = random.Random(seed)
ds = [json.loads(l) for l in open("out/decisions_v1.0.jsonl")]
kept = sorted(d["id"] for d in ds if d["status"] == "kept")
rej = [d for d in ds if d["status"] == "rejected"]
A = rng.sample(sorted(d["id"] for d in rej), 30)
close = sorted([d for d in rej if d["id"] not in A and len(d["failed"]) == 1 and 4 <= d["score"] <= 6],
               key=lambda d: (abs(d["score"] - 5), d["id"]))
pool = close[:]; rng.shuffle(pool); pool.sort(key=lambda d: abs(d["score"] - 5))
B = [d["id"] for d in pool[:10]]
C = rng.sample(kept, 6)
used = set(A) | set(B) | set(C)
H = [k for k in kept if k not in used]
r1_rej = sorted(d["id"] for d in rej if d["r1"] and d["id"] not in used)
H += rng.sample(r1_rej, 13)
other = sorted(d["id"] for d in rej if not d["r1"] and d["id"] not in used and d["id"] not in H)
H += rng.sample(other, 30 - len(H))
sets = {"seed": seed, "A_random_rejects": A, "B_close_calls": B, "C_kept_sample": C, "H_heldout": H}
allids = A + B + C + H; assert len(set(allids)) == len(allids) == 76
order = allids[:]; rng.shuffle(order)
Path("audit/sets.json").write_text(json.dumps(sets, indent=1))
Path("audit/sheet_order.json").write_text(json.dumps(order, indent=1))
print({k: len(v) for k, v in sets.items() if k != "seed"}, "sheet:", len(order))
