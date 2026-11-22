#!/usr/bin/env python3
"""fix_pronunciation.py: re-voice three body beats so am_eric says three words right. No narration_text, caption or
on-screen word changes: only the text handed to the voice is respelled, the way name_voice.py voices the student's name.

What was wrong (faster-whisper small.en transcript of the first build, gate-reports/whisper-check.txt):
  B05 "Jobscan" was heard as "Jobskin"; B08 "Anthropic" as "and thropic"; B16 "an either-or rule" as "in either a rule".
Each respelling below was picked by voicing candidates in the full sentence and transcribing them with the same model
(gate-reports/whisper-check-pronunciation.txt has the result for the beats as built).

The toolkit's own lexicon (runtime/pronunciation/*.json, read by generate_audio_kokoro.py) lives inside the toolkit,
which this reel does not modify, so the override lives here. Run after generate_audio_kokoro.py and name_voice.py and
before finish_audio.py (build_audio.sh does this). Writes mp3/beat-<BID>.mp3 with generate_audio_kokoro.py's own
encoder and text normalisation, so these beats differ from the others only in the respelled word.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "brutalist.art"
sys.path.insert(0, str(KIT / "runtime" / "scripts"))
import generate_audio_kokoro as g  # noqa: E402  (the toolkit's voice engine: model paths, normaliser, mp3 writer)

SAY = {                      # beat: (word as written and captioned, what the voice reads)
    "B05": ("Jobscan", "Job-scan"),
    "B08": ("Anthropic", "Ann-throppick"),
    "B16": ("either-or", "either or"),
}

k = g.load_engine()
sheet = json.loads((HERE / "beat_sheet.json").read_text())
for b in sheet["beats"]:
    if b["beat_id"] not in SAY:
        continue
    word, say = SAY[b["beat_id"]]
    text = b["narration_text"]
    assert text.count(word) == 1, f"{b['beat_id']} narration changed; update fix_pronunciation.py: {word!r}"
    voice = b.get("voice") or g.default_voice(sheet)
    spoken = g.normalize_for_tts(text.replace(word, say), voice)
    samples, sr = k.create(spoken, voice=voice, speed=1.0, lang=g.lang_for(voice))
    out = HERE / (b.get("audio_file") or f"mp3/beat-{b['beat_id']}.mp3")
    g.write_mp3(samples, sr, out)
    print(f"[fix_pronunciation] {out.name}  {len(samples) / sr:.2f}s  {word!r} voiced as {say!r} "
          f"({k.tokenizer.phonemize(say, g.lang_for(voice))})")
