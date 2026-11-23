# BUILD-PROMPT

These are the commands that rebuilt the film, in the order they ran. My
working prompts to Claude Code were many and checkpoint by checkpoint
(FILM-CP1 to FILM-CP11, 2026-11-21 and 2026-11-22), and are not reproduced;
a reconstructed summary is at the end.

## Prerequisites
- The Brutalist toolkit (github.com/nikbearbrown/brutalist.art) at revision
  22264a332f6bf8825cdd639bcd33864563801f55 (2026-10-03), the same as my
  pitch film. My checkout has three local changes, all from Assignment 1
  (my Assignment 1 folder's SOURCES.md, line 12; my pitch film's
  SOURCES.md, lines 42-45):
  - ten example files under youtube/brutalist/ deleted, because they trip
    ./setup's ElevenLabs guard; the film uses none of them;
  - runtime/remotion/package-lock.json regenerated; the film has no
    Remotion beats;
  - a 9-line patch to runtime/scripts/compile.py, so that the Gate V check
    inside ./art final honors ART_STRICT the way run.sh does and fails only
    on exit code 2 or more. It made no difference here: ART_STRICT was at
    its default (1), and the final's Gate V reported "Clean — no
    BLOCKER/MAJOR defects", which it writes only when it finds no defect of
    any severity (exit 0).
- Python: the toolkit's .venv, Python 3.11.16, first on PATH. Packages the
  build used, as installed: manim 0.18.1, kokoro-onnx 0.6.1, onnxruntime
  1.30.0, phonemizer 3.4.0, espeakng-loader 0.2.4, numpy 2.4.6, Pillow
  10.4.0, scipy 1.17.1, ManimPango 0.5.0, pycairo 1.29.1.
- ffmpeg and ffprobe 9.0.2.
- Node v20.20.2 (Homebrew's keg-only node@20). The toolkit expects it; this
  film has no Remotion beats.
- The Kokoro model files kokoro-v1.0.onnx and voices-v1.0.bin in the
  toolkit's runtime/models/kokoro/, which ./setup downloads from the
  kokoro-onnx "model-files-v1.0" release.
- The EB Garamond font installed where Pango finds it (my installed
  EBGaramond-Regular.ttf is byte-identical to the toolkit's
  runtime/fonts/EB_Garamond/static/ copy), and Menlo, which ships with
  macOS (B11's fingerprint).
- LaTeX is not needed: no scene uses MathTex or Tex.

## Environment (same for every step)
export PATH="<TOOLKIT>/.venv/bin:<NODE20>/bin:$PATH"
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR=<SCRATCH>
R=<this folder>

<TOOLKIT> is the brutalist.art checkout, <NODE20> is Node 20's install
folder, <SCRATCH> is a scratch folder outside the repo, and R is the
absolute path to this folder (fall-2026/prasad-s/final-film-job-search-agent)
in my clone of the course repo. PYTHONDONTWRITEBYTECODE=1 keeps __pycache__
folders out of the repo. No gate override was set at any step: ART_QC,
ART_STRICT and ART_FACTS were at their defaults, which are all on.

## The voice pipeline
1. make_sheet.py reads NARRATION.md and writes beat_sheet.json: 17 beats,
   B1 to B17, each with its narration, its scene fields from SHOTLIST.md,
   and engine "kokoro-paused". It refuses to write if any narration line
   contains my surname. On a re-run it keeps each beat's actual_duration_s,
   audio_file, pieces and tts_phoneme_overrides while that beat's narration
   is unchanged.
2. tools/voice_with_pauses.py voices every beat. Kokoro barely pauses at a
   full stop, colon or dash, and kokoro-onnx's own sentence_pause and
   clause_pause need per-phoneme timings that this model does not output.
   So the script splits each narration line after . ? ! and after : ; and
   em dashes, voices each piece separately at speed 1.0 in am_onyx with the
   toolkit's own functions, and joins the pieces with silence. The setting
   is A: 0.30 s after a sentence, 0.15 s after a colon, semicolon or dash
   (setting B, 0.45 s and 0.25 s, was tested and not chosen).
   - The trim: each piece is cut at 35 dB below its loudest 10 ms, which
     drops the model's low hum after a piece; from each edge, the cut then
     walks outward through quiet frames that are mostly above 3 kHz (louder
     than -50 dB, at least 40% of their energy above 3 kHz, gaps of up to
     50 ms, at most 250 ms), so a quiet final s, z, f or t release is kept,
     and then keeps 30 ms more. The first version, cut at 35 dB alone,
     clipped the final sibilant of "applications" (B3), "postings" (B13)
     and "less" (B15); the second version kept them.
   - B1's "Prasad": the piece that says it is phonemized as the toolkit
     would, espeak-ng's pɹˈæsæd is swapped for pɹəsˈɑːd, and the piece is
     voiced with is_phonemes=True. The swap is copied from my Assignment 1
     override (week-01-video/tools/kokoro_phoneme_override.py), which is
     unchanged. B1 records tts_phoneme_overrides the way that script did.
   - It writes mp3/beat-<id>.mp3 and mp3/timings.json, and each beat's
     actual_duration_s, audio_file and pieces (each sentence or clause with
     its start_s and end_s in the beat's audio). scenes.py places every cue
     from those pieces.
3. The toolkit's stock runtime/scripts/generate_audio_kokoro.py is not part
   of the rebuild. It voices only beats whose engine is "kokoro", so it
   skips every "kokoro-paused" beat; if it voiced them, it would replace
   the paused narration and drop B1's swap. From FILM-CP5 to FILM-CP9 the
   stock script voiced the narration, and the Assignment 1 override,
   run in place, voiced B1; tools/voice_with_pauses.py replaced both in
   FILM-CP10.

## Steps
Order from scratch: beat_sheet.json is committed with the measured audio,
the pieces and the final's build records, but mp3/ is gitignored. A rebuild
can start at step 3 only where mp3/ exists. From a fresh clone mp3/ is
missing, so run step 2 first; re-voicing may shift the durations slightly,
and the scenes follow them. To regenerate the sheet itself, run step 1,
then step 2.
1. Sheet (in R): python3 make_sheet.py
2. Narration (in R): python3 tools/voice_with_pauses.py .
   It finds the toolkit at brutalist.art beside the course repo, or at
   $ART_HOME. 17 beats, 221.48 s in all.
3. Review cut (in <TOOLKIT>): ./art run "$R" --height 2160, then
   ./art todo "$R"
4. Final (in <TOOLKIT>): ./art final "$R" --height 2160 --out
   "$R/exports/landscape"
5. Master check (in <TOOLKIT>): python3 runtime/scripts/master_check.py
   "$R" --mp4 "$R/exports/landscape/job-search-agent-film.mp4"
6. Duration and hash: ffprobe the master and run shasum -a 256 on it (see
   "The duration check by hand").
7. Receipts: copy MASTERCHECK.md and
   exports/landscape/job-search-agent-film.verified.json into receipts/ as
   MASTERCHECK.redacted.md and job-search-agent-film.verified.redacted.json,
   with the home-folder path replaced by <home>.

## The three review builds
Every build ran ./art run "$R" --height 2160 with strict gates, and
rendered all 17 scenes.
- Review cut 1, FILM-CP8: the 17 scenes from SHOTLIST.md, with
  the narration voiced by the stock script (B1 by the Assignment 1
  override). 206.208 s.
- Review cut 2, FILM-CP9: the fixes from my review of cut 1
  (part labels; B1's tagline and a smaller disclosure footer; B2's Approve
  click; B3's title; B4's ILLUSTRATION label and "snake oil" gloss; B5's
  not-to-scale note and earlier "1 offer"; B6's paraphrase of AP2; B9
  without condition ids; B11's answer from Alex's profile; B12's "Next"
  shown longer). B3 and B6 were re-voiced. 205.708 s.
- Between cut 2 and cut 3, FILM-CP10: the narration was re-voiced
  with pauses by tools/voice_with_pauses.py, and B3 now opens "It matters
  because hiring is flooded."
- Review cut 3, committed in FILM-CP11: every scene rebuilt for
  the paused audio, with every cue placed from the pieces. A cue phrase
  that matches none of its beat's pieces raises an error naming the beat
  and the phrase. Before the build, the old clips were moved into
  _superseded/review-cut-2/. 221.750 s.

Gate results, the same in all three builds (GATE-LOG.md has the lines):
Gate F passed; Gate L "clean — beat mix OK"; Gate SHAPE skipped, not a
finance reel; Gate A 17 of 17 clean, 0 warnings, 0 errors; Gate W 17 of 17
clean; Gate B 17 of 17 CLEAN; Gate V frames=34 BLOCKER=0 MAJOR=0;
./art todo 17 of 17 filled.

## The final and the master
./art final ran once, on 2026-11-22. Gate T passed on 17 of 17 beats at the
first attempt (TYPECHECK.md: Overall PASS, FAILs 0), and the final's own
Gate V check on the master was clean. master_check.py printed
"[master] PASS  3840×2160  24fps  yuv420p  h264  221.8s" (GATE MASTER:
PASS).

My master: exports/landscape/job-search-agent-film.mp4, 3840×2160, 24 fps,
video H.264 (High, yuv420p), audio AAC (LC, 48 kHz, stereo), 221.750 s,
20,095,046 bytes, SHA-256
a0e5c025c58bfcac867d1242499f4aab0bd5e83ee6cc811cee57a2aff0dc1b54 (it
matches the sha256 field of the export receipt). A rebuild may not be
byte-identical, so its hash may differ.

## The duration check by hand
master_check.py's duration assertion was skipped: it imports clock_check.py,
which is missing from the toolkit at this revision (MASTERCHECK.md, Notes).
So I checked the duration with ffprobe instead. The master runs 221.750 s.
That equals the sum of the 17 render_duration_s values in beat_sheet.json
(221.750 s), and is 0.270 s over the sum of the 17 actual_duration_s values,
the narration (221.48 s). The difference is frame rounding: each beat's
clip is rounded up to a whole frame at 24 fps.

## What not to do
- Don't re-run make_sheet.py after ./art final: it rewrites beat_sheet.json
  and drops the build records (metadata.build, each beat's build and
  render_duration_s).
- Don't rebuild without first moving the old clips into _superseded/:
  ./art run renders only a scene whose manim/<beat>.mp4 is missing, so it
  would reuse old clips cut to old lengths. Move everything in clips/,
  manim/ and media/ into _superseded/<name>/ first, as was done for
  review-cut-1 and review-cut-2.
- Don't run the stock generate_audio_kokoro.py on this folder (see "The
  voice pipeline").
- Don't commit the master or anything in exports/: .gitignore excludes
  *.mp4 and exports/.

## Authoring prompt (reconstructed summary, not verbatim)
"In this folder, write make_sheet.py (it writes beat_sheet.json from
NARRATION.md: 17 beats, B1 to B17, voice am_onyx) and scenes.py: one drawn
Manim scene per beat, named <beat id>_<Name>, built from SHOTLIST.md with
the toolkit's show-tell drawing kit, labels as SHOTLIST.md gives them. Don't
change the narration or anything in mp3/. If a shot can't be done as
written, stop and ask me. Pre-check in scratch at low resolution with Gates
A, W and B and Gate V's frame check, then build the 4K review cut. Don't run
./art final until I say so, and don't stage or commit."
