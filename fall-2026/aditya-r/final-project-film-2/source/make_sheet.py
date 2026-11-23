#!/usr/bin/env python3
"""make_sheet.py — beat_sheet.json for the DayThread Final Project Film (2026-11-23) (show-tell, all beats drawn in Manim).

Narration is read from ../SCRIPT.md (the `VO:` line under each `### <BID> — …` heading), so the script
file is the single source of the words. A `[C]` in the heading puts "Constructed — proposed workflow" on
that beat. Re-running keeps measured audio fields (audio_file, actual_duration_s, words, tail) for any beat
whose narration is unchanged, so it never wipes the audio clock.
Shape copied from brutalist.art/skills/make/show-tell/reference/example-make_sheet.py.
"""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "daythread-final-project-film"
TITLE = "DayThread — Final Project Film"
SPARSE_REASON = ("show-tell style: one drawn scene on a cream stage per beat, minimal labels, the voice "
                 "carries the explanation. Only underfill and clustered are waived; edge-bleed, empty-frame "
                 "and contrast still apply.")

beats, cur = [], None
for line in (HERE.parent / "SCRIPT.md").read_text().splitlines():
    m = re.match(r"### (B[A-Z0-9]+) — (.*)$", line)
    if m:
        cur = {"bid": m.group(1), "title": m.group(2).replace("[C]", "").strip(),
               "constructed": "[C]" in m.group(2), "vo": None, "visual": []}
        beats.append(cur)
    elif cur and line.startswith("VO:"):
        cur["vo"] = line[3:].strip()
    elif cur and line.startswith("- Visual:"):
        cur["visual"].append(line[len("- Visual:"):].strip())
    elif cur and cur["visual"] and line.startswith("  ") and not line.startswith("  -"):
        cur["visual"][-1] += " " + line.strip()

CLASS = {"BIDEA": "BIDEA_Title", "B01": "B01_WhatItIs", "B02": "B02_Why", "B03": "B03_Exists",
         "B04": "B04_Others", "B05": "B05_Focus", "B06": "B06_Contract", "B07": "B07_Handoffs",
         "B08": "B08_Loop", "B09": "B09_Checker", "B10": "B10_Data", "B11": "B11_Resources",
         "B12": "B12_Steps", "B13": "B13_EvalChecker", "B14": "B14_Failures", "B15": "B15_Controlled",
         "B16": "B16_Limits", "BOUT": "BOUT_Outro"}

B = []
for b in beats:
    assert b["vo"], b["bid"]
    vis = " ".join(b["visual"])
    beat = {"beat_id": b["bid"], "act": b["title"], "lane": "manim", "proof_gate": "SHOW",
            "narration_text": b["vo"], "estimated_duration_s": round(len(b["vo"].split()) / 2.5, 1),
            "voice": "am_onyx", "engine": "kokoro",
            "constructed_caption": b["constructed"],
            "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": vis, "show": [{"at": 0.1, "event": vis}],
                     "manim": {"class": CLASS[b["bid"]]}, "motion_claim": vis},
            "qc": {"sparse_by_design": True, "sparse_reason": SPARSE_REASON}}
    if b["bid"] == "BOUT":
        beat["kind"] = "outro_voice"
        beat["tail_silence_s"] = 1.0
    B.append(beat)

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "DAYTHREAD · FINAL PROJECT FILM", "skill": "show-tell", "style_preset": "show-tell",
    "channel": "aditya-raj-info7375", "persona": "synthesized voice (Kokoro am_onyx) reading Aditya Raj's script",
    "author": "Aditya Raj", "voice": "am_onyx", "voice_kokoro": "am_onyx", "engine": "kokoro",
    "clock": "narration", "palette": "claude", "register": "Teardown", "fps": 24, "aspect_ratio": "16:9",
    "width": 3840, "height": 2160, "caption_policy": "burned-in disclosure + constructed-workflow captions (scene-drawn)",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("Assignment identity over template defaults (Aditya, 2026-10-14; kept for the 2026-11-23 film): drawn Manim title "
                              "instead of the hesitant writer; no key-terms card, no Your Turn, no verdict card; the "
                              "outro is a drawn card (DayThread · Aditya Raj · github.com/aditya-raj-sde) instead of "
                              "ClaudeTitleOutro, which hardcodes @NikBearBrown + mascot. bookend_check's outro rule "
                              "fails by design and is recorded in gate-reports/."),
    "audience": "INFO 7375 instructor/TAs and engineering hiring reviewers",
    "source_doc": "../SCRIPT.md (v1, 2026-11-23); daythread/SOURCES.md (S1–S4 read by Aditya 2026-10-14); replay/RESULTS.md (2026-10-25)",
    "playlist": "INFO 7375 final project film", "chapter_number": 0,
    "tags": ["DayThread", "agentic AI", "human-in-the-loop", "INFO 7375", "final project film"]},
    "beats": B}

old = HERE / "beat_sheet.json"
if old.exists():
    prev = {b["beat_id"]: b for b in json.loads(old.read_text())["beats"]}
    for b in B:
        p = prev.get(b["beat_id"], {})
        if p.get("narration_text") == b["narration_text"]:
            for k in ("audio_file", "actual_duration_s", "words", "speech_s", "tail_silence_s"):
                if k in p:
                    b[k] = p[k]
old.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
print(len(B), "beats;", sum(len(b["narration_text"].split()) for b in B), "words; est",
      round(sum(b["estimated_duration_s"] for b in B)), "s")
