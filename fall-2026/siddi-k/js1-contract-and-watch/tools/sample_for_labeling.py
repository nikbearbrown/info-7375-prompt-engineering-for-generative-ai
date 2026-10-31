#!/usr/bin/env python3
"""Draw the 20 postings for hand labelling (10 development, 10 held-out) from a saved board response.

Reproducible: same snapshot + same seed -> same 20 ids and the same split. The sample is
stratified by a title keyword screen (STRATUM_RE) so the experiment is not almost all
"not relevant": 10 postings whose title matches, 10 whose title does not, and each split gets
5 of each. Exact-duplicate titles (the same role posted in several cities) are collapsed to the
first id before drawing, so 20 labels are not spent on copies. --no-stratify draws 20 at random.

    python tools/sample_for_labeling.py evidence/snapshot-morning/databricks-jobs.json.gz --seed 7375

Writes labels/labeling-sheet.csv (label columns blank, for hand filling) and
labels/postings-to-label.md (each posting's fields and description as plain text).
"""
from __future__ import annotations

import argparse
import csv
import gzip
import html
import json
import random
import re
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
STRATUM_RE = re.compile(r"data|machine learning|\bML\b|\bAI\b|analytics|\bLLM|GenAI", re.I)


class _Text(HTMLParser):
    BLOCK = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "tr", "ul", "ol"}

    def __init__(self) -> None:
        super().__init__()
        self.out: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "li":
            self.out.append("\n- ")
        elif tag in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        self.out.append(data)


def plain_text(content: str | None) -> str:
    """Greenhouse returns the description as escaped HTML; unescape once, then drop the tags."""
    p = _Text()
    p.feed(html.unescape(content or ""))
    text = "".join(p.out).replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def load_jobs(path: Path) -> list[dict]:
    raw = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
    return json.loads(raw)["jobs"]


def draw(jobs: list[dict], seed: int, stratify: bool) -> list[tuple[dict, str]]:
    seen, unique = set(), []
    for j in sorted(jobs, key=lambda j: j["id"]):
        t = j["title"].strip().lower()
        if t not in seen:
            seen.add(t)
            unique.append(j)
    rng = random.Random(seed)
    if not stratify:
        picked = rng.sample(unique, 20)
        return [(j, "dev" if i < 10 else "heldout") for i, j in enumerate(picked)]
    match = [j for j in unique if STRATUM_RE.search(j["title"])]
    rest = [j for j in unique if not STRATUM_RE.search(j["title"])]
    a, b = rng.sample(match, 10), rng.sample(rest, 10)
    out = [(j, "dev") for j in a[:5] + b[:5]] + [(j, "heldout") for j in a[5:] + b[5:]]
    return out


def names(items) -> str:
    return "; ".join(x.get("name", "") for x in (items or []))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("snapshot", type=Path)
    ap.add_argument("--seed", type=int, default=7375)
    ap.add_argument("--no-stratify", action="store_true")
    ap.add_argument("--out", type=Path, default=HERE / "labels")
    a = ap.parse_args()

    picked = draw(load_jobs(a.snapshot), a.seed, not a.no_stratify)
    a.out.mkdir(parents=True, exist_ok=True)
    with (a.out / "labeling-sheet.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["posting_id", "split", "title", "location", "label", "reason"])
        for j, split in picked:
            w.writerow([j["id"], split, j["title"].strip(), (j.get("location") or {}).get("name", ""), "", ""])

    lines = [f"# Postings to label ({len(picked)})", "",
             f"Drawn by `tools/sample_for_labeling.py {a.snapshot.as_posix()} --seed {a.seed}"
             f"{' --no-stratify' if a.no_stratify else ''}`. Text below is the posting's own description "
             "with HTML removed; nothing is summarised or rewritten.", ""]
    for n, (j, split) in enumerate(picked, 1):
        lines += [f"## {n}. {j['title'].strip()} ({split})", "",
                  f"- posting_id: `{j['id']}`",
                  f"- location.name: {(j.get('location') or {}).get('name', '')}",
                  f"- departments: {names(j.get('departments'))}",
                  f"- offices: {names(j.get('offices'))}",
                  f"- first_published: {j.get('first_published')} · updated_at: {j.get('updated_at')}",
                  f"- absolute_url: {j.get('absolute_url')}", "",
                  plain_text(j.get("content")), "", "---", ""]
    (a.out / "postings-to-label.md").write_text("\n".join(lines), encoding="utf-8")
    for j, split in picked:
        print(f"{split:8} {j['id']}  {j['title'].strip()}  | {(j.get('location') or {}).get('name', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
