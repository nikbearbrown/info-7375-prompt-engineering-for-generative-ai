#!/usr/bin/env python3
"""
check_facts.py -- hard rule 1: numbers come from one data file.

  1. Every spoken form recorded in data/facts.json occurs in that beat's
     narration_text (so a number on screen is the number the voice says).
  2. Every B05 grid cue occurs in the B05 narration.
  3. scene.py contains no string literal with a digit in it (docstrings and
     the file paths it loads are the only exceptions), so nothing numeric can
     be hand-typed into an animation.

Writes qc_reports/facts_check.txt. Exit 1 on any failure.
"""
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
facts = json.loads((ROOT / "data/facts.json").read_text())
sheet = json.loads((ROOT / "beat_sheet.json").read_text())
narr = {b["beat_id"]: b["narration_text"] for b in sheet["beats"]}

lines, bad = [], 0

lines.append("1. spoken forms vs narration")
for key, f in facts["numbers"].items():
    for bid, phrase in f["spoken"].items():
        ok = phrase.lower() in narr[bid].lower()
        bad += not ok
        lines.append("  %-4s %-24s %-10s %-40r %s" % (
            "ok" if ok else "FAIL", key, bid, phrase, f["display"]))
    if "note" in f:
        lines.append("       note: " + f["note"])

lines.append("\n2. B05 grid cues vs narration")
for item in facts["test_grid"]["columns"] + facts["test_grid"]["rows"]:
    ok = item["cue"].lower() in narr["B05"].lower()
    bad += not ok
    lines.append("  %-4s %r" % ("ok" if ok else "FAIL", item["cue"]))

lines.append("\n3. digits in scene.py string literals")
tree = ast.parse((ROOT / "scene.py").read_text())
docs = set()
for node in ast.walk(tree):
    if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)):
        body = getattr(node, "body", [])
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            docs.add(id(body[0].value))
ALLOW = [re.compile(p) for p in (r"^B\d\d$",            # beat ids
                                 r"^#[0-9A-Fa-f]{6}$",   # colours
                                 r"^[\w/]+\.json$")]     # files it loads
hits = []
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str) \
            and id(node) not in docs and re.search(r"\d", node.value):
        if any(p.match(node.value) for p in ALLOW) or node.value in facts["numbers"]:
            continue                                     # facts.json keys
        if not re.search(r"\d", re.sub(r"%[-+ #0]*[\d.]*[a-z]", "", node.value)):
            continue                                     # printf specs in logs
        hits.append((node.lineno, node.value))
for ln, v in hits:
    lines.append("  FAIL scene.py:%d %r" % (ln, v))
bad += len(hits)
if not hits:
    lines.append("  ok   no hand-typed digits")

lines.append("\nRESULT: %s" % ("PASS" if not bad else "FAIL (%d)" % bad))
out = "\n".join(lines)
(ROOT / "qc_reports").mkdir(exist_ok=True)
(ROOT / "qc_reports/facts_check.txt").write_text(out + "\n")
print(out)
sys.exit(1 if bad else 0)
