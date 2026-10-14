# Readback — Final Project Pitch Film

**Aravind Ravi** · INFO 7375 · Fall 2026
**Working title:** Readback. *Hear how AI reads your instructions before it acts on them.*
**Target role:** AI Product Manager
**Runtime:** 3:02 (182.46 s) · 1920×1080, 24 fps · `aravind-r-readback-pitch.mp4`
**Master SHA-256:** `4334b59eae58cd946716cc924da4fb47a28ffae236c19605a01cad89568278eb` (v2 visuals; v1 is in git history at `31005a1`)

The film pitches Readback: a tool that will show a product manager which clause of their eval rubric an AI judge reads differently than they meant. It answers the assignment's seven questions; the same answers are written out in [`PROJECT-BRIEF.md`](PROJECT-BRIEF.md). It is a pitch, not a build. What exists today and what will exist are listed at the end of the brief and in the film's last beat.

**Narration** is synthesized locally from my own approved script, using the free Kokoro voice `am_onyx`, and the film says so in its first line. No paid generation, API key, media account or public upload was used.

**Visuals (v2, 14 Oct 2026):** this film replaces my first cut. The narration audio is bit-identical; only the visuals changed. The v2 visuals add:
- one colour per role;
- a progress rail (What · Why · Who · Proves · Scope · Risk · Why me);
- a rubric page that carries through every beat;
- the real AMI DECISIONS counts and recap outputs on screen;
- a frame-by-frame check that no text overlaps anything.

v1 was frozen 89.7 % of the time (holds of 3 s or more); v2 is frozen 14.4 %, and no hold is longer than 4 s. Plan: `gates/v2-visual-plan.md`.

## What's in this folder

| Path | What it is |
|---|---|
| `aravind-r-readback-pitch.mp4` | The film |
| `PROJECT-BRIEF.md` | The seven answers, with **Exists today** and **Will exist** lists |
| `beat_sheet.json` | Narration and visual plan, in show-tell format. Each beat carries `question_ids`, `claim_status`, `evidence` and `on_screen_label` |
| `make_sheet.py`, `scenes.py`, `add_holds.py`, `overlap_check.py` | The beat-sheet generator, the Manim scenes (BIDEA, B01–B08), the per-beat hold padding, and my frame-by-frame text-overlap check |
| `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md` | The toolkit's required paperwork: claims, work order, prompts |
| `gates/v2/` | **Reports for the submitted film:** the gate table (`GATES.md`), toolkit gate reports (A, W, B, V, T, bookend, factcheck, render logs), my overlap check, `honesty-audit-v2.md`, the contact sheet (1 frame / 2 s) and one frame per beat |
| `gates/` (top level) | v1's gate reports and honesty audit (kept as history; the narration rows still apply), plus the v2 plan and the B05 probe sheet |
| `case-study/` | Real data and runs: 10 AMI meetings (CC BY 4.0), the constructed recap PRD, system prompt and rubric (labelled CONSTRUCTED), and 10 real recap outputs from Claude Opus 5.5 (14 Oct 2026) |
| `toolkit-patches/` | My patch to the toolkit's outro: my own handle, and no mascot |
| `FRICTIONAL.md`, `SOURCES.md`, `BUILD-PROMPT.md` | Dated log, sources and credits, and the prompts and commands that rebuild the film |

## Rebuild the film

**Toolkit:** [brutalist.art](https://github.com/nikbearbrown/brutalist.art), pinned at commit **`cd4bf20904be4e7d63babd9622b17963c2361b27`**. Don't use current upstream: it pins Manim 0.20, and this film was rendered with Manim 0.18.1.

**Machine setup** (my Week 1 install; see `FRICTIONAL.md` there):
- Python 3.12 venv with the toolkit's `requirements.txt` (manim 0.18.1).
- Homebrew `ffmpeg`, `cairo`, `pango` and `espeak-ng`.
- Node ≥ 20.
- The toolkit's `youtube/` folder moved out of the checkout, so `./setup` passes its ElevenLabs guard.
- `A01/brutalist-env.sh`, which activates the venv and sets `PHONEMIZER_ESPEAK_LIBRARY=/opt/homebrew/lib/libespeak-ng.1.dylib`.

From this folder (`REEL` = its absolute path; `ART` = the toolkit checkout):

```bash
git -C "$ART" checkout cd4bf20 && git -C "$ART" apply "$REEL/toolkit-patches/ClaudeTitleOutro-handle-hideMascot.patch"
source "$ART/../brutalist-env.sh"
python3 make_sheet.py                                          # beat_sheet.json (narration + plan)
(cd "$ART" && python3 runtime/scripts/generate_audio_kokoro.py "$REEL")   # Kokoro am_onyx → mp3/, the clock
python3 add_holds.py                                           # hold after each beat → actual_duration_s
(cd "$ART" && python3 runtime/scripts/align.py "$REEL")       # word timings → mp3/words.json
(cd "$ART" && ./art run "$REEL" --height 1080)                 # Gates F, L, A, W, B, V + review cut
(cd "$ART" && ./art final "$REEL" --height 1080 --out "$REEL/exports/landscape")   # Gate T + master
cp exports/landscape/aravind-r-readback-pitch.mp4 .
(cd "$ART" && python3 runtime/scripts/bookend_check.py "$REEL" && python3 runtime/qc/factcheck_check.py "$REEL")
for c in BIDEA_Hook B01_WhatItIs B02_Difference B03_FirstMinute B04_Proves B05_InOutFirst B06_Risk B07_WhyMe B08_ExistsWill; do
  manim -r 384,216 --fps 24 --disable_caching --media_dir /tmp/ov overlap_check.py $c | grep '\[overlap\]'   # expect 0 overlaps
done
```

The rebuild is deterministic. Rebuilding from this folder on 14 Oct 2026 produced a file byte-identical to the gated master, with all 4,378 decoded frames identical.

These steps only rebuild the film from the committed case-study files. The data and the feature run have their own steps; see `case-study/data/sample/README.md` and `BUILD-PROMPT.md`. Re-running `case-study/run_feature.py` asks Claude again, so the recaps it writes will differ. The committed outputs dated 14 Oct 2026 are the record the film quotes.
