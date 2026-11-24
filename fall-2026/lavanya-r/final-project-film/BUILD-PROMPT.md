# Build Prompt

Rebuild the unpublished `readme-checker-film` reel (README Checker pitch film, cut 4) from this folder.

Read `beat_sheet.json`, `PROJECT-BRIEF.md`, `APPENDIX.md`, `SOURCES.md`, `gate-reports/FACTCHECK.md`,
and the current `skills/make/show-tell/SKILL.md` in Brutalist (commit `519fcbb`) first. Preserve every
supplied claim, every published number, and every line of real terminal output exactly. Use the final
beat sheet as the build contract: show-tell style, Plain register, Claude palette, Kokoro `af_bella`,
21 beats, about 3 min 51 s. The skill's defaults ("Liam, in for Bear", the `@NikBearBrown` folder label
and the locked `ClaudeTitleOutro` card) are deliberately overridden, because the assignment requires
narrating as myself with no instructor name, persona or credit line.

The film follows four parts, in this order, and every beat's on-screen header names its part:

| Part | Beats | Content |
|---|---|---|
| 1 · What and why | BHELLO, BIDEA, B00, B00A, B01, B01T | What I'm building and why it matters, done by about 0:50. No "how": no terms card, no container. |
| 2 · What exists | B02T, B06, B06A, B06B, B06C | By hand, CI, Runme and Doc Detective, ExecutionAgent and Installamatic, then the comparison table that restates why mine is worth building. |
| 3 · Methods | B03, B04, B05, B05A, B05B, B05C, B11 | The tool, the agent loop, the report, the data, the build order, the resources, safety. |
| 4 · Evaluation | B08, B08A | What I'll measure, and the targets that mean it worked or didn't. |
| outro | B14 | My own outro. |

1. Set up the toolkit with `git clone https://github.com/nikbearbrown/brutalist.art`, then
   `git checkout 519fcbb` and `./setup --install`. At this commit setup exits 1 on its own
   ElevenLabs guard (it flags example films inside the toolkit). The install still completes;
   confirm the voice works with `python3 runtime/scripts/setup_smoke_kokoro.py`. Render with
   **Manim 0.20.1**: put the Python environment that has it first on `PATH` (on my machine,
   `export PATH=~/anaconda3/bin:$PATH`; `/usr/local/bin/python3` has Manim 0.18 and no `manim` command).
2. Make an empty working folder named `readme-checker-film`, outside the Brutalist checkout,
   containing `build/make_sheet.py` and `build/scene_body.py`. Run `python3 make_sheet.py` to
   write `beat_sheet.json`. My first name is spelled `Luh-vun-ya` in `narration_text` only, so
   Kokoro says it correctly; on screen it is always "Lavanya". Do not change this spelling.
   Re-running `make_sheet.py` clears the measured durations, so run step 3 again after it.
3. Generate the narration with
   `python3 ~/brutalist.art/runtime/scripts/generate_audio_kokoro.py .`.
   Then pad B14 with a 1.0 s silent tail
   (`ffmpeg -i mp3/beat-B14.mp3 -af "apad=pad_dur=1.0"`) and write its measured duration back
   to `actual_duration_s` and `mp3/timings.json`. Check BHELLO, BIDEA, B06A, B06B and B14 with a
   faster-whisper transcript before rendering.
4. Build the drawings with
   `cat ~/brutalist.art/skills/make/show-tell/templates/iso_kit.py scene_body.py > scenes.py`.
   Keep the final structure:
   - BHELLO is my own intro.
   - BIDEA is the only Remotion beat: `BrutalistHesitantWriter`, one line, `charMs: 60`,
     `fontSize: 110`, correcting "fix" to "find". Slower settings leave the frame empty and fail
     Gate V.
   - B01T and B02T show only two real terminal lines each, labelled `real output · Oct 13, 2026`.
   - B14 is my own outro (box and title only).
   - Beat IDs added in cut 4 are digit-style (B00A, B06A–B06C, B05A–B05C, B08A). Gate W only
     analyses classes named like `B07_Foo` / `B18A_Foo`, so names such as `BWHAT` would skip it.
   README pages stay as grey lines with ✓ / ⚠ / ✗ marks; do not show README commands on screen.
5. Write the gate paperwork before the first run (`SOURCES.md`, `FACTCHECK.md`, `SHOTLIST.md`,
   `PROMPTS.md`; copies are in `gate-reports/`). Then run
   `~/brutalist.art/art run readme-checker-film --height 2160` from the parent folder. Read
   `_qc/REPORT.md` and `layout_audit.md`, and fix every BLOCKER, MAJOR and layout error or warning
   before continuing (Gate B is strict: a warning stops the run). After any voice or scene edit,
   move the stale clip to `_superseded/` and check file timestamps to confirm a rebuild really ran.
6. Run
   `~/brutalist.art/art final readme-checker-film --height 2160 --out readme-checker-film/exports/landscape`
   and stop. GATE T must pass. Expect `bookend_check.py` to flag the missing `ClaudeTitleOutro`;
   that is intentional (see FRICTIONAL.md). Never publish or upload.

Honesty rules:
- The report in B05 must remain labelled `CONSTRUCTED MOCK-UP · not built yet`.
- The README Checker row in B06C must remain labelled `(planned)`.
- The thresholds in B08A must remain labelled `targets set now, before anything is built`, and B08
  must show the scores as `?` with "These numbers don't exist yet."
- Everything about the README Checker is future tense. The only past-tense claims are the two
  manual README runs on 2026-10-13, my public `webapp` repo, the published prior work in
  SOURCES.md, and the resources checked on 2026-11-23 (FACTCHECK rows 28–29).
