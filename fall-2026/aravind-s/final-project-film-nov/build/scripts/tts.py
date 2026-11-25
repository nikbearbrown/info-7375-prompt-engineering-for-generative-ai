"""Narration: Kokoro (kokoro_onnx), voice am_onyx, speed 1.0, 24 kHz, one WAV per beat from beats.json's spoken text.
Run with $TTS_PY (a Python with kokoro_onnx and numpy). The voice model folder comes from the environment variable
KOKORO_MODELS: the folder that holds kokoro-v1.0.onnx and voices-v1.0.bin. See build/BUILD-NOTES.md.
With beat ids as arguments (tts.py B13 B15), only those beats."""
import json, os, sys, wave
from pathlib import Path
import numpy as np
from kokoro_onnx import Kokoro

FILM = Path(__file__).resolve().parents[2]
if not os.environ.get("KOKORO_MODELS"):
    raise SystemExit("Set KOKORO_MODELS to the folder with kokoro-v1.0.onnx and voices-v1.0.bin (build/BUILD-NOTES.md).")
MODELS = Path(os.environ["KOKORO_MODELS"]).expanduser()
for name in ("kokoro-v1.0.onnx", "voices-v1.0.bin"):
    if not (MODELS / name).is_file():
        raise SystemExit(f"KOKORO_MODELS has no {name}: {MODELS}")
OUT = FILM / "build" / "audio"; OUT.mkdir(parents=True, exist_ok=True)
only = set(sys.argv[1:])
k = Kokoro(str(MODELS / "kokoro-v1.0.onnx"), str(MODELS / "voices-v1.0.bin"))
durs = {}
for b in json.load(open(FILM / "beats.json")):
    if not b["spoken"] or (only and b["id"] not in only):
        continue
    samples, sr = k.create(b["spoken"], voice="am_onyx", speed=1.0, lang="en-us")
    pcm = (np.clip(samples, -1, 1) * 32767).astype("<i2")
    with wave.open(str(OUT / f"{b['id']}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())
    durs[b["id"]] = round(len(samples) / sr, 3)
    print(b["id"], durs[b["id"]], "s", flush=True)
prev = json.loads((OUT / "durations.json").read_text()) if (OUT / "durations.json").exists() else {}
prev.update(durs)
(OUT / "durations.json").write_text(json.dumps(prev, indent=1))
