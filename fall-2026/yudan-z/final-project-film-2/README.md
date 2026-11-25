# Final Project Film — *A Job Agent I Can Check*

My INFO 7375 final project film: a job-search agent that reads public job boards every day and judges each new posting with a rule I can recompute by hand. The film follows the four parts of the brief: summary, what others have done, methods, evaluation. The detail is in `APPENDIX.md`.

- **Student:** Yudan Zhou (`@yudanzhou`)
- **Film:** `job-search-agent-film.mp4`, 3:49, 1920×1080, H.264 + AAC
- **Narration:** a synthetic voice (Kokoro `af_heart`, local) reading my own script, approved beat by beat on 2026-11-23

| File | What |
|---|---|
| `job-search-agent-film.mp4` | the film |
| `APPENDIX.md` | data, method step by step, resources, evaluation plan, other work, fact-check summary |
| `FRICTIONAL.md` | my dated log of what was checked, changed or rejected while making the film |
| `FACTCHECK.md` | every spoken claim with its verdict and source |
| `beat_sheet.json` | narration and picture plan for all 15 beats, with measured audio durations |
| `scene_body.py` | the 13 drawn scenes (Manim) |
| `SHOTLIST.md`, `SOURCES.md` | toolkit paperwork, written before rendering |
| `gate-reports/` | toolkit quality gates: Gate V (0 BLOCKER / 0 MAJOR), Gate T (PASS), layout audit, master verification |
| `evidence/` | my own PowerShell run of R6 on four sponsorship phrasings (a known limit, see `APPENDIX.md` §D) |
| `build/` | my outro component (`StudentTitleOutro.tsx` + `Root.tsx.diff`) and the Windows `npx` wrapper |

The project evidence the film cites is in my `js1-contract-and-watch` and `js2-loop-tools-diff` folders.
