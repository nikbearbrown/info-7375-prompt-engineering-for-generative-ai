# GATE-LOG.md — job-search-agent-film

Gate result lines from the console output of the three 4K review builds
(`./art run <reel> --height 2160`, strict gates: ART_STRICT=1, ART_QC=1, the toolkit
defaults) and of the final export (`./art final <reel> --height 2160 --out
<reel>/exports/landscape`), followed by the master check. Only gate result lines are
kept (plus each scene's `[run] rendering` line and the exit status), in log order;
Manim's progress bars and other console output are left out. Home-folder paths were
replaced with `<home>`; nothing else was edited. Gate A's `[static-check]` lines do
not name their scene: they run in the same order as Gate W's lines, B1 to B17.

## Review cut 1 (2026-11-22)

The first 4K review cut (FILM-CP8): all 17 scenes rendered from the new scenes.py.

```text
### ./art run <home>/Documents/Code/info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/final-film-job-search-agent --height 2160
[run] GATE L — beat-mix lint
[beat-lint] clean — beat mix OK (beat_sheet.json)
[run] GATE SHAPE — finance chart-shape enforcement
[gate-shape] skip — not a finance reel (beat_sheet.json)
[run] GATE A — static pre-flight
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[run] GATE W — WCAG contrast + margins + text-overlap (independent second check)
[gateW] B1_OpeningCard clean
[gateW] B2_Packet clean
[gateW] B3_Flood clean
[gateW] B4_ApplyTools clean
[gateW] B5_Funnel clean
[gateW] B6_PaymentChecks clean
[gateW] B7_NotFound clean
[gateW] B8_Alex clean
[gateW] B9_Evidence clean
[gateW] B10_Plug clean
[gateW] B11_Fingerprint clean
[gateW] B12_Laptop clean
[gateW] B13_Locked clean
[gateW] B14_Checks clean
[gateW] B15_Traps clean
[gateW] B16_Controlled clean
[gateW] B17_End clean
[run] rendering B1_OpeningCard
[audit] scenes: 4 snapshots → CLEAN
[run] rendering B2_Packet
[audit] scenes: 20 snapshots → CLEAN
[run] rendering B3_Flood
[audit] scenes: 21 snapshots → CLEAN
[run] rendering B4_ApplyTools
[audit] scenes: 14 snapshots → CLEAN
[run] rendering B5_Funnel
[audit] scenes: 14 snapshots → CLEAN
[run] rendering B6_PaymentChecks
[audit] scenes: 18 snapshots → CLEAN
[run] rendering B7_NotFound
[audit] scenes: 15 snapshots → CLEAN
[run] rendering B8_Alex
[audit] scenes: 8 snapshots → CLEAN
[run] rendering B9_Evidence
[audit] scenes: 25 snapshots → CLEAN
[run] rendering B10_Plug
[audit] scenes: 22 snapshots → CLEAN
[run] rendering B11_Fingerprint
[audit] scenes: 26 snapshots → CLEAN
[run] rendering B12_Laptop
[audit] scenes: 33 snapshots → CLEAN
[run] rendering B13_Locked
[audit] scenes: 12 snapshots → CLEAN
[run] rendering B14_Checks
[audit] scenes: 20 snapshots → CLEAN
[run] rendering B15_Traps
[audit] scenes: 10 snapshots → CLEAN
[run] rendering B16_Controlled
[audit] scenes: 22 snapshots → CLEAN
[run] rendering B17_End
[audit] scenes: 5 snapshots → CLEAN
[art] wrote <home>/Documents/Code/info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/final-film-job-search-agent/job-search-agent-film-slate.mp4  (206.2s, audio: per-beat timeline (source audio preserved), drawtext: no — PIL overlays)
[art] slots: 17/17 filled — B1:MANIM B2:MANIM B3:MANIM B4:MANIM B5:MANIM B6:MANIM B7:MANIM B8:MANIM B9:MANIM B10:MANIM B11:MANIM B12:MANIM B13:MANIM B14:MANIM B15:MANIM B16:MANIM B17:MANIM
[run] GATE V — frame-level visual QC on the compiled reel
[gate-v] frames=34 BLOCKER=0 MAJOR=0 → <home>/Documents/Code/info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/final-film-job-search-agent/_qc/REPORT.md
RUN EXIT=0
```

## Review cut 2 (2026-11-22)

The second 4K review cut (FILM-CP9), after my twelve review fixes: all 17 scenes re-rendered after their old clips were moved to _superseded/review-cut-1/.

```text
### ./art run <home>/Documents/Code/info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/final-film-job-search-agent --height 2160
[run] GATE L — beat-mix lint
[beat-lint] clean — beat mix OK (beat_sheet.json)
[run] GATE SHAPE — finance chart-shape enforcement
[gate-shape] skip — not a finance reel (beat_sheet.json)
[run] GATE A — static pre-flight
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[run] GATE W — WCAG contrast + margins + text-overlap (independent second check)
[gateW] B1_OpeningCard clean
[gateW] B2_Packet clean
[gateW] B3_Flood clean
[gateW] B4_ApplyTools clean
[gateW] B5_Funnel clean
[gateW] B6_PaymentChecks clean
[gateW] B7_NotFound clean
[gateW] B8_Alex clean
[gateW] B9_Evidence clean
[gateW] B10_Plug clean
[gateW] B11_Fingerprint clean
[gateW] B12_Laptop clean
[gateW] B13_Locked clean
[gateW] B14_Checks clean
[gateW] B15_Traps clean
[gateW] B16_Controlled clean
[gateW] B17_End clean
[run] rendering B1_OpeningCard
[audit] scenes: 4 snapshots → CLEAN
[run] rendering B2_Packet
[audit] scenes: 22 snapshots → CLEAN
[run] rendering B3_Flood
[audit] scenes: 27 snapshots → CLEAN
[run] rendering B4_ApplyTools
[audit] scenes: 14 snapshots → CLEAN
[run] rendering B5_Funnel
[audit] scenes: 12 snapshots → CLEAN
[run] rendering B6_PaymentChecks
[audit] scenes: 18 snapshots → CLEAN
[run] rendering B7_NotFound
[audit] scenes: 17 snapshots → CLEAN
[run] rendering B8_Alex
[audit] scenes: 8 snapshots → CLEAN
[run] rendering B9_Evidence
[audit] scenes: 25 snapshots → CLEAN
[run] rendering B10_Plug
[audit] scenes: 22 snapshots → CLEAN
[run] rendering B11_Fingerprint
[audit] scenes: 26 snapshots → CLEAN
[run] rendering B12_Laptop
[audit] scenes: 29 snapshots → CLEAN
[run] rendering B13_Locked
[audit] scenes: 12 snapshots → CLEAN
[run] rendering B14_Checks
[audit] scenes: 22 snapshots → CLEAN
[run] rendering B15_Traps
[audit] scenes: 10 snapshots → CLEAN
[run] rendering B16_Controlled
[audit] scenes: 22 snapshots → CLEAN
[run] rendering B17_End
[audit] scenes: 5 snapshots → CLEAN
[art] wrote <home>/Documents/Code/info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/final-film-job-search-agent/job-search-agent-film-slate.mp4  (205.7s, audio: per-beat timeline (source audio preserved), drawtext: no — PIL overlays)
[art] slots: 17/17 filled — B1:MANIM B2:MANIM B3:MANIM B4:MANIM B5:MANIM B6:MANIM B7:MANIM B8:MANIM B9:MANIM B10:MANIM B11:MANIM B12:MANIM B13:MANIM B14:MANIM B15:MANIM B16:MANIM B17:MANIM
[run] GATE V — frame-level visual QC on the compiled reel
[gate-v] frames=34 BLOCKER=0 MAJOR=0 → <home>/Documents/Code/info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/final-film-job-search-agent/_qc/REPORT.md
RUN EXIT=0
```

## Review cut 3 (2026-11-22)

The third 4K review cut, for the paused narration (FILM-CP10), with cues timed from each beat's voiced pieces: all 17 scenes re-rendered after their old clips were moved to _superseded/review-cut-2/.

```text
### ./art run <home>/Documents/Code/info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/final-film-job-search-agent --height 2160
[run] GATE L — beat-mix lint
[beat-lint] clean — beat mix OK (beat_sheet.json)
[run] GATE SHAPE — finance chart-shape enforcement
[gate-shape] skip — not a finance reel (beat_sheet.json)
[run] GATE A — static pre-flight
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[static-check] 1 scene(s): 1 clean · 0 warn · 0 error
[run] GATE W — WCAG contrast + margins + text-overlap (independent second check)
[gateW] B1_OpeningCard clean
[gateW] B2_Packet clean
[gateW] B3_Flood clean
[gateW] B4_ApplyTools clean
[gateW] B5_Funnel clean
[gateW] B6_PaymentChecks clean
[gateW] B7_NotFound clean
[gateW] B8_Alex clean
[gateW] B9_Evidence clean
[gateW] B10_Plug clean
[gateW] B11_Fingerprint clean
[gateW] B12_Laptop clean
[gateW] B13_Locked clean
[gateW] B14_Checks clean
[gateW] B15_Traps clean
[gateW] B16_Controlled clean
[gateW] B17_End clean
[run] rendering B1_OpeningCard
[audit] scenes: 4 snapshots → CLEAN
[run] rendering B2_Packet
[audit] scenes: 24 snapshots → CLEAN
[run] rendering B3_Flood
[audit] scenes: 23 snapshots → CLEAN
[run] rendering B4_ApplyTools
[audit] scenes: 16 snapshots → CLEAN
[run] rendering B5_Funnel
[audit] scenes: 12 snapshots → CLEAN
[run] rendering B6_PaymentChecks
[audit] scenes: 18 snapshots → CLEAN
[run] rendering B7_NotFound
[audit] scenes: 17 snapshots → CLEAN
[run] rendering B8_Alex
[audit] scenes: 8 snapshots → CLEAN
[run] rendering B9_Evidence
[audit] scenes: 25 snapshots → CLEAN
[run] rendering B10_Plug
[audit] scenes: 22 snapshots → CLEAN
[run] rendering B11_Fingerprint
[audit] scenes: 26 snapshots → CLEAN
[run] rendering B12_Laptop
[audit] scenes: 29 snapshots → CLEAN
[run] rendering B13_Locked
[audit] scenes: 12 snapshots → CLEAN
[run] rendering B14_Checks
[audit] scenes: 20 snapshots → CLEAN
[run] rendering B15_Traps
[audit] scenes: 12 snapshots → CLEAN
[run] rendering B16_Controlled
[audit] scenes: 22 snapshots → CLEAN
[run] rendering B17_End
[audit] scenes: 5 snapshots → CLEAN
[art] wrote <home>/Documents/Code/info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/final-film-job-search-agent/job-search-agent-film-slate.mp4  (221.7s, audio: per-beat timeline (source audio preserved), drawtext: no — PIL overlays)
[art] slots: 17/17 filled — B1:MANIM B2:MANIM B3:MANIM B4:MANIM B5:MANIM B6:MANIM B7:MANIM B8:MANIM B9:MANIM B10:MANIM B11:MANIM B12:MANIM B13:MANIM B14:MANIM B15:MANIM B16:MANIM B17:MANIM
[run] GATE V — frame-level visual QC on the compiled reel
[gate-v] frames=34 BLOCKER=0 MAJOR=0 → <home>/Documents/Code/info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/final-film-job-search-agent/_qc/REPORT.md
RUN EXIT=0
```

## Final export (2026-11-22)

The first final attempt: GATE T passed on all 17 beats and the master was written; nothing needed fixing.

```text
### ./art final <home>/Documents/Code/info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/final-film-job-search-agent --height 2160 --out <home>/Documents/Code/info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/final-film-job-search-agent/exports/landscape
[typecheck] wrote <home>/Documents/Code/info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/final-film-job-search-agent/TYPECHECK.md
[typecheck] §8.10 B1: SKIP
[typecheck] §8.10 B2: SKIP
[typecheck] §8.10 B3: SKIP
[typecheck] §8.10 B4: SKIP
[typecheck] §8.10 B5: SKIP
[typecheck] §8.10 B6: SKIP
[typecheck] §8.10 B7: SKIP
[typecheck] §8.10 B8: SKIP
[typecheck] §8.10 B9: SKIP
[typecheck] §8.10 B10: SKIP
[typecheck] §8.10 B11: SKIP
[typecheck] §8.10 B12: SKIP
[typecheck] §8.10 B13: SKIP
[typecheck] §8.10 B14: SKIP
[typecheck] §8.10 B15: SKIP
[typecheck] §8.10 B16: SKIP
[typecheck] §8.10 B17: SKIP
[typecheck] GATE T: PASS
[art] wrote <home>/Documents/Code/info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/final-film-job-search-agent/exports/landscape/job-search-agent-film.mp4  (221.7s, audio: per-beat timeline (source audio preserved), drawtext: no — PIL overlays)
[art] slots: 17/17 filled — B1:MANIM B2:MANIM B3:MANIM B4:MANIM B5:MANIM B6:MANIM B7:MANIM B8:MANIM B9:MANIM B10:MANIM B11:MANIM B12:MANIM B13:MANIM B14:MANIM B15:MANIM B16:MANIM B17:MANIM
FINAL EXIT=0
```

## Master check (2026-11-22)

Its duration assertion is skipped because clock_check.py is missing from the toolkit; the duration was checked by hand with ffprobe (221.750 s, equal to the sum of the 17 render_duration_s values, and 0.270 s over the 221.48 s sum of actual_duration_s).

```text
### python3 <home>/Documents/Code/brutalist.art/runtime/scripts/master_check.py <home>/Documents/Code/info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/final-film-job-search-agent --mp4 <home>/Documents/Code/info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/final-film-job-search-agent/exports/landscape/job-search-agent-film.mp4
[master] PASS  3840×2160  24fps  yuv420p  h264  221.8s
MASTER EXIT=0
```
