"""Draw the held-out set (seeded, before any filter exists) and write its blind sheet.

Held-out = 20 random postings whose title names an engineering role + 10 random others.
The pool rule below is a title regex chosen by Claude Code so the held-out set contains
some plausible positives; it is not the filter. These 30 keys are excluded from every
audit draw and are used only to measure the one change (CHANGE.md).

    python3 -m jobfilter.heldout --draw
"""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

from .corpus import HERE, load
from .sheets import write_sheet

SEED = 20261125
ENGINEERING_TITLE = re.compile(r"(?<![a-z0-9])(engineer|engineering|developer|sre|swe)(?![a-z0-9])", re.I)
N_ENGINEERING, N_OTHER = 20, 10
LABELS = HERE / "labels"
KEYS = LABELS / "heldout-keys.json"


def draw(postings: list, seed: int = SEED) -> list:
    eng = sorted((p for p in postings if ENGINEERING_TITLE.search(p["title"])), key=lambda p: p["key"])
    other = sorted((p for p in postings if not ENGINEERING_TITLE.search(p["title"])), key=lambda p: p["key"])
    rng = random.Random(seed)
    chosen = rng.sample(eng, N_ENGINEERING) + rng.sample(other, N_OTHER)
    rng.shuffle(chosen)
    return chosen


def heldout_keys() -> set:
    return set(json.loads(KEYS.read_text())["keys"])


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv != ["--draw"]:
        print("usage: python3 -m jobfilter.heldout --draw", file=sys.stderr)
        return 2
    corpus = load()
    chosen = draw(corpus["postings"])
    LABELS.mkdir(exist_ok=True)
    KEYS.write_text(json.dumps({
        "seed": SEED, "pool_rule": ENGINEERING_TITLE.pattern,
        "n_engineering_title": N_ENGINEERING, "n_other": N_OTHER,
        "keys": [p["key"] for p in chosen]}, indent=1) + "\n")
    write_sheet(LABELS / "heldout-sheet.md", "Held-out labeling sheet (blind)",
                f"30 postings drawn with seed {SEED} before any filter code existed: 20 random postings with an "
                "engineering word in the title, 10 random others, shuffled. No filter output appears here. "
                "These are never used to tune the filter; they measure one change, once.",
                chosen)
    print(f"held-out: {len(chosen)} postings -> labels/heldout-sheet.md, labels/heldout-sheet.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
