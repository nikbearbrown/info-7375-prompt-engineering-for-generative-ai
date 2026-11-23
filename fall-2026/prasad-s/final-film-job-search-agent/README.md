# WorthLoop: the final project film

Final Project Film, INFO 7375, due 2026-11-23. Prasad Shinde.

This film presents my final project, WorthLoop: an agent I'm building
that watches job boards for one person, judges each new posting, and
prepares an application only for the ones worth their time, released only
when the person approves that exact packet. In 3:41.75 it follows the
professor's four parts, with my words read by a synthetic voice.

## The film
- File: job-search-agent-film.mp4 (built in exports/landscape/).
- 3840×2160, 24 fps, H.264 (High, yuv420p) and AAC (LC, 48 kHz, stereo).
- 221.750 s (3:41.75), 20,095,046 bytes.
- SHA-256: a0e5c025c58bfcac867d1242499f4aab0bd5e83ee6cc811cee57a2aff0dc1b54
- Not in git: .gitignore excludes *.mp4 and exports/. It will be submitted
  on Canvas.

## The four parts

| Professor's part | Beats | In the film |
|---|---|---|
| 1. Executive summary | B1–B3 | 0:00.00–0:41.25 |
| 2. What others have done | B4–B7 | 0:41.25–1:28.21 |
| 3. Methods | B8–B12 | 1:28.21–2:28.75 |
| 4. Evaluation | B13–B16 | 2:28.75–3:34.00 |
| Closing | B17 | 3:34.00–3:41.75 |

The times are the sums of the beats' render_duration_s in beat_sheet.json.

## Files
- README.md: this file.
- OUTLINE.md: the four-part outline, checked against the code on
  2026-11-21.
- NARRATION.md: the narration, B1 to B17, in my words, with wording fixes
  from Claude.ai that I accepted (SOURCES.md).
- SHOTLIST.md: what each beat shows.
- FACTCHECK.md: every factual claim in the narration, with its source.
- PROMPTS.md: what was generated, and how.
- SOURCES.md: outside sources, my own work, Claude's part, tools and
  licenses, and the disclosures.
- APPENDIX.md: the detail behind the film's Methods and Evaluation.
- BUILD-PROMPT.md: how the film was built, and how to rebuild it.
- make_sheet.py: writes beat_sheet.json from NARRATION.md.
- tools/voice_with_pauses.py: voices every beat, with pauses between
  sentences and clauses.
- beat_sheet.json: the 17 beats: narration, measured audio, voiced pieces,
  scene fields and the final's build records.
- scenes.py: the 17 drawn Manim scenes.
- GATE-LOG.md: the gate result lines from the three review builds, the
  final and the master check.
- TYPECHECK.md: Gate T's report from ./art final.
- _qc/REPORT.md and _qc/contact_sheet.png: Gate V's report and sampled
  frames, from the final's check of the master.
- qc-sheet.png: the contact sheet from the third review build.
- layout_audit.md and layout_audit.json: Gate B's audit of the last scene
  rendered; the toolkit overwrites them for each scene.
- receipts/MASTERCHECK.redacted.md and
  receipts/job-search-agent-film.verified.redacted.json: the master check
  and the export receipt (hashes of the inputs and the master), with my
  home path replaced by <home>.
- .gitignore: keeps the audio, clips, renders, MP4s and local build ledgers
  out of git.
- Local only, not in git: mp3/, manim/, clips/, media/, mp4/, exports/,
  _superseded/ (the old clips of review cuts 1 and 2), images/ and pantry/
  (both empty), MASTERCHECK.md, build-state.json, todo.json, ToDo.md,
  STATUS.md, and the review cut, job-search-agent-film-slate.mp4.

## Decisions, 2026-11-21
- Voice: Kokoro am_onyx, a synthetic text-to-speech voice run locally,
  reading my words, picked by ear over af_bella on 2026-11-21. SOURCES.md
  will disclose it. Kokoro barely pauses on its own, so
  tools/voice_with_pauses.py voices each sentence and clause separately
  and joins them with short silences (0.30 s after a sentence, 0.15 s
  after a colon, semicolon or dash). "Prasad" uses the phoneme swap from
  my Assignment 1 override (week-01-video/tools/kokoro_phoneme_override.py),
  copied into that script; the Assignment 1 file is unchanged.
  - Result: all 17 beats were voiced that way, 221.48 s of narration, and
    B1's swap fired. SOURCES.md discloses the voice, and the opening card
    says "Voice: synthetic (Kokoro)".
- Length: about 4 minutes, no more than 5. Part 1 ends before 1:00.
  - Result: planned about 4 minutes; measured 3:41.75. Part 1 ends at
    0:41.25.
- The detail goes in APPENDIX.md (not yet written), submitted with the film.
  - Result: APPENDIX.md was drafted on 2026-11-22. It will be submitted
    with the film.
- Toolkit: Brutalist (brutalist.art) at revision 22264a3, the same as my
  pitch film (final-project-film/).
  - Result: built at 22264a3, with three local changes from Assignment 1
    (BUILD-PROMPT.md), none of which changed this film's output.
- The video stays out of GitHub. This README will record its filename,
  size and SHA-256.
  - Result: recorded under "The film"; .gitignore excludes *.mp4 and
    exports/.

## Checked / Not checked
A draft for me to edit and sign.

Checked:
- Claude Code ran these; I re-ran the hash and duration myself:
  - Every ./art run gate passed in all three review builds; Gate T and the
    master check passed at the final (GATE-LOG.md).
  - The master's duration, by hand: 221.750 s, the sum of the 17 render
    durations (BUILD-PROMPT.md).
  - The master's SHA-256 matches the export receipt.
- I watched all three review cuts.
- I watched the master (FILM-CP11).
- I read every outside source cited in the film on 2026-11-22
  (FACTCHECK.md).

Not checked:
- The licenses of the Kokoro model weights and of espeak-ng: none on disk
  (SOURCES.md).
- A rebuild from a fresh clone (mp3/ isn't in git, so it needs re-voicing
  first).
- No one new to the project has watched the film yet.

Signed: Prasad Shinde  Date: 11/22/2026
