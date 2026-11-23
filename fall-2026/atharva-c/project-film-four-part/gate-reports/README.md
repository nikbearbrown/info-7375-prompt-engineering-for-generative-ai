# Gate reports — Seeded Faults four-part project film

Toolkit: Brutalist (github.com/nikbearbrown/brutalist.art) at commit `b21f625`, free local pipeline only. Final run 2026-11-23 (label-size fix; see below).

| Gate | What it checks | Result | File |
|---|---|---|---|
| L / SHAPE | beat-mix lint; finance chart shapes | **PASS** / skipped (not a finance reel) | `art-run.log` |
| A (static pre-flight) | every scene stays in the frame and safe area | **PASS** (15/15 clean) | `art-run.log`, `art-run-labelfix.log` |
| W (contrast, margins, overlap) | WCAG contrast and text overlap | **PASS** | `art-run.log` |
| B (layout audit) | rendered text inside the safe area, no collisions | **PASS** (every scene CLEAN) | `GATE-B-layout_audit.md` (last scene audited) |
| V (frame-level visual QC) | 30 sampled frames | **PASS** (0 BLOCKER, 0 MAJOR) | `GATE-V-REPORT.md`, `GATE-V-contact_sheet.png` |
| T (type lock, before final) | text size and contrast at each clip midpoint | **PASS** (15/15, 0 FAILs) | `GATE-T-TYPECHECK.md` |
| F (fact-check) | FACTCHECK.md rows resolved | 16 rows, none unresolved; **1 advisory** (below) | `GATE-F-factcheck.txt`, `../film-source/FACTCHECK.md` |
| Render integrity (`art final`) | master plus hashes of every input | **ready**: 3840×2160, 237.2 s, sha256 `7557b426…a638` | `render-integrity.verified.json`, `art-final.log` |

## Failures fixed along the way
- **Gate A** failed on M3 (CONSTRUCTED stamp ran off the frame), with safe-area warnings on E3, I3 and V2. Fixed by moving the stamps and labels inward.
- **Gate B** failed on I1 (the real `unexpected_count=50` line was wider than planned and touched a check mark), on I2 (the monospace result rows overlapped and ran off-frame), and on I3 (a label sat on the table drawing). Re-laid out: the I2 rows are now serif text with the same values from `output_holdout.txt`.
- **Requirements pass (2026-11-22):** I3, M4 and V1 were reworded to cover Professor Bear's asks (what prior work found and why mine matters; the Claude Pro plan and no other accounts or compute; a check on the tool itself), and E2, I3, M3, M4 and V3 were trimmed to stay under 4 minutes. The six changed beats were re-rendered and every gate rerun clean. A final pass put back the run-and-score step in M3 (lost in the trim) and shortened V3. Both re-rendered, all gates clean.
- **Small-text fix (2026-11-23):** a TA comment on an earlier film asked for larger text, and the serif text already had a size-44 floor, but three monospace labels were below it (`unexpected_count=50` and `FAIL 50` in I1 at 36; `e5aac1c · 2026-11-22` in M2B at 40). All three were raised to 44, the floor now applies to monospace text too, and `unexpected_count=50` moved to x = -2.85 to stay inside the safe area. I1 and M2B were re-rendered (`art-run-labelfix.log`); Gates A, W, B and V were clean, then Gate T passed 15/15 and `art final` produced a new master (`art-final.log`).
- **Gate V** flagged one MAJOR low-contrast frame in M2A (pale bar). Fixed by using the darker kraft colour. E3's crowded "caught / missed" headers were also simplified.

## Known, explained non-passes
- **FC-4 advisory, "7 beats uncovered".** `factcheck_check.py` only recognises beat IDs that start with "B" (`BEAT_RE = B[0-9A-Z]+`). This film's beats are E/I/M/V, so no row registers as covering a beat, even though FACTCHECK.md has a row for every claim-bearing beat. Advisory only, not blocking.
- **SKIN LINT** (COLD OPEN LAW / OUTRO LAW): same choice as the pitch film. No instructor persona cold open, and no `ClaudeTitleOutro`, which hard-codes the instructor's handle. Advisory.

## Note on the logs
`art-run.log`, `art-run-labelfix.log`, `art-final.log` and `render-integrity.verified.json` are copied from the build folder, with the local home path replaced by `~` (privacy). The film's sha256 in `render-integrity.verified.json` matches `../seeded-faults-project.mp4`.
