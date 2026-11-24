#!/usr/bin/env python3
"""voice_with_pauses.py — voice every beat of this film with real pauses at sentence and clause ends.

Why: Kokoro barely pauses at a full stop, colon or dash, so the beats run together. kokoro-onnx
0.6.1 has sentence_pause / clause_pause, but it can only place them with per-phoneme timings,
and kokoro-v1.0.onnx outputs audio only; without timings it pauses only between 510-phoneme
batches, and no beat in this film is that long. The toolkit itself has no pause inside a beat
(only whole-beat silence, build_safety.intentional_silence, and compile.py's end padding).

So for each beat in beat_sheet.json this script:
  - splits the narration after sentence ends (. ? !) and after colons, semicolons and em
    dashes, keeping the punctuation with each piece;
  - voices each piece on its own, at speed 1.0, in the sheet's voice (am_onyx);
  - cuts each piece's leading and trailing near-silence at 35 dB below the piece's peak,
    but keeps a quiet s, z, f or t release at either edge, then 30 ms more (see tighten());
  - joins the pieces with exact silence: SENTENCE_GAP_S after . ? ! and CLAUSE_GAP_S after
    : ; — (nothing after the last piece);
  - writes mp3/beat-<id>.mp3, sets actual_duration_s and audio_file, writes the pieces' text,
    start_s and end_s into the beat's "pieces", and rewrites mp3/timings.json.

The setting is A: 0.30 s after a sentence, 0.15 s after a clause. (Setting B, tested and not
chosen, was 0.45 s and 0.25 s.)

"Prasad": the phoneme swap (espeak-ng's pɹˈæsæd → pɹəsˈɑːd, "pruh-SAAD") is copied from
week-01-video/tools/kokoro_phoneme_override.py, the Assignment 1 override, unchanged. A piece
that says "Prasad" is phonemized exactly as the toolkit would, swapped, and voiced with
is_phonemes=True; the beat records tts_phoneme_overrides the way that script did. It refuses
if the word count and the espeak matches disagree.

Everything else is the toolkit's own code, the functions the Assignment 1 override imports:
normalize_for_tts, lang_for, load_engine, write_mp3 (mono, Kokoro's 24 kHz, libmp3lame -q:a 2),
measure, plus build_safety's validate_project, validate_approvals, default_voice,
writable_path and atomic_json. It edits nothing in the toolkit.

make_sheet.py gives every beat engine "kokoro-paused", so the toolkit's
generate_audio_kokoro.py skips these beats (it voices only engine "kokoro"); this script
voices only "kokoro-paused" beats and refuses any other. make_sheet.py keeps actual_duration_s,
audio_file, tts_phoneme_overrides and pieces on a re-run, while a beat's narration is unchanged.

Usage (toolkit .venv first on PATH):
    python3 tools/voice_with_pauses.py .               # every beat
    python3 tools/voice_with_pauses.py . --only B3     # one beat; other timings kept
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

import numpy as np

ART_HOME = Path(os.environ.get("ART_HOME") or Path(__file__).resolve().parents[5] / "brutalist.art")
sys.path.insert(0, str(ART_HOME / "runtime" / "scripts"))

from build_safety import (atomic_json, default_voice, validate_approvals,  # noqa: E402
                          validate_project, writable_path)
from generate_audio_kokoro import (lang_for, load_engine, measure,  # noqa: E402
                                   normalize_for_tts, write_mp3)

ENGINE = "kokoro-paused"
SENTENCE_GAP_S = 0.30          # setting A
CLAUSE_GAP_S = 0.15            # setting A
SENTENCE_ENDS = ".?!"
CLAUSE_ENDS = ":;—"
SPLIT = re.compile(r"(?<=[.?!:;—])\s+")
# Copied from week-01-video/tools/kokoro_phoneme_override.py (OVERRIDES["Prasad"]), unchanged:
# espeak-ng output (en-us)  ->  intended pronunciation
PRASAD = ("pɹˈæsæd", "pɹəsˈɑːd")     # pruh-SAAD


def pieces_of(text):
    """The narration split after . ? ! : ; and em dashes, each piece keeping its punctuation."""
    return [p for p in SPLIT.split(text.strip()) if p]


def gap_after(piece):
    end = piece.rstrip()[-1:]
    return SENTENCE_GAP_S if end in SENTENCE_ENDS else CLAUSE_GAP_S if end in CLAUSE_ENDS else 0.0


def _walk(hiss, edge, step, gap, limit):
    """The farthest hiss frame reached from frame `edge` going `step` (-1 or +1), allowing at
    most `gap` other frames between hiss frames and going at most `limit` frames."""
    best, other, j = edge, 0, edge + step
    while 0 <= j < len(hiss) and abs(j - edge) <= limit:
        if hiss[j]:
            best, other = j, 0
        else:
            other += 1
            if other > gap:
                break
        j += step
    return best


def tighten(samples, sr, db=-35.0, keep=0.03, frame=0.01, floor=-50.0, treble=0.4, gap=5, window=0.25):
    """Cut the piece's leading and trailing near-silence, keeping a quiet s, z, f or t release.

    kokoro-onnx trims with librosa's default (60 dB below peak), which leaves the model's
    low-level tail, measured at 35-50 dB below the speech peak for 0.3-0.7 s, with almost none
    of its energy above 3 kHz. Most of a word's last sound sits higher (the "s" of "fits" and
    "payments", 26-36 dB below). So the piece is first cut to its frames (10 ms) louder than
    `db` below its loudest frame.

    But a final s or z can sit just under that line: "applications" (B3), "postings" (B13)
    and "less" (B15) ended 35-41 dB below their peaks, and a 35 dB cut kept 10-20 ms of their
    80-120 ms sibilant. So from each loud edge the trim keeps walking outward through "hiss"
    frames, louder than `floor` dB and with at least `treble` of their energy above 3 kHz,
    allowing up to `gap` other frames between them (the dip before the "s" of "less", the
    closure before the "t" of "next"), for at most `window` seconds. It then keeps `keep`
    seconds beyond whichever edge it reached. The hum fails the treble test, so the gaps stay
    close to the gaps asked for.
    """
    n = max(1, int(frame * sr))
    usable = len(samples) // n * n
    frames = samples[:usable].reshape(-1, n)
    rms = np.sqrt((frames ** 2).mean(1))
    ref = rms.max()
    loud = np.nonzero(rms > ref * 10 ** (db / 20))[0]
    if not len(loud):
        return samples
    power = np.abs(np.fft.rfft(frames * np.hanning(n), axis=1)) ** 2
    high = power[:, np.fft.rfftfreq(n, 1 / sr) > 3000].sum(1) / np.maximum(power.sum(1), 1e-20)
    hiss = (rms > ref * 10 ** (floor / 20)) & (high >= treble)
    limit = int(round(window / frame))
    first = _walk(hiss, loud[0], -1, gap, limit)
    last = _walk(hiss, loud[-1], +1, gap, limit)
    pad = int(keep * sr)
    return samples[max(0, first * n - pad): min(len(samples), (last + 1) * n + pad)]


def voice_piece(k, piece, voice, bid):
    """Samples for one piece at speed 1.0, the Prasad swap applied when the piece says it.

    Returns (samples, sr, swaps), where swaps is how many "Prasad" were swapped."""
    lang = lang_for(voice)
    text = normalize_for_tts(piece)
    n_text = text.count("Prasad")
    if not n_text:
        samples, sr = k.create(text, voice=voice, speed=1.0, lang=lang)
        return tighten(samples, sr), sr, 0
    phonemes = k.tokenizer.phonemize(text, lang)
    n_ph = phonemes.count(PRASAD[0])
    if n_text != n_ph:
        sys.exit(f"[pauses] {bid}: 'Prasad': {n_text} in text but {n_ph} espeak matches "
                 f"({PRASAD[0]!r}) — refusing to guess")
    samples, sr = k.create(phonemes.replace(*PRASAD), voice=voice, speed=1.0, lang=lang, is_phonemes=True)
    return tighten(samples, sr), sr, n_text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reel", type=Path)
    ap.add_argument("--only", nargs="+", help="beat ids to voice (default: every beat)")
    a = ap.parse_args()

    folder = a.reel.resolve()
    sheet_path = folder / "beat_sheet.json"
    sheet = json.loads(sheet_path.read_text(encoding="utf-8"))
    validate_project(sheet)
    validate_approvals(folder, sheet)
    selected_voice = default_voice(sheet)

    beats = [b for b in sheet["beats"] if a.only is None or b["beat_id"] in a.only]
    if a.only and sorted(b["beat_id"] for b in beats) != sorted(set(a.only)):
        sys.exit(f"[pauses] --only names a beat that is not in the sheet: {a.only}")
    wrong = [b["beat_id"] for b in beats if b.get("engine") != ENGINE]
    if wrong:
        sys.exit(f"[pauses] REFUSED: engine is not {ENGINE!r} on {wrong}; re-run make_sheet.py")

    timings_path = writable_path(folder, "mp3/timings.json")
    timings_path.parent.mkdir(exist_ok=True)
    timings = {}
    if a.only and timings_path.exists():
        timings = json.loads(timings_path.read_text(encoding="utf-8"))

    k = load_engine()
    for b in beats:
        bid = b["beat_id"]
        voice = b.get("voice") or selected_voice
        pieces = pieces_of(b["narration_text"])
        parts, record, t, sr, swaps = [], [], 0.0, None, 0
        for i, piece in enumerate(pieces):
            samples, sr, n = voice_piece(k, piece, voice, bid)
            swaps += n
            gap = gap_after(piece) if i < len(pieces) - 1 else 0.0
            dur = len(samples) / sr
            record.append({"text": piece, "start_s": round(t, 3), "end_s": round(t + dur, 3)})
            parts += [samples, np.zeros(int(round(gap * sr)), dtype=samples.dtype)]
            t += dur + gap
        out = writable_path(folder, f"mp3/beat-{bid}.mp3")
        write_mp3(np.concatenate(parts), sr, out)
        dur = measure(out)
        b["audio_file"] = f"mp3/beat-{bid}.mp3"
        b["actual_duration_s"] = round(dur, 2)
        b["pieces"] = record
        if swaps:
            b["tts_phoneme_overrides"] = {"Prasad": {"count": swaps, "from": PRASAD[0], "to": PRASAD[1]}}
        else:
            b.pop("tts_phoneme_overrides", None)
        timings[bid] = round(dur, 2)
        print(f"[pauses] beat-{bid}.mp3  {dur:.2f}s  voice={voice}  {len(pieces)} pieces"
              + (f"  Prasad swapped x{swaps}" if swaps else ""))

    atomic_json(sheet_path, sheet)
    atomic_json(timings_path, dict(sorted(timings.items(), key=lambda kv: int(kv[0][1:]))))
    print(f"[pauses] {len(beats)} beat(s) voiced · sentence gap {SENTENCE_GAP_S} s · clause gap {CLAUSE_GAP_S} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
