"""Measure filter variants against Lavanya's hand verdicts.

python3 -B audit/measure.py            # dev labels only: groups A, B, C
python3 -B audit/measure.py --heldout  # group H (only for the final check)

A posting counts as wrong when the filter keeps it and the hand verdict is
"n", or rejects it and the hand verdict is "y". "?" verdicts are left out.
Each variant changes ONE thing from FILTER.md v1.0.
"""

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from agent import corpus, filter as flt  # noqa: E402

CANADA = re.compile(r"Ontario|British Columbia|Quebec|Alberta|Toronto|"
                    r"Vancouver|Montreal|Canada", re.IGNORECASE)


def base():
    """FILTER.md v1.0, the version the audit measured (config/filter-v1.0.json)."""
    return json.loads((HERE / "config" / "filter-v1.0.json").read_text())


def variants():
    v = {"v1.0 (as written)": (base(), {})}
    c = base(); c["threshold"] = 4
    v["X1 threshold 5 -> 4"] = (c, {})
    c = base(); c["role_words"] = c["role_words"] + ["Forward Deployed"]
    v["X2 S1 + 'Forward Deployed'"] = (c, {})
    v["X3 R5 uses the LARGEST years asked"] = (base(), {"r5": "max"})
    v["X4 ', CA' after a Canadian place is not California"] = (base(), {"canada": True})
    v["v1.1 (X4 adopted; config/filter.json)"] = (
        json.loads((HERE / "config" / "filter.json").read_text()), {})
    return v


def evaluate(p, cfg, opts):
    r = flt.evaluate(p, cfg)
    if opts.get("r5") == "max" and r["matched"]["R5"]:
        fires = max(r["matched"]["R5"]) > cfg["max_years_asked"]
        if fires and "R5" not in r["rejected_by"]:
            r["rejected_by"] = [x for x in r["rejected_by"] if x != "below_threshold"] + ["R5"]
            r["verdict"] = "reject"
    if opts.get("canada"):
        parts = [x for x in flt.location_parts(p["locations"])
                 if not (CANADA.search(x) and re.search(r",\s*CA(?![A-Za-z])", x))]
        if parts and not flt.us_parts(parts, cfg) and r["verdict"] != "reject":
            r["verdict"], r["rejected_by"] = "reject", ["R3"]
    return r


def main():
    groups = ("H",) if "--heldout" in sys.argv else ("A", "B", "C")
    draw = json.loads((HERE / "audit/draw.json").read_text())
    hand = {json.loads(l)["key"]: json.loads(l)["verdict"]
            for l in open(HERE / "audit/hand_verdicts.jsonl")}
    keys = [k for g in groups for k in draw["groups"][g]
            if hand.get(k) in ("y", "n")]
    posts = {p["key"]: p for p in corpus.load(HERE / "runs/2026-11-24T220432Z-live")}
    all_posts = list(posts.values())
    print(f"labels: groups {'+'.join(groups)}, {len(keys)} judged y/n")
    for name, (cfg, opts) in variants().items():
        wrong, fk, fr = [], 0, 0
        for k in keys:
            v = evaluate(posts[k], cfg, opts)["verdict"]
            if v == "keep" and hand[k] == "n":
                fk += 1; wrong.append(k)
            if v != "keep" and hand[k] == "y":
                fr += 1; wrong.append(k)
        kept_all = sum(1 for p in all_posts if evaluate(p, cfg, opts)["verdict"] == "keep")
        print(f"{name:52} wrong {len(wrong):2}/{len(keys)} "
              f"(kept-but-n {fk}, rejected-but-y {fr})  kept overall {kept_all}")


if __name__ == "__main__":
    main()
