# Sources and contributions

## What Claude contributed
Claude (Opus 5.5) worked in the Claude Code desktop app on 2026-10-14. It wrote the following first drafts:
- all code in `stopline/`, `tests/`, `data/build_synthetic.py` and `film/make_sheet.py`
- the synthetic incidents, evidence and **labels**
- the drafts of this file, `PROJECT-BRIEF.md`, `README.md`, `BUILD-PROMPT.md` and the opening `FRICTIONAL.md` entries

It also ran the tests and the evaluation and saved the output in `reports/`.
**Review status (2026-10-14):** I reviewed all 11 checks in `stopline/checks.py`, including three exercises: changing a value, removing a rule, and explaining the two misses (see FRICTIONAL.md).

Because Claude wrote the rules, the test set and the labels, the 15/17 agreement figure is not independent evidence.

## What I made
- Project idea and the choice of domain (supply chain / manufacturing quality)
- Target role and the answer to "why this project"
- The SAP QM comparison, from my own SAP experience
- Film build in WSL with Claude Code, 2026-10-14
- Watched and approved the final film, 2026-10-15

## Third-party tools and assets
| Item | Version | Use | Licence |
|---|---|---|---|
| Python | 3.12.5 | runs StopLine | PSF License |
| brutalist.art toolkit | commit `4115560aa73692b5451ee2e8bd4c3f1e51523b5a` (cloned 2026-10-14) | film pipeline | **No LICENSE file in the repo at that commit.** Course-provided; ask the instructor before redistributing. |
| Kokoro TTS (`kokoro-onnx` 0.4.7, model `kokoro-v1.0.onnx`, voice `am_onyx`) | installed by `./setup --install` in WSL Ubuntu, 2026-10-14 | narration voice | Kokoro-82M: Apache-2.0 (per its model card) |
| Manim 0.20.1, ManimPango 0.6.1, Python 3.14.4, Node 22.23.3, ffmpeg 8.0.1 (WSL Ubuntu) | 2026-10-14 | rendering | Manim: MIT; ffmpeg: LGPL/GPL; Remotion: Remotion License (free for individuals) |

## Data
No real data is used. Every incident, lot, part, measurement and date is invented in `data/build_synthetic.py`.

## Alternatives inspected
- **SAP QM usage decision (QA11/QA32)**, 2026-10-14. Observations are from my own experience in SAP, not re-checked on a current system. It checks recorded results, the lot and the timing; it can refuse or warn; it checks structured results only, not the written justification.
  - Supporting public pages that Claude found: [SAP KBA 1958483 preview](https://userapps.support.sap.com/sap/support/knowledge/en/1958483) (viewed 2026-10-14) and [SAP Help 4.6C: Making the Usage Decision](https://help.sap.com/saphelp_46c/helpdata/EN/8d/3e6657eab611d3b29c0050da4ceab0/content.htm).
- [SoftExpert 8D non-conformity report](https://www.softexpert.com/en/features/non-conformity-report-8D): found, **not compared**.
