#!/usr/bin/env python3
"""tools/make_srt.py: builds subtitles from the real audio.

Transcribes each public/audio/<id>.wav with faster-whisper for word timings, but keeps the WORDS from the narration
script (src/narration/<id>.txt), so captions never show a mis-hearing. Writes:
  out/productlens-project-film.srt   (deliverable)
  src/config/subtitles.json          (cues the film can burn in when SHOW_SUBTITLES is on)
Run:  ~/brutalist.art/.venv/bin/python tools/make_srt.py
"""
import json, math, re
from pathlib import Path
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parents[1]
FPS = 30
scenes = json.loads((ROOT / "src/config/scenes.json").read_text())
dur = json.loads((ROOT / "src/config/durations.json").read_text())
model = WhisperModel("small.en", compute_type="int8")


def frames(s):
    return math.ceil((dur.get(s["id"], s["fallbackSeconds"]) + s.get("padSeconds", 0.6)) * FPS)


def chunks(words, max_chars=64):
    """Group script words into caption lines of at most ~64 characters, breaking after punctuation when possible."""
    out, cur = [], []
    for w in words:
        if cur and (len(" ".join(cur + [w])) > max_chars):
            out.append(cur); cur = []
        cur.append(w)
        if re.search(r"[.?!;:]$", w) and len(" ".join(cur)) > 28:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


cues, t0 = [], 0.0
for s in scenes:
    wav, txt = ROOT / f"public/audio/{s['id']}.wav", ROOT / f"src/narration/{s['id']}.txt"
    if wav.exists() and txt.exists():
        script_words = txt.read_text().split()
        segs, _ = model.transcribe(str(wav), word_timestamps=True)
        heard = [w for seg in segs for w in seg.words]
        lines = chunks(script_words)
        # map script lines onto heard-word timings proportionally by word index
        n_s, n_h, i = len(script_words), max(1, len(heard)), 0
        for line in lines:
            a, b = i, i + len(line) - 1
            ha, hb = min(n_h - 1, round(a * n_h / n_s)), min(n_h - 1, round(b * n_h / n_s))
            start = heard[ha].start if heard else a / n_s * dur[s["id"]]
            end = heard[hb].end if heard else (b + 1) / n_s * dur[s["id"]]
            cues.append({"start": round(t0 + start, 3), "end": round(t0 + max(end, start + 0.8), 3), "text": " ".join(line)})
            i = b + 1
    t0 += frames(s) / FPS

for c, nxt in zip(cues, cues[1:]):
    c["end"] = min(c["end"], nxt["start"] - 0.05)


def ts(x):
    h, m = divmod(int(x), 3600); m, sec = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{sec:02d},{int(round((x - int(x)) * 1000)):03d}"


(ROOT / "out").mkdir(exist_ok=True)
(ROOT / "out/productlens-project-film.srt").write_text(
    "\n".join(f"{n}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n" for n, c in enumerate(cues, 1)))
(ROOT / "src/config/subtitles.json").write_text(json.dumps(cues, indent=1) + "\n")
print(f"{len(cues)} cues over {t0:.1f}s")
