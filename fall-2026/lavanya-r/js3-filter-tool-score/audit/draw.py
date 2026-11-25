"""Draw the postings Lavanya judges by hand, with the committed seed.

Groups (decided before the draw; AUDIT.md section 1):
  A  30 random rejects          (simple random from every filter v1.0 reject)
  B  10 closest calls           (5 random at score 4, just below the threshold,
                                 5 random at score 5, exactly at it; both among
                                 postings that passed every hard reject)
  C  10 random kept             (from the 115 kept)
  H  30 held out for Chapter 9  (from postings that passed every hard reject,
                                 not in A-C: 15 kept + 15 below threshold)

The sheet shuffles all 80 together and shows no group, verdict or score, so
the hand verdict is blind to what the filter said.

python3 -B audit/draw.py     -> audit/draw.json (groups) and audit/sheet.jsonl
"""

import json
import pathlib
import random
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from agent import corpus  # noqa: E402

SEED = int((HERE / "audit" / "SEED").read_text().split()[0])
QUAL = re.compile(r"(qualif|you have|you might thrive|requirements|about you|"
                  r"what we.re looking for|you.ll bring|you bring|we.re looking)",
                  re.IGNORECASE)


def excerpt(text, n=4):
    """Up to n lines after the first qualifications-like heading; else the
    first 350 characters. Shown so the verdict isn't from the title alone."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for i, l in enumerate(lines):
        if QUAL.search(l) and len(l) < 120:
            return [x[:220] for x in lines[i + 1:i + 1 + n]]
    return [text[:350]]


def main():
    recs = [json.loads(l) for l in open(HERE / "out/filter/v1.0/decisions.jsonl")]
    rng = random.Random(SEED)
    rejects = [r["key"] for r in recs if r["verdict"] == "reject"]
    kept = [r["key"] for r in recs if r["verdict"] == "keep"]
    s4 = [r["key"] for r in recs if r["rejected_by"] == ["below_threshold"]
          and r["score"] == 4]
    s5 = [r["key"] for r in recs if r["verdict"] == "keep" and r["score"] == 5]
    below = [r["key"] for r in recs if r["rejected_by"] == ["below_threshold"]]

    A = rng.sample(rejects, 30)
    B = rng.sample(s4, 5) + rng.sample(s5, 5)
    C = rng.sample([k for k in kept if k not in B], 10)
    used = set(A + B + C)
    H = (rng.sample([k for k in kept if k not in used], 15)
         + rng.sample([k for k in below if k not in used], 15))
    groups = {"A": A, "B": B, "C": C, "H": H}

    order = A + B + C + H
    rng.shuffle(order)
    posts = {p["key"]: p for p in corpus.load(HERE / "runs/2026-11-24T220432Z-live")}
    (HERE / "audit" / "draw.json").write_text(json.dumps(
        {"seed": SEED, "groups": groups,
         "sheet_order": order}, indent=1) + "\n")
    with open(HERE / "audit" / "sheet.jsonl", "w") as f:
        for i, k in enumerate(order, 1):
            p = posts[k]
            f.write(json.dumps({"n": i, "key": k, "company": p["board"],
                                "title": p["title"].strip(),
                                "locations": p["locations"],
                                "excerpt": excerpt(p["text"]), "url": p["url"]},
                               ensure_ascii=False) + "\n")
    print({g: len(v) for g, v in groups.items()}, "sheet:", len(order))


if __name__ == "__main__":
    main()
