# BUILD-PROMPT — final-project-pitch-nishant-u

The main prompts I gave Claude Code on 2026-10-14, in order, then the exact commands that rebuild the
film from a fresh Brutalist checkout. Local paths are written with `~` (my home folder). Short
follow-ups (a `cd`, "yes") are left out.

## Prompts

### 1. Setup check

> I'm making a 2–4 minute narrated pitch film with this Brutalist checkout. I used it on 2026-09-26
> for a Week 1 explainer: I installed ffmpeg (winget Gyan.FFmpeg) and MiKTeX, applied local fixes saved
> in brutalist-fixes.diff, and ran with PYTHONUTF8=1. Free local pipeline only: no paid generation, no
> API keys, no uploads.
> 1. Run git status and git pull. Tell me whether upstream changed and whether my local fixes still
>    apply. Don't overwrite or discard them without asking me.
> 2. Confirm ffmpeg, ffprobe, pdflatex, and the Kokoro voice still work.
> 3. Check whether a show-tell skill exists. Summarize its format: beat structure, picture style,
>    on-screen text rules, and the expected beat_sheet.json schema.
> 4. List every quality gate the toolkit provides (including render-integrity), with the exact command
>    for each and where it writes its report.
> 5. Run the smoke test with PYTHONUTF8=1.
>
> Report each item as pass/fail with the exact error if any. Do not install anything without asking.

### 2. Decisions after the setup check

> 1. Smoke test: do NOT change Gate V or any quality check. Instead, move the review-cut timecode
>    burn-in into the bottom-left strip that Gate V already masks, so my Windows fix and the gate agree.
>    Also tell me whether the timecode appears only in the review cut or also in the final master. Rerun
>    the smoke test with PYTHONUTF8=1 and report pass/fail. Update brutalist-fixes.diff with this change.
> 2. show-tell: I'll use its format, because my assignment says show-tell is the right format for a
>    pitch. But my rules say narrate as myself and don't use the instructor's name, persona, or credit
>    line. So for my film: no "Liam"/"Bear" greeting, no claude-liam channel, no BHTF "Your turn"
>    bookend; first-person narration as Nishant; a Kokoro voice that is NOT the persona's am_onyx (list
>    the available Kokoro voices and suggest one male American voice); keep isometric Manim pictures,
>    1–3 word labels, at most 2–3 per beat, size ≥32, title-safe area. Tell me which beat types (BIDEA,
>    BDEFS, BOUT, etc.) I can keep, which I must drop or rename, and whether bookend_exempt is needed if
>    I remove bookends.
> 3. Show me the finished quality-gate inventory: name, exact command, report location, and which ones
>    apply to my final film.
> 4. Then create ~/info-7375-prompt-engineering-for-generative-ai/fall-2026/nishant-u/final-project-film/FRICTIONAL.md
>    with dated entries (2026-10-14) for: the pull; ./setup exiting on the upstream ElevenLabs guard; the
>    smoke-test Gate V edge-bleed; the show-tell sign-off note in CLAUDE.md, and my decision to use the
>    format without the persona.

### 3. Branch

> Yes, make a new branch for this assignment. Base it on the course repo's main branch (the
> upstream/original main, not my Week 1 branch), so my Week 1 files don't get mixed in. Name it
> nishant-u-final-project-film. Carry the untracked final-project-film/ folder over to it. Don't commit
> anything yet. Show me git status when done.

### 4. The brief

> Create fall-2026/nishant-u/final-project-film/PROJECT-BRIEF.md: one page answering the seven pitch
> questions below in plain sentences. Keep my wording; only tighten. Rules: past tense only for things
> that exist; everything else uses "will". Invent no users, metrics, or results. End with two lists,
> "Exists today" and "Will exist". […the "Exists today" list to verify, and my answers to Q1–Q7, as
> they now appear in PROJECT-BRIEF.md…] Then add a dated 2026-10-14 entry to FRICTIONAL.md […]. Also
> note that the Jobright claim in Q2 comes from a third-party review (careery.pro, 2026), so I can list
> it in SOURCES.md later. Show me the finished brief and the "can't verify" results.

### 5. The beat sheet

> 1. In PROJECT-BRIEF.md, change "In this course I already shipped two pieces" to "In this course I
>    already submitted two pieces". Nothing else changes.
> 2. Write fall-2026/nishant-u/final-project-film/beat_sheet.json for my pitch film, using the show-tell
>    format from skills/make/show-tell/ (follow reference/example-make_sheet.py for the schema) with these
>    changes: no persona (no "Liam"/"Bear" greeting, no claude-liam channel, no persona field, no BHTF or
>    BOUT; BDEFS folderLabel ""; channel_title unset); voice am_michael, engine kokoro, for every beat;
>    bookend_exempt ["cold-open","bvdt","bhtf"] with a reason; slug final-project-pitch-nishant-u; title
>    "A job-search agent that shows its evidence". Structure (target ~3 minutes, about 400–450 spoken
>    words, short sentences, first person as Nishant): BIDEA the problem in one line; BDEFS 2–3 terms;
>    body beats Q1–Q7 in order, then one "exists today vs will exist" beat; BEND a final drawn Manim beat
>    with my name and the working title as labels. Narration must use the exact facts in
>    PROJECT-BRIEF.md: past tense only for things in "Exists today"; "will" for everything else. No
>    invented numbers, users, or results. Pictures: one simple isometric Manim drawing per beat in the
>    show-tell style, with labels of 1–3 words, at most 2–3 per beat, size 32 or more, inside the
>    title-safe area. Any picture showing the agent's output, a shortlist, a scorecard, or a posting with
>    evidence labels must carry an on-screen "constructed" label, because none of it exists yet. Don't
>    draw LinkedIn or Jobright logos; use generic shapes with the names as text labels. On the Jobright
>    beat, add a small source label "careery.pro review, 2026". Don't render yet.

### 6. Decisions on the first draft

> 1. Keep the length. Don't cut B07 or B11.
> 2. BDEFS: use these terms and narration (my course defines "record" as the deterministic rule
>    verdict, not the posting line): "Two verdicts", "Evidence labels", "Human gate" […].
> 3. BEND labels: "Nishant U" and "Job-search agent". BEND narration […].
> 4. Re-run make_sheet.py, then build_safety and skin-lint again.
> 5. Create the files the build needs: SHOTLIST.md and PROMPTS.md in the format the toolkit expects;
>    FACTCHECK.md listing every factual claim in the narration with its source, each marked
>    "unverified — Nishant to sign off", with a sign-off line for me, unsigned.
> 6. Generate the narration audio only (Kokoro, local), with no video render. Report each beat's
>    actual_duration_s and the real total runtime. Listen-check the pronunciations […].
> 7. Add a FRICTIONAL.md entry for today […].

### 7. Name and trims

> 1. My name was pronounced wrong. In the BIDEA and BEND narration, spell it "Nee-shaant" for the voice
>    only. Keep "Nishant U" as the on-screen label and "Nishant" in every written file. Transcribe both
>    beats again to check.
> 2. Replace the BEND narration with […].
> 3. Trim these lines to get the runtime to about 3:40 (no facts lost): B03, B05, B08, B10, B11 […].
> 4. Re-run make_sheet.py, re-voice only the changed beats, then update SHOTLIST.md and the matching
>    FACTCHECK.md rows (fix the "raw" mismatch it noted). Report the new total runtime.
> 5. Add one FRICTIONAL.md line […].

### 8. The build

> 1. Name is fine now; keep "Nee-shaant".
> 2. Small fixes, then re-voice only these two beats: B05 […], B11 […]. Update SHOTLIST.md and the
>    matching FACTCHECK.md rows. Report the new total runtime; it must stay under 3:55.
> 3. Then build the film: write manim/scenes.py with one isometric scene per body beat (B00–B11, BEND),
>    following the show-tell skill and templates/iso_kit.py, using exactly the visuals, labels and
>    "constructed" flags already in beat_sheet.json. Run the pre-render gates (A, W) and fix anything they
>    flag. Render with art run (free local pipeline, PYTHONUTF8=1), then art final into the
>    final-project-film folder. Don't weaken or skip any gate. If one fails, fix the scene and re-render.
> 4. Report: the path to the final mp4, its real runtime, and pass/fail for every gate that ran […].
> 5. Add FRICTIONAL.md entries for anything that broke during the render and how you fixed it.

### 9. Fact-check sign-off

> I checked every FACTCHECK.md row against its source myself, including opening the careery.pro
> review. Change all verdicts to PASS and fill the sign-off with "Nishant U — 2026-10-14". Then run
> factcheck_check.py and report the result.

### 10. Submission

> The film is approved; I watched it fully on 2026-10-14. Finish the submission in
> fall-2026/nishant-u/final-project-film/: README.md, BUILD-PROMPT.md, SOURCES.md, gate reports,
> clean-up check and .gitignore, commit only this folder on branch nishant-u-final-project-film, push to
> my fork, build the zip on my Desktop, and add a final FRICTIONAL.md entry.

## Rebuild commands

Tested on Windows 11 with Git Bash, Python 3.12, Manim Community 0.18.1, ffmpeg 9.0.2, Node.js and Google
Chrome. Everything is free and local: no API keys, no paid calls, no uploads.

```bash
# 1. Brutalist toolkit at the commit this film was built on, plus my local fixes
git clone https://github.com/nikbearbrown/brutalist.art ~/brutalist.art
cd ~/brutalist.art
git checkout 519fcbb
git apply ~/info-7375-prompt-engineering-for-generative-ai/fall-2026/nishant-u/final-project-film/brutalist-fixes.diff

# 2. Dependencies: Python packages, Remotion's node_modules, the free Kokoro model.
#    setup installs first, then may stop on its ElevenLabs guard (toolkit example files); see FRICTIONAL.md.
./setup --install

# 3. Environment for every command below
export PYTHONUTF8=1                                    # Windows console: UTF-8 output
export PATH="$(python3 -c 'import sysconfig; print(sysconfig.get_path("scripts", "nt_user"))'):$PATH"
                                                       # manim.exe lives in the Python user Scripts folder
export ART_CHROME="C:/Program Files/Google/Chrome/Application/chrome.exe"
export ART_CHROME_MODE=chrome-for-testing              # Remotion uses installed Chrome; no browser download
F=~/info-7375-prompt-engineering-for-generative-ai/fall-2026/nishant-u/final-project-film

# 4. Beat sheet (narration lives in make_sheet.py NARRATION)
cd "$F" && python3 make_sheet.py

# 5. Narration audio: Kokoro am_michael, local; writes mp3/ and measured durations into the sheet
python3 ~/brutalist.art/runtime/scripts/generate_audio_kokoro.py "$F"

# 6. Review cut: Gates build_safety, F, L, A, W, B, then the Remotion bookends, compile, Gate V
cd ~/brutalist.art && ./art run "$F"

# 7. Clean 4K master into the film folder: Gate T, then encode, render-integrity, Gate V, .verified.json
./art final "$F" --out "$F"
```

Notes:
- `scenes.py` must sit at the film folder's root (not `manim/`): `run.sh` renders only from
  `<reel>/scenes.py`, and the kit's pacing reads `beat_sheet.json` beside it. It registers the toolkit's
  EB Garamond font (`~/brutalist.art/runtime/fonts/EB_Garamond/`) itself, or `$ART_HOME` if set.
- `art run` renders only beats whose `manim/<BID>.mp4` is missing; after editing a scene, move its old
  clip and `media/videos/` aside before re-running.
- Optional check: `python3 ~/brutalist.art/runtime/qc/factcheck_check.py "$F"` (clean as committed).
