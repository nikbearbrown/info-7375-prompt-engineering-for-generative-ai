# Phase 5 plan, declared before any held-out look (2026-11-25)

**One change, to one object: the filter file.** `threshold` goes from 0.80 to 0.70, in
`experiments/FILTER.exp1-threshold-0.70.md` (v1.1.0-e.exp1). Nothing else changes, and `FILTER.md`
stays frozen at v1.1.0-e (tag `js3-filter-final`).

## Why this change
- It is the Checkpoint 1 decision run in reverse: 0.70 was the draft value, and Aravind raised it to
  0.80 because a core PM role with location = 0 or experience = 0 then scored 0.75 and passed.
- So it isolates a single hand-set number whose effect was argued but never measured on labels.
- **Dev cannot choose a change:** all 20 dev labels are not_relevant, v1.1.0-e rejects all 20, and
  exp1 also surfaces 0 dev postings. The choice therefore rests on the Checkpoint 1 reasoning, not
  on dev.

## What it does on the snapshot (no labels)
- keep 4 → 16, cannot_tell 3 → 6, reject 1,057 → 1,042.

## How it is measured
- Held-out relevance labels only (`tools/eval-labels.mjs --set heldout --heldout-final`). Every look
  is logged to `phase5/heldout-log.jsonl`.
- Exactly two held-out evaluations: the baseline (v1.1.0-e) and exp1.
- Reported as counts: relevant surfaced / relevant, and relevant surfaced / surfaced. The sheet is
  enriched, so these are not population rates.

## Prediction, written before looking
- Recall can only rise or stay the same, because a lower threshold only adds postings.
- Precision may fall: under W13 reasoning, exp1 lets location-0 and experience-0 core PM roles
  through.
