# BUILD-PROMPT

**Swathi Baba Eswarappa** · INFO 7375 · Final Project Pitch Film
Built with **Claude Code (Opus 5.5)** on **2026-10-13**, macOS 26.6.2 / arm64.

This file records the prompts, the commands that were actually executed, and the
flags needed to reproduce the build.

---

## 1. The governing prompt

The session brief I gave Claude Code (from `CLAUDE-CODE-PROMPT.md`, everything below its line):

> Build my INFO 7375 Final Project Pitch Film in this folder.
>
> - **Student:** Swathi Baba Eswarappa
> - **Film file:** `BabaEswarappa_Swathi_INFO7375_FinalProjectFilm.mp4`
> - **Project pitched:** "Cite or Refuse," a source-grounded tax helper for international
>   students. It is a pitch, not a build: nothing in the project exists yet.
> - **Runtime:** 2–4 minutes, hard ceiling 240 s.
> - **Framework:** Brutalist, free local pipeline only (Kokoro narration, Manim visuals,
>   FFmpeg). No paid generation, no API keys, no upload.
>
> **Inputs:** `beat_sheet.json` (13 beats; treat `narration_text` as approved and do not
> change any claim, number, or wording without asking), `PROJECT-BRIEF.md`, `TEST-NOTES.md`,
> and the Week 1 helpers `scene.py`, `build_mux.py`, `qc_frames.py`, `make_srt.py`,
> `build.sh`. Reuse the `Beat` helper class and its checks; replace the Week 1 scenes with 13
> new ones named as in `beat_sheet.json` (`B01_TwoAnswers` … `B13_Close`). Locate the
> Brutalist toolkit and Kokoro environment in `~/Downloads/brutalist/` first and report.
>
> **Hard rules.**
> 1. Numbers come from one data file, `data/facts.json`; scenes read from it; check each
>    number also appears in the narration where it is spoken.
> 2. Planned-system diagrams (B04, B06) carry a visible PROPOSED badge; the B08 terminal
>    carries "CONSTRUCTED MOCK-UP" for the whole beat, with dashes instead of scoreboard
>    numbers. Nothing unbuilt is drawn as if it runs.
> 3. No screenshots of chatbot answers; B01 shows plain number cards with
>    "ChatGPT, Oct 9, 2026". No personal details anywhere.
> 4. No overlapping text; every scene must pass `assert_no_text_overlap`; keep captions short.
> 5. Audio is the master clock; pin cues with `at`/`pin`; keep trailing holds small.
> 6. One clear drawn picture per beat, minimal on-screen text.
> 7. Narrate as me, in the beat-sheet voice. No instructor name, persona, or credit line.
>
> **Build steps.** (1) Check prerequisites. (2) Kokoro dry run, then narration; report
> per-beat durations. (3) Smoke-render one scene at low quality, then all 13 at 1080p.
> (4) Week 1 gates: `qc_frames.py`, the `Beat` assertions, `build_mux.py` runtime gate.
> (5) The Brutalist toolkit's own quality gates, including any render-integrity check;
> save their reports here; do not ship over a failure. (6) Composite the mp4 and captions;
> verify duration, size, audio levels. (7) Write this file. Do not write `FRICTIONAL.md`.
> Draft `README.md` and `SOURCES.md` for review. Stop and ask whenever a rule conflicts
> with the build.

### Standing constraints applied throughout

- **Every number on screen is read from `data/facts.json`**; `check_facts.py` fails the build
  if a string literal in `scene.py` contains a digit, or if a fact's spoken form is missing
  from its beat's narration.
- **Anything unbuilt is labelled on screen**: PROPOSED · NOT BUILT (B04, B06, B07, B11),
  CONSTRUCTED MOCK-UP (B08, whole beat), "will exist" / "will run" (B09, B10).
- **Narration text was edited only with my approval**, in three places: B02 (wording written by
  Claude (chat) and approved by me, prompt (b)); "A I" → "AI" in B08 and B09 (my choice from samples, prompt (d)); and B08
  "they run" → "they will run" (proposed by Claude Code to meet the honesty rule, approved
  by me, prompt (e)). Kokoro's script writes `actual_duration_s` and `audio_file` back into
  `beat_sheet.json`; a diff against the copy taken before each edit
  (`build/beat_sheet.orig.json`, `build/beat_sheet.before_*.json`) confirms no other
  beat's `narration_text` changed.
- **Audio is the master clock**; each scene pads itself to its narration length.

## 2. Prerequisite findings (recorded as asked)

- **`.venv-kokoro` was not found.** It is not in `~/Downloads/brutalist/` or anywhere under
  the home folder to depth 4. The Anaconda Python (`/opt/anaconda3/bin/python3`, 3.12.2)
  already had `kokoro_onnx` 0.6.1, `onnxruntime` 1.30.0 and `manim` 0.18.1, and passed the
  toolkit's own `runtime/scripts/setup_smoke_kokoro.py` ("kokoro synth OK — mean_volume
  -21.8 dB"). Every Python step below uses that interpreter. Nothing was installed.
- **`./setup` stopped early.** The toolkit's setup check aborts on an ElevenLabs-reference
  lint that matches files under `brutalist.art/youtube/` (added to that folder on Oct 9, not
  part of this film). It never reached its READY report, so each dependency was checked by
  hand instead: ffmpeg/ffprobe 9.0.1, Manim CE v0.18.1, LaTeX + dvisvgm, espeak-ng 1.52.0
  (both env-var paths exist), Kokoro model files `kokoro-v1.0.onnx` (325 MB) and
  `voices-v1.0.bin` (28 MB) in `brutalist.art/runtime/models/kokoro/`, and the smoke test above.
- **No gate named "render integrity" exists** in the toolkit README or docs. With my approval,
  these four toolkit gates were run in its place, and all reports are saved in `qc_reports/`.
  (Prompt (e) later found the local toolkit out of date and added five upstream gates; see
  the second table below.)

  | Gate | Toolkit script | What it checks | Result |
  |---|---|---|---|
  | **A** | `runtime/qc/static_scene_check.py` (per class) | runs each `construct()` against a stub Manim: scene logic, visual variety, coordinates | 12 clean · 1 warn (B08, stub-geometry artifact, see §6) |
  | **W** | `runtime/qc/wcag_margin_check.py` | static WCAG contrast, margins, text-on-text | 13 clean (+ my contrast table: all colours ≥ 5.7:1) |
  | **B** | `runtime/qc/manim_layout_audit.py` (per class) | real Manim bounding boxes of every Text at every steady state | 0 errors · 4 warnings, all reviewed (see §6) |
  | **V** | `runtime/qc/final_frame_check.py` | samples the final mp4 per beat: edge bleed, underfill, low contrast | 26 frames · 0 BLOCKER · 0 MAJOR |

- **The local toolkit was out of date** (found in prompt (e)). The assignment says to clone
  the toolkit; this machine's copy is commit `29ba0e8` (2026-09-15), but upstream `origin/main`
  is `519fcbb` (2026-10-12). Upstream has since added the `show-tell` skill the assignment
  names and several gates. No upstream file uses the words "render integrity" either; the
  closest is GATE MASTER, which checks that the compiled master is clean and meets the
  toolkit's spec. `build/run_upstream_gates.sh` takes the gate scripts from upstream
  `origin/main` (via `git fetch` + `git archive`; the local checkout's files are not
  changed), runs them on a temporary staged copy of the film, and saves their reports in
  `qc_reports/upstream/`. Final results:

  | Upstream gate | Script | What it checks | First run | Final |
  |---|---|---|---|---|
  | **LOUDNESS** | `runtime/scripts/loudness_check.py` | integrated −28…−18 LUFS, true peak ≤ −1 dBTP, no silent beat | FAIL (−16.0 LUFS) | PASS −19.01 LUFS, −1.51 dBTP |
  | **MASTER** | `runtime/scripts/master_check.py` | 3840×2160, 24 fps, yuv420p, h264, audio, duration | FAIL (1920×1080, 60 fps) | PASS |
  | **T** | `runtime/scripts/type_check.py` | text size, overflow, contrast, overlap at each clip's midpoint | FAIL (B04, B10) then B11 | PASS, 13 beats measured |
  | **SRT** | `runtime/scripts/srt_check.py` | caption file well-formed | PASS | PASS, 80 cues |
  | **SHARPNESS** | `runtime/scripts/sharpness_check.py` | per-beat blur against the reel median | PASS | PASS |

  Not applicable to this film: BOOKEND, BANNED-CARD, LANE, CONTENT, FRAME and ZDEFAULT check
  the toolkit's Remotion cards, slates and Claude bookends, which this Manim film does not use.

## 3. Prompts that changed the output

**(a) After the prerequisite report.** I approved the substitutions and set the recording
requirements for this file:

> Yes, use the Anaconda Python and run all four gates, starting with the Kokoro dry run.
> Work only inside ~/Downloads/brutalist/final-project-film and save all gate reports there.
> In BUILD-PROMPT.md, record that .venv-kokoro wasn't found, that ./setup stopped early
> because of files in brutalist.art/youtube/, and which four gates you ran instead of a named
> render-integrity check.

The narration needed **no cuts**: measured audio was 231.72 s, 235.32 s with gaps, under
the 240 s ceiling on the first pass.

**(b) After reviewing the first cut.** I sent a revised B02 line (written in a separate Claude
chat session, approved by me), changed one grid cell, and set the loudness:

> Please make these changes, then re-run all gates:
> 1. Change B02 narration to: "So I checked the official twenty twenty five instructions for
>    Form ten forty N R. Page seven lists fifteen thousand seven hundred fifty as the filing
>    threshold for single students eligible under the India treaty. One run's number matched
>    that figure. The other did not. Neither answer told me which to trust." Regenerate only
>    B02's audio.
> 2. In the B05 grid, show Claude's tax-year cell as "No / No / Partly" (or "1 of 3, partly")
>    instead of "PARTLY".
> 3. Normalize the audio to -16 LUFS.
> If the new runtime goes over 240 s, stop and propose a cut before rendering.
> Keep everything else as is, and tell me the final runtime and the path to the mp4.

Effect: B02 audio went from 17.90 s to **20.71 s**. Narration total 234.53 s, **238.13 s**
with gaps, still under the ceiling, so no cut. B02's two cue phrases were re-pinned to the new
wording ("One run's number matched", "The other did not"). Claude's tax-year cell now reads
"No / No / Partly" (`data/facts.json`), fitted to its cell. `build_mux.py` gained a two-pass
EBU R128 loudnorm step (`--lufs -16`). Only B02 and B05 were re-rendered, then every gate was
re-run through `./build.sh --mux-only`.

**(c) Voice change.** I switched the narrator to a female American English voice:

> Now switch the narration voice to a natural-sounding female American English Kokoro voice.
> List the available voices first; prefer af_heart or af_bella if they exist. Update the voice
> fields in beat_sheet.json, regenerate the narration for all beats with the new voice
> (keeping the new B02 wording), re-time the scenes to the new audio, keep the audio at
> -16 LUFS, and re-run all gates. If the runtime goes over 240 s, stop and propose a cut
> before rendering. Record the voice change in BUILD-PROMPT.md, and tell me which voice you
> chose, the final runtime, and the path to the mp4.

`--list-voices` showed 11 American English female voices (`af_alloy`, `af_aoede`, `af_bella`,
`af_heart`, `af_jessica`, `af_kore`, `af_nicole`, `af_nova`, `af_river`, `af_sarah`,
`af_sky`); both preferred voices were present. **Chosen: `af_heart`**, the voice Kokoro's
own model card rates highest. Both `metadata.voice` and `metadata.voice_kokoro` changed from
`am_michael` to `af_heart`; nothing else in `beat_sheet.json` changed except the measured
durations. A diff confirmed all 13 `narration_text` fields unchanged, B02 included.
af_heart speaks faster: narration 215.05 s, **218.54 s** final with gaps (was 238.13 s), so
no cut. The cues re-time themselves from `mp3/timings.json`, so no scene code changed; all
13 scenes were re-rendered and every gate re-run. The am_michael narration is kept in
`build/mp3_am_michael/`.

**(d) "A I" pronunciation.** Listening, I heard af_heart say "A I" as "ia" in B08 and B09.
I asked for spelling samples first, with nothing else regenerated, and for captions to show
"AI" whatever the narration spelled:

> The af_heart voice says "A I" like "ia" at about 2:22 (B09). It also appears in B08.
> Please: 1. Test a few spellings for B08 and B09 only, for example "A.I.", "A-I", and
> "ay eye", and save a short sample of each so I can listen and pick. 2. Do not regenerate
> anything else until I choose. 3. Keep the on-screen captions showing "AI" whatever
> spelling the narration uses.

`build/ai_spelling_samples.py` voiced only the affected sentence of each beat, in five
spellings, to `samples/ai_spelling/` (`B08_1` … `B09_5`, loudness-matched to −16 LUFS).
Both the script and the samples were test-only and were deleted after I chose.
Checksums confirmed `mp3/` and `beat_sheet.json` untouched. Kokoro's phonemes showed why:
`A I` → `ɐ aɪ` ("uh-eye"); `A.I.` → `ˈeɪ.ˈaɪ.` (pauses); `A-I` → `ˈeɪaɪ` (I unstressed);
`ay eye` → `ˈaɪ ˈaɪ` ("eye eye", wrong); `AI` → `ˌeɪˈaɪ` ("ay-EYE"). `make_srt.py`
gained a caption form map so captions show "AI" for any of these spellings. Then:

> Use "AI" for B08 and B09, then rebuild and re-run all gates

`narration_text` changed "A I" → "AI" in B08 and B09 only (diff-checked). Only those two
beats were regenerated (B08 16.06 → 16.43 s, B09 16.55 → 16.60 s) and re-rendered, then
every gate was re-run through `./build.sh --mux-only`. Final: **219.05 s**.

**(e) Rubric check.** I pasted the assignment description and asked Claude Code to check
the submission against the grading rubric:

> so everything is doe correct;y , most importantly check if we folowed the fgrading.
> rubrics correctly or else I will loose marks

Claude Code compared the film and folder against each rubric line and the honesty rule,
found the out-of-date toolkit (§2), and ran the upstream gates: LOUDNESS, MASTER and T failed.
It asked four questions, and I chose: **−19 LUFS** (inside the gate's window, replacing my
earlier −16); a **3840×2160, 24 fps** master; B08 **"they will run"** in place of "they run"
(Claude Code's proposal, to match "everything else is will"); and all the smaller fixes. While it
worked I added:

> Two notes: 1) FRICTIONAL.md is now written and saved in this folder, so please don't treat
> it as missing, and don't edit it. 2) When regenerating B08, keep the "AI" spelling (not
> "A I"). After all fixes, re-run both the local gates and the upstream gates, and show me the
> results before anything else.

Changes, all re-verified by both gate sets:
- **B08 narration** → "In the first minute, they will run one command, …", keeping "AI".
  Only B08 was regenerated (16.43 → 16.36 s). FRICTIONAL.md was not opened or edited.
- **Midpoint guard** in `Beat.play()`: GATE T samples each clip at its midpoint, so any
  animation that would straddle it (±0.2 s) now starts just after. In B10 a half-drawn red
  strike line had read as a 9 px label on top of the text.
- **B04**: arrow tips stop 0.18 units short of the branch boxes, since GATE T had fused
  arrow and label into one overlapping blob.
- **B05**: the header now reads "MY TEST, OCT 9, 2026 · 3 TOOLS × 3 QUESTIONS · ONE RUN
  EACH", because the honesty rule asks for the date on any chatbot result shown. Date read
  from `data/facts.json`.
- **B11**: the value bar in the red "bad extraction" cell turns light with it; grey on red
  was 2.80:1, under GATE T's 3.0:1 floor.
- **Master** re-rendered at 3840×2160, 24 fps (`render_all.sh "-qk --frame_rate 24"
  2160p24`; 13 scenes in 1:52); `build_mux.py` now writes 24 fps 4K with loudness
  `--lufs -19`; `qc_frames.py` scales frames to 1080p for its sweep.
- **README.md** gained the target role.

Final: **3:38.68 (218.68 s)**. It is slightly under the narration-plus-gaps sum (219.00 s)
because at 24 fps each segment is trimmed to whole frames.

**(f) Documentation.** I approved updating the documents, with one correction:

> Yes, update the docs, with one correction: in SOURCES.md, say the B08 future-tense wording
> was proposed by Claude Code and approved by me, not that it is my wording. Then show me
> README.md and SOURCES.md in full for my review before removing the DRAFT markers.

## 4. Commands actually executed

Environment:

```bash
export ART_HOME="$HOME/Downloads/brutalist/brutalist.art"
export PHONEMIZER_ESPEAK_LIBRARY=/opt/homebrew/lib/libespeak-ng.dylib
export ESPEAK_DATA_PATH=/opt/homebrew/share/espeak-ng-data
PY=/opt/anaconda3/bin/python3
```

Prerequisites:

```bash
which ffmpeg ffprobe manim latex dvisvgm; ffmpeg -version | head -1; manim --version
ls -la "$ART_HOME/runtime/models/kokoro"
$PY "$ART_HOME/runtime/scripts/setup_smoke_kokoro.py"     # kokoro synth OK, -21.8 dB
(cd "$ART_HOME" && ./setup)                               # stopped early, see §2
```

Narration (the toolkit's own script, unmodified):

```bash
cp beat_sheet.json build/beat_sheet.orig.json
$PY "$ART_HOME/runtime/scripts/generate_audio_kokoro.py" . --dry-run   # 13 beats, $0.00
$PY "$ART_HOME/runtime/scripts/generate_audio_kokoro.py" .
# after prompt (b):
$PY "$ART_HOME/runtime/scripts/generate_audio_kokoro.py" . --only B02 --dry-run
$PY "$ART_HOME/runtime/scripts/generate_audio_kokoro.py" . --only B02
```

After prompt (c), all 13 beats with the new voice:

```bash
sed -i '' 's/"voice": "am_michael"/"voice": "af_heart"/; s/"voice_kokoro": "am_michael"/"voice_kokoro": "af_heart"/' beat_sheet.json
$PY "$ART_HOME/runtime/scripts/generate_audio_kokoro.py" --list-voices
$PY "$ART_HOME/runtime/scripts/generate_audio_kokoro.py" . --dry-run
$PY "$ART_HOME/runtime/scripts/generate_audio_kokoro.py" .
# after prompt (d):
$PY build/ai_spelling_samples.py                                        # samples only (since deleted)
$PY "$ART_HOME/runtime/scripts/generate_audio_kokoro.py" . --only B08 B09
# after prompt (e):
$PY "$ART_HOME/runtime/scripts/generate_audio_kokoro.py" . --only B08
```

Final per-beat durations, `af_heart`, final wording (am_michael values in brackets):

| Beat | s | Beat | s | Beat | s |
|---|---|---|---|---|---|
| B01 | 17.39 (19.20) | B06 | 18.09 (19.58) | B11 | 16.53 (18.26) |
| B02 | 19.20 (20.71) | B07 | 14.78 (16.00) | B12 | 17.98 (19.58) |
| B03 | 15.70 (17.26) | B08 | 16.36 (17.37) | B13 | 13.10 (14.02) |
| B04 | 17.39 (18.77) | B09 | 16.60 (18.39) | | |
| B05 | 18.01 (19.48) | B10 | 14.27 (15.91) | **total** | **215.40** (234.53) |

Facts gate, smoke test, then all 13:

```bash
$PY check_facts.py                                           # writes qc_reports/facts_check.txt
manim -ql --disable_caching scene.py B05_Alternatives        # smoke, 480p15
build/render_all.sh -ql 480p15                               # all 13, assertions only
build/render_all.sh -qh 1080p60                              # all 13 @ 1920x1080, 60 fps
manim -qh --disable_caching --media_dir build/mq/B10_Scope scene.py B10_Scope  # after B10 fix
manim -qh --disable_caching --media_dir build/mq/B02_OfficialCheck scene.py B02_OfficialCheck  # prompt (b)
manim -qh --disable_caching --media_dir build/mq/B05_Alternatives scene.py B05_Alternatives    # prompt (b)
build/render_all.sh -qh 1080p60                              # prompt (c): all 13 to the af_heart audio
manim -qh --disable_caching --media_dir build/mq/B08_FirstMinute scene.py B08_FirstMinute  # prompt (d)
manim -qh --disable_caching --media_dir build/mq/B09_Proves scene.py B09_Proves            # prompt (d)
build/render_all.sh -ql 480p15                               # prompt (e): midpoint guard, assertions only
build/render_all.sh "-qk --frame_rate 24" 2160p24            # prompt (e): all 13 @ 3840x2160, 24 fps
manim -qk --frame_rate 24 --disable_caching --media_dir build/mq/B11_Risk scene.py B11_Risk  # B11 contrast fix
```

`build/render_all.sh` renders the scenes in parallel, each with its own `--media_dir`.
A first attempt sharing one media folder failed on 7 scenes: Manim's text cache is not
safe to share between processes.

Toolkit gates (A, W, B) and Week 1 gates:

```bash
for S in B01_TwoAnswers ... B13_Close; do
  $PY "$ART_HOME/runtime/qc/static_scene_check.py" scene.py --class "$S"     # Gate A
  $PY "$ART_HOME/runtime/qc/manim_layout_audit.py" scene.py --class "$S"     # Gate B
done
$PY "$ART_HOME/runtime/qc/wcag_margin_check.py" scene.py                     # Gate W
$PY qc_frames.py --border 16 --step 4   # 4K frames scaled to 1080p; every 4th frame at 24 fps
$PY build_mux.py --gap 0.30            # two-pass loudnorm: -16 LUFS in (b), -19 LUFS since (e)
$PY make_srt.py
```

Gate V on the master, then the final pass through the committed script:

```bash
$PY "$ART_HOME/runtime/qc/final_frame_check.py" . \
    --mp4 BabaEswarappa_Swathi_INFO7375_FinalProjectFilm.mp4 \
    --sheet build/qc_timeline_sheet.json
./build.sh --mux-only        # re-ran every gate above in order; all passed
build/run_upstream_gates.sh  # upstream LOUDNESS, MASTER, SRT, SHARPNESS, T; all passed
```

Verification:

```bash
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate,channels \
        -show_entries format=duration,size -of default=nw=1 BabaEswarappa_Swathi_INFO7375_FinalProjectFilm.mp4
ffmpeg -i BabaEswarappa_Swathi_INFO7375_FinalProjectFilm.mp4 -map 0:a -af volumedetect -f null /dev/null
ffmpeg -i BabaEswarappa_Swathi_INFO7375_FinalProjectFilm.mp4 -map 0:a -af ebur128=peak=true -f null /dev/null
ffmpeg -i BabaEswarappa_Swathi_INFO7375_FinalProjectFilm.mp4 -map 0:a -af silencedetect=n=-45dB:d=1.5 -f null /dev/null
```

Result (`qc_reports/final_master_verification.txt` and `qc_reports/upstream/`):
**3:38.68 (218.68 s)**, 16.9 MB, H.264 **3840×2160 24 fps** yuv420p + AAC 48 kHz stereo;
**−19.0 LUFS** integrated, true peak −1.51 dBTP; no silent beat; 80 caption cues, none
showing "A I". Captions are timed from the narration, so the last cue can end a fraction of
a second after the picture: each segment is trimmed to whole frames.

## 5. Reproducible flags

| Flag | Value | Why it matters |
|------|-------|----------------|
| Python | `/opt/anaconda3/bin/python3` (3.12.2) | `.venv-kokoro` not present; this interpreter passed the Kokoro smoke test |
| Kokoro voice | `af_heart` (was `am_michael` until prompt (c)) | `beat_sheet.json` → `metadata.voice` and `metadata.voice_kokoro` |
| Brutalist toolkit | local copy, commit `29ba0e8` (2026-09-15); upstream gates from `519fcbb` (2026-10-12) | scripts used unmodified; nothing written into the toolkit's files |
| Manim quality | `-qk --frame_rate 24` → 3840×2160 @ 24 fps | GATE MASTER spec; `--disable_caching`, per-scene `--media_dir` for parallel renders |
| inter-beat gap | `0.30 s` | 12 gaps = 3.60 s of the runtime (218.68 s total) |
| x264 | `-preset medium -crf 18`, `yuv420p` | visually lossless, widely playable |
| audio | AAC 192 kbps, 48 kHz, stereo | two-pass `loudnorm I=-19:TP=-1.5:LRA=11`, linear; inside GATE LOUDNESS's −28…−18 window |
| runtime gate | `120 ≤ d ≤ 240` s | `build_mux.py` exits non-zero outside 2–4 min |
| frame-safety gate | outer `16 px` at 1080p scale, every `4th` frame | `qc_frames.py` |
| midpoint guard | `MID_PAD = 0.2 s` | no animation within 0.2 s of a clip's midpoint, where GATE T samples |
| chrome rules | `±6.25` x, `±3.0` y (units) | inside the toolkit's 5% title-safe area; Week 1's ±6.85 would bleed under Gate V |
| DIM grey | `#8A8A90` | Week 1's `#6B6B70` is about 3.6:1 on the ground; this is 5.73:1 (WCAG AA) |
| captions | ≤ 2 lines × 42 chars per cue | rule 4: short captions; timed by word position |
| Gate V timeline | `build/qc_timeline_sheet.json` | measured segment length + 0.30 s gap per beat |

## 6. Verification built into the build

- `check_facts.py`: every fact's spoken form found in its beat (18 checks), every B05 grid
  cue found (6), no digit in any `scene.py` string literal except beat ids, hex colours, the
  JSON paths it loads and log format specs. Numbers shown but not spoken are listed in the
  report with notes: the date "Oct 9, 2026" (B01 cards, B05 header), the 2023–2025 tabs
  (B03), PR #6 (B12).
- `Beat.play()` now runs `assert_in_safe_area()` and `assert_no_text_overlap()` after
  **every** animation, not just at `lock()`, so a mid-beat collision that is later cleared
  cannot pass. `assert_in_safe_area()` also checks left/right, not only top/bottom.
- `REAL_MANIM` guard: Gate A runs `construct()` against a stub Manim with placeholder
  geometry, so the `Beat` geometry assertions skip themselves there and run in every real render.
- Midpoint guard in `Beat.play()` (prompt (e)): the frame upstream GATE T samples is always settled.
- `lock()` flags any trailing hold over 2.5 s. Final worst hold: **2.13 s** (B06).
- **Gate A** caught B13 as "shapes never change", an all-text beat that also broke rule 6.
  B13 now draws solid ticks for what exists and dashed markers for what will exist.
- **Gate B**'s first pass flagged the footer source line touching the safe edge (x = 6.30)
  in four beats; the chrome moved in to ±6.25. Remaining warnings, reviewed against frames:
  B03 "label on a line" (back-page outlines hidden under the filled front page) and B10
  (the red strike-through lines are intentional).
- **Gate A** B08 warning: the stub placed one terminal line at y = −3.4; the real render
  puts it at y ≈ −2.6, and the real safe-area assertion passed.
- **Frame review by eye** (`qc_reports/end_frames_all_beats.png`) caught one defect no
  gate saw: B10's "tests pass on a fresh clone" ran into its dashed box, a text-on-shape
  overlap. Fixed, with an explicit in-scene check for that label.

## 7. One-command rebuild

```bash
./build.sh              # facts -> narration -> Gates A/W -> scenes -> Gate B -> frames -> mux -> Gate V
./build.sh --mux-only   # skip narration and render; re-run every gate and re-mux
build/run_upstream_gates.sh   # current upstream toolkit gates -> qc_reports/upstream/
```
