"""What moves the score: the comparisons pre-registered in FREEZE.json, on one label file.

  .venv/bin/python -m js3.experiment --labels labels/heldout2_labels.csv   -> experiments/RESULTS_H2.json
  .venv/bin/python -m js3.experiment --labels labels/dev_labels.csv        (code check on dev only)

Each comparison changes exactly one object against the frozen baseline (filter v1.0, threshold 6). The inputs (corpus,
labels) and every other setting stay fixed. v1.1 is reported as a combination. For Claude, the arms are the
two contexts, and the baseline is arm A.
"""
import argparse
import csv
import json
from pathlib import Path

from .audit import confusion
from .corpus import load_corpus
from .filter import load_filter, score_posting

ROOT = Path(__file__).resolve().parent.parent
FILTER_CHANGES = [("C-a", "cand-a_boilerplate", None, "filter file"), ("C-b", "cand-b_years", None, "filter file"),
                  ("C-e", "cand-e_earlycareer3", None, "filter file"), ("C-t", "v1.0", 5, "setting: threshold 6 -> 5"),
                  ("v1.1 (combination)", "v1.1", None, "three filter-file changes")]


def metrics(m):
    tp, fp, fn, tn = (m.get(k, 0) for k in ("TP", "FP", "FN", "TN"))
    return {**m, "recall": f"{tp}/{tp + fn}", "precision": f"{tp}/{tp + fp}", "agreement": f"{tp + tn}/{tp + fp + fn + tn}"}


def claude_verdicts(arm, keys):
    out = {}
    for k in keys:
        f = ROOT / "experiments" / "claude_context" / "raw" / arm / (k.replace(":", "__") + ".json")
        if f.exists():
            r = json.loads(f.read_text())
            out[k] = ("keep" if r["parsed"]["verdict"] == "yes" else "reject") if r["valid"] else "invalid"
    return out


def run(labels):
    corpus = load_corpus()
    with Path(labels).open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    base_cfg = load_filter("v1.0")
    base = {r["key"]: score_posting(corpus[r["key"]], base_cfg) for r in rows}
    res = {"labels": str(labels), "n": len(rows), "baseline": "filter v1.0, threshold 6",
           "baseline_metrics": metrics(confusion(rows, {k: v["verdict"] for k, v in base.items()})), "comparisons": []}
    for name, fv, thr, obj in FILTER_CHANGES:
        cfg = load_filter(fv)
        if thr is not None:
            cfg["threshold"] = thr
        new = {r["key"]: score_posting(corpus[r["key"]], cfg) for r in rows}
        res["comparisons"].append({
            "change": name, "object": obj, "filter": fv, "threshold": cfg["threshold"],
            "metrics": metrics(confusion(rows, {k: v["verdict"] for k, v in new.items()})),
            "flips": [{"sheet_id": r["sheet_id"], "key": r["key"], "title": corpus[r["key"]]["title"], "label": r["label"],
                       "reason": r["reason"], "from": base[r["key"]]["verdict"], "to": new[r["key"]]["verdict"],
                       "baseline": base[r["key"]].get("arithmetic"), "changed": new[r["key"]].get("arithmetic")}
                      for r in rows if new[r["key"]]["verdict"] != base[r["key"]]["verdict"]]})
    keys = [r["key"] for r in rows]
    arms = {a: claude_verdicts(a, keys) for a in ("A", "B")}
    if all(len(v) == len(keys) for v in arms.values()):
        for a in ("A", "B"):
            res[f"claude_arm_{a}"] = metrics(confusion(rows, arms[a])) | {"invalid": sum(v == "invalid" for v in arms[a].values())}
        res["claude_context_flips"] = [{"sheet_id": r["sheet_id"], "title": corpus[r["key"]]["title"], "label": r["label"],
                                        "A": arms["A"][r["key"]], "B": arms["B"][r["key"]]}
                                       for r in rows if arms["A"][r["key"]] != arms["B"][r["key"]]]
    else:
        res["claude"] = "no Claude responses for these postings (the experiment ran on H2 only)"
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    r = run(a.labels)
    if a.out:
        Path(a.out).write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
    print("baseline", {k: r["baseline_metrics"][k] for k in ("recall", "precision", "agreement")})
    for c in r["comparisons"]:
        print(f"{c['change']:<20} {c['object']:<26} recall {c['metrics']['recall']:<6} precision {c['metrics']['precision']:<6} "
              f"agreement {c['metrics']['agreement']:<6} flips {len(c['flips'])}")
    for a in ("A", "B"):
        if f"claude_arm_{a}" in r:
            m = r[f"claude_arm_{a}"]
            print(f"Claude arm {a}: recall {m['recall']} precision {m['precision']} agreement {m['agreement']} invalid {m['invalid']}")
