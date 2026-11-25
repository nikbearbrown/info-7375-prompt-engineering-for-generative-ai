"""A FITTED number (Chapter 9): fit the keep threshold on my audit labels (dev = groups A, B, C: 46 postings),
then measure it on the two held-out sets (H, H2), which played no part in the fit. Everything else stays as in v1.2.
A posting is kept iff it fails none of R1b/R2/R5 ... (v1.2's rule) EXCEPT that the score threshold is the fitted value
instead of the hand-set 5. Ties in dev accuracy go to the hand-set value 5, then to the lower threshold.
Run:  python3 tools/fit_threshold.py   -> out/fit_threshold.json"""
import json, sys
from pathlib import Path
sys.path.insert(0, ".")
from js3 import filter as F
corpus = {p["id"]: p for p in F.load_corpus()}
base = F.load_filter("filters/filter_v1.2.json")
s = json.loads(Path("audit/sets.json").read_text())
hv = {json.loads(l)["id"]: json.loads(l)["verdict"] for l in open("labels/hand_verdicts.jsonl")}
for l in open("labels/hand_corrections.jsonl"): r = json.loads(l); hv[r["id"]] = r["verdict"]
hv2 = {json.loads(l)["id"]: json.loads(l)["verdict"] for l in open("labels/hand_verdicts_h2.jsonl")}
dev = [i for g in ("A_random_rejects", "B_close_calls", "C_kept_sample") for i in s[g] if hv[i] != "?"]
H = [i for i in s["H_heldout"] if hv[i] != "?"]; H2 = [i for i in json.loads(Path("audit/sets_h2.json").read_text())["H2_heldout"] if hv2[i] != "?"]
def kept(i, t):
    c = dict(base, keep_threshold=t); return F.evaluate(corpus[i], c)["status"] == "kept"
def score(ids, lab, t):
    tp = sum(kept(i, t) and lab[i] == "y" for i in ids); fp = sum(kept(i, t) and lab[i] == "n" for i in ids)
    fn = sum(not kept(i, t) and lab[i] == "y" for i in ids); return dict(acc=round((len(ids) - fp - fn) / len(ids), 3), tp=tp, fp=fp, fn=fn)
grid = list(range(3, 10))
devres = {t: score(dev, hv, t) for t in grid}
best = max(grid, key=lambda t: (devres[t]["acc"], t == 5, -t))
out = {"dev_n": len(dev), "dev_y": sum(hv[i] == "y" for i in dev), "grid": grid, "dev": devres, "fitted_threshold": best,
       "H": {t: score(H, hv, t) for t in (5, best)}, "H2": {t: score(H2, hv2, t) for t in (5, best)}}
Path("out/fit_threshold.json").write_text(json.dumps(out, indent=1))
print(f"dev: {len(dev)} postings, {out['dev_y']} y"); [print(f"  threshold {t}: {devres[t]}") for t in grid]
print(f"fitted threshold = {best} (hand-set = 5)")
for k in ("H", "H2"): print(f"{k}: hand-set 5 -> {out[k][5]}   fitted {best} -> {out[k][best]}")
