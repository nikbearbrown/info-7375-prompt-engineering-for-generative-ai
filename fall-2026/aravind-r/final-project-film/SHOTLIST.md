# SHOTLIST — Readback (show-tell) · v2 visuals

Typed work order for v2. The narration clips and beat durations are identical to v1 (`mp3/` copied byte for byte). Everything is made by the free local pipeline: Kokoro narration, Manim drawings for BIDEA–B08, and the Remotion outro. There are no slates, pantry media, stock footage, generated imagery or sound effects.

**Design system:** `../gates/v2-visual-plan.md`.
- **Colour roles:**
  - ink: Readback and the PM's instruction, and all text;
  - kraft (tan): existing tools and evidence;
  - red: the disputed clause, C4, only;
  - grey: planned work.
- **Progress rail** along the top: What · Why · Who · Proves · Scope · Risk · Why me.
- **The rubric page** carries through the film. It has a dark header band and clauses C1–C5, with red always on C4.
- **Cue timing:**
  - every cue is timed to `mp3/words.json`;
  - transitions run 0.4–0.8 s;
  - nothing animates across a clip's midpoint (`P()`);
  - a focus dim marks each topic change.

| Beat | Lane | Fill | What moves (and why) | Output |
|---|---|---|---|---|
| BIDEA | manim | `BIDEA_Hook` | Rubric C1–C5 draws; "Aravind Ravi · read by a synthetic voice"; a recap card; 3 judges; stamps pass, pass, fail; C4 red; "Does the judge misread my rubric?" types | `manim/BIDEA.mp4` |
| B01 | manim | `B01_WhatItIs` | "Readback"; three rays converge on C4 and turn red; "Did you mean…?" → PM; the diagram collapses to the rubric icon; grey repo, `$ readback-pm check rubric.md`, case study, eval log, before → after | `manim/B01.mp4` |
| B02 | manim | `B02_Difference` | The icon grows back into the page; "score: pass" vs "ship decision: wrong"; the grid builds row by row from logged checks; Readback column grey "planned" / "never"; Spec Kit row | `manim/B02.mp4` |
| B03 | manim | `B03_FirstMinute` | Reader figure; "first 60 seconds" stopwatch; README opens and scrolls to the table; 5 headers with "—" cells; PM end user; the stopwatch sweeps | `manim/B03.mp4` |
| B04 | manim | `B04_Proves` | "it will show I can:"; 4 skill labels connect to their evidence; grey labels → judge runs commits; the real AMI line → real recap line; anchor; 4 features → 1 | `manim/B04.mp4` |
| B05 | manim | `B05_InOutFirst` | 10 meeting cards → real DECISIONS bars (ValueTracker); real recap word counts vs the 250 line; IS1004d call-out; OUT; C4 → ? → PM; grey first-run checklist; commit order; full-contrast close | `manim/B05.mp4` |
| B06 | manim | `B06_Risk` | "overfitting"; a revise loop; the deck splits dev / held-out; the padlock snaps shut; "held-out score: —"; same-model vs cross-model circles | `manim/B06.mp4` |
| B07 | manim | `B07_WhyMe` | "a mix"; the "new to me" bracket; a timeline with tan role chips ("internal — not shown"); PR #8 ✓, PR #23 · DRAFT; grey Readback; links from the new skills | `manim/B07.mp4` |
| B08 | manim | `B08_ExistsWill` | "exists · 14 Oct 2026" (real items, the real excerpt) vs "will exist" (grey); everything fades, the rubric page comes to the centre (match-cut) | `manim/B08.mp4` |
| BOUT | bookend | Remotion `ClaudeTitleOutro` (my patch: handle, `hideMascot`) | "Readback.", "Aravind Ravi · INFO 7375"; no mascot | `media/BOUT.mp4` |
