#!/usr/bin/env python3
"""pad_audio.py: silence padding for CueGate film 2, run once right after generate_audio_kokoro.py.

Why: the SKEPTIC's questions are one to three seconds long. Voiced back to back, the act cards and the
first SKEPTIC label would be gone before anyone could read them. So, by a fixed rule (below), some beats
get silence added to their narration mp3. The voice itself is never sped up, slowed down or cut.

  - act-card questions (I1, M1, V1 = B07, B12, B19): silence BEFORE the line, so the card holds to 3.0 s
  - the first SKEPTIC line (E2a = B02, which carries the on-screen SKEPTIC label): silence after, to 4.0 s
  - every other SKEPTIC line: at least 0.5 s of silence after it, and at least 2.6 s in all
  - the outro (BOUT): a 1.0 s silent tail (the show-tell house rule)
  - DEEPAK's other lines: no padding

For each padded beat the sheet records speech_s (the voice alone), pad_lead_s, pad_tail_s and the new
actual_duration_s, and mp3/timings.json gets the new duration. The scene pacing (say() in scenes_film.py)
and the captions (make_captions.py) use speech_s and pad_lead_s, so they stay on the spoken word.
Running it twice does nothing the second time (each padded file's sha256 is recorded).

Usage: python3 pad_audio.py            (in the reel folder)
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ACT_CARDS = {"B07", "B12", "B19"}
FIRST_SKEPTIC = "B02"
LEAD_TO, FIRST_TO, SKEPTIC_MIN, SKEPTIC_PAUSE, OUTRO_TAIL = 3.0, 4.0, 2.6, 0.5, 1.0


def pads(bid, speaker, speech):
    """(lead, tail) seconds of silence for one beat, from its speech length."""
    if bid == "BOUT":
        return 0.0, OUTRO_TAIL
    if speaker != "SKEPTIC":
        return 0.0, 0.0
    if bid in ACT_CARDS:
        return round(max(0.0, LEAD_TO - speech), 2), 0.0
    if bid == FIRST_SKEPTIC:
        return 0.0, round(max(SKEPTIC_PAUSE, FIRST_TO - speech), 2)
    return 0.0, round(max(SKEPTIC_PAUSE, SKEPTIC_MIN - speech), 2)


def probe(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)]))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sheet_p = HERE / "beat_sheet.json"
    sheet = json.loads(sheet_p.read_text())
    tp = HERE / "mp3" / "timings.json"
    timings = json.loads(tp.read_text()) if tp.exists() else {}
    for b in sheet["beats"]:
        bid = b["beat_id"]
        mp3 = HERE / "mp3" / f"beat-{bid}.mp3"
        if not mp3.exists():
            sys.exit(f"pad_audio.py: {mp3} is missing; run generate_audio_kokoro.py first")
        if b.get("padded_sha256") == sha(mp3):
            continue                                    # already padded, file unchanged
        speech = round(probe(mp3), 2)
        lead, tail = pads(bid, b.get("speaker"), speech)
        b["speech_s"], b["pad_lead_s"], b["pad_tail_s"] = speech, lead, tail
        if lead or tail:
            filt = []
            if lead:
                filt.append(f"adelay={int(round(lead * 1000))}:all=1")
            if tail:
                filt.append(f"apad=pad_dur={tail}")
            tmp = mp3.with_suffix(".padded.mp3")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-af", ",".join(filt),
                            "-c:a", "libmp3lame", "-q:a", "2", str(tmp)], check=True)
            tmp.replace(mp3)
        d = round(probe(mp3), 2)
        b["actual_duration_s"] = d
        b["padded_sha256"] = sha(mp3)
        timings[bid] = d
        print(f"pad_audio: {bid} {b.get('speaker')} speech {speech:.2f}s lead {lead:.2f}s tail {tail:.2f}s -> {d:.2f}s")
    sheet_p.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
    tp.write_text(json.dumps(timings, indent=2))
    tot = sum(b["actual_duration_s"] for b in sheet["beats"])
    print(f"pad_audio: timeline {tot:.2f}s ({int(tot // 60)}:{tot % 60:05.2f})")


if __name__ == "__main__":
    main()
