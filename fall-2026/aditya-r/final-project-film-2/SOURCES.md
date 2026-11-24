# SOURCES — DayThread Final Project Film (2026-11-23)

## Outside sources used in the film

| # | Source | Used in | Read by Aditya? |
|---|---|---|---|
| S1 | Lifeline, "Automatic Fall Detection Systems for Seniors" — https://www.lifeline.com/medical-alert-systems/fall-detection/ | B04: "Fall detection technology does not detect 100% of all falls." | Yes, 2026-10-14 |
| S2 | DailyCall, "AI Companion for Elderly Loved Ones" — https://dailycall.care/ai-companion-for-elderly | B04: "DailyCall uses AI-generated phone calls for daily check-ins."; "Helpful summaries after calls" | Yes, 2026-10-14 |
| S4 | DailyCall, "Safety Policy" — https://dailycall.care/safety-policy | B04: "DailyCall cannot guarantee that every safety concern will be detected, interpreted correctly, or delivered to the right person in time." | Yes, 2026-10-14 |
| S5 | Hugging Face model card, `distilbert/distilroberta-base` — https://huggingface.co/distilbert/distilroberta-base | B09, B11: base model name; licence Apache-2.0 (from the Hugging Face API, 2026-11-23) | No. Only the licence and availability were checked |
| S6 | INFO 7375 course repo, chapter 10 "Planning Before Acting", section "Evidence belongs on the edges" | B06, B09: delegation as a contract with testable handoffs; "an edge needs something that fails differently from the thing it certifies" | Course material |
| S7 | INFO 7375 "Final Project — An Agentic System You Choose" (Canvas, due 20 Dec) | B08, B12–B15: loop, stop condition, held-out set, five deliberate failures, controlled failure | Course material |

The S1–S4 quotes were checked word for word against the pages on 2026-10-14 (see
`../final-project-film/SOURCES.md`). These are the companies' own pages, not independent
evaluations; neither product was tested. A published study on AI clinical summaries was
considered and **not used**: its page could not be read (see FRICTIONAL.md, 15:40).

## Own material

- The replay result in B02/B03 comes from Aditya's 2026-10-25 run
  (`../final-project-film/replay/RESULTS.md`): synthetic fixture, fictional client, Claude via
  Claude Code CLI.
- The appendix and plan are Aditya's project plan, drafted with Claude on 2026-11-23.

## Toolkit and licences

- brutalist.art toolkit, `main` @ `519fcbb`, skill `show-tell`: `iso_kit.py` and 11 original props
  pasted verbatim by `source/assemble_scenes.py`. No toolkit source changes.
- Manim Community 0.20.1 (MIT). Kokoro TTS via kokoro-onnx 0.6.1 (Apache-2.0), voice `am_onyx`.
  faster-whisper 1.2.1 (MIT), used for checks only. FFmpeg. EB Garamond (SIL OFL).
- No images, video, music or generated media from anyone else.

## What Claude contributed (Claude Code, 2026-11-23)

- Read both assignment rubrics, the course repo and the Frictional repo, and proposed the plan
  (four-part structure, delegation contract, fine-tuned checker), which Aditya approved.
- Drafted `SCRIPT.md` v1, `APPENDIX.md`, the scene code (`source/scenes_body.py`, reusing the
  October helpers), FACTCHECK/SHOTLIST/PROMPTS, this file, BUILD-PROMPT.md, README.md and
  FRICTIONAL.md.
- Ran the narration, the toolkit gates, the final export and the extra checks; fixed the gate
  failures recorded in FRICTIONAL.md.

## What Aditya contributed

- The project, the October brief and replay, the prediction and its review.
- The decisions for this film: keep the DayThread name, upload tonight, Kokoro voice at a similar
  length, the concern-detector checker.
- Watching the film and approving or rejecting it before anything is posted.
