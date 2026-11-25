"""B: a FITTED check of the hand-set threshold. Offline.

    python3 tools/fit_threshold.py

Fit: for thresholds 3..11, run filter v1.1 with only the threshold changed, on the 58 DEV (audit) labels, blind and
corrected. "Best" = most agreement; ties go to the current value (6), then to the lower threshold.
The held-out 20 are scored for each threshold too, but only AFTER the fitted value is printed, and they do not
choose it. Writes out/fit-threshold.json. Nothing is adopted automatically: v1.1 keeps 6 unless Riya decides.
"""

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import measure  # noqa: E402
from js3 import corpus, evidence, filter as F  # noqa: E402

TO = measure.TO_LABEL


def preds(flt, posts, items):
    return {i["item"]: TO[F.apply(posts[(i["board"], i["id"])], flt, evidence.claims)["decision"]] for i in items}


def main():
    base = F.load_filter(ROOT / "filters" / "filter-v1.1.json")
    posts = corpus.by_key(corpus.load())
    sample = measure.sample()
    dev = [i for i in sample if i["split"] == "audit"]
    held = [i for i in sample if i["split"] == "heldout"]
    out = {"filter": "v1.1 with only the threshold changed", "current": base["threshold"], "dev": {}, "heldout": {}}
    for corrected in (False, True):
        measure.CORRECTED = corrected
        labels = measure.load_labels()
        tag = "corrected" if corrected else "blind"
        rows = {}
        for t in range(3, 12):
            f = copy.deepcopy(base)
            f["threshold"] = t
            rows[t] = measure.score(preds(f, posts, dev), labels, dev)
        best = max(rows, key=lambda t: (rows[t]["agree"], t == base["threshold"], -t))
        out["dev"][tag] = {"fitted_threshold": best, "by_threshold": rows}
        print(f"dev {tag}: " + "  ".join(f"t={t}:{r['agree']}/{r['n']}" for t, r in rows.items()) + f"  -> fitted {best}")
    for corrected in (False, True):  # held-out only reported after the fit above
        measure.CORRECTED = corrected
        labels = measure.load_labels()
        tag = "corrected" if corrected else "blind"
        rows = {}
        for t in range(3, 12):
            f = copy.deepcopy(base)
            f["threshold"] = t
            rows[t] = measure.score(preds(f, posts, held), labels, held)
        out["heldout"][tag] = rows
        print(f"held-out {tag}: " + "  ".join(f"t={t}:{r['agree']}/{r['n']}" for t, r in rows.items()))
    (ROOT / "out" / "fit-threshold.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
