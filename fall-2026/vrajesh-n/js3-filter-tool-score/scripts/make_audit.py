"""Build the BLIND reject-audit sheet from results/filter-v1.json. Seeded, so it can be rebuilt exactly.
Usage: python scripts/make_audit.py
Writes review/audit-sheet.md (what Vrajesh reads, no filter verdict), review/audit-labels.csv (blank, he fills it),
review/audit-key.json (group + filter verdict per item; opened only AFTER the labels are saved)."""
import csv
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from earlybird import boards  # noqa: E402

SEED, N_RANDOM_REJECT, N_CLOSE_R1, N_CLOSE_YEARS, N_KEPT = 7375, 35, 8, 4, 15
rows = json.loads((ROOT / "results/filter-v1.json").read_text(encoding="utf-8"))
rej = [r for r in rows if r["verdict"] == "not_relevant"]
kept = [r for r in rows if r["verdict"] == "relevant"]
rng = random.Random(SEED)

random_rej = rng.sample(rej, N_RANDOM_REJECT)
taken = {(r["board"], r["id"]) for r in random_rej}
# Close calls (defined before looking at them): (a) R1 rejects whose title still says engineer/developer/architect
# with no seniority word, i.e. just outside the role list; (b) R2 rejects where the only trigger is exactly "3+ years".
near_r1 = [r for r in rej if r["failed_check"] == "R1" and (r["board"], r["id"]) not in taken
           and re.search(r"engineer|developer|architect|programmer", r["title"], re.I)
           and not re.search(r"\b(senior|sr|staff|principal|lead|manager|head|director)\b", r["title"], re.I)]
near_yrs = [r for r in rej if r["failed_check"] == "R2" and "asks for 3+ years" in r["justification"]
            and (r["board"], r["id"]) not in taken]
close = rng.sample(near_r1, N_CLOSE_R1) + rng.sample(near_yrs, N_CLOSE_YEARS)
sample_kept = rng.sample(kept, N_KEPT)

items = ([("random_reject", r) for r in random_rej] + [("close_call", r) for r in close]
         + [("kept", r) for r in sample_kept])
rng.shuffle(items)  # blind: order tells nothing about group

desc = {}
for f in sorted((ROOT / "data/snapshot-2026-11-01").glob("*.json")):
    for p in boards.parse(f.stem.split("_")[0], f.read_text(encoding="utf-8")):
        desc[(f.stem, p["id"])] = p["descriptionPlain"]

def snippets(text):
    out = []
    for label, pat in (("years", r"\d+\s*\+?\s*(?:-|to)?\s*\d*\s*years?"), ("clearance", r"clearance|ts/sci|top secret"),
                       ("sponsor", r"sponsor"), ("training", r"\btraining\b")):
        m = re.search(pat, text, re.I)
        if m:
            a, b = max(0, m.start() - 70), min(len(text), m.end() + 70)
            out.append(f"{label}: ...{text[a:b]}...")
    return out

md = ["# Reject audit sheet (blind)\n",
      "Judge each posting yourself. Question: **given FILTER.md v1 and Rohan Desai (new grad, needs sponsorship), "
      "is this a posting worth his time?** Write Y, N, or ? (cannot tell) in `audit-labels.csv`.\n",
      "You do not see the filter's verdict. The key (`audit-key.json`) is opened only after the labels are saved.\n"]
labels, key = [["n", "verdict", "note"]], []
for n, (group, r) in enumerate(items, 1):
    d = desc[(r["board"], r["id"])]
    md.append(f"\n## {n}. {r['title']}\n- board: {r['board']}  |  location: {r['location']}\n- url: {r['url']}\n"
              f"- description (first 600 chars): {d[:600]}\n" + "".join(f"- {s}\n" for s in snippets(d)))
    labels.append([n, "", ""])
    key.append({"n": n, "group": group, "board": r["board"], "id": r["id"], "title": r["title"],
                "filter_verdict": r["verdict"], "failed_check": r["failed_check"]})
(ROOT / "review/audit-sheet.md").write_text("".join(md), encoding="utf-8")
with open(ROOT / "review/audit-labels.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(labels)
(ROOT / "review/audit-key.json").write_text(json.dumps(key, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"seed {SEED}: {len(items)} items = {N_RANDOM_REJECT} random rejects of {len(rej)}, "
      f"{len(close)} close calls (pools: {len(near_r1)} R1-near, {len(near_yrs)} years==3), {N_KEPT} kept of {len(kept)}")
