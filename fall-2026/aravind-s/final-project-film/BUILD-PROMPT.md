# BUILD-PROMPT: rebuild this film

Everything below is free and local: no paid services, no API keys, no uploads, no publishing.

## 0. One-time environment (macOS, as built on 2026-10-09)

```bash
brew install node ffmpeg cairo pkgconf pango
git clone https://github.com/nikbearbrown/brutalist.art.git
cd brutalist.art && git checkout 22264a3
python3.12 -m venv .venv && source .venv/bin/activate
./setup --install
```

- Versions used: Python 3.12.14, Manim Community 0.18.1, kokoro-onnx with the v1.0 model files, faster-whisper, Node and the toolkit's Remotion install.
- Known toolkit issue: `./setup` can stop before its readiness table because its ElevenLabs guard matches example files in the toolkit's own `youtube/` folder. To confirm readiness by hand, import `manim`, `kokoro_onnx`, `faster_whisper` and `PIL`, then run `python3 runtime/scripts/setup_smoke_kokoro.py`.

## 1. The evidence (from the Klaxon repo root)

```bash
python3.12 -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/python -m klaxon.demo duplicate-webhook --handler naive
.venv/bin/python -m klaxon.demo duplicate-webhook --handler idempotent
```

The naive run must print `RESULT: money check FAILED (dashboard GREEN, ledger balanced, money off by +$69.68)` and the idempotent run `RESULT: money check PASSED`. The run is seeded, so these numbers are the same on every machine. Every number in the film comes from these two runs.

## 2. Sheet and audio (copy the folder to a scratch location so build files stay out of git)

```bash
cp -R <course-repo>/fall-2026/aravind-s/final-project-film /tmp/klaxon-pitch
cd /tmp/klaxon-pitch
python3 make_sheet.py                       # beat_sheet.json from the narration
cd <brutalist.art> && source .venv/bin/activate
python3 runtime/scripts/generate_audio_kokoro.py /tmp/klaxon-pitch
python3 /tmp/klaxon-pitch/finish_audio.py   # 0.8 s lead on BIDEA, 1.0 s tail on BOUT, measured durations
python3 runtime/scripts/align.py /tmp/klaxon-pitch
python3 /tmp/klaxon-pitch/make_shotlist.py
python3 /tmp/klaxon-pitch/build_scenes.py <brutalist.art>
```

Do not run `make_sheet.py` while a render is running: it rewrites `beat_sheet.json`, which the render reads.

## 3. Review cut and final

```bash
./art run /tmp/klaxon-pitch --height 1080
./art final /tmp/klaxon-pitch --height 1080 --out /tmp/klaxon-pitch/final
python3 runtime/qc/factcheck_check.py /tmp/klaxon-pitch
python3 runtime/scripts/bookend_check.py /tmp/klaxon-pitch
```

`art run` renders the 19 Manim scenes at 4K, the three Remotion beats, and a 1080p review cut, with Gates F, L, A, W, B and V. `art final` runs GATE T, then writes the master and a `.verified.json` receipt with its SHA-256. `bookend_check.py` reports one expected failure: the outro is a drawn title instead of the toolkit's `ClaudeTitleOutro`, which hard-codes the instructor's handle (see FRICTIONAL.md).

## Paste-ready Claude Code prompt

```text
Rebuild the INFO 7375 Klaxon pitch film in /tmp/klaxon-pitch with the brutalist.art
checkout at <toolkit path> (commit 22264a3), its .venv active. Do not change the
narration in make_sheet.py or the scenes in scene_body.py.
1. In the Klaxon repo, run the tests and both demo commands; confirm the naive run
   is off by +$69.68 and the idempotent run passes.
2. Run make_sheet.py, generate the Kokoro audio (am_onyx), finish_audio.py, align.py,
   make_shotlist.py and build_scenes.py.
3. Run ./art run /tmp/klaxon-pitch --height 1080. Stop and report if any gate fails.
4. Sample frames at 15/50/85% of each beat, look at them, and report defects.
5. Run ./art final /tmp/klaxon-pitch --height 1080 --out /tmp/klaxon-pitch/final and
   report the receipt's SHA-256.
No paid services, no direct API calls, no publishing.
```
