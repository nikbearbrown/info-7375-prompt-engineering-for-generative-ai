#!/usr/bin/env python3
"""name_voice.py: re-voice BIDEA and BOUT so am_eric says my name the way I pronounce it.

Kokoro's English phonemizer says "Suketh Produtoor" wrongly. I gave the pronunciation in Devanagari,
सुकेत रेड्डी फ्रंदटूर. espeak's Hindi G2P (inside kokoro-onnx) turns that into phonemes, and am_eric speaks
them, with the rest of each line phonemized in English as usual. I approved this rendering by ear on 2026-10-14
("A-intro-am_eric-from-your-guide.mp3"). narration_text and the captions keep the English spelling.

Run after generate_audio_kokoro.py and before finish_audio.py (build_audio.sh does this). Writes the raw
mp3/beat-BIDEA.mp3 and mp3/beat-BOUT.mp3; finish_audio.py then pads them.
"""
import json, subprocess, sys, tempfile
from pathlib import Path
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).resolve().parent
KIT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "brutalist.art"
GUIDE = "सुकेत रेड्डी फ्रंदटूर"            # my pronunciation guide: Suketh Reddy Produtoor

k = Kokoro(str(KIT / "runtime/models/kokoro/kokoro-v1.0.onnx"), str(KIT / "runtime/models/kokoro/voices-v1.0.bin"))
en = lambda t: k.tokenizer.phonemize(t, lang="en-us")
first, reddy, last = k.tokenizer.phonemize(GUIDE, lang="hi").split()

sheet = json.loads((HERE / "beat_sheet.json").read_text())
narr = {b["beat_id"]: b["narration_text"] for b in sheet["beats"]}
lines = {
    "BIDEA": ("Hi, I'm Suketh Produtoor. ", lambda rest: en("Hi, I'm") + f" {first} {last}. " + en(rest)),
    "BOUT": ("Fine Print. Suketh Reddy Produtoor.", lambda rest: en("Fine Print.") + f" {first} {reddy} {last}."),
}
for bid, (head, build) in lines.items():
    text = narr[bid]
    assert text.startswith(head) or text == head, f"{bid} narration changed; update name_voice.py: {text[:60]!r}"
    phonemes = build(text[len(head):].strip())
    samples, sr = k.create(phonemes, voice="am_eric", is_phonemes=True)
    with tempfile.NamedTemporaryFile(suffix=".wav") as w:
        sf.write(w.name, samples, sr)
        out = HERE / "mp3" / f"beat-{bid}.mp3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", w.name, "-b:a", "192k", str(out)], check=True)
    print(f"[name_voice] {out.name}  {len(samples) / sr:.2f}s  phonemes: {phonemes[:70]}…")
