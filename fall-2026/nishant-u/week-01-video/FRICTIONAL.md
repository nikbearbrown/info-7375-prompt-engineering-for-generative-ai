# FRICTIONAL — what went wrong and what I did

Entries marked **(before the build session)** happened while setting up the toolkit, before the
Claude Code session that built the video. For those, only the evidence listed is on record.

## 2026-09-26

**Setup's ElevenLabs guard stops `./setup` (before the build session).**
`./setup --install` installed everything (Python packages, 189 Remotion modules, fonts, the Kokoro
model) but then exited early. Its "ElevenLabs guard" matched ElevenLabs code patterns in 10 files
under `youtube/brutalist/` (e.g. `claude-liam-brutalist-command-setup/beat_sheet.json`); these
are the toolkit's own example files. Re-checked 2026-09-27: it still matches the same ten files.
What I did: I approved running a temporary copy of the setup script with the guard removed, in
the session scratchpad, to run the readiness checks. No repo files changed. Result: everything
was ready except Manim equation beats (`pdflatex` and `dvisvgm` were missing).

**ffmpeg was missing (before the build session).**
Setup reported ffmpeg missing. I installed it with `winget install Gyan.FFmpeg` (ffmpeg 9.0.2,
gyan.dev full build; install folder dated 2026-09-26 15:22) and reopened the terminal. The
readiness check then showed ffmpeg and ffprobe working, and the Kokoro voice test passed.

**Installed LaTeX (before the build session).**
Manim's `MathTex` needs a LaTeX install, and setup had found `pdflatex` and `dvisvgm` missing. I
installed MiKTeX with `winget install MiKTeX.MiKTeX` (MiKTeX 25.12, folder dated 2026-09-26
15:27). I verified it with a test Manim MathTex render of the softmax formula (exit code 0).

**Smoke-test bugs (before the build session). Fixes (a) and (b) are in `brutalist-fixes.diff`, 15:39.**
`./art smoke` failed on three issues. I approved local fixes for (a) and (b); for (c) no code was
changed.
- *(a) Slug:* `build_safety.py` rejected the smoke fixture's slug `_smoke`, because a slug must
  start with a letter or digit. Changed it to `smoke`, with the matching one-line change in
  `runtime/scripts/smoke_test.sh` (`_smoke-slate.mp4` → `smoke-slate.mp4`).
- *(b) Windows font path:* `compile.py` passed a raw Windows font path into ffmpeg's `drawtext`
  filter, where `\` is an escape character and the drive-letter colon splits options. Added
  `ffmpeg_filter_path()` to convert it to forward slashes and escape the colon. This fix was used
  in this build: the review cuts' timecode burn-in rendered with it.
- *(c) UTF-8 console:* Python crashed printing "→" to the cp1252 Windows console (`'charmap'`
  codec error). No code was changed; the run used `PYTHONUTF8=1`.

After these, the smoke test rendered a 13.9 s mp4. Visual QC flagged the review timestamp
overlay as edge bleed. I stopped there, since the render itself worked.

**Skipped the ai-explainer framing beats on purpose.**
The ai-explainer skill requires a Claude-app cold open, a typed overview, a "Your turn" prompt,
a title outro, and the narrator saying "Liam, in for Bear". I skipped all of them and used a
silent 3-second title card. I wanted a class explainer of my own script, not a channel episode,
and the extra beats would have added 30–45 s. The skip is recorded in `beat_sheet.json`
(`_comment_skipped_framing`); every build still prints two skin-lint warnings about it.

**First draft ran 88.5 s, not 2–3 minutes.**
My beat estimates added up to 170 s, but Kokoro reads the script in 85.5 s (plus the 3 s title).
The toolkit's rule is that measured narration sets the clock, so I didn't stretch visuals or pad
the ending.

**Final master blocked at first: missing paperwork.**
`compile.py` refused a clean master without `FACTCHECK.md`, `SHOTLIST.md` and `PROMPTS.md`. Drafts
1 and 2 were built as review cuts until those existed.

## 2026-09-27

**Added two evidence beats rather than padding.**
I added cases to `maxsub_runs.py` and reran it: [1000, 1001], [0, 1] and [0, −1000]. Their real
output became beat B06B ("same gap, same answer") and an extension of B08 (underflow to exactly
0.0). I also added a 0.8 s pause after each narrated beat except the last (`pad_gaps.py`), about
6.4 s in total. The runtime went from 88.5 s to 116.4 s.
The requested beat id `B06b` had to become `B06B`, because the toolkit rejects lowercase ids.

**Kokoro and "Done directly".**
A transcript of draft 1 heard B03's opening "Done directly" as "Undirectly". I changed the line
to "Computed directly". In draft 2 the isolated beat audio said "Computed directly", but a
full-cut transcript still heard only "Directly". In the final master, two speech-to-text models
both hear "Computed directly". The transcripts are the evidence; I didn't confirm by ear that
Kokoro itself mispronounced "Done".

**B07 wording correction.**
The original line "the two methods differ in the last digit" was not true of every value: p₁ and
p₃ differ in the last digit, but p₂ is identical on both paths. Changed to "for two of the three
probabilities, the methods differ in the last digit", then regenerated and re-rendered only B07.
FACTCHECK row 35 records it as CORRECTED.

**Quality gates failed the first 4K master; fixed the layouts.**
- *Gate T (type check):* B05's terracotta text was 2.74:1 on cream, below the 4.5:1 WCAG minimum.
  Every accent-coloured glyph moved to a darker `#A44A32` (5.11:1); the lighter terracotta stayed
  for lines and boxes only.
- *Gate V (frame check):* 9 BLOCKER and 4 MAJOR findings. The source labels sat inside the frame's
  safe margin, the B07 numbers were too wide, and three frames were too empty (B00, and B02 and
  B06B mid-beat). I fixed them by moving labels, resizing, and re-laying out B02 (two columns) and
  B06B (inputs shown first with "p = ?" placeholders). I didn't use the gate's `sparse_by_design`
  waiver.
- Found by eye, not by either gate: after one fix, a B06B source label overlapped "gap of 1 in
  both". Split the label onto two lines.
- Earlier, a Python patch run through the shell turned two TeX backslash sequences into control
  characters and broke `scenes.py`. Repaired using character codes.

**`_qc/REPORT.md` was overwritten.**
The final build's frame check writes its own report to `_qc/REPORT.md`, and it replaced the manual
QC notes from drafts 1 and 2. Restored them to `_qc/MANUAL-QC.md`, which the gate does not touch.

**Row 11 error caught in my FACTCHECK review.**
Row 11 (B04) listed only the shifted probabilities, under both the "raw" and "shifted" labels. I
caught it while reading every row against `maxsub_runs.stdout.txt` and re-running the script.
The row now lists the raw [0.09003057317038045, 0.24472847105479764, 0.6652409557748219] and
shifted [0.09003057317038046, 0.24472847105479764, 0.6652409557748218] values separately.
