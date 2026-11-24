# Readback — Final Project Films

## Project film (four-part brief, 2026-11-23)

**Aravind Ravi** · INFO 7375 · Fall 2026
**File:** `film/project/aravind-r-readback-project-film.mp4` · 3:56.8 · 1920×1080, 24 fps
**SHA-256:** `37cbfaa6b2949adb2835d1e86ff3b4bcc4b09c8a76fda57fc3d374cbb7c739a0`
**PR:** https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/pull/54

The project film follows the course's four-part brief: an executive summary (what Readback is and why it matters), an introduction (what others have built, scoped to the tools I checked: Maxim AI, orq.ai and GitHub Spec Kit), methods (how it will be built, where the data comes from, and what I have to build it with) and evaluation (three checks, each with a pass and a fail condition). Readback is for any AI feature whose acceptance criteria an AI judge grades: when judges disagree, it will trace the disagreement to the criterion that caused it and ask the PM a clarifying question, never rewriting the criterion itself. The AMI meeting-recap feature is the test case only; it appears in Methods and Evaluation, under a "test case" tag. Everything Readback does is planned: no judge has run, no human labels exist and no agreement has been measured. The real material on screen is the AMI data and the ten recaps from 14 Oct 2026.

### What's in `film/project/`

| Path | What it is |
|---|---|
| `aravind-r-readback-project-film.mp4` | The film |
| `beat_sheet.json` | Narration and visual plan in show-tell format: 20 drawn beats (B01–B20) and the outro (BOUT), each with its clip and measured durations. Written by `make_sheet.py` |
| `make_sheet.py` | Writes `beat_sheet.json`: my approved narration, the voice spellings (Readback as "Reed-back"), each beat's hold, and the outro's props |
| `scenes.py` | The 20 Manim scenes, `B01_Hook` … `B20_Close` |
| `add_holds.py` | Trims each narration clip's edge silence to 0.05 s and pads the beat's hold |
| `normalize_audio.py` | Rebuilds the narration track the way the toolkit's compile does and normalises it to −16 LUFS (`mp3/master-16lufs.wav`), which `art final --audio` uses |
| `qc_film.py` | My Phase 4 measurements: freeze, black frames, loudness, silence, background colour at every cut, section-boundary frames and contact sheets (`gates/QC.json`) |
| `overlap_check.py` | Frame-by-frame text-overlap check at 24 fps (text vs text, shape vs text) |
| `strings_dump.py`, `positioning_check.py` | The positioning audit: every on-screen string on every frame, plus the narration, checked against the test-case rule (`gates/positioning-audit.md`) |
| `stt_check.py` | Speech-to-text on the full film and on each clip alone, compared with the script (`gates/stt-full-master.txt`) |
| `make_storyboard.py` | Builds `storyboard.png` from each beat's last frame in the master |
| `CLAIMS.md` | Every narration sentence and on-screen number, mapped to an evidence path or marked PLANNED |
| `EVAL-PLAN.md` | The evaluation plan: judges, human labels, the three checks and their pass/fail conditions (PLANNED, nothing run) |
| `DESIGN.md` | The design system and per-beat plan, with every on-screen number and its source |
| `FACTCHECK.md` | The toolkit's claims table (81 rows) |
| `SHOTLIST.md` | The work order, including every hold over 2.5 s and its reason |
| `PROMPTS.md` | The prompts behind the real material on screen, and the prompts I sent to Claude Code |
| `TYPECHECK.md` | Gate T's report from the last `art final` |
| `gates/` | `GATES.md` is the summary of every gate on the delivered master; the other files are the reports and logs it cites. `review-cut-1/` keeps the first review cut's evidence as history |
| `storyboard.png` | One still per beat, taken from the master |
| `style-frames/` | One frame per part, taken from the master |
| [`APPENDIX-METHODS-EVAL.md`](film/project/APPENDIX-METHODS-EVAL.md) | Appendix: how Readback traces a disagreement to a criterion, cost and compute, statistical limits, and generality (PLANNED) |

### Rebuild the project film

Same toolkit pin and machine setup as the pitch film below. These are the commands I ran, in order, from `film/project/` (`P` = its absolute path; `ART` = the toolkit checkout; `QC="$ART/runtime/qc"`; `SC="$ART/runtime/scripts"`). The render logs are `gates/art-run-*.log` and `gates/art-final-*.log`.

```bash
git -C "$ART" checkout cd4bf20
git -C "$ART" apply "$P/../../toolkit-patches/ClaudeTitleOutro-handle-hideMascot-polarity-bg-tagline.patch"
source "$ART/../brutalist-env.sh"
python3 make_sheet.py                                                   # beat_sheet.json
(cd "$ART" && python3 runtime/scripts/generate_audio_kokoro.py "$P")    # Kokoro am_onyx → mp3/beat-*.mp3
python3 add_holds.py                                                    # trim clip edges, add each beat's hold
(cd "$ART" && python3 runtime/scripts/align.py "$P")                    # word timings → mp3/words.json
(cd "$ART" && ./art run "$P" --height 1080)                             # Gates F, L, A, W, B, V + review cut
python3 normalize_audio.py                                              # → mp3/master-16lufs.wav
(cd "$ART" && ./art final "$P" --height 1080 --out "$P/exports/landscape" --audio "$P/mp3/master-16lufs.wav")   # Gate T + master
cp exports/landscape/aravind-r-readback-project-film.mp4 aravind-r-readback-project-film.mp4
cp exports/landscape/aravind-r-readback-project-film.verified.json gates/master.verified.json
```

The checks, on the delivered master:

```bash
M="$P/aravind-r-readback-project-film.mp4"
python3 qc_film.py "$M"
python3 "$QC/final_frame_check.py" "$P" --mp4 "$M"                      # Gate V
python3 "$QC/beat_lint.py" "$P"
python3 "$SC/bookend_check.py" "$P"
python3 "$QC/factcheck_check.py" "$P"
for c in B01_Hook B02_Stakes B03_Readback B04_Maxim B05_Orq B06_SpecKit B07_Gap B08_WhyMine B09_TestBench B10_Feature \
         B11_Rubric B12_Labels B13_Judges B14_Trace B15_Have B16_Planted B17_Kappa B18_BeforeAfter B19_Scorecard B20_Close; do
  python3 "$QC/static_scene_check.py" "$P/scenes.py" --class "$c" --quiet                     # Gate A
  python3 "$QC/wcag_margin_check.py" "$P/scenes.py" --class "$c" --quiet                      # Gate W
  python3 "$QC/manim_layout_audit.py" "$P/scenes.py" --class "$c" --png --curve-strict        # Gate B
  manim -r 384,216 --fps 24 --disable_caching --media_dir "$TMP/ovl/$c" overlap_check.py "$c"   # expect 0 overlaps
  manim -r 384,216 --fps 24 --disable_caching --media_dir "$TMP/str/$c" strings_dump.py "$c"    # input to the positioning audit
done
python3 positioning_check.py                                            # → gates/positioning-audit.md
python3 stt_check.py "$M"                                               # → gates/stt-full-master.txt
python3 make_storyboard.py "$FRAMES"                                    # → storyboard.png
```

Notes on what differed from a clean run:
- The toolkit was already at `cd4bf20` with the patch applied in its working tree; the patch file is that diff (`git -C "$ART" diff -- runtime/remotion/src/scenes/ClaudeTitleOutro.tsx`). The `checkout` and `apply` lines rebuild that state on a clean checkout; I didn't run them during the build.
- The narration was voiced in full once. After each script change only the changed beats were re-voiced, with a one-off sheet of those beats (`generate_audio_kokoro.py "$P" --sheet beat_sheet.revoice.json`), then `add_holds.py` and `align.py` again.
- `art run` skips beats that already have a clip. To re-render a beat, I moved its `manim/` and `clips/` files into `_superseded/` (git-ignored) first.
- `$TMP` is any scratch folder. `$FRAMES` holds each beat's last frame (beat end − 0.06 s; the outro 0.25 s before the end), grabbed from the master with `ffmpeg` by a scratch helper that isn't in the repo.
- I haven't rebuilt the project film from a clean checkout. The delivered master is the one measured in `gates/GATES.md`.

## Pitch film (2026-10-14)

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

### What's in this folder

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

### Rebuild the film

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
