# SHOTLIST — agent-proving-ground-progress

Typed work order. Every beat is `shot.type GRAPHIC · source own · graphic.engine manim`, rendered by the pipeline from `scenes.py` to `manim/<BEAT_ID>.mp4`. `run.sh` finds scenes by `class B..._Name(Scene)`.

Audio: `sentence_audio.py` (copied from the October pitch) voices each sentence with Kokoro `am_onyx`, 0.35 s between sentences, plus a 1.5 s silent tail on B13. Voice-only respellings: "E2B" → "E-2-B", the repo URL → "github dot com, slash tushar-patel twenty-eight, slash agent-proving-ground" (whisper-checked, `_qc/gates/whisper_check.txt`).

| Beat | Scene class | Kind | Slot | Evidence |
|---|---|---|---|---|
| B01 | `B01_Hello` | Constructed | `manim/B01.mp4` | — |
| B02 | `B02_Done` | Constructed | `manim/B02.mp4` | — |
| B03 | `B03_Loop` | Constructed | `manim/B03.mp4` | — |
| B04 | `B04_Others` | Constructed | `manim/B04.mp4` | October PROJECT-BRIEF.md §2; Drupal link in SOURCES.md |
| B05 | `B05_WhyMine` | Constructed | `manim/B05.mp4` | — |
| B06 | `B06_RealRun` | Real output | `manim/B06.mp4` | evidence/B6.txt |
| B07 | `B07_PolicyGate` | Real output | `manim/B07.mp4` | evidence/B7.txt |
| B08 | `B08_Data` | Real output | `manim/B08.mp4` | evidence/B8.txt |
| B09 | `B09_Isolation` | Real output | `manim/B09.mp4` | evidence/B9.txt |
| B10 | `B10_Predictions` | Real output | `manim/B10.mp4` | evidence/B10.txt |
| B11 | `B11_Results` | Real output | `manim/B11.mp4` | evidence/B11.txt |
| B12 | `B12_PassMeans` | Real output | `manim/B12.mp4` | evidence/B12.txt |
| B13 | `B13_Next` | Constructed | `manim/B13.mp4` | evidence/B13.txt |

## Open slots (human)

None. No screenshots, recordings or pantry media: REAL beats are drawn from captured text, not screenshots.
