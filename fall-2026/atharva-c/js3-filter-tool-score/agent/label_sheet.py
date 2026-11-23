"""Draw the seeded hand-label sample and split it into dev and held-out.

Run once, before agent/filter.py exists, so that the labels cannot be shaped by
what the filter does:

    python3 -m agent.label_sheet evidence/run-20261123-185425Z --seed 2026

Writes labels/dev.csv and labels/heldout.csv (refuses to overwrite them).
The `my_label` and `my_reason` columns are left empty for me to fill in by hand.

Sampling (v2, Nov 23; v1 is described in FRICTIONAL.md): 90 postings in three
strata, each split half dev / half held-out.

  A1  title has "engineer", "developer" or "software" AND none of the G1/G2
      words (FILTER.md v1.0)              -> ALL of them (50 of 50)
  A2  same title words, WITH a G1/G2 word  -> random 20 of 149
  B   every other title                    -> random 20 of 201

Why: true keeps are rare (a first draw of 60 random-within-A/B had about one
likely keep in its held-out half), so held-out could not measure any change.
Cost of this design: A1 reuses the G1/G2 word list, so the label set is NOT a
random sample of the 400. Rates measured on it are rates on this stratified
set; a whole-run estimate must weight each stratum by its size (50/149/201).
A2 and B are there so gate errors (a "Senior" title that is really entry
level, a non-engineering title that fits Sam) can still show up.

    python3 -m agent.label_sheet --show <uid>     # print one posting to read while labeling
"""

from __future__ import annotations

import argparse
import csv
import random
import re
import sys
from pathlib import Path

from agent.postings import load_run

RUN = "evidence/run-20261123-185425Z"
STRATUM_A = re.compile(r"engineer|developer|software", re.I)
GATE_WORDS = re.compile(
    r"\b(Senior|Sr|Staff|Principal|Lead|Manager|Director|Head|VP|Vice President|Chief|President|Intern|Internship)\b"
)
N_A2, N_B = 20, 20
COLUMNS = ["uid", "split", "stratum", "board", "title", "location", "url", "my_label", "my_reason"]


def stratum(p: dict) -> str:
    if STRATUM_A.search(p["title"]):
        return "A2" if GATE_WORDS.search(p["title"]) else "A1"
    return "B"


def draw(postings: list[dict], seed: int) -> list[dict]:
    rng = random.Random(seed)
    pools = {k: sorted((p for p in postings if stratum(p) == k), key=lambda p: p["uid"]) for k in ("A1", "A2", "B")}
    sizes = {"A1": len(pools["A1"]), "A2": N_A2, "B": N_B}
    rows = []
    for name in ("A1", "A2", "B"):
        picked = rng.sample(pools[name], sizes[name])   # A1: all of them, in random order
        for i, p in enumerate(picked):
            rows.append({
                "uid": p["uid"], "split": "dev" if i < len(picked) // 2 else "heldout", "stratum": name,
                "board": p["board"], "title": p["title"], "location": p["location"], "url": p["url"],
                "my_label": "", "my_reason": "",
            })
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run", nargs="?", default=RUN)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--out", default="labels")
    ap.add_argument("--show", metavar="UID")
    args = ap.parse_args(argv)

    postings = load_run(args.run)
    if args.show:
        p = next((p for p in postings if p["uid"] == args.show), None)
        if p is None:
            print(f"no posting {args.show}", file=sys.stderr)
            return 1
        print(f"{p['title']}\n{p['location']}  |  {p['board']}  |  {p['url']}\n\n{p['text']}")
        return 0

    out = Path(args.out)
    targets = [out / "dev.csv", out / "heldout.csv"]
    if any(t.exists() for t in targets):
        print("labels/dev.csv or labels/heldout.csv already exists; not overwriting.", file=sys.stderr)
        return 1
    out.mkdir(parents=True, exist_ok=True)
    rows = draw(postings, args.seed)
    for t, split in zip(targets, ("dev", "heldout")):
        with t.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS)
            w.writeheader()
            w.writerows(r for r in rows if r["split"] == split)
    counts = {k: sum(1 for p in postings if stratum(p) == k) for k in ("A1", "A2", "B")}
    got = {k: sum(1 for r in rows if r["stratum"] == k) for k in counts}
    print(f"seed {args.seed}: " + ", ".join(f"{k} {got[k]} of {counts[k]}" for k in counts))
    print(f"wrote {targets[0]} ({sum(r['split'] == 'dev' for r in rows)}) and {targets[1]} ({sum(r['split'] == 'heldout' for r in rows)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
