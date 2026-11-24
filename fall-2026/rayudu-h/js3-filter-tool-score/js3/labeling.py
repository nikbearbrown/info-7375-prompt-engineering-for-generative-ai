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


# ---- the second labeling pass (added Nov 23, 2026) ---------------------------------------------
# The first view (excerpt above) never showed an experience requirement: in all 90 labeled postings
# whose text states one, it came after the 400-character excerpt. The second view shows, for every
# posting by the same rule: title, location, a 250-character role summary, and every sentence that
# states a number of years: each "N years" phrase with ~110 characters on each side, verbatim, at most 3.
YEARS = re.compile(r"\b(\d{1,2})\s*\+?\s*(?:\+\s*)?(?:or more\s+)?years?\b", re.I)
SUMMARY_CHARS = 250
YEARS_SENTENCES = 3
WINDOW = 110


def states_years(text: str) -> bool:
    return any(int(m.group(1)) < 30 for m in YEARS.finditer(text or ""))


def years_sentences(text: str) -> list:
    """Every "N years" phrase with about WINDOW characters on each side, verbatim (at most 3).

    Fixed before any second-pass label (Nov 23): the first version split on sentence ends, but
    Greenhouse text runs its bullets together, so the cut at 220 characters often fell before the
    years phrase. A window around each match always shows the phrase itself.
    """
    t = re.sub(r"\s+", " ", text or "").strip()
    out, last_end = [], -1
    for m in YEARS.finditer(t):
        if int(m.group(1)) >= 30 or m.start() < last_end:
            continue
        a, b = max(0, m.start() - WINDOW), min(len(t), m.end() + WINDOW)
        a = t.rfind(" ", 0, a) + 1 if a > 0 else 0
        b2 = t.find(" ", b)
        b = len(t) if b2 < 0 else b2
        out.append(("…" if a > 0 else "") + t[a:b] + ("…" if b < len(t) else ""))
        last_end = b
        if len(out) == YEARS_SENTENCES:
            break
    return out


def view_v2(posting: dict) -> dict:
    t = re.sub(r"\s+", " ", posting.get("text") or "").strip()
    i = t.lower().find(CUE)
    start = i if i >= 0 else 0
    summary = t[start:start + SUMMARY_CHARS] + ("…" if len(t) > start + SUMMARY_CHARS else "")
    return {"summary": summary, "experience": years_sentences(posting.get("text") or "")}


def write_sheet_v2(items: list, path) -> None:
    lines = ["# Labeling sheet, second pass (blind)", "",
             "Question for each posting: **is this worth Priya's time to read in full?** Answer **y**, **n** or **?**. "
             "Priya: MS Dec 2025, one 8-month AI Engineer co-op.", "",
             f"Every item shows the title, the location, {SUMMARY_CHARS} characters of role summary (from \"About the "
             f"role\", or the start of the text), and every \"N years\" phrase with about {WINDOW} characters on each side, "
             f"verbatim (at most {YEARS_SENTENCES}). No score, filter decision or earlier "
             "verdict is shown.", ""]
    for it in items:
        lines += [f"## {it['item']}. {it['title']}", f"{it['company']} · {it['location']} · {it['url']}", "",
                  f"> {it['summary']}", ""]
        lines += [f"- Experience: “{s}”" for s in it["experience"]] + [""]
    with open(path, "w") as f:
        f.write("\n".join(lines))
