# BUILD-PROMPT

**Swathi Baba Eswarappa** · INFO 7375 · Week 1 Explainer Video
Built with **Claude Code (Opus 5)** on **2026-09-23**, macOS 26.6.2 / arm64.

This file records the prompts, the commands that were actually executed, and the
flags needed to reproduce the build.

---

## 1. The governing prompt

The session brief I gave Claude Code, condensed to its operative content:

> Produce the complete INFO 7375 Week 1 Explainer Video submission in this repository.
>
> - **Student:** Swathi Baba Eswarappa
> - **Deliverable:** `BabaEswarappa_Swathi_INFO7375_Week01_Video.zip`
> - **Concept:** "The unit is a token, not a word — and why that breaks letter-counting
>   prompts" (Chapter 1, Part 1). Stick to this one concept; do not summarise the chapter.
> - **Persona:** Dunkin — practical, punchy, Boston-sharp, technically grounded, zero fluff.
> - **Runtime:** 3:30–4:00, hard ceiling 4:00.
> - **Framework:** Brutalist (Film as Code), free local pipeline only — Kokoro narration,
>   Manim/Remotion visuals, FFmpeg. No paid generation, no API keys.
>
> **Step 1 — mechanistic groundwork.** Run `tiktoken` locally over `strawberry`,
> `banana`, `occurrence` in both `cl100k_base` and `o200k_base`. Capture the exact
> integer IDs and substrings. Show how character counts are lost across subword
> boundaries. Then state explicitly what this does **not** establish.
>
> **Step 2 — deliverables.** `beat_sheet.json`, `scene.py`, `README.md`,
> `BUILD-PROMPT.md`, `SOURCES.md`, `FRICTIONAL.md`.
>
> **Step 3 — build.** Check prerequisites, generate Kokoro narration, render the
> visuals, composite to a playable `.mp4`, verify it is non-zero and within the runtime
> target, and package the zip excluding `node_modules`, `__pycache__`, and caches.

### Standing constraints applied throughout

- **Every number on screen must be machine-generated**, read from probe output at render
  time — never hand-typed into the animation.
- **Anything constructed must be labelled constructed on screen.**
- **No fabricated Claude transcript.** (Resolved by showing none at all.)
- **Audio is the master clock**; the picture conforms to the voiceover, not the reverse.

## 2. Two prompts that changed the output

Worth recording, because they are where the video improved:

**(a) After the first probe run** — the probe showed `banana` is a *single* token and that
the two encodings split `strawberry` differently. I directed a second probe to exploit
both, plus a control:

> Probe two more things: that the split is a property of the tokenizer rather than the
> word, and what happens to the token IDs when you space the letters out. The spacing one
> is the control experiment for the whole claim.

This produced B06, B07 and B08 — including the finding that in the spaced encoding, token
id `436` occurs three times at positions `[2, 7, 8]`, the exact character indices the
tokenizer had destroyed. That became the payoff shot.

**(b) After the first audio pass came in at 3:55.89:**

> That is too close to the ceiling once gaps are added. Cut words rather than speeding up
> the voice, and protect the boundary beat — trim the four longest and regenerate only those.

## 3. Commands actually executed

Environment (needed because of the two failures in `FRICTIONAL.md`):

```bash
brew install ffmpeg espeak-ng
export ART_HOME="$PWD/brutalist.art"
export PHONEMIZER_ESPEAK_LIBRARY=/opt/homebrew/lib/libespeak-ng.dylib
export ESPEAK_DATA_PATH=/opt/homebrew/share/espeak-ng-data
```

Toolkit and weights:

```bash
git clone https://github.com/nikbearbrown/brutalist.art     # commit 6a8380a
python3 -m venv .venv-kokoro
.venv-kokoro/bin/pip install kokoro-onnx soundfile
mkdir -p brutalist.art/runtime/models/kokoro
cd brutalist.art/runtime/models/kokoro
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

Step 1 — the real numbers:

```bash
python3 code/tokenize_probe.py  | tee code/token_probe_output.txt
python3 code/embedding_probe.py | tee code/embedding_probe_output.txt
```

Step 3 — narration (Brutalist's own script, unmodified):

```bash
.venv-kokoro/bin/python brutalist.art/runtime/scripts/generate_audio_kokoro.py week-01-video --dry-run
.venv-kokoro/bin/python brutalist.art/runtime/scripts/generate_audio_kokoro.py week-01-video
# after the trim:
.venv-kokoro/bin/python brutalist.art/runtime/scripts/generate_audio_kokoro.py week-01-video --only B05 B06 B08 B09
```

Visuals — smoke test first, then all ten:

```bash
manim -ql --disable_caching scene.py B03_Tokenize          # smoke, 480p15
for S in B01_Hook B02_Claim B03_Tokenize B04_Indices B05_Embedding \
         B06_TokenizerDependence B06B_Frequency B07_Banana B08_SpacedControl \
         B09_Boundary B10_Close; do
  manim -qh --disable_caching scene.py "$S"                # 1080p60
done
```

Composite, captions, verify:

```bash
python3 qc_frames.py --border 16 --step 8      # fails if content touches the frame edge
python3 build_mux.py --gap 0.30
python3 make_srt.py
ffprobe -v error -show_entries format=duration,size -of default=nw=1 \
  BabaEswarappa_Swathi_INFO7375_Week01_Video.mp4
ffmpeg -i BabaEswarappa_Swathi_INFO7375_Week01_Video.mp4 -map 0:a -af volumedetect -f null /dev/null
```

Package:

```bash
zip -r BabaEswarappa_Swathi_INFO7375_Week01_Video.zip week-01-video \
  -x "*/media/*" "*/__pycache__/*" "*/build/segments/*" "*.pyc" "*/node_modules/*" "*/.DS_Store"
```

## 4. Reproducible flags

| Flag | Value | Why it matters |
|------|-------|----------------|
| tokenizer encodings | `cl100k_base`, `o200k_base` | both probed; the difference between them *is* the B06 argument |
| Kokoro voice | `am_michael` | set in `beat_sheet.json` → `metadata.voice_kokoro` |
| embedding illustration seed | `7375` | makes the CONSTRUCTED vectors in B05 reproducible |
| Manim quality | `-qh` → 1920×1080 @ 60 fps | `--disable_caching` so a script edit always re-renders |
| inter-beat gap | `0.30 s` | `build_mux.py --gap`; 10 gaps = 3.00 s of the runtime |
| x264 | `-preset medium -crf 18`, `yuv420p` | visually lossless, widely playable |
| audio | AAC 192 kbps, 48 kHz, stereo | |
| runtime gate | `120 ≤ d ≤ 240` s | `build_mux.py` exits non-zero if the master falls outside 2–4 min |
| frame-safety gate | outer `16 px`, every `8th` frame | `qc_frames.py` exits non-zero if any scene puts content in the border |
| chrome margin | `0.58` from frame edge | was `0.42`; widened after the header measured ~13 px from the top |

## 5. One-command rebuild

Everything above is captured in `build.sh`:

```bash
./build.sh              # probes -> narration -> scenes -> mux
./build.sh --mux-only   # re-composite only
```

## 6. Verification built into the build

The pipeline fails loudly rather than shipping a bad master:

- `tokenize_probe.py` asserts `decode(encode(w)) == w` for every word and prints the result.
- `scene.py` reads all displayed integers from the probe JSON — a stale probe cannot
  silently disagree with the narration.
- `build_mux.py` prints per-beat video/audio deltas (worst observed: **0.02 s**) and
  returns exit code 1 if the master is outside the 2–4 minute window.
- `qc_frames.py` decodes every scene to raw RGB and returns exit code 1 if any non-background
  pixel lands in the outer border — added after a caption in B02 shipped clipped.
- `Beat.assert_in_frame()` runs at the end of every scene and raises if a visible mobject's
  bounding box leaves the frame. This is deliberately a *geometric* check, not a pixel one:
  content pushed entirely off-frame (as B07's last line was) leaves no pixels for the sweep.
- `Beat.hold_until(t)` pins a cue to a narration timestamp instead of letting animations run
  back to back — added after B10's sign-off card appeared 6.5 s before it was spoken.
- `Beat.assert_in_safe_area()` fails if any non-chrome part crosses the top or bottom rule.
  The frame checks could not catch this: content can sit well inside the frame and still be
  drawn into the footer band, as B03's token IDs and B04's closing caption were.
- `Beat.assert_no_text_overlap()` fails if two visible `Text` mobjects intersect. Distinct
  from the frame checks: a caption can be well inside the frame and still be drawn through a
  diagram, as B05's did. It caught a second, unnoticed collision in B08 on its first run.
- `Beat.at(phrase)` / `Beat.pin(phrase)` convert a phrase in the narration to a timestamp by
  word position, so a cue waits for the sentence that justifies it. 54 cues are pinned this
  way; every phrase is validated against `beat_sheet.json` before rendering.
- `lock()` prints each beat's **trailing hold** (animation end vs narration end). A large
  value means the picture finished early and is holding — which is how B08's payoff ended up
  on screen ~20 s before it was spoken. Worst hold is now 6.38 s, down from 22.25 s.
