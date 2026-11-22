#!/usr/bin/env python3
"""make_sheet.py — beat_sheet.json for job-search-agent-film (WorthLoop, the final project film).

Audio-only for now: it builds the 17 narration beats, B1-B17, from NARRATION.md in this
folder, so the narration can be voiced and measured before any scene is built. Voice:
Kokoro am_onyx (metadata.voice_kokoro); engine "kokoro" on every beat.

Each narration_text is exactly that beat's line in NARRATION.md, without the "B# — " label.
The opening card and the "On screen:" line are on-screen text, not narration: neither
becomes a beat or part of one. The opening card will be B1's picture.

Refuses to write if any narration_text contains "Shinde", or if NARRATION.md does not hold
exactly 17 beats, B1 to B17, in order.

Re-run after audio generation: it keeps each beat's measured actual_duration_s and
audio_file, and B1's tts_phoneme_overrides (written by the Assignment 1 override), but only
while that beat's narration_text is unchanged. A beat whose text changed loses them and
needs new audio. Scene fields (act, lane, shot, qc, ...) are not written yet.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "job-search-agent-film"
TITLE = "WorthLoop"
VOICE = "am_onyx"
N_BEATS = 17
LABEL = re.compile(r"^(B\d+) — (.+)$")
KEEP = ("actual_duration_s", "audio_file", "tts_phoneme_overrides")

old = {}
if (HERE / "beat_sheet.json").exists() and (HERE / "beat_sheet.json").stat().st_size:
    old = {b["beat_id"]: b for b in json.loads((HERE / "beat_sheet.json").read_text(encoding="utf-8"))["beats"]}


def carry(b):
    """Keep measured audio from a previous run, only if the narration is unchanged."""
    o = old.get(b["beat_id"], {})
    if o.get("narration_text") == b["narration_text"]:
        for k in KEEP:
            if k in o:
                b[k] = o[k]
    elif any(k in o for k in KEEP):
        print(f"{b['beat_id']}: narration changed; its old audio is not carried over, so it needs new audio")
    return b


def words(text):
    return sum(1 for t in text.split() if re.search(r"[A-Za-z0-9]", t))


def est(text):
    return round(words(text) / 2.5, 1)


def refuse(msg):
    sys.exit(f"make_sheet.py: REFUSED, nothing written: {msg}")


beats = []
for line in (HERE / "NARRATION.md").read_text(encoding="utf-8").splitlines():
    m = LABEL.match(line)
    if m:
        bid, text = m.group(1), m.group(2).strip()
        beats.append(carry({"beat_id": bid, "narration_text": text,
                            "estimated_duration_s": est(text), "engine": "kokoro"}))

ids = [b["beat_id"] for b in beats]
if ids != [f"B{i}" for i in range(1, N_BEATS + 1)]:
    refuse(f"expected exactly {N_BEATS} beats, B1 to B{N_BEATS} in order; found {len(ids)}: {ids}")
for b in beats:
    if "shinde" in b["narration_text"].lower():
        refuse(f'{b["beat_id"]}: narration_text contains "Shinde"')

sheet = {"metadata": {
    "slug": SLUG,
    "title": TITLE,
    "voice_kokoro": VOICE,
    "engine": "kokoro",
    "source_doc": "NARRATION.md (this folder)",
}, "beats": beats}

(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
total_words = sum(words(b["narration_text"]) for b in beats)
measured = [b["actual_duration_s"] for b in beats if "actual_duration_s" in b]
print(f"{len(beats)} beats; {total_words} words; est {round(sum(b['estimated_duration_s'] for b in beats))} s "
      f"at 2.5 words/s; measured audio kept for {len(measured)} beat(s)")
