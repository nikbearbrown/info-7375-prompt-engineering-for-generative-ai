"""The blind labeling sheet: every sampled posting, shuffled, with no score, decision or set shown.

Each item shows the same three things, extracted the same way for every posting:
title, location, and 400 characters of text starting at "About the role" (or at the start
of the text when a posting has no such heading). The URL is given for opening the posting.
"""
from __future__ import annotations

import csv
import random
import re

EXCERPT_CHARS = 400
CUE = "about the role"
VERDICTS = {"y": "relevant", "n": "not relevant", "?": "can't tell"}


def excerpt(text: str) -> str:
    t = re.sub(r"\s+", " ", text or "").strip()
    i = t.lower().find(CUE)
    start = i if i >= 0 else 0
    out = t[start:start + EXCERPT_CHARS]
    return out + ("…" if len(t) > start + EXCERPT_CHARS else "")


def company(posting: dict) -> str:
    return {"anthropic": "Anthropic", "notion": "Notion", "perplexity": "Perplexity"}.get(posting["board"],
                                                                                        posting["board"])


def build(keys: list, postings: dict, seed: int) -> list:
    rng = random.Random(seed)
    order = list(keys)
    rng.shuffle(order)
    return [{"item": i + 1, "key": k, "company": company(postings[k]), "title": postings[k]["title"],
             "location": postings[k]["location"] or "(no location)", "url": postings[k]["url"],
             "excerpt": excerpt(postings[k]["text"])} for i, k in enumerate(order)]


def write_sheet(items: list, path) -> None:
    lines = ["# Labeling sheet (blind)", "",
             "Question for each posting: **is this worth Priya's time to read in full?** "
             "Answer **y** (relevant), **n** (not relevant) or **?** (can't tell without more).", "",
             "No score, filter decision or sample set is shown. Every item shows the title, the location, and "
             f"{EXCERPT_CHARS} characters of text starting at \"About the role\" (or at the start of the text when "
             "there is no such heading), the same rule for every posting.", ""]
    for it in items:
        lines += [f"## {it['item']}. {it['title']}", f"{it['company']} · {it['location']} · {it['url']}", "",
                  f"> {it['excerpt']}", ""]
    with open(path, "w") as f:
        f.write("\n".join(lines))


def write_template(items: list, path) -> None:
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item", "key", "verdict", "note", "labeled_at"])
        for it in items:
            w.writerow([it["item"], it["key"], "", "", ""])


def read_labels(path) -> dict:
    """key -> {'verdict': 'relevant'|'not relevant'|"can't tell", 'note': ..., 'item': ...} for labeled rows."""
    out = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            v = (row.get("verdict") or "").strip()
            if v:
                if v not in VERDICTS.values():
                    raise ValueError(f"item {row['item']}: unknown verdict {v!r}")
                out[row["key"]] = {"verdict": v, "note": row.get("note", ""), "item": int(row["item"]),
                                   "labeled_at": row.get("labeled_at", "")}
    return out
