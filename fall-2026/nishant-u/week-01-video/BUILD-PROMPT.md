# BUILD-PROMPT

## The main prompts I gave Claude Code (2026-09-26/27, in order, condensed)

1. **Plan.** "I'm making a class explainer video (2–3 minutes) with this toolkit. Use the free
   pipeline only: Kokoro narration, Manim for equations, Remotion if needed. No ElevenLabs, no
   Higgsfield, no API keys, nothing uploaded." Read the README and the ai-explainer skill and say
   whether ai-explainer or hai fits. Create `beat_sheet.json` from my 8-beat script. Use the
   numbers exactly as written from `maxsub_runs.py` output (2026-09-26). Equations in Manim
   MathTex. "Source: maxsub_runs.py output, 2026-09-26" wherever real output appears. Don't
   render; show the summary and wait.
2. **Decisions and first draft.** Skip all four framing beats; add a silent 3 s title card
   ("Why subtracting the max changes nothing that matters · Nishant · INFO 7375 Week 1").
   Precise labels: "Totals computed from printed values." (B03, B04) and "Worked by hand from the
   formula." (B06 middle steps). B07: "differ in the last digit". Generate Kokoro narration,
   render a first draft, report runtime and failures.
3. **Draft 2.** Add [1000, 1001] and [0, −1000] to `maxsub_runs.py`, rerun it, and show the full
   output. New beat B06b from the real values (3 decimals, labelled). Extend B08 with the
   [0, −1000] case. B03 "Done directly" → "Computed directly". About 0.8 s of silence between
   beats. Regenerate, re-render, QC.
4. **Paperwork and master.** Create `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md`. FACTCHECK lists
   every on-screen number, its source (printed / computed / by hand) and date, honestly. Render
   the clean master with no beat IDs or timecode, check the frames, report.
5. **B07 correction.** "for two of the three probabilities, the methods differ in the last
   digit". Regenerate only B07's audio, rerun `pad_gaps.py`, re-render only B07, update
   FACTCHECK and SHOTLIST, run the final build. If GATE T flags small source labels, enlarge
   rather than remove them.
6. **Sign-off.** Update the FACTCHECK status line with my review. Delete the "no human review"
   bullet. Fix row 11 so raw and shifted probabilities are shown correctly. Remove "and no human
   has re-run the script".
7. **Write-ups.** README, FRICTIONAL, SOURCES, BUILD-PROMPT, and a list of which files to submit.

## Exact rebuild commands (Git Bash, Windows)

`maxsub_runs.py` expects the course repo cloned at
`%USERPROFILE%\info-7375-prompt-engineering-for-generative-ai` (`~/info-7375-prompt-engineering-for-generative-ai`
in Git Bash). It imports `probabilities()` from
`lessons/01-randomness-and-first-prompts/code/main.py` there, and fails if the repo is elsewhere.

```bash
cd ~/week-01-video
python maxsub_runs.py > maxsub_runs.stdout.new.txt
diff maxsub_runs.stdout.txt maxsub_runs.stdout.new.txt && echo "output matches"

python ~/brutalist.art/runtime/scripts/generate_audio_kokoro.py ~/week-01-video
python pad_gaps.py

cd manim
for pair in B00:TitleCard B01:OverflowOpen B02:SoftmaxDefinition B03:RawPath \
            B04:ShiftedPathSideBySide B05:ShiftInvariance B06:OverflowVsShifted \
            B06B:GapNotSize B07:LastDigit B08:Limits; do
  b=${pair%%:*}; c=${pair##*:}
  python -m manim render -r 3840,2160 --fps 24 --media_dir ../_manim_build \
         --disable_caching -v ERROR scenes.py "$c"
  cp "$(find ../_manim_build/videos -name "$c.mp4" | head -1)" "$b.mp4"
done
cd ..

cd ~/brutalist.art
bash ./art final ~/week-01-video --out ~/week-01-video
```

`./art final` runs Gate T (typography), Gate F (paperwork), the beat lint, and Gate V (frame
check) before writing `week-01-softmax-max-subtraction.mp4`. It refuses to build if any gate
fails.
