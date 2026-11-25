#!/usr/bin/env python3
"""
check_labels.py -- every label, badge, number and footer exactly as written.

scene.py logs every string it draws to build/onscreen/<beat>.json (written by
Beat.lock() during a real render). For each beat this checks:

  1. Every drawn string occurs word for word in that beat's production_viz
     (label + mechanic), except the chrome tags listed in CHROME.
  2. Every 'quoted' string in the mechanic is on screen (drawn pieces joined
     in drawing order, whitespace collapsed), except the few the mechanic
     itself says are NOT shown (NOT_DRAWN).
  3. The required items: the label, the part header, the status badge, the
     footer, the B07 loop and the B11 target rows.

Writes qc_reports/label_check.txt. Exit 1 on any failure.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sheet = json.loads((ROOT / "beat_sheet.json").read_text())
facts = json.loads((ROOT / "data/facts.json").read_text())

PARTS = {"B01": "1 · EXECUTIVE SUMMARY", "B02": "1 · EXECUTIVE SUMMARY",
         "B03": "2 · INTRODUCTION", "B04": "2 · INTRODUCTION",
         "B05": "3 · METHODS", "B06": "3 · METHODS", "B07": "3 · METHODS",
         "B08": "3 · METHODS", "B09": "4 · EVALUATION", "B10": "4 · EVALUATION",
         "B11": "4 · EVALUATION"}
BADGE = {"B01": "PLANNED", "B04": "PLANNED", "B05": "COMPLETED · JS3",
         "B06": "PLANNED (NOT BUILT)", "B07": "PLANNED", "B08": "PLANNED",
         "B09": "PLANNED", "B10": "PLANNED", "B11": "PROPOSED TARGETS — NOT RESULTS"}
EXTRA = {"B07": ["collect -> filter -> match -> check -> record -> stop"],
         "B11": ["wrong matches 0", "unsupported claims 0", "unauthorized actions 0",
                 "planted differences flagged all",
                 "missed matches ≤ 2 (of employers with records)"],
         "B08": ["Priya Nair — FICTIONAL"]}
# quoted in the mechanic as what must NOT appear
NOT_DRAWN = {"B04": ["error"]}
# chrome, not beat content: beat id and the author/course tag
CHROME = {"S. BABA ESWARAPPA · %s" % facts["numbers"]["course"]["display"]}


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


lines, bad = [], 0
for b in sheet["beats"]:
    bid, pv = b["beat_id"], b["graphic"]["production_viz"]
    spec = pv["label"] + " " + pv["mechanic"]
    f = ROOT / "build/onscreen" / ("%s.json" % bid)
    if not f.exists():
        lines.append("%s  FAIL  no on-screen log (render the scene first)" % bid)
        bad += 1
        continue
    drawn = json.loads(f.read_text())
    joined = norm(" ".join(drawn))
    fails = []

    for s in drawn:
        if s == bid or s in CHROME:
            continue
        if s not in spec:
            fails.append("drawn but not in production_viz: %r" % s)

    for q in re.findall(r"'([^']+)'", pv["mechanic"]):
        if q in NOT_DRAWN.get(bid, []):
            if any(q in s for s in drawn if s != pv["label"]):
                fails.append("drawn but the mechanic says not to: %r" % q)
            continue
        if norm(q) not in joined:
            fails.append("quoted in mechanic, not on screen: %r" % q)

    need = [pv["label"], PARTS[bid]] + ([BADGE[bid]] if bid in BADGE else []) \
        + ([facts["footers"][bid]] if bid in facts["footers"] else []) + EXTRA.get(bid, [])
    for s in need:
        if norm(s) not in joined:
            fails.append("required, not on screen: %r" % s)
    if not pv["label"].startswith(PARTS[bid]):
        fails.append("label does not start with part header %r" % PARTS[bid])

    bad += len(fails)
    lines.append("%s  %s  %d strings drawn, %d quoted checked" % (
        bid, "FAIL" if fails else "ok  ", len(drawn),
        len(re.findall(r"'([^']+)'", pv["mechanic"]))))
    lines += ["      " + x for x in fails]

lines.append("\nRESULT: %s" % ("PASS" if not bad else "FAIL (%d)" % bad))
out = "\n".join(lines)
(ROOT / "qc_reports").mkdir(exist_ok=True)
(ROOT / "qc_reports/label_check.txt").write_text(out + "\n")
print(out)
sys.exit(1 if bad else 0)
