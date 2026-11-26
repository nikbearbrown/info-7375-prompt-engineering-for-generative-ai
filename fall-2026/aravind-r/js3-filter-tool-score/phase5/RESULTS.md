# Phase 5 results: what moves the score (2026-11-25)

The plan (`phase5/PLAN.md`, commit `452cffbf`) was committed before any held-out look. Both held-out
evaluations are logged, with every row, in `phase5/heldout-log.jsonl` (2 entries).

## Held-out: baseline vs one change

| | v1.1.0-e (baseline) | v1.1.0-e.exp1 (threshold 0.70) |
|---|---|---|
| Held-out labels (Aravind) | 0 relevant, 20 not_relevant, 0 cannot_tell | (same labels) |
| Surfaced (keep or cannot_tell) | 0 | 0 |
| Relevant surfaced / relevant | n/a (0 relevant) | n/a |
| Relevant surfaced / surfaced | n/a (nothing surfaced) | n/a |
| Not-relevant postings correctly rejected | 20 / 20 | 20 / 20 |
| Snapshot counts (no labels) | keep 4, cannot_tell 3 | keep 16, cannot_tell 6 |

**What this shows, and what it doesn't:**
- **No posting in the held-out set is relevant.** The set was drawn enriched (8 of 20 PM- or
  product-titled), but under the corrected definition none qualifies. So **recall cannot be measured,
  and the threshold change cannot be judged on held-out.**
- The change quadruples the snapshot shortlist (4 → 16 kept). None of the 12 new keeps is in the
  held-out set, so whether they are right is untested.
- **The only measured fact:** neither version surfaced a held-out posting labeled not_relevant (0 of
  20).
  - 0 of 20 has an exact 95% upper bound of **16.8%** on the share of not-relevant held-out postings a
    version would surface.
  - That bound is for this enriched sample only. It is not a population rate.
- **Dev gives the same picture:** 0 relevant of 20; both versions surface none.
- **Prompt and context changes cannot be measured on held-out either.** The FILTER.md §4 amendment
  measures them on the held-out postings Aravind labeled relevant or cannot_tell, and that set is
  **empty**. No prompt change was run.
- **The one place the threshold *was* tested against hand judgments is the audit:** 15 closest calls,
  final verdicts (`audit/RESULTS.md`, view B: 0 errors at 0.80). That is dev use; those rows shaped
  v1.1.

## Persistence is not proof of training

If the scorer behaves the same way in a later session, nothing was trained.
- The behavior lives in files: `FILTER.md` §6, `persona-prefs.json`, `prompts/justify.v1.md`, and the
  frozen data, read again on every run.
- Claude's weights did not change between the claude.ai chats.
- Every `claude -p` call ran with `--no-session-persistence`, from an empty folder. The manual
  claude.ai replies came from fresh incognito chats.
- A change that "sticks" across sessions shows only that a file, a cache, or the context someone gave
  it persisted.
- To claim learning, you would need a model whose parameters changed. Nothing in this project
  changes any model parameter.

## Addendum: diff-set (post hoc, not held-out)

- **What it is:** a blind sheet of **exactly the 12 postings that threshold 0.70 keeps and v1.1.0-e
  does not** (`phase5/diffset/diffset-sheet.csv`, built by `tools/make-diffset.mjs`, row order
  shuffled with seed 20261127).
- **What it is not:** the set was chosen *by* the filter difference, after the held-out result. It
  is **post hoc, not held-out, not a random sample.** It can only say whether the extra keeps are
  right; it cannot give recall.
- **Overlap:** 9 of the 12 are audit rows Aravind already judged, mostly closest calls. 0 are on the
  label sheet. Re-labeling them blind doubles as a consistency check against the audit verdicts.
- **Blind:** the sheet shows no score, decision, or version. Those are in
  `phase5/diffset/key.json`; don't open it before labeling.
- **How to label:** with the same tool, in label mode:
  `~/.nvm/versions/node/v20.20.2/bin/node tools/judge-audit.mjs --sheet phase5/diffset/diffset-sheet.csv`.

### Result (labels by Aravind, blind, 2026-11-25; commit `5540e14b`)

**Of the 12 postings that threshold 0.70 keeps and v1.1.0-e does not, Aravind labeled 3 relevant
and 9 not relevant.**
- **Share of these extra keeps that are relevant: 3 of 12** (exact 95% interval 5.5% to 57.2%). This
  describes this post-hoc set only: not a rate, and not held-out.
- **2 of the 3 relevant ones (D04 = A022, D12 = A042) were already on the v1.1.0-e shortlist as
  cannot_tell.** exp1 only turns them into keeps.
- **So exp1 newly surfaces 10 postings, of which 1 is relevant** (D09 = A065, "5+ yrs min (stretch)").
- **The 9 not-relevant extra keeps are exactly the failure the threshold was raised to prevent**
  (Checkpoint 1, W13):
  - 6 state 8+ or 10+ years: D01–D03, D05–D07
  - 1 states "10-15 yrs" and is a hybrid role: D11
  - 2 are in London: D08, D10

  Each scored 0.70 or 0.75 on title + topic + one of location or experience.
- **Consistency check:** 7 of the 9 rows that are also audit rows had audit verdicts. **All 7 diff-set
  labels agree with Aravind's final audit verdicts.** The other 2 (A061, A065) were in the unjudged
  PM stratum.
- **Verdict on the one change:** on this post-hoc set, lowering the threshold to 0.70 adds 9 wrong
  keeps for 1 right one. This supports keeping 0.80. It is still not a held-out result, and the set
  was chosen by the change itself.

| row | posting | title | v1.1.0-e → exp1 | label | audit row | audit final verdict | Aravind's note |
|---|---|---|---|---|---|---|---|
| D01 | gh-stripe:8122188 | Product Manager, Strategic Apps | reject 0.75 → keep 0.75 | not_relevant | A037 | not_relevant | 8+ yrs min; body says Staff PM → n |
| D02 | gh-stripe:7392697 | Product Manager, Link - Consumer | reject 0.75 → keep 0.75 | not_relevant | A013 | not_relevant | 8+ yrs min → n |
| D03 | gh-stripe:7983854 | Product Manager, Disputes | reject 0.75 → keep 0.75 | not_relevant | A030 | not_relevant | 8+ yrs PM min → n |
| D04 | gh-stripe:8195440 | Product Manager, Connect Growth & Monetization | cannot_tell 0.875 → keep 0.875 | relevant | A022 | relevant | >3 yrs min, SEA/NY/SF → r |
| D05 | gh-stripe:8301646 | Product Manager, Radar | reject 0.75 → keep 0.75 | not_relevant | A049 | not_relevant | 8+ yrs PM min → n |
| D06 | gh-airbnb:8081925 | Product Manager, Services | reject 0.7 → keep 0.7 | not_relevant | A047 | not_relevant | 10+ yrs consumer PM required → n |
| D07 | gh-stripe:8306158 | Product Manager, Radar - Fraud and Abuse Prevention | reject 0.7 → keep 0.7 | not_relevant | — | — | 8+ yrs PM min → n |
| D08 | lv-spotify:03437e2a-2d5e-4593-9e97-11271014932e | Product Manager - Data Platform | reject 0.7 → keep 0.7 | not_relevant | A061 | — | London → n |
| D09 | gh-stripe:8275556 | Product Manager, Sandboxes | reject 0.775 → keep 0.775 | relevant | A065 | — | 5+ yrs min (stretch), SEA/SF → r |
| D10 | lv-spotify:7f0a8faa-f4f5-4db9-9f51-4101d6a29b34 | Product Manager - Customer Service Platform | reject 0.7 → keep 0.7 | not_relevant | — | — | London → n |
| D11 | gh-airbnb:8303047 | Product Manager, LATAM (Miami or San Francisco) | reject 0.7 → keep 0.7 | not_relevant | — | — | 10-15 yrs required; PMM hybrid → n |
| D12 | gh-stripe:8223723 | Product Manager - Issuance, Bridge | cannot_tell 0.875 → keep 0.875 | relevant | A042 | relevant | 5+ yrs PREFERRED only, SF/NY → r |
