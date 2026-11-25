# Build notes

Built by Claude Code on 2026-11-20 (ET) from SCRIPT.md / beats.json. Nothing here touches the Klaxon repo: the panel
footage was served from a scratch copy of `fef450b` (`git archive`, outside the repo) on 127.0.0.1:8091, stopped after.
No Docker, no model calls, and nothing committed or pushed in Klaxon.

Final render on 2026-11-22 (ET), after Aravind approved the review cut with no changes: the same build, with two
changes in `assemble.py`, the file name (`klaxon-final-project-film.mp4`, was `klaxon-final-project-film-REVIEW.mp4`)
and the title tag ("Klaxon: Final Project Film", was "Klaxon: Final Project Film (review cut)"). Its video, audio
and caption streams hash the same as the review cut's (ffmpeg `streamhash`, SHA-256); only the container changed.

## Output

- `out/klaxon-final-project-film.mp4`: 1920x1080, 30 fps, H.264 + AAC 48 kHz, soft English captions
  (mov_text), 4:34.6 (8237 frames), loudness about -17 LUFS integrated. Timings per beat and part: `out/TIMINGS.md`.
- `out/captions.srt` (the soft track's text), `out/narration.wav`, `out/timeline.json` (frames per beat and step).

## What the build needs (environment variables)

No path in the build files names a particular computer. Set these first; keep your own values in a local file that
you source, and do not commit it.

| Variable | What it is | Used by |
|---|---|---|
| `PW_PY` | A Python with Playwright and its Chromium (`pip install playwright`, then `python -m playwright install chromium`) | `capture.py`, `measure.py`, `stage.py` |
| `TTS_PY` | A Python with `kokoro-onnx` (0.6.1 was used), `numpy` and `Pillow` | `tts.py`, `assemble.py`, `contact.py` |
| `KOKORO_MODELS` | The folder that holds the Kokoro v1.0 model files `kokoro-v1.0.onnx` and `voices-v1.0.bin`; `tts.py` reads it and stops if it is unset | `tts.py` |
| `KLAXON_REPO` | A clone of https://github.com/AravindKumar2504/klaxon (public), only to capture the footage again | step 0 |

Also `ffmpeg` on the PATH (assembly) and `python3` for `beats.py` and `make_script_md.py`. Run every command from the
film folder (the one that holds `beats.json`).

## Rebuild (in order)

0. Footage (optional: `build/capture/` already holds it). Start the scratch panel, then
   `"$PW_PY" build/scripts/capture.py` and `"$PW_PY" build/scripts/measure.py`.
   - Scratch panel: `git -C "$KLAXON_REPO" archive fef450b | tar -x -C <scratch>/klaxon-fef450b`; in it,
     `python3.12 -m venv .venv` and `.venv/bin/pip install -c requirements/graph.lock.txt -c
     requirements/dev.lock.txt -e '.[services]'`; then `.venv/bin/python -m klaxon.panel --port 8091`.
   - The terminal card's text: in the scratch copy, `make eval-cases | grep -E '^[a-z]|action that fits'`, saved as
     `build/capture/eval-cases-card.txt` in the film folder.
1. Narration: `"$TTS_PY" build/scripts/tts.py [B13 B15 ...]` (Kokoro am_onyx, speed 1.0; with beat ids, only those
   beats). Writes `audio/*.wav` and updates `audio/durations.json`.
2. Frames: `"$PW_PY" build/scripts/stage.py` (every card is HTML in `cards/`, rendered to `stills/`; it refuses any em
   dash on screen). It needs only `build/capture/`, `beats.json` and `audio/durations.json`, so it runs without the
   voice model.
3. Cut: `"$TTS_PY" build/scripts/assemble.py` (needs the WAVs from step 1).
4. Eye check: `"$TTS_PY" build/scripts/contact.py` (contact sheets in `frames/`).

## If a beat's words change

Edit `beats.py`, run it (`python3 beats.py beats.json`), then `python3 build/scripts/make_script_md.py`, then steps 1
(only the changed beats), 2 and 3. Every later beat moves in time automatically; captions follow the new text.
