# BUILD-PROMPT: rebuild this video

Everything below is free and local. It makes no paid services, API calls,
uploads, or publishing.

## 0. One-time environment (macOS, as built on 2026-09-26)

```bash
brew install node ffmpeg cairo pkgconf pango
git clone https://github.com/nikbearbrown/brutalist.art.git
cd brutalist.art && git checkout cd4bf20
python3.12 -m venv .venv && source .venv/bin/activate
./setup --install
```

- **Versions used:** Node 26.10.0, FFmpeg 9.0.2, Python 3.12.14, Manim 0.18.1, kokoro-onnx, and faster-whisper 1.2.1.
- **Why the extra Homebrew packages:** `cairo`, `pkgconf`, and `pango` let pip build `pycairo` and `manimpango`, which have no prebuilt wheel for this setup.
- **Known toolkit issue:** after installing everything, `./setup` can exit before printing its readiness table. Its ElevenLabs guard matches example files inside the toolkit's own `youtube/` folder. To confirm readiness by hand, import `manim`, `kokoro_onnx`, `faster_whisper`, and `PIL`, then run `python3 runtime/scripts/setup_smoke_kokoro.py`.

## 1. Evidence (from the course repository root)

```bash
python3 fall-2026/aravind-s/week-01-video/evidence/softmax_steps.py
```

The output must match `evidence/softmax_steps_output.txt`. Every number in
`scenes.py` is copied from it.

## 2. Audio first (from the toolkit root, venv active)

Copy the folder to a scratch location first, so build files stay out of git:

```bash
cp -R <course-repo>/fall-2026/aravind-s/week-01-video /tmp/week-01-video
python3 runtime/scripts/generate_audio_kokoro.py /tmp/week-01-video
python3 runtime/scripts/align.py /tmp/week-01-video
```

The narration durations become the clock. `scenes.py` reads
`mp3/words.json`, so each value appears when it is spoken.

## 3. Review cut

```bash
./art run /tmp/week-01-video --height 1080
```

This renders the nine Manim scenes at 4K and compiles a 1080p review cut. It
runs the toolkit's gates:

- L: beat mix
- A: static pre-flight
- W: contrast and margins
- B: layout audit, strict
- V: frame check

## 4. Final

```bash
./art final /tmp/week-01-video --height 1080 --out /tmp/week-01-video/final
```

This writes the master mp4 and a `.verified.json` receipt with its SHA-256 hash.

## Paste-ready Claude Code prompt

```text
Rebuild the INFO 7375 Week 1 explainer video in /tmp/week-01-video with the
brutalist.art checkout at <toolkit path> (commit cd4bf20), its .venv active.
Do not change the narration in beat_sheet.json or the numbers in scenes.py.
1. Run evidence/softmax_steps.py from the course repo and confirm it matches
   evidence/softmax_steps_output.txt.
2. Generate the Kokoro audio (am_onyx) and align the words.
3. Run ./art run /tmp/week-01-video --height 1080. Stop and report if any gate fails.
4. Sample frames at 15/50/85% of each beat, look at them, and report defects.
5. Run ./art final /tmp/week-01-video --height 1080 --out /tmp/week-01-video/final
   and report the receipt's SHA-256.
No paid services, no direct API calls, no publishing.
```

## The prompts that produced the video

PROMPTS.md has the original request and the per-beat visual prompts.
SOURCES.md records who did what.
