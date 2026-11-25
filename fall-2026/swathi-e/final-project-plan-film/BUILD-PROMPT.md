# BUILD-PROMPT — Final Project Film (plan)

**Swathi Baba Eswarappa** · INFO 7375 · Final Project Film
Built with **Claude Code (Opus 5.5)** on **2026-11-22**, macOS 26.7.3 / arm64.

## 1. The governing prompt

`CLAUDE-CODE-PROMPT.md` (everything below its line), Phase 1 run first, then my
decisions message, which approved Phases 2 and 3:

1. Voice `af_heart`, matching the pitch film's final cut.
2. No git command anywhere. Upstream gates come from the local `519fcbb` copy.
3. Output `BabaEswarappa_Swathi_INFO7375_FinalProjectPlanFilm.mp4`.
4. `#6B6B70` → `#8A8A90` in B03, B05 and B11. Runtime gate 120–300 s.
5. B11: "PROPOSED TARGETS — NOT RESULTS" stays through the sign-off.
6. "November seventeenth" accepted.
7. GATE MASTER + Gate V in place of "render integrity".
8. The audio pipeline may write `actual_duration_s` and `audio_file`.
9. A failed gate is reported, never bypassed.
10. B05 figures checked read-only against the JS3 folder.
11. Writes only inside this folder.

## 2. Environment

```bash
export ART_HOME="$HOME/Downloads/brutalist/brutalist.art"     # toolkit, commit 29ba0e8, read-only
export PHONEMIZER_ESPEAK_LIBRARY=/opt/homebrew/lib/libespeak-ng.dylib
export ESPEAK_DATA_PATH=/opt/homebrew/share/espeak-ng-data
export PYTHONDONTWRITEBYTECODE=1                               # never write caches into the toolkit
PY=/opt/anaconda3/bin/python3                                  # 3.12.2; .venv-kokoro not present
```

## 3. Commands actually executed

Beat sheet edits (backup first) and narration:

```bash
cp beat_sheet.json build/beat_sheet.orig.json
sed -i '' 's/"voice": "am_michael"/"voice": "af_heart"/; s/"voice_kokoro": "am_michael"/"voice_kokoro": "af_heart"/; s/"#6B6B70"/"#8A8A90"/' beat_sheet.json
$PY "$ART_HOME/runtime/scripts/generate_audio_kokoro.py" . --dry-run    # 11 beats, $0.00
$PY "$ART_HOME/runtime/scripts/generate_audio_kokoro.py" .              # 242.92 s of narration
```

Per-beat narration (s): B01 20.01 · B02 18.18 · B03 25.34 · B04 16.90 · B05 32.46 ·
B06 31.03 · B07 19.90 · B08 22.36 · B09 16.06 · B10 17.13 · B11 23.55.

Facts, smoke test, assertions, master render:

```bash
$PY check_facts.py
manim -ql --disable_caching --media_dir build/smoke scene.py B05_CompletedWork
build/render_all.sh -ql 480p15                       # all 11, Beat assertions after every cue
build/render_all.sh "-qk --frame_rate 24" 2160p24    # all 11 @ 3840x2160, 24 fps (1:45)
```

Local gates, mux and captions, then upstream gates:

```bash
./build.sh --mux-only        # facts, Gate A, Gate W, labels, Gate B, frame sweep, mux (-19 LUFS), SRT, Gate V
build/run_upstream_gates.sh  # LOUDNESS, MASTER, SRT, SHARPNESS, T from the local 519fcbb copy
```

Gate A was re-run once, by hand, after a fix to `scene.py` (§5):

```bash
for S in B01_WhatItIs ... B11_Targets; do
  $PY "$ART_HOME/runtime/qc/static_scene_check.py" scene.py --class "$S"
done > qc_reports/gateA_static_scene_check.txt
```

Verification:

```bash
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,pix_fmt,sample_rate,channels \
        -show_entries format=duration,size -of default=nw=1 BabaEswarappa_Swathi_INFO7375_FinalProjectPlanFilm.mp4
ffmpeg -i BabaEswarappa_Swathi_INFO7375_FinalProjectPlanFilm.mp4 -map 0:a -af ebur128=peak=true -f null /dev/null
ffmpeg -i BabaEswarappa_Swathi_INFO7375_FinalProjectPlanFilm.mp4 -map 0:a -af silencedetect=n=-45dB:d=1.5 -f null /dev/null
shasum -a 256 BabaEswarappa_Swathi_INFO7375_FinalProjectPlanFilm.mp4
# contact sheet: one frame every 6 s (ffmpeg fps=1/6), timestamped and tiled with Pillow
```

## 4. Reproducible flags

| Flag | Value |
|---|---|
| Kokoro voice | `af_heart` (`metadata.voice`, `metadata.voice_kokoro`) |
| Manim | CE v0.18.1, `-qk --frame_rate 24` (3840×2160), `--disable_caching`, one `--media_dir` per scene |
| Inter-beat gap | 0.30 s (10 gaps = 3.00 s) |
| x264 / audio | `-preset medium -crf 18`, yuv420p / AAC 192 kbps 48 kHz stereo, two-pass `loudnorm I=-19:TP=-1.5:LRA=11` |
| Runtime gate | 120 ≤ d ≤ 300 s |
| Frame-safety sweep | 16 px border at 1080p scale, every 4th frame |
| Midpoint guard | no animation within 0.2 s of a clip's midpoint (GATE T samples there) |
| Chrome | rules at x ±6.25, y ±3.0; label top-left from `beat_sheet.json`; footer verbatim from `data/facts.json` |
| Colours | ground `#0B0B0C`; FG `#F5F3EF`, DIM `#8A8A90` (5.73:1), AMBER, RED, GREEN, BLUE, VIOLET (all ≥ 5.7:1) |

## 5. Fixes made during the build

- **Empty first clip.** A cue pinned at 0 s made a 0.04 s wait, which is zero
  frames at 15 fps, and ffmpeg refused to combine B06, B08 and B10.
  `hold_until` now skips waits shorter than one frame.
- **Chrome tag.** The label gate caught "S.BABAESWARAPPA·INFO7375": Manim's
  `Text.text` drops spaces. The tag is now built from the original string.
- **Gate A crash.** Gate A's stub Manim has no `config.frame_rate`, so
  `hold_until` only reads it under real Manim. Render output is unchanged.
- **Visual fixes from end-frame review.** B01's set-aside cards now stack in a
  neat grid, and B02's error cards sit clear of the tilted beam.
- **End holds.** Four holds over 2.5 s (B02, B03, B09, B10) were cut with cues on
  the closing phrases. Worst remaining: 2.34 s (B10).

## 6. Gate failures fixed after my approval

First full gate run: Gate A failed on B11 ("shapes never change": an all-text
beat) and GATE T failed on B08 (text-run overlap). I approved two fixes:

- **B08:** the green approve→card line stops 0.15 units short of both ends, so
  GATE T no longer reads the badge, line and card as one fused text blob.
- **B11:** a dashed amber marker beside each target row, with no new text.

No narration, label, number, `beat_sheet.json` content or gate changed.
Claude Code's first version of the B08 fix crashed Gate A's stub Manim (list
arithmetic). The points were wrapped in `np.array`, which is identical under
real Manim, and B08 was re-rendered so the render matches the source.

```bash
manim -qk --frame_rate 24 --disable_caching --media_dir build/mq/B08_GateAndResources scene.py B08_GateAndResources
manim -qk --frame_rate 24 --disable_caching --media_dir build/mq/B11_Targets scene.py B11_Targets
./build.sh --mux-only        # every local gate, re-mux
build/run_upstream_gates.sh  # all five upstream gates
```

## 7. Final results

| Gate | Result |
|---|---|
| Facts · Labels | PASS · PASS (11/11) |
| Gate A · Gate W | 11 clean · 11 clean |
| Gate B | 0 errors; 4 warnings, reviewed (three intended strike-throughs; B03 two-line footer) |
| Frame sweep · Runtime (120–300 s) · Gate V | PASS · PASS · 0 BLOCKER / 0 MAJOR |
| Upstream LOUDNESS · MASTER · SRT · SHARPNESS · T | PASS · PASS · PASS (83 cues) · PASS · PASS |

Master: **4:05.78 (245.78 s)**; Part 1 ends at 0:38.48; −19.0 LUFS, true peak
−1.5 dBTP; 3840×2160 24 fps.
SHA-256 `f702ec08fdc8c73ab5d29fd1a8981a181d56bc121da09e00d634a33338db849d`.
