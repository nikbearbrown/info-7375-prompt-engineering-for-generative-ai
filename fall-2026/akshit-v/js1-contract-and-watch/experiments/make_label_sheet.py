"""Draw the 20 postings to hand-label (10 development, 10 held-out) from a saved real response.

Draws from technical-titled postings only: 14 plausible candidates (no disqualifying
title word) and 6 others, split 7 + 3 into each set.
The draw uses a fixed seed so it can be repeated. The sheet shows no verdicts
(rule or Claude), so hand labels are made blind.

    python experiments/make_label_sheet.py evidence/raw/<stamp>_figma_live.json
"""
import argparse
import csv
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent.postings import load_postings  # noqa: E402
from agent.rule import DISQUALIFYING_WORDS, whole_word  # noqa: E402

HERE = Path(__file__).resolve().parent
TECH = re.compile(r"engineer|data|analytic|analyst|scientist|infrastructure|platform|developer"
                  r"|machine learning|\bml\b|\bai\b", re.I)
SEED = 7375


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("raw", type=Path)
    args = ap.parse_args()

    pool = sorted((p for p in load_postings(args.raw) if TECH.search(p["title"])), key=lambda p: p["id"])
    # Draw history (all on 2026-10-31, before any labels were made):
    #  1. plain random 20 from the pool: 19 obvious non-matches, could not tell two prompts apart;
    #  2. 10 data-like titles + 10 others: still about half Manager/Director/Intern titles;
    #  3. (used) 14 plausible candidates (technical title, no disqualifying word) + 6 others.
    def disqualified(p):
        return any(whole_word(w).search(p["title"]) for w in DISQUALIFYING_WORDS)
    candidates = [p for p in pool if not disqualified(p)]
    others = [p for p in pool if disqualified(p)]
    rng = random.Random(SEED)
    a, b = rng.sample(candidates, 14), rng.sample(others, 6)
    sets = ([("dev", p) for p in a[:7] + b[:3]] + [("heldout", p) for p in a[7:] + b[3:]])

    sheet = HERE / "labels.csv"
    with sheet.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["set", "id", "title", "hand_label", "note"])
        for s, p in sets:
            w.writerow([s, p["id"], p["title"], "", ""])

    lines = [f"# Postings to hand-label (drawn from {args.raw.name}, seed {SEED}, pool of {len(pool)})",
             "", "Label each one `relevant` or `not_relevant` in labels.csv, using LABELING_RULE.md.", ""]
    for s, p in sets:
        lines += [f"## [{s}] {p['id']}: {p['title']}", f"location: {p['location_name']}  ",
                  f"url: {p['absolute_url']}", "", p["content_text"], ""]
    (HERE / "postings_to_label.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {sheet} and postings_to_label.md")
    for s, p in sets:
        print(f"  {s:8} {p['id']}  {p['title']}")


if __name__ == "__main__":
    main()
