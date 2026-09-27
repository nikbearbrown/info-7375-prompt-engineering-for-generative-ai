# Manual QC log — week-01-softmax-max-subtraction

Kept separate from `_qc/REPORT.md`, which Gate V (`final_frame_check.py`) overwrites on every
final build. That overwrite erased the draft-1/draft-2 notes on 2026-09-27; restored below from
the session record.

## Draft 1 (2026-09-26) — 1080p review cut, 88.5 s
Frames read at 15/50/85% and last frame of every beat. Fixed:
- B01 BLOCKER: output card overflowed both frame edges.
- B03 MAJOR: "Totals computed from printed values." clipped at right edge.
- B04 MAJOR: raw column 20.086 collided with the column divider.
- B05 BLOCKER (algebra): cancellation strike hit "=" and missed the "m" of e^{-m} in the numerator.
- B06 MINOR: divider touched "shared by both"; content top-clustered.
- B08 BLOCKER: last line clipped at right edge.

## Draft 2 (2026-09-27) — 1080p review cut, 114.8 s
- scenes.py patch corrupted two TeX strings (shell collapsed backslashes) — repaired.
- B06B MAJOR: "gap of 1 in both" collided with the source label; lower third empty — re-spaced.
- Transcript: B03 "Computed directly" audible in the isolated beat; full-cut transcript heard "Directly".

## Master pass (2026-09-27) — 4K
Gate T (type_check.py):
- B05 FAIL contrast: terracotta #D97757 glyphs 2.74:1 on cream. Fixed by moving every accent
  GLYPH (B01, B02, B04, B05, B06, B07, B08) to #A44A32 (5.11:1, WCAG AA); #D97757 kept for
  non-text marks only (rules, boxes, strikes). Gate T then PASS; all source labels were above the
  41 px floor, so none needed enlarging.

Gate V (final_frame_check.py) first run — 9 BLOCKER, 4 MAJOR:
- BLOCKER edge-bleed B01–B04, B07: bottom-left source labels sat ~74 px from the frame edge
  (safe inset 96 px); B07 numbers wider than the safe area. Fixed: labels moved inside the inset;
  B07 mono 72 -> 60.
- MAJOR underfill B00 (50%), B02 at 50%, B06B at 50%. Fixed by layout, not by waiver:
  B00 larger type + spacing; B02 two-column (scores/result left, formula right) under a heading;
  B06B shows both input rows with "p = ?" placeholders that resolve on "The result matches",
  subtraction line moved to the top.
- Found by eye, not by the gate: B06B source label overlapped "gap of 1 in both" after a move —
  split the label onto two right-aligned lines.

Local Gate V harness (`_qc/gate_v_local.py`, same analyze_frame, same 50/85% fractions): all
beats pass before the final build.

## Final master (2026-09-27)
`week-01-softmax-max-subtraction.mp4` — 3840x2160 h264, 24 fps, AAC 48 kHz stereo, 116.42 s, 9.8 MB.
- Gate T PASS; Gate V 0 BLOCKER / 0 MAJOR (20 frames, `_qc/REPORT.md`); factcheck_check clean.
- One frame per beat read from the master itself: no beat-id or timecode burn-in, no clipping,
  no collisions.
- Audio: mean -27.4 dB, max -5.5 dB (audible).
- Transcript (whisper small.en and medium.en): B03 "Computed directly, … 2.7, 7.4, and 20.1";
  B07 "for two of the three probabilities, the methods differ in the last digit".
