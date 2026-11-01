"""Build the result tables in SAMPLING.md and PROMPT-EXPERIMENT.md from experiments/output/ and labels/.
Every number in those tables comes from here; nothing is typed in by hand. Written by Claude.

    python tools/make_reports.py
"""
from __future__ import annotations

import collections
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "experiments" / "output"
START, END = "<!-- generated:start -->", "<!-- generated:end -->"


def jsonl(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def wilson(k: int, n: int, z: float = 1.96) -> str:
    if n == 0:
        return "n/a"
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return f"{max(0, c - h):.0%}–{min(1, c + h):.0%}"


def short(v) -> str:
    return {"relevant": "R", "not_relevant": "N"}.get(v, "✗")


def labels() -> dict:
    return {int(r["posting_id"]): r for r in jsonl(ROOT / "labels" / "hand_labels.jsonl")}


def sampling_table() -> str:
    recs = jsonl(OUT / "sampling.jsonl")
    if not recs:
        return "_No sampling runs yet._"
    hand = labels()
    by = collections.OrderedDict()
    for r in recs:
        by.setdefault(r["posting_id"], []).append(r)
    rows = ["| posting_id | title | verdicts in run order (R relevant, N not, ✗ invalid) | modal share | hand label | modal = hand? |",
            "|---|---|---|---|---|---|"]
    unanimous = 0
    for pid, rs in by.items():
        vs = [r["verdict"] for r in sorted(rs, key=lambda r: (r["ran_at"], r["repeat"]))]
        valid = [v for v in vs if v]
        modal, n = collections.Counter(valid).most_common(1)[0] if valid else (None, 0)
        unanimous += len(set(vs)) == 1
        h = hand.get(pid, {}).get("label")
        rows.append(f"| {pid} | {rs[0]['title'].strip()} | {' '.join(short(v) for v in vs)} | {n}/{len(vs)} | "
                    f"{h or '(not labelled)'} | {'yes' if h and modal == h else ('no' if h else '–')} |")
    models = sorted({r["claude_model"] for r in recs})
    days = sorted({r["ran_at"][:16] for r in recs})
    rows += ["", f"{len(recs)} calls on {len(by)} postings, prompt `{recs[0]['prompt_version']}`, model "
             f"{', '.join(models)}, run {days[0]} → {days[-1]} UTC. {unanimous} of {len(by)} postings got the same "
             f"verdict on every call. Invalid outputs: {sum(1 for r in recs if r['status'] != 'ok')}."]
    return "\n".join(rows)


def experiment_tables() -> str:
    runs = {p.stem.replace("experiment_", ""): jsonl(p) for p in sorted(OUT.glob("experiment_*.jsonl"))}
    if not runs:
        return "_No experiment runs yet._"
    summary = ["| prompt | split | agree with hand labels | 95% Wilson interval | invalid outputs |", "|---|---|---|---|---|"]
    for name, rs in runs.items():
        k = sum(r["match"] for r in rs)
        summary.append(f"| `{rs[0]['prompt_version']}` | {rs[0]['split']} | {k}/{len(rs)} | {wilson(k, len(rs))} | "
                       f"{sum(1 for r in rs if r['status'] != 'ok')} |")
    detail = []
    for split in ("dev", "held_out"):
        cols = [n for n in runs if n.endswith(split)]
        if not cols:
            continue
        ids = [r["posting_id"] for r in runs[cols[0]]]
        titles = {r["posting_id"]: r["title"].strip() for n in cols for r in runs[n]}
        hand = {r["posting_id"]: r["hand_label"] for n in cols for r in runs[n]}
        detail += ["", f"**{split}**", "", "| posting_id | title | hand | " + " | ".join(f"`{n.rsplit('_', 1)[0] if not n.endswith('held_out') else n[:-9]}`" for n in cols) + " |",
                   "|---|---|---|" + "---|" * len(cols)]
        for i in ids:
            cells = []
            for n in cols:
                r = next((x for x in runs[n] if x["posting_id"] == i), None)
                cells.append("–" if r is None else f"{short(r['verdict'])}{'' if r['match'] else ' ✗'}")
            detail.append(f"| {i} | {titles[i]} | {short(hand[i])} | " + " | ".join(cells) + " |")
    return "\n".join(summary + detail + ["", "R relevant, N not relevant; a trailing ✗ marks disagreement with the hand label."])


def fill(path: Path, body: str) -> None:
    text = path.read_text(encoding="utf-8")
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: f"{START}\n{body}\n{END}", text, flags=re.S)
    path.write_text(new, encoding="utf-8")


if __name__ == "__main__":
    fill(ROOT / "SAMPLING.md", sampling_table())
    fill(ROOT / "PROMPT-EXPERIMENT.md", experiment_tables())
    print("updated SAMPLING.md and PROMPT-EXPERIMENT.md")
