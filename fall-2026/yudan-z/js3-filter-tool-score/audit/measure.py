"""Measure filter versions against the hand labels (audit/labels-final.csv).

python -m audit.measure filter/filter-v1.json filter/filter-v2a.json ...
Counts 'keep' and 'cannot tell' as "reaches Mira" (both are shown to her); 'reject' as not.
Reports dev (45 rows used while designing changes) and held-out (16 rows) separately.
"""
import csv
import json
import math
import sys

from agent import filter as F

LABELS, KEY, DATA = "audit/labels-final.csv", "audit/sample-key.json", "data/postings.jsonl"


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(max(0, c - h), 3), round(min(1, c + h), 3))


def load():
    key = {str(r["row"]): r for r in json.load(open(KEY, encoding="utf-8"))["rows"]}
    post = {}
    for line in open(DATA, encoding="utf-8"):
        p = json.loads(line)
        post[p["key"]] = p
    rows = []
    for r in csv.DictReader(open(LABELS, encoding="utf-8-sig")):
        k = key[r["row"]]
        rows.append({"row": int(r["row"]), "group": k["group"], "label": r["YOUR VERDICT (Y / N / ?)"].strip().upper(),
                     "posting": post[k["key"]]})
    return rows, post


def confusion(rows, cfg):
    c = {"TP": 0, "FP": 0, "FN": 0, "TN": 0, "FN_rows": [], "FP_rows": []}
    for r in rows:
        if r["label"] not in ("Y", "N"):
            continue
        shown = F.score(r["posting"], cfg)["decision"] != "reject"
        if r["label"] == "Y":
            c["TP" if shown else "FN"] += 1
            if not shown:
                c["FN_rows"].append(r["row"])
        else:
            c["FP" if shown else "TN"] += 1
            if shown:
                c["FP_rows"].append(r["row"])
    return c


def main(paths):
    rows, post = load()
    out = []
    for path in paths:
        cfg = F.load(path)
        dev = confusion([r for r in rows if r["group"] != "held-out"], cfg)
        held = confusion([r for r in rows if r["group"] == "held-out"], cfg)
        allp = [F.score(p, cfg)["decision"] for p in post.values()]
        res = {"filter": path, "version": cfg["version"], "dev": dev, "held_out": held,
               "all_postings": {d: allp.count(d) for d in ("keep", "cannot tell", "reject")}}
        out.append(res)
        for name, c in (("dev", dev), ("held-out", held)):
            print(f"{cfg['version']:6} {name:8} TP {c['TP']:2} FP {c['FP']:2} FN {c['FN']:2} TN {c['TN']:2}"
                  f"  missed Y rows {c['FN_rows']}  shown N rows {c['FP_rows']}")
        print(f"{cfg['version']:6} all 1,595: {res['all_postings']}")
    rr = [r for r in rows if r["group"] == "random-reject"]
    k = sum(r["label"] == "Y" for r in rr)
    print(f"random rejects of v1 labelled Y by hand: {k}/{len(rr)}, Wilson 95% interval {wilson(k, len(rr))}")
    json.dump({"results": out, "random_reject_Y": [k, len(rr), wilson(k, len(rr))]},
              open("runs/measure.json", "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
