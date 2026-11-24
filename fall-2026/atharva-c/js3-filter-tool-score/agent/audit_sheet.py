"""Draw the reject-audit sheets from one filter run, for judging by hand.

    python3 -m agent.audit_sheet evidence/filter-v1.0/decisions.jsonl --seed 2026

Writes audit/<version>/ (refuses to overwrite):
  rejects.csv      30 rejects drawn uniformly at random (seeded) from ALL rejects
  close_calls.csv  every posting that passed the gates with score 0.40-0.60
  kept.csv         every kept posting
`my_judgment` (should keep / should reject) and `my_reason` are left empty.
The filter's own score and rules are shown so I can see WHY, but the judgment
is mine, made by reading the posting (python3 -m agent.label_sheet --show UID).
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

COLUMNS = ["uid", "title", "location", "filter_keep", "score", "gates", "rules", "years", "my_judgment", "my_reason"]
N_REJECTS = 30


def row(d: dict) -> dict:
    return {"uid": d["uid"], "title": d["title"], "location": d["location"], "filter_keep": d["keep"],
            "score": d["score"], "gates": " ".join(d["gates"]),
            "rules": " ".join(f"{k}={v}" for k, v in d["rules"].items() if v), "years": d["years"],
            "my_judgment": "", "my_reason": ""}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("decisions")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--out", default="audit")
    args = ap.parse_args(argv)

    ds = [json.loads(l) for l in open(args.decisions, encoding="utf-8")]
    version = Path(args.decisions).parent.name
    out = Path(args.out, version)
    if out.exists():
        print(f"{out} exists; not overwriting.", file=sys.stderr)
        return 1
    rejects = sorted((d for d in ds if not d["keep"]), key=lambda d: d["uid"])
    sheets = {
        "rejects.csv": random.Random(args.seed).sample(rejects, N_REJECTS),
        "close_calls.csv": sorted((d for d in ds if not d["gates"] and 0.40 <= d["score"] <= 0.60),
                                  key=lambda d: (-d["score"], d["uid"])),
        "kept.csv": sorted((d for d in ds if d["keep"]), key=lambda d: (-d["score"], d["uid"])),
    }
    out.mkdir(parents=True)
    for name, items in sheets.items():
        with (out / name).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS)
            w.writeheader()
            w.writerows(row(d) for d in items)
        print(f"{out / name}: {len(items)}")
    print(f"random rejects drawn from {len(rejects)} rejects, seed {args.seed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
