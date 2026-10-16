#!/usr/bin/env python3
"""make_srt.py: captions for the master, from the script itself (not from speech recognition).

The narration text in beat_sheet.json is exactly what Kokoro spoke, so the caption words are exact. Timing is
per beat from the measured audio (actual_duration_s, cumulative), split into sentence-sized cues by their share of
the beat's characters. BIDEA's 0.8 s lead silence is skipped. Writes exports/landscape/<slug>.srt.
"""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
sheet = json.loads((HERE / "beat_sheet.json").read_text())
slug = sheet["metadata"]["slug"]


def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def chunks(text, limit=84):
    """Sentences, and sentences longer than `limit` characters split at a comma or semicolon."""
    out = []
    for sent in re.split(r"(?<=[.?!])\s+", text.strip()):
        while len(sent) > limit:
            cut = max(sent.rfind(", ", 0, limit), sent.rfind("; ", 0, limit), sent.rfind(": ", 0, limit))
            if cut < 20:
                cut = sent.rfind(" ", 0, limit)
            out.append(sent[:cut + 1].strip()); sent = sent[cut + 1:].strip()
        if sent:
            out.append(sent)
    return out


cues, t0 = [], 0.0
for b in sheet["beats"]:
    dur = float(b["actual_duration_s"])
    lead = 0.8 if b["beat_id"] == "BIDEA" else 0.0
    tail = float(b.get("tail_silence_s") or 0.0)
    speech = max(0.5, dur - lead - tail)
    parts = chunks(b["narration_text"]); total = sum(len(p) for p in parts)
    t = t0 + lead
    for p in parts:
        d = speech * len(p) / total
        cues.append((t, t + d - 0.02, p)); t += d
    t0 += dur

out = HERE / "exports" / "landscape" / f"{slug}.srt"
out.write_text("\n".join(f"{i}\n{ts(a)} --> {ts(b)}\n{txt}\n" for i, (a, b, txt) in enumerate(cues, 1)))
print(f"{out.name}: {len(cues)} cues, ends {ts(cues[-1][1])}")
