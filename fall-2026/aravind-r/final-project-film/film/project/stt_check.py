#!/usr/bin/env python3
"""stt_check.py — speech-to-text on the full delivered film, compared with the script (one diff over the whole film).

Usage: python3 stt_check.py <film.mp4>   → writes gates/stt-full-master.txt and prints it.

faster-whisper (small.en, int8, CPU) transcribes the film's soundtrack with word timestamps. Each heard word is put
in the beat whose span contains its midpoint (spans from beat_sheet.json render_duration_s). The script per beat is the
Kokoro input (narration_text) with the spoken spelling "Reed-back" read as Readback. Both sides are normalised only
for formatting, not wording: lowercase, punctuation and hyphens dropped, numbers written as words ("86" = "eighty
six", "14th" = "fourteenth", ".6" = "point six"), word spacing and spelling ignored (Spec Kit = Speckit, re-measure = remeasure, co-pilot = copilot, behavior = behaviour),
and the spellings Readback / read back / Reed-back treated as one word. Every remaining difference is listed with the
script line and the heard line. Each beat that differs also has its own narration clip (audio_file) transcribed alone
with the same model, which shows whether the difference is in the clip or comes from transcribing the film in one pass.
"""
import difflib
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
film = sys.argv[1]
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen " \
       "seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
ORD = {"first": "1st", "fourteenth": "14th"}


def num_words(n):
    n = int(n)
    if n < 20:
        return ONES[n]
    t, o = divmod(n, 10)
    return TENS[t] + ("" if o == 0 else " " + ONES[o])


def norm(text):
    t = text.lower().replace("’", "'")
    t = re.sub(r"\b(reed-back|reed back|readback|read back|reedback)\b", "readback", t)
    t = t.replace("ork.ai", "ork dot ai").replace("speckit", "spec kit")
    t = re.sub(r"\bbehavior\b", "behaviour", t)                       # en-US spelling from the model
    t = re.sub(r"\bco[- ]pilot\b", "copilot", t)
    t = re.sub(r"(?<![\d.])\.(\d)", r"point \1", t)               # .6 → point 6
    t = re.sub(r"\b0\.(\d)\b", r"point \1", t)
    t = re.sub(r"\b14th\b", "fourteenth", t)
    t = re.sub(r"\b(\d{1,2})\b", lambda m: num_words(m.group(1)), t)
    t = re.sub(r"\bremeasure\b", "re measure", t)
    t = re.sub(r"[-–—]", " ", t)
    t = re.sub(r"[^a-z' ]", " ", t)
    return [w.strip("'") for w in t.split() if w.strip("'")]


beats = json.load(open(os.path.join(HERE, "beat_sheet.json")))["beats"]
spans, t = [], 0.0
for b in beats:
    d = float(b.get("render_duration_s") or b["actual_duration_s"])
    spans.append((b["beat_id"], t, t + d, b["narration_text"]))
    t += d

wav = os.path.join(tempfile.mkdtemp(prefix="stt-"), "film.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", film, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
from faster_whisper import WhisperModel  # noqa: E402
model = WhisperModel("small.en", device="cpu", compute_type="int8")
segs, _ = model.transcribe(wav, language="en", word_timestamps=True)
words = [((w.start + w.end) / 2, w.word) for s in segs for w in s.words]   # a word belongs to the beat holding its midpoint

out = [f"Speech-to-text on the full film ({os.path.basename(film)}), faster-whisper small.en, compared with the script.",
       "One diff over the whole film (so a word that straddles a cut is not counted twice), each difference mapped to the",
       "beat its script words belong to. Formatting is normalised (numbers, hyphens, punctuation, quote marks, word",
       "spacing and spelling (Spec Kit / Speckit, re-measure / remeasure, co-pilot / copilot, behavior / behaviour), and the",
       "spoken spellings Reed-back and Ork dot AI); every remaining wording difference is listed. Every beat's own clip is also",
       "transcribed alone with the same model, so a word the voice says unclearly shows up even where the full film is heard right.", ""]
clip = {b["beat_id"]: b.get("audio_file") for b in beats}
persist = 0
sw, sbeat = [], []
for bid, a, z, script in spans:
    toks = norm(script)
    sw += toks
    sbeat += [bid] * len(toks)
heard_all = "".join(w for _, w in words).strip()
hw = norm(heard_all)
diffs = {}
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, sw, hw, autojunk=False).get_opcodes():
    if tag == "equal":
        continue
    bid = sbeat[min(i1, len(sbeat) - 1)]
    diffs.setdefault(bid, []).append(f"{tag}: script “{' '.join(sw[i1:i2])}” → heard “{' '.join(hw[j1:j2])}”")
alone_only = 0
for bid, a, z, script in spans:
    f = clip.get(bid)
    alone, ops = None, []
    if f and os.path.exists(os.path.join(HERE, f)):
        alone = " ".join(x.text.strip() for x in model.transcribe(os.path.join(HERE, f), language="en")[0])
        ops = [o for o in difflib.SequenceMatcher(None, norm(script), norm(alone), autojunk=False).get_opcodes() if o[0] != "equal"]
    if bid not in diffs:
        if not ops:
            out.append(f"{bid}  matches the script (full film and its own clip)")
            continue
        alone_only += 1
        sa, ha = norm(script), norm(alone)
        out.append(f"{bid}  matches in the full film; its own clip alone differs ({f}): {alone}")
        out.append("   → on its own clip: " + "; ".join(f"script “{' '.join(sa[i1:i2])}” → heard “{' '.join(ha[j1:j2])}”" for _, i1, i2, j1, j2 in ops))
        continue
    heard = "".join(w for m, w in words if a <= m < z).strip()
    out.append(f"{bid}  DIFFERS")
    out.append(f"   script: {script.replace('Reed-back', 'Readback')}")
    out.append(f"   heard:  {heard}")
    out += [f"   - {d}" for d in diffs[bid]]
    if alone is not None:
        sa, ha = norm(script), norm(alone)
        persist += bool(ops)
        out.append(f"   own clip alone ({f}): {alone}")
        out.append("   → on its own clip: " + ("matches the script" if not ops else "; ".join(
            f"script “{' '.join(sa[i1:i2])}” → heard “{' '.join(ha[j1:j2])}”" for _, i1, i2, j1, j2 in ops)))
out += ["", f"{len(diffs)} of {len(spans)} beats differ from the script after normalisation; {len(sw)} script words, {len(hw)} heard words.",
        f"{persist} of {len(diffs)} differing beats also differ when their own clip is transcribed alone; "
        f"{alone_only} more beat(s) match in the full film but differ on their own clip."]
text = "\n".join(out) + "\n"
open(os.path.join(HERE, "gates", "stt-full-master.txt"), "w").write(text)
print(text)
