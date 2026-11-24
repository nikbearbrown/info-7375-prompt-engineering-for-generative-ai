#!/usr/bin/env python3
"""sentence_audio.py — per-sentence Kokoro narration with a fixed pause.

Reel-local tool for agent-proving-ground-progress (copied from the October
pitch's sentence_audio.py; not part of the shared toolkit).
Same engine, voice, text normalisation and output contract as
runtime/scripts/generate_audio_kokoro.py, but each beat is voiced one
sentence at a time and the sentences are joined with exactly PAUSE_S of
silence (ffmpeg concat).

Silence handling:
  - Kokoro's own trailing silence varies per sentence (0.03-0.58 s measured),
    so the edges BETWEEN sentences are trimmed to a 40 ms margin before the
    pause goes in; otherwise the "pause" would vary by half a second.
  - The beat's first lead-in and last tail are left exactly as Kokoro made
    them: no silence is added at the start or end of a beat, except
    TAIL_PAD_S (B13 only, so the repo URL holds on screen).

Writes per beat: mp3/beat-<ID>.mp3, actual_duration_s, audio_file, and
`sentences`: [{text, start_s, end_s}] — speech onset/offset of each sentence
on the beat's own clock (first/last sample above -45 dBFS). Also updates
mp3/timings.json. narration_text is never modified.

Usage:  python3 sentence_audio.py [--only B04 B13]
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

REEL = Path(__file__).resolve().parent
ART_HOME = REEL.parents[2]
sys.path.insert(0, str(ART_HOME / "runtime" / "scripts"))
import generate_audio_kokoro as kok                                   # noqa: E402
from build_safety import atomic_json, validate_project, writable_path  # noqa: E402

PAUSE_S = 0.25
MARGIN_S = 0.04
# B13: 1.5 s so the repo URL holds on screen. B12: 0.04 s so the timeline is 5,646 frames
# (235.250 s). At 5,645 frames (235.2083 s) the toolkit's final cut, "-t" written to three
# decimals (235.208), dropped the last video frame and render-integrity gate 11 failed.
TAIL_PAD_S = {"B13": 1.5, "B12": 0.04}
THRESH = 10 ** (-45 / 20)
# Voice-only respellings: what Kokoro is given, never narration_text or the
# screen. Each was whisper-checked (see _qc/gates/whisper_check.txt).
SAY = {
    r"\bE2B\b": "E-2-B",
    r"\bINFO 7375\b": "info seventy-three seventy-five",
    r"github\.com/tushar-patel28/agent-proving-ground":
        "github dot com, slash tushar-patel twenty-eight, slash agent-proving-ground",
}


def spoken(sentence):
    for pat, say in SAY.items():
        sentence = re.sub(pat, say, sentence)
    return kok.normalize_for_tts(sentence)


def sentences_of(text):
    parts = [p for p in re.split(r"(?<=[.?!])\s+", text.strip()) if p]
    assert " ".join(parts) == " ".join(text.split()), "split lost text"
    return parts


def write_wav(path, samples, sr):
    ints = np.clip(np.asarray(samples) * 32767, -32768, 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(ints.tobytes())


def silence_wav(path, seconds, sr):
    subprocess.run([kok.FFMPEG, "-y", "-v", "error", "-f", "lavfi", "-i",
                    f"anullsrc=r={sr}:cl=mono", "-t", f"{seconds}", "-c:a", "pcm_s16le",
                    str(path)], check=True)


def voice_beat(k, bid, text, voice, out_mp3):
    lang = kok.lang_for(voice)
    parts = sentences_of(text)
    segs, sr = [], None
    for i, s in enumerate(parts):
        x, sr = k.create(spoken(s), voice=voice, speed=1.0, lang=lang)
        x = np.asarray(x, dtype=np.float32)
        loud = np.where(np.abs(x) > THRESH)[0]
        m = int(MARGIN_S * sr)
        a = max(0, loud[0] - m) if i > 0 else 0                    # keep beat lead-in
        b = min(len(x), loud[-1] + 1 + m) if i < len(parts) - 1 else len(x)  # keep tail
        seg = x[a:b]
        on = (loud[0] - a) / sr
        off = (loud[-1] + 1 - a) / sr
        segs.append((s, seg, on, off))

    timeline, t, pieces = [], 0.0, []
    with tempfile.TemporaryDirectory(prefix=".sent-", dir=out_mp3.parent) as tmp:
        tmp = Path(tmp)
        gap = tmp / "gap.wav"
        silence_wav(gap, PAUSE_S, sr)
        gap_s = wave.open(str(gap)).getnframes() / sr
        for i, (s, seg, on, off) in enumerate(segs):
            p = tmp / f"s{i:02d}.wav"
            write_wav(p, seg, sr)
            pieces.append(p)
            timeline.append({"text": s, "start_s": round(t + on, 3), "end_s": round(t + off, 3)})
            t += len(seg) / sr
            if i < len(segs) - 1:
                pieces.append(gap)
                t += gap_s
        if bid in TAIL_PAD_S:
            pad = tmp / "tail.wav"
            silence_wav(pad, TAIL_PAD_S[bid], sr)
            pieces.append(pad)
        listing = tmp / "list.txt"
        listing.write_text("".join(f"file '{p}'\n" for p in pieces))
        enc = tmp / "beat.mp3"
        subprocess.run([kok.FFMPEG, "-y", "-v", "error", "-f", "concat", "-safe", "0",
                        "-i", str(listing), "-c:a", "libmp3lame", "-q:a", "2", str(enc)],
                       check=True)
        os.replace(enc, out_mp3)
    return timeline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=None)
    a = ap.parse_args()

    sheet_path = writable_path(REEL, "beat_sheet.json")
    sheet = json.loads(sheet_path.read_text())
    validate_project(sheet)
    before = {b["beat_id"]: b["narration_text"] for b in sheet["beats"]}
    default = kok.default_voice(sheet)
    k = kok.load_engine()

    timings_path = writable_path(REEL, "mp3/timings.json")
    timings = json.loads(timings_path.read_text()) if timings_path.exists() else {}
    for b in sheet["beats"]:
        bid = b["beat_id"]
        if a.only is not None and bid not in a.only:
            continue
        voice = b.get("voice") or default
        out = writable_path(REEL, f"mp3/beat-{bid}.mp3")
        b["sentences"] = voice_beat(k, bid, b["narration_text"], voice, out)
        dur = kok.measure(out)
        b["audio_file"] = f"mp3/beat-{bid}.mp3"
        b["actual_duration_s"] = round(dur, 2)
        b["sentence_pause_s"] = PAUSE_S
        if bid in TAIL_PAD_S:
            b["tail_silence_s"] = TAIL_PAD_S[bid]
        timings[bid] = round(dur, 2)
        print(f"[sentences] {bid} {dur:6.2f}s  {len(b['sentences'])} sentence(s)  "
              f"starts {[s['start_s'] for s in b['sentences']]}")

    assert {b["beat_id"]: b["narration_text"] for b in sheet["beats"]} == before
    atomic_json(sheet_path, sheet)
    atomic_json(timings_path, timings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
