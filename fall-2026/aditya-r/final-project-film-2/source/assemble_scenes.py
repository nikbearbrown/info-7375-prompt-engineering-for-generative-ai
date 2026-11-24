#!/usr/bin/env python3
"""assemble_scenes.py — writes scenes.py = iso_kit.py (verbatim) + the original props this film
uses (data copied verbatim from iso_originals_25.py, plus its make_original factory verbatim) +
scenes_body.py. show-tell rule: PASTE the kit, never import it (Gate A copies only scenes.py).
Edit scenes_body.py, then re-run this; never edit scenes.py by hand."""
import ast, pprint
from pathlib import Path
HERE = Path(__file__).resolve().parent
TPL = Path.home() / "Desktop/Brutalist/brutalist.art/skills/make/show-tell/templates"
PROPS = ["review-desk", "permission-gate", "memory-drawers", "task-queue", "agent-workstation", "evidence-binder",
         "approval-stamp", "budget-slots", "comparison-trays", "secure-vault", "context-crate"]
kit = (TPL / "iso_kit.py").read_text()
orig = (TPL / "iso_originals_25.py").read_text()
head, factory = orig.split("\ndef make_original", 1)
data = ast.literal_eval(head.split("=", 1)[1].strip())
subset = {k: data[k] for k in PROPS}
body = (HERE / "scenes_body.py").read_text()
out = (kit.rstrip() + "\n\n\n# ═════════════════════════════ ORIGINAL PROPS (subset of iso_originals_25.py, verbatim data) ═════════════════════════════\n"
       + "_ST_ORIGINALS_25 = " + pprint.pformat(subset, width=110, sort_dicts=False) + "\n\n"
       + "def make_original" + factory.rstrip() + "\n\n" + body)
(HERE / "scenes.py").write_text(out)
print("scenes.py:", len(out.splitlines()), "lines; props:", ", ".join(PROPS))
