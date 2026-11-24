# SHOTLIST — agent-proving-ground-progress (v2)

Typed work order. Every beat is `shot.type GRAPHIC · source own · graphic.engine manim`, rendered by the pipeline from `scenes.py` to `manim/<BEAT_ID>.mp4`. `run.sh` finds scenes by `class B..._Name(Scene)`.

Audio: `sentence_audio.py` (copied from the October pitch) voices each sentence with Kokoro `am_onyx`, 0.25 s between sentences (tightened from 0.35 s to bring the runtime to about 3:54), plus a 1.5 s silent tail on B13 and a 0.04 s silent tail on B12 (keeps the timeline on a frame count the toolkit's 3-decimal final cut represents exactly). Voice-only respellings: "E2B" → "E-2-B"; "INFO 7375" → "info seventy-three seventy-five"; the repo URL → "github dot com, slash tushar-patel twenty-eight, slash agent-proving-ground" (whisper-checked, `_qc/gates/whisper_check.txt`).

| Beat | Scene class | Kind | Slot | Evidence |
|---|---|---|---|---|
| B01 | `B01_Hello` | Constructed | `manim/B01.mp4` | — |
| B02 | `B02_Done` | Constructed | `manim/B02.mp4` | — |
| B03 | `B03_WhatItIs` | Constructed | `manim/B03.mp4` | — |
| B04 | `B04_FirstMinute` | Constructed (terminal mock-up) | `manim/B04.mp4` | October PROJECT-BRIEF.md:14 |
| B05 | `B05_Others` | Constructed | `manim/B05.mp4` | October PROJECT-BRIEF.md §2 |
| B06 | `B06_WhyMine` | Constructed | `manim/B06.mp4` | October PROJECT-BRIEF.md:38 |
| B07 | `B07_OneRun` | Constructed | `manim/B07.mp4` | evidence/B6.txt, B7.txt, B9.txt |
| B08 | `B08_Tasks` | Constructed | `manim/B08.mp4` | evidence/B8.txt (split membership) |
| B09 | `B09_BuiltSoFar` | Real output | `manim/B09.mp4` | evidence/B6.txt, B7.txt, B9.txt, B13.txt |
| B10 | `B10_Judged` | Constructed | `manim/B10.mp4` | evidence/B8.txt, B10.txt |
| B11 | `B11_Results` | Real output | `manim/B11.mp4` | evidence/B11.txt, B12.txt |
| B12 | `B12_Left` | Constructed | `manim/B12.mp4` | evidence/B13.txt |
| B13 | `B13_Close` | Constructed | `manim/B13.mp4` | evidence/B13.txt |

## Open slots (human)

None. No screenshots, recordings or pantry media: REAL beats are drawn from captured text, not screenshots.
