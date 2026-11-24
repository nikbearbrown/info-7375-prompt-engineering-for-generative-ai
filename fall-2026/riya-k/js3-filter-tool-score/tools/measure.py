"""Compare Riya's blind hand labels with the filter and with Claude. Offline; reads only saved files.

    python3 tools/measure.py audit                      # reject audit + closest calls + kept sample (filter v1)
    python3 tools/measure.py heldout                    # every filter version and every Claude run on the held-out 20
    python3 tools/measure.py heldout --filters v1 v1.1 --claude B1-baseline E2-prompt-v2

Mapping: filter kept = "show", rejected = "not", cannot_tell = "cannot_tell". Intervals are Wilson 95% intervals for
the sample, NOT measured rates for all postings.
"""

import argparse
import collections
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from js3 import corpus, evidence, filter as F  # noqa: E402

TO_LABEL = {"kept": "show", "rejected": "not", "cannot_tell": "cannot_tell"}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def load_labels():
    d = json.loads((ROOT / "audit" / "hand-labels.json").read_text())
    return {int(k): v for k, v in d["labels"].items() if v.get("verdict")}


def sample():
    return json.loads((ROOT / "audit" / "sample.json").read_text())["items"]


def audit():
    labels = load_labels()
    items = [i for i in sample() if i["split"] == "audit"]
    missing = [i["item"] for i in items if i["item"] not in labels]
    out = {"labeled": len(items) - len(missing), "missing": missing, "strata": {}}
    for s, name in [("R", "random rejects"), ("N", "closest calls"), ("K", "kept sample"), ("T", "cannot_tell sample")]:
        rows = []
        for i in items:
            if i["stratum"] != s or i["item"] not in labels:
                continue
            h = labels[i["item"]]
            rows.append({"item": i["item"], "board": i["board"], "id": i["id"], "title": i["title"],
                         "filter": i["v1_decision"], "score": i["v1_score"], "hand": h["verdict"],
                         "note": h.get("note", ""), "agree": TO_LABEL[i["v1_decision"]] == h["verdict"]})
        n = len(rows)
        wrong = [r for r in rows if not r["agree"]]
        hard_wrong = [r for r in rows if r["hand"] in ("show", "not") and not r["agree"]]
        lo, hi = wilson(len(hard_wrong), n)
        out["strata"][s] = {"name": name, "n": n, "disagree": len(wrong), "disagree_not_cannot_tell": len(hard_wrong),
                            "hand_counts": dict(collections.Counter(r["hand"] for r in rows)),
                            "wilson95_hard_wrong": [round(lo, 3), round(hi, 3)], "rows": rows}
    return out


def filter_preds(version):
    flt = F.load_filter(ROOT / "filters" / f"filter-{version}.json")
    posts = corpus.by_key(corpus.load())
    return {i["item"]: TO_LABEL[F.apply(posts[(i["board"], i["id"])], flt, evidence.claims)["decision"]]
            for i in sample()}


def claude_preds(label):
    d = ROOT / "runs" / "claude" / label
    out = {}
    for f in d.glob("item-*.json"):
        r = json.loads(f.read_text())
        out[r["item"]] = (r["parsed"] or {}).get("verdict", "unparsed")
    return out


def score(preds, labels, items):
    rows = [(preds.get(i["item"], "missing"), labels[i["item"]]["verdict"]) for i in items if i["item"] in labels]
    n = len(rows)
    agree = sum(p == h for p, h in rows)
    tp = sum(p == "show" and h == "show" for p, h in rows)
    shown = sum(p == "show" for p, _ in rows)
    wanted = sum(h == "show" for _, h in rows)
    lo, hi = wilson(agree, n)
    return {"n": n, "agree": agree, "agree_rate": round(agree / n, 3) if n else None,
            "wilson95": [round(lo, 3), round(hi, 3)], "show_predicted": shown, "show_hand": wanted, "show_both": tp,
            "confusion (pred,hand)": dict(collections.Counter(f"{p}->{h}" for p, h in rows))}


def heldout(filters, runs, split):
    labels = load_labels()
    items = [i for i in sample() if i["split"] == split]
    res = {"split": split, "n_labeled": sum(i["item"] in labels for i in items), "filters": {}, "claude": {}}
    for v in filters:
        res["filters"][v] = score(filter_preds(v), labels, items)
    for r in runs:
        res["claude"][r] = score(claude_preds(r), labels, items)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["audit", "heldout", "dev"])
    ap.add_argument("--filters", nargs="*", default=None)
    ap.add_argument("--claude", nargs="*", default=None)
    a = ap.parse_args()
    if a.what == "audit":
        res = audit()
    else:
        fl = a.filters or sorted(p.stem.replace("filter-", "") for p in (ROOT / "filters").glob("filter-*.json"))
        cl = a.claude if a.claude is not None else sorted(p.name for p in (ROOT / "runs" / "claude").iterdir()
                                                          if p.is_dir() and json.loads((p / "meta.json").read_text())
                                                          ["split"] == ("heldout" if a.what == "heldout" else "audit"))
        res = heldout(fl, cl, "heldout" if a.what == "heldout" else "audit")
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
