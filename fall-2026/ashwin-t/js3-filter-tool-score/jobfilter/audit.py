"""The reject audit (FILTER.md section 8). Draw a blind sample, then score Ashwin's verdicts against the filter.

    python3 -m jobfilter.audit --draw      # writes labels/audit-sheet.{md,csv} and labels/audit-selection.json
    python3 -m jobfilter.audit --report    # needs every verdict filled; writes audit/REPORT-v1.0.md

Strata (all from the 775 development postings; held-out keys never enter):
  random_reject    30 random rejects, without replacement            -> estimates the false-negative share
  close_below      up to 6 eligible postings at score 6 (rejected)   -> closest calls under threshold 7
  close_at         up to 5 kept postings at score 7                  -> closest calls at threshold
  kept_random      up to 6 more kept postings, random                -> false-positive check
  exclusion_check  level-II and "manager" rejects (all) + 3 forward-deployed, each would score >= 7 without the gate
  review           every REVIEW posting
A posting drawn by two strata appears once on the sheet and keeps both categories.
Only random_reject and kept_random are random samples; the other strata are chosen on purpose and are never
pooled into a rate.
"""
from __future__ import annotations

import json
import math
import random
import sys

from .corpus import HERE, load
from .filter import KEEP, REJECT, REVIEW
from .heldout import heldout_keys
from .sheets import read_verdicts, write_sheet

SEED = 20261126
VERSION = "v1.0"
LABELS = HERE / "labels"
SELECTION = LABELS / "audit-selection.json"


def _would_keep_without_gate(d: dict) -> bool:
    g = d.get("gate")
    return bool(g and g["role_matched"] and not g["passed"] and d["location"]["status"] == "eligible"
                and d["n_topic_groups"] >= 2 and d["score"] >= 7)


def strata(dev: list, seed: int = SEED) -> dict:
    rng = random.Random(seed)
    by = lambda pred: sorted((d["key"] for d in dev if pred(d)))
    rejects = by(lambda d: d["decision"] == REJECT)
    below = by(lambda d: d["decision"] == REJECT and d.get("gate", {}).get("passed")
               and d["location"]["status"] == "eligible" and d["score"] == 6)
    at = by(lambda d: d["decision"] == KEEP and d["score"] == 7)
    kept = by(lambda d: d["decision"] == KEEP)
    excl = [d for d in dev if _would_keep_without_gate(d)]
    must = sorted(d["key"] for d in excl if any(("level" in r) or ('"manager"' in r) for r in d["reasons"]))
    fd = sorted(d["key"] for d in excl if any("forward deployed" in r for r in d["reasons"]) and d["key"] not in must)
    review = by(lambda d: d["decision"] == REVIEW)
    pick = lambda pop, n: sorted(rng.sample(pop, min(n, len(pop))))
    s = {}
    s["random_reject"] = {"population": rejects, "selected": pick(rejects, 30)}
    s["close_below"] = {"population": below, "selected": pick(below, 6)}
    s["close_at"] = {"population": at, "selected": pick(at, 5)}
    rest = [k for k in kept if k not in s["close_at"]["selected"]]
    s["kept_random"] = {"population": rest, "selected": pick(rest, 6)}
    fd_pick = pick(fd, 3)
    s["exclusion_check"] = {"population": sorted(must + fd), "selected": sorted(must + fd_pick)}
    s["review"] = {"population": review, "selected": review}
    return s


def draw() -> None:
    dev = json.loads((HERE / "runs" / VERSION / "decisions-dev.json").read_text())
    held = heldout_keys()
    assert not held & {d["key"] for d in dev}, "held-out key in development decisions"
    s = strata(dev)
    cats = {}
    for name, v in s.items():
        for k in v["selected"]:
            cats.setdefault(k, []).append(name)
    order = sorted(cats)
    random.Random(SEED + 1).shuffle(order)
    SELECTION.write_text(json.dumps({
        "filter_version": VERSION, "seed": SEED, "sheet_order_seed": SEED + 1,
        "strata": {k: {"population_size": len(v["population"]), "n_selected": len(v["selected"]),
                       "population": v["population"], "selected": v["selected"]} for k, v in s.items()},
        "sheet_order": order, "categories": cats}, indent=1) + "\n")
    postings = {p["key"]: p for p in load()["postings"]}
    write_sheet(LABELS / "audit-sheet.md", "Reject-audit labeling sheet (blind)",
                f"{len(order)} development postings drawn with seed {SEED} from filter {VERSION}'s output, in shuffled "
                "order. The filter's decision, score and the reason a posting was drawn are **not shown**. Do not open "
                "`audit-selection.json` or `runs/` until every verdict is written.",
                [postings[k] for k in order])
    print(f"audit sheet: {len(order)} postings; " + ", ".join(f"{k} {len(v['selected'])}/{len(v['population'])}"
                                                            for k, v in s.items()))


def wilson(k: int, n: int, z: float = 1.96) -> tuple:
    """95% Wilson score interval for k of n. (None, None) when n == 0."""
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centre - half), min(1.0, centre + half))


def tally(selection: dict, verdicts: dict, decisions: dict) -> dict:
    out = {}
    for name, v in selection["strata"].items():
        rows = [(k, decisions[k]["decision"], verdicts[k]["verdict"]) for k in v["selected"]]
        y = sum(1 for _, _, h in rows if h == "Y")
        n = sum(1 for _, _, h in rows if h == "N")
        q = sum(1 for _, _, h in rows if h == "?")
        out[name] = {"rows": rows, "Y": y, "N": n, "?": q, "selected": len(rows),
                     "population_size": v["population_size"]}
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["--draw"]:
        draw()
        return 0
    if argv == ["--report"]:
        from .audit_report import write_report
        write_report()
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
