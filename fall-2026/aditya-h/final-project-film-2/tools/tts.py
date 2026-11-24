#!/usr/bin/env python3
"""tools/tts.py: voices every src/narration/<id>.txt into public/audio/<id>.wav with a local Kokoro voice,
then measures each file and writes src/config/durations.json (seconds), so scene lengths follow the real audio.

Free and local: Kokoro-82M (Apache-2.0) via kokoro-onnx, using the model files already in ~/brutalist.art.
Run with the toolkit's Python:  ~/brutalist.art/.venv/bin/python tools/tts.py [scene_id ...]
To use recorded narration instead: drop <id>.wav files into public/audio/ and run  tools/tts.py --measure-only
"""
import json, re, sys, wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NARR, AUDIO, DUR = ROOT / "src/narration", ROOT / "public/audio", ROOT / "src/config/durations.json"
VOICE, SPEED = "am_michael", 1.08
# voice-only respellings (on-screen text and narration files keep the real spelling)
SAY = {r"\bHasija\b": "Ha-see-jah", r"\bA/B\b": "A B", r"\bProductLens\b": "Product Lens", r"\bProductboard\b": "Product board"}


def speakable(t: str) -> str:
    for pat, rep in SAY.items():
        t = re.sub(pat, rep, t)
    return t


def measure(p: Path) -> float:
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def main(argv):
    AUDIO.mkdir(parents=True, exist_ok=True)
    only = [a for a in argv if not a.startswith("--")]
    if "--measure-only" not in argv:
        from kokoro_onnx import Kokoro
        base = Path.home() / "brutalist.art/runtime/models/kokoro"
        k = Kokoro(str(base / "kokoro-v1.0.onnx"), str(base / "voices-v1.0.bin"))
        for f in sorted(NARR.glob("*.txt")):
            if only and f.stem not in only:
                continue
            a, sr = k.create(speakable(f.read_text().strip()), voice=VOICE, speed=SPEED, lang="en-us")
            pcm = (np.clip(a, -1, 1) * 32767).astype("<i2")
            with wave.open(str(AUDIO / f"{f.stem}.wav"), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())
            print(f"voiced {f.stem}")
    d = {p.stem: round(measure(p), 3) for p in sorted(AUDIO.glob("*.wav"))}
    DUR.write_text(json.dumps(d, indent=2) + "\n")
    print(f"{len(d)} files, total {sum(d.values()):.1f}s -> {DUR.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
