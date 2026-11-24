#!/usr/bin/env python3
"""positioning_check.py — the positioning audit gate (my brief, revision of 23 Nov 2026).

Readback is for any AI feature's acceptance criteria; the AMI meeting-recap feature is only the test bench. This gate:
  1. quotes every narration sentence and every on-screen string that mentions meetings, recaps, AMI (or an AMI meeting
     ID) or C4, and checks each sits in Methods or Evaluation, in a scene that carries the "test case" tag;
  2. checks the executive summary has zero such references, spoken or on screen;
  3. quotes the lines heard in 0:00–1:00 that say what Readback is for.
Inputs: beat_sheet.json (narration, part, durations) and _qc/positioning/strings_<Scene>.json (from strings_dump.py).
Output: gates/positioning-audit.md, and PASS/FAIL on the last line printed.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TERMS = re.compile(r"\b(meetings?|recaps?|AMI|C4|(?:ES|IS)\d{4}[a-d])\b", re.I)
SENT = re.compile(r'(?<=[.?!])\s+(?=[A-Z"\'])')
TEST_TAG = re.compile(r"test case", re.I)

sheet = json.load(open(os.path.join(HERE, "beat_sheet.json")))
beats = sheet["beats"]
t, start = 0.0, {}
for b in beats:
    start[b["beat_id"]] = t
    t += float(b.get("render_duration_s") or b["actual_duration_s"])


def clock(s):
    return f"{int(s // 60)}:{s % 60:04.1f}"


fails, out = [], ["# Positioning audit — Readback project film", "",
                  "Gate (my brief, 23 Nov 2026): every mention of meetings, recaps, AMI (or an AMI meeting ID) or C4 sits in Methods "
                  "or Evaluation, in a scene tagged \"test case\"; the executive summary has none; the first minute says Readback is "
                  "for any AI feature's acceptance criteria. Narration from `beat_sheet.json`; on-screen strings from every frame of "
                  "every scene (`strings_dump.py`, 24 fps). Spoken \"Reed-back\" is shown as Readback.", "",
                  "## 1 · Narration that mentions the test case", "", "| Beat | Part | Starts | Sentence | Terms | Verdict |", "|---|---|---|---|---|---|"]
for b in beats:
    for sent in SENT.split(b["narration_text"].strip()):
        terms = sorted({m.group(0) for m in TERMS.finditer(sent)}, key=str.lower)
        if not terms:
            continue
        ok = b["act"] in ("methods", "evaluation")
        if not ok:
            fails.append(f"narration {b['beat_id']}: {sent}")
        out.append(f"| {b['beat_id']} | {b['act']} | {clock(start[b['beat_id']])} | {sent.replace('Reed-back', 'Readback')} | "
                   f"{', '.join(terms)} | {'OK' if ok else 'FAIL'} |")

out += ["", "## 2 · On-screen strings that mention the test case", "",
        "| Scene | Part | On screen (s into the beat) | String | Terms | Scene tagged \"test case\"? | Verdict |", "|---|---|---|---|---|---|---|"]
missing = []
for b in beats:
    cls = (b.get("shot", {}).get("manim") or {}).get("class")
    if not cls:
        continue
    path = os.path.join(HERE, "_qc", "positioning", f"strings_{cls}.json")
    if not os.path.exists(path):
        missing.append(cls)
        continue
    rows = json.load(open(path))
    tagged = any(TEST_TAG.search(r["text"]) for r in rows)
    for r in rows:
        terms = sorted({m.group(0) for m in TERMS.finditer(r["text"])}, key=str.lower)
        if not terms:
            continue
        ok = b["act"] in ("methods", "evaluation") and tagged
        if not ok:
            fails.append(f"on screen {cls}: {r['text']}")
        out.append(f"| {cls} | {b['act']} | {r['first']:.1f}–{r['last']:.1f} | {r['text']} | {', '.join(terms)} | "
                   f"{'yes' if tagged else 'no'} | {'OK' if ok else 'FAIL'} |")
if missing:
    fails.append(f"no strings dump for: {', '.join(missing)}")

summ = [b for b in beats if b["act"] == "summary"]
hits = [b["beat_id"] for b in summ if TERMS.search(b["narration_text"])]
for b in summ:
    cls = b["shot"]["manim"]["class"]
    path = os.path.join(HERE, "_qc", "positioning", f"strings_{cls}.json")
    if os.path.exists(path):
        hits += [f"{cls}: {r['text']}" for r in json.load(open(path)) if TERMS.search(r["text"])]
out += ["", "## 3 · Executive summary (" + ", ".join(b["beat_id"] for b in summ) + ")", "",
        f"References to meetings, recaps, AMI or C4, spoken or on screen: **{len(hits)}**" + (f" ({'; '.join(hits)})" if hits else "") + "."]
if hits:
    fails.append("summary references: " + "; ".join(hits))

out += ["", "## 4 · The first minute (0:00–1:00): what Readback is for", "",
        "Every line heard before 1:00 that says what Readback is for, with the time it starts (from `mp3/words.json`):", ""]
_w = json.load(open(os.path.join(HERE, "mp3", "words.json")))
WORDS, FPS, used = _w["beats"], float(_w.get("fps", 24)), {}
for b in beats:
    if start[b["beat_id"]] >= 60:
        break
    for sent in SENT.split(b["narration_text"].strip()):
        if re.search(r"AI feature|criteria|criterion|rubric|copilot|Reed-back", sent):
            first = sent.split()[0].strip(".,:;?!'\"").lower()
            at = next((x["startFrame"] / FPS for x in WORDS.get(b["beat_id"], [])
                       if x["text"].strip(".,:;?!'\"").lower() == first and x["startFrame"] / FPS >= used.get(b["beat_id"], -1)), 0.0)
            used[b["beat_id"]] = at + 0.01
            out.append(f"- **{b['beat_id']} · {clock(start[b['beat_id']] + at)}** — \"{sent.replace('Reed-back', 'Readback')}\"")

verdict = "PASS" if not fails else "FAIL"
out += ["", f"## Result: **{verdict}**", ""] + [f"- {f}" for f in fails]
os.makedirs(os.path.join(HERE, "gates"), exist_ok=True)
open(os.path.join(HERE, "gates", "positioning-audit.md"), "w").write("\n".join(out) + "\n")
print("\n".join(out[-(len(fails) + 3):]))
print(f"[positioning] {verdict} — {len(fails)} finding(s)")
sys.exit(0 if not fails else 1)
