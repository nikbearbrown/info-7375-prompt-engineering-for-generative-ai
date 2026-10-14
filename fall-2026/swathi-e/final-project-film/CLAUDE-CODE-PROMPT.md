# Prompt for Claude Code — Final Project Pitch Film

Paste everything below the line into Claude Code, opened in the new `final-project-film` folder.

---

Build my INFO 7375 Final Project Pitch Film in this folder.

**Student:** Swathi Baba Eswarappa
**Film file:** `BabaEswarappa_Swathi_INFO7375_FinalProjectFilm.mp4`
**Project pitched:** "Cite or Refuse," a source-grounded tax helper for international students. It is a pitch, not a build: nothing in the project exists yet.
**Runtime:** 2–4 minutes, hard ceiling 240 s.
**Framework:** Brutalist, free local pipeline only (Kokoro narration, Manim visuals, FFmpeg). No paid generation, no API keys, no upload.

## Inputs already in this folder

- `beat_sheet.json`: 13 beats. Treat `narration_text` as approved. Do not change any claim, number, or wording without asking me first. If a line must be cut for runtime, propose the cut and wait.
- `PROJECT-BRIEF.md` and `TEST-NOTES.md`: the facts behind the narration.
- Week 1 helpers copied from my Week 1 build: `scene.py`, `build_mux.py`, `qc_frames.py`, `make_srt.py`, `build.sh`. Reuse the `Beat` helper class and its checks (`assert_in_frame`, `assert_in_safe_area`, `assert_no_text_overlap`, `hold_until`, `at`/`pin`). Replace the Week 1 scenes with 13 new ones named as in `beat_sheet.json` (`B01_TwoAnswers` … `B13_Close`).

The Brutalist toolkit and my Kokoro environment are in `~/Downloads/brutalist/` (`brutalist.art/` and `.venv-kokoro/`). Locate them first and tell me what you found before building. The environment variables from Week 1 may be needed:
`PHONEMIZER_ESPEAK_LIBRARY=/opt/homebrew/lib/libespeak-ng.dylib`, `ESPEAK_DATA_PATH=/opt/homebrew/share/espeak-ng-data`.

## Hard rules

1. **Numbers come from one data file.** Create `data/facts.json` holding every number shown on screen ($15,750, $15,000, page 7, Oct 9 2026, tax year 2025, the test grid cells from TEST-NOTES.md). Scenes read from it; nothing is hand-typed in an animation. Check that each number also appears in the narration where it is spoken.
2. **Labels.** Planned-system diagrams (B04, B06) carry a visible PROPOSED badge. The B08 terminal carries "CONSTRUCTED MOCK-UP" for the whole beat, with dashes instead of scoreboard numbers. Nothing unbuilt is drawn as if it runs.
3. **No screenshots of chatbot answers.** B01 shows the two figures as plain number cards with "ChatGPT, Oct 9, 2026". No personal details anywhere (no university, job, or account details).
4. **No overlapping text.** My Week 1 film lost a point for overlapping labels. Every scene must pass `assert_no_text_overlap`, and keep captions short.
5. **Audio is the master clock.** Pin visual cues to narration phrases with `at`/`pin`; keep trailing holds small.
6. **Simple pictures.** One clear drawn picture per beat, minimal on-screen text, narration carries the explanation.
7. **Narrate as me.** Use the voice in `beat_sheet.json` unless I change it. Do not use my instructor's name, persona, or credit line anywhere.

## Build steps

1. Check prerequisites (ffmpeg, manim, Kokoro venv, model files). Report anything missing; do not install paid tools.
2. Kokoro dry run, then generate narration. Report each beat's actual duration and the total.
3. Smoke-render one scene at low quality, show me, then render all 13 at 1080p.
4. Run my Week 1 gates: `qc_frames.py`, the `Beat` assertions, and `build_mux.py` runtime gate (120–240 s).
5. **Run the Brutalist toolkit's own quality gates** as described in its README (including any render-integrity check), and save their reports in this folder. If the film fails render integrity, fix and re-render; do not ship over it.
6. Composite the final mp4 and captions; verify duration, size, and audio levels with ffprobe/ffmpeg.
7. Write `BUILD-PROMPT.md` recording this prompt, any prompts that changed the output, and the commands actually executed, in the same format as my Week 1 file.

Do not write `FRICTIONAL.md`; I write that myself. You may draft `README.md` and `SOURCES.md` for me to review, with SOURCES.md stating clearly what Claude contributed.

Stop and ask me whenever a rule conflicts with the build.
