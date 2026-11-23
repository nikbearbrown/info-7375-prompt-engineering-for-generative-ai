#!/usr/bin/env python3
"""make_sheet.py — build beat_sheet.json for the Seeded Faults four-part project film (show-tell style).

Narration is read from the submission's beat_sheet.json (the source of truth) and audio fields
already measured here (actual_duration_s, audio_file) are carried forward, so re-running this
never drops the audio. No instructor persona: no hesitant-writer/terms/Your Turn bookends, and
the outro is a drawn title scene (ClaudeTitleOutro hard-codes the instructor's handle).
"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
SRC = Path.home() / "Projects/INFO7375/fall-2026/atharva-c/project-film-four-part/beat_sheet.json"
SLUG = "seeded-faults-project"
TITLE = "Seeded Faults"
VOICE = "am_michael"

CLASSES = {"E1": "E1_TableChecks", "E2": "E2_CrackedPass", "E3": "E3_Scoreboard", "I1": "I1_TwoTools",
           "I2": "I2_Drafters", "I3": "I3_Lineage", "M1": "M1_PublicData", "M2A": "M2A_CleanBaseline",
           "M2B": "M2B_Locked", "M3": "M3_Plan", "M4": "M4_Resources", "V1": "V1_Balance", "V2": "V2_Line",
           "V3": "V3_Close"}
SPARSE = ("show-tell style: one drawn object or scene on a cream stage per beat, minimal labels, "
          "narration carries the explanation; only underfill and clustered are waived.")

old = {}
if (HERE / "beat_sheet.json").exists():
    for b in json.loads((HERE / "beat_sheet.json").read_text()).get("beats", []):
        old[b["beat_id"]] = b
src = json.loads(SRC.read_text())

beats = []
for s in src["beats"]:
    bid = s["beat_id"]
    b = {"beat_id": bid, "act": s["act"], "lane": "manim", "proof_gate": "SHOW",
         "narration_text": s["narration_text"], "estimated_duration_s": s["estimated_duration_s"],
         "voice": VOICE, "engine": "kokoro",
         "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": s["new_visual_element"],
                  "manim": {"class": CLASSES[bid]}, "motion_claim": s["new_visual_element"]},
         "qc": {"sparse_by_design": True, "sparse_reason": SPARSE}}
    for k in ("on_screen_label", "evidence"):
        if k in s:
            b[k] = s[k]
    beats.append(b)

beats.append({"beat_id": "BOUT", "act": "outro", "lane": "manim", "proof_gate": "SHOW",
              "narration_text": "Seeded Faults. By Atharva C.", "estimated_duration_s": 3.5,
              "voice": VOICE, "engine": "kokoro", "kind": "outro_voice", "tail_silence_s": 1.0,
              "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": "Title and author name, drawn.",
                       "manim": {"class": "BOUT_Title"}, "motion_claim": "title lands, name lands"},
              "qc": {"sparse_by_design": True, "sparse_reason": "Title card: one title and one name by design."}})

for b in beats:   # carry measured audio forward only if the narration hasn't changed
    o = old.get(b["beat_id"])
    if o and o.get("narration_text") == b["narration_text"]:
        for k in ("actual_duration_s", "audio_file"):
            if o.get(k) is not None:
                b[k] = o[k]

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "DATA ENGINEERING · FINAL PROJECT FILM", "skill": "show-tell",
    "style_preset": "show-tell", "channel": "atharva-c",
    "author": "Atharva C", "voice": VOICE, "voice_kokoro": VOICE, "engine": "kokoro", "clock": "narration",
    "palette": "claude", "fps": 24, "aspect_ratio": "16:9", "width": 3840, "height": 2160, "caption_policy": "none",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("INFO 7375 project film: as in the pitch film, the course requires narrating as myself with no instructor "
                              "name, persona or credit line, so the persona cold open, recap and Your Turn bookends are "
                              "dropped and the outro is a drawn title scene with my own name."),
    "audience": "INFO 7375 instructor/TAs; data engineering hiring managers",
    "source_doc": "SCRIPT-DRAFT.md, FAULT-CATALOGUE.md and evidence/ in the submission folder",
    "tags": ["data engineering", "data quality", "dbt", "Great Expectations", "Claude Code", "INFO 7375"]},
    "beats": beats}
(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
print(len(beats), "beats;", sum(1 for b in beats if b.get("actual_duration_s")), "with measured audio")
