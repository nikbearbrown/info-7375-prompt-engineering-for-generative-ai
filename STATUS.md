# Book build state — INFO 7375

Updated 2026-09-06. Current phase: Gate 2 manuscript review, with the Cajal production pass completed under the author's explicit instruction. Human review gates remain unsigned.

## Recorded human decisions

The author approved the Blueprint in earlier conversational replies. The latest instruction is explicit: “Approve the research packet and draft the chapters.” [The approval record](research/approval-20260906.md) records the author's Gate 1 decision and authorizes drafting all fifteen chapters. It is not an agent's independent signature. No additional planning or research approval is needed to continue the remaining chapters.

- [x] Gate 0 — Blueprint approved in conversation.
- [x] Gate 1 — research packet approved by the author, 2026-09-06, with its stated scope and exclusions.
- [x] Gate 2 — full AI draft assembled; awaiting human review before Gate 3.
- [ ] Gate 3 — human rewrite and author sign-off.
- [ ] Gate 4 — full manuscript claims checked and approved.
- [ ] Gate 5 — 20 figures generated and agent-audited; human review pending.
- [ ] Gate 6 — figure audits approved.

## Saved full draft

[Chapter index](chapters/README.md). Chapters 1–15 total **83,578 whitespace-delimited words** including retained figure-provenance comments. They are AI drafts awaiting human review, not finished author text. All have unsigned review sidecars with `verified:false`. Gate 2 means the full draft exists; it does not grant Gate 3 author sign-off.

[Batch 1 report](chapters/draft-batch-01-report.md) preserves the initial structural checks and validation. Final validation reports no structural failures across all fifteen manuscripts. All 15 lesson demos, 90 lesson tests, and 13 integration tests pass. The Cajal pass produced 15 chapter-specific SCOPE plans, 20 accessible SVG sources, 20 matching 300-DPI PNGs, and 20 in-chapter references and captions. Automated audits passed structure, accessibility metadata, palette, prohibited-effect, raster-dimension, and grayscale checks. Existing course code and unrelated syllabus/ changes are untouched. No live model calls, commits, pushes, human approvals, or EPUB builds occurred.

## Open item — chapter 1 expansion, 2026-09-07

At the author's instruction ("fine to have a long chapter"), chapter 1 was restructured
into Part 1 (what a language model does: next-token prediction, the chat scaffold,
pretraining and preference tuning, scale derivations, the transformer sketch, and the
stochastic-parrot argument) and Part 2 (the existing randomness material, plus a new
worked prompt sequence). It is now 8,729 words with five figures.

Two consequences need an author decision:

- **The draft word ceiling was raised from 8,000 to 9,000** in
  [check-drafts.py](research/check-drafts.py) to accommodate it. No other chapter is
  near either bound. Reverting the ceiling means cutting roughly 750 words from Part 1.
- **[chapters-spec.md](chapters-spec.md) chapter 1 is now stale.** Its five content
  blocks describe Part 2 only; the Cajal candidate names one figure where there are
  five. The spec was approved at Gate 1, so it has been left unedited rather than
  silently rewritten to match the manuscript.

New Part 1 sources are registered in [sources.md](research/sources.md) as
bibliographic citations that were **not** link-checked in this pass. The scale
derivations are reproducible via [llm_scale.py](research/llm_scale.py) and recorded in
[llm-scale.json](research/llm-scale.json); they are logged as unverified claim
`C01-scale` in [facts.json](facts/facts.json). Chapter 1's review sidecar remains
`verified: false`.

## Next gate — human review required

Review the complete manuscript before Gate 3. The author may rewrite, request revisions, or decline sign-off. Do not run the human-only signing command on the author's behalf.

Do not proceed into human rewrite, full fact-check, human figure approval, or EPUB delivery without the next human decision. Human rewrite and final visual approval remain human-only.

## Metadata and runtime honesty

Conversational approvals above supersede earlier pending labels in planning/research prose. No agent has run the human-only verify.py sign command. Existing research/fact sidecars remain unchanged; new draft sidecars are verified:false. This records actual author authorization without pretending an automated signature or per-claim fact-check occurred.

No background drafting or figure job is running after this turn. Drafting and the requested Cajal production pass are complete; later human gates await review.
