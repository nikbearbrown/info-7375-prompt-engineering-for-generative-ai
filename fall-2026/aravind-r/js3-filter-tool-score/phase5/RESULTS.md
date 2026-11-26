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

## Addendum: diff-set (post hoc, not held-out), labels pending

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
