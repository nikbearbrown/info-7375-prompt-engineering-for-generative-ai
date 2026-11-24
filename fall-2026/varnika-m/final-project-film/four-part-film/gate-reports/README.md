# Gate reports — A Job-Search Agent You Can Check

Copied from the brutalist.art toolkit (`b21f625`) after the final export on 2026-11-23. Every gate passed.

| Gate | What it checks | Report |
|---|---|---|
| F | Fact check (every claim has a source) and bookends | `gate-F.md` |
| L, A, W | Beat mix; render-free scene pre-flight; WCAG contrast, margins and text overlap | `gate-L-A-W.md` |
| B | Pixel layout audit of each rendered scene (labels on lines, safe area) | Passed for all 18 scenes in the runs logged in `../FRICTIONAL.md`; the toolkit keeps only the last scene's report |
| V | Frame-level visual check of the whole cut (36 frames) | `gate-V-REPORT.md`, `gate-V-contact-sheet.png` |
| T | Type check: minimum text size and 4.5:1 contrast | `gate-T-TYPECHECK.md` |

What failed on the way, and the fixes, are in `../FRICTIONAL.md`.
