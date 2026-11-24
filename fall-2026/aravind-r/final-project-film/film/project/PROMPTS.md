# PROMPTS — Readback project film

No generative media: no image, video or voice-cloning prompts. The narration is the free local Kokoro voice `am_onyx`, synthesized from the script I approved (Phase 1 on 2026-11-23, and the revised narration that evening). Every visual is a deterministic Manim or Remotion render. The three B02 vignettes are constructed illustrations drawn in Manim; they are not generated images or real product outputs.

## Prompts behind real material shown in the film

**Recap feature (the B10 excerpt from ES2007a, and the B14 excerpt from ES2010b).** The system prompt is `../../case-study/constructed/recap-system-prompt.md` (everything below its `---` line). `../../case-study/run_feature.py` sent it with `claude -p --system-prompt … --tools "" --output-format json`, with each meeting's `transcript.txt` as the input. The outputs, with their date, Claude Code version and model, are in `../../case-study/outputs/feature-run/`.

No other Claude response appears on screen.

## How the film was made

These are my prompts to Claude Code, in order. The log, with each decision, is `../../FRICTIONAL.md`.

1. **"Readback project film (four-part brief)" (2026-11-23).** It set the four parts (executive summary, introduction, methods, evaluation), the hard rules (honesty, labels, prior work as plain text, no instructor persona, the pitch films untouched, a free local pipeline, commits without attribution trailers) and the phases with stop points.
2. **Phase approvals:** Phase 1 (narration and claims), Phase 2 (storyboard), then "Approve, go to Phase 3".
3. **My review requests before Phase 5:**
   - B15's checklist only ticks what is set up on this Mac;
   - the human labels read as mine and planned;
   - prior work is scoped to "the tools I checked";
   - B13 is reworded and Readback respelled for the voice;
   - the storyboard is regenerated and every gate re-run;
   - the submission options, then my choice of route, and four checks (clip hashes, full-film speech-to-text, the B15 wording, a full gate re-run).
4. **My feedback on the review cut:**
   - the positioning (Readback is for any AI feature's acceptance criteria; the AMI meeting-recap feature is only the test bench);
   - P0 items 1–7 and P1 items 8–13;
   - a new positioning-audit gate;
   - text before voicing.
5. **Approvals:** "OK, go" for the revised narration and build, then "Approve cut".

For each step, Claude Code drafted the narration, the claims ledger (`CLAIMS.md`), the evaluation plan (`EVAL-PLAN.md`), the design system (`DESIGN.md`), the scenes and the gate reports. I approved each phase before the next.
