# SOURCES

What I used, what I made, and what Claude contributed to CueGate film 2 (the project film). Rows marked with a date were checked on that date. The day-one evidence notes are in evidence/day-one/; every claim and its source is in appendix/FACTCHECK.md.

## What I used (third party)

| Item | Use | Licence / terms | Accessed |
| --- | --- | --- | --- |
| Brutalist video toolkit, https://github.com/nikbearbrown/brutalist.art, commit 519fcbb96e9e1898d374c8794117cab494ffc5cb | Film pipeline: Kokoro narration, Manim scenes, Remotion outro, compile and gates | No licence is stated in the repository at that commit: no LICENSE, LICENCE or COPYING file, and the GitHub API reports none (checked 2026-10-14). Used as the course requires. | Cloned 2026-10-14; same checkout used 2026-11-23 |
| Brutalist show-tell kit code (skills/make/show-tell/templates/iso_kit.py, lines 16-118, 153-163, 311-338) | Drawing primitives and pacing for the Manim scenes | As above (no licence stated). Not included in this submission: reel/build_scenes.py copies these lines from the pinned checkout at build time, after checking the file's sha256. | 2026-11-23 |
| Kokoro TTS voices am_onyx and af_bella, model files kokoro-v1.0.onnx and voices-v1.0.bin (github.com/thewh1teagle/kokoro-onnx, release model-files-v1.0) | Narration audio for DEEPAK (am_onyx) and the SKEPTIC (af_bella), generated locally | Kokoro-82M model: Apache-2.0 (Hugging Face model card for hexgrad/Kokoro-82M, checked 2026-10-14). kokoro-onnx 0.6.1 runtime: MIT (GitHub API, checked 2026-10-14). | 2026-11-23 |
| EB Garamond font (bundled in brutalist.art/runtime/fonts/EB_Garamond/) | All on-screen text: Manim labels, the E1 still's tags, the outro card | SIL Open Font License 1.1 (OFL.txt beside the font) | 2026-11-23 |
| Manim Community 0.20.1, Remotion 4, ffmpeg 9.0.1, faster-whisper (base.en) | Rendering, encoding, a local pronunciation check | Each under its own open-source licence; run locally, nothing redistributed | 2026-11-23 |
| Lakew, Di Gangi, Federico, "Controlling the Output Length of Neural Machine Translation", IWSLT 2019, https://aclanthology.org/2019.iwslt-1.31 | I3 (B09): length control in translation | Read only; title and a short quote in appendix/FACTCHECK.md | 2026-11-23 |
| Karakanta, Negri, Turchi, "Is 42 the Answer to Everything in Subtitling-oriented Speech Translation?", IWSLT 2020, https://aclanthology.org/2020.iwslt-1.26 | I3 (B09): length alone is not enough for subtitles | Read only; title and short quotes in appendix/FACTCHECK.md | 2026-11-23 |
| Hugging Face model API and file endpoints for eight public models (appendix/MODELS.md) | Whether candidate local models download without an account | Read only; nothing downloaded beyond one byte of each config.json | 2026-11-23 |
| Netflix Partner Help: English (USA) Timed Text Style Guide | "Streaming platforms set hard limits on how fast a line can be read" (B03) | Read only (short quotes in evidence/day-one/netflix.md) | 2026-10-14 |
| Gotham Lab, Netflix subtitle delivery requirements guide (secondary) | "delivery guides say files that break them get sent back" (B03) | Read only | 2026-10-14 |
| Subtitle Edit documentation, https://subtitleedit.github.io/subtitleedit/ | Named in B08; one of "the tools I checked" in B03 | Read only | 2026-10-14 |
| Editsub, https://editsub.com/ | Named in B08; one of "the tools I checked" in B03 | Read only | 2026-10-14 |
| EZTitles, https://eztitles.com/ | Named in B08 | Read only | 2026-10-14 |
| Tears of Steel (Blender Foundation), https://download.blender.org/demo/movies/ToS/subtitles/TOS-en.srt | Candidate test data named in M2 (B13); no subtitle text used in the film | Film: Creative Commons Attribution 3.0 (mango.blender.org/about). The subtitle file's own licence is not stated on the pages checked, and I have not confirmed it. | 2026-10-14 |

## What I made

- The CueGate plan, the narration, the four-part structure and my answers about resources.
- The subtitle line in E1 and E2 ("I really don't think we should go in there tonight, not after what happened."), written by me for the pitch film.
- The screenshot of my Claude exchange shown in E1 (evidence/claude-exchange.png, taken 2026-10-14), shown unaltered and scaled only.
- No drawings or stock images from anyone else. Every picture in the film is drawn by the film's own Manim code (reel/scenes_film.py), is the local Remotion outro, or is my own screenshot.

## What Claude contributed

- 2026-11-23, claude.ai (Claude Opus 5.5): drafted FILM2-SCRIPT.md (the film's script and picture plan), the RESOURCES.md template, CLAUDE-CODE-PROMPT-FILM2.md (the build prompt) and the prompt overrides. I reviewed and edited them. My answers in RESOURCES.md (evidence/RESOURCES.md) are my own.
- 2026-10-14, Claude desktop app (Opus 5): the exchange shown in E1 and E2, reproduced exactly with its date (evidence/claude-exchange.md and .png). It is a chat, not an API call. CueGate does not use Claude as its model; the shortening step will use a local open-weight model.
- 2026-11-23, Claude Code (Claude Opus 5.5): turned my script into beat_sheet.json, wrote the film's scene code, pad_audio.py, make_e1.py, make_captions.py, first versions of the GATE P paperwork, rebuild-film2.sh and this folder's README and SOURCES; fetched and checked the two IWSLT papers; ran the model-download check; ran the Brutalist pipeline and every gate. My decisions and review lines are in REVIEW.md; the tool events are in BUILD-LOG-FILM2.md.

## Mock-ups

Every picture of something not built is labelled CONSTRUCTED on screen: the gate (B04, B05), the report card (B06), CueGate's place on the map (B11), the test set (B13), the pipeline (B14–B16), the scoreboard (B20, "no results yet"), the meaning check (B22) and the tally sheet (B23). The only interface on screen is my real Claude screenshot in E1. No screenshot of CueGate exists, because no CueGate code exists yet.
