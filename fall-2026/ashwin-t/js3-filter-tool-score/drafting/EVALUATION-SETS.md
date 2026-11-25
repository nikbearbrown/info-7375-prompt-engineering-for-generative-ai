# Label sets and what each may be used for (Claude Code, 2026-11-25)

Drafted by Claude Code from Ashwin's instructions in chat on 2026-11-25. Kept here so the README and CHANGE.md can
state exactly which labels touched which decision.

## The label files

| File | Who made it | Use |
|---|---|---|
| `labels/heldout-sheet.csv` | Ashwin, blind (committed alone at `9757ee7b`: Y 7, N 19, ? 4) | Held-out measurement of one frozen change |
| `labels/audit-sheet.csv` | Ashwin, blind (filling now) | Reject audit; the only verdicts `--report` reads |
| `labels/audit-ai-draft.csv` | Codex, inferred from Ashwin's 30 held-out labels | Proposals only; never copied into `audit-sheet.csv`, never read by code |
| `labels/audit-ai-assisted.csv` | Codex's suggestions for batch 1 (10 rows, same as the draft), adopted by Ashwin on 2026-11-25 **without reviewing the postings** | AI-assisted verdicts; not hand judgments, not in `audit-sheet.csv`, not counted toward the hand-judged audit |

## Minimum audit sample

The brief asks for at least 30 random rejects judged by hand, plus the closest calls near the threshold and a
sample of what was kept. `jobfilter/audit_batches.py` takes those four strata unchanged from the saved selection
(seed 20261126): random_reject 30, close_below 6, close_at 5 and kept_random 6. That makes 47 distinct postings,
in 5 blind batches in `labels/audit-minimum-batches.md`. Nothing was redrawn.

The other two strata, `exclusion_check` (8) and `review` (7), add 14 more distinct postings. They are optional. If
they stay unjudged, the FILTER.md section 10 row "level-II and forward-deployed exclusions kept" stays **not
measured**, and the sign-off must list it under Not checked.

Ashwin's clearance rule: if a posting needs a clearance and Supriya's eligibility is unknown, the verdict is `?`.
Willingness to get a clearance is not eligibility. `data/supriya-sharma.resume.json` says nothing about citizenship
or clearance.

## If Codex's proposals influence a rule change

Codex's draft was inferred from the 30 held-out labels. If any proposal in it shapes a rule change, for example as
a reason, a tie-breaker or a confirmation, then:

- CHANGE.md must say that the original held-out labels informed the proposals behind the change.
- The 30-posting comparison must not be called untouched or held out.
- Further tuning needs an evaluation set that nothing has touched.

## Candidate unused evaluation set

`../js1-contract-and-watch/snapshots/cloudflare-2026-10-29T23-55-50Z.json` is a JS1 snapshot of the Cloudflare
board, with 463 postings.

- No key overlaps the 805-posting JS3 corpus (checked 2026-11-25).
- JS1's README lists it as unused.
- None of the five JS1 sampling postings come from it.
- Neither filter v1.0, the Codex draft nor any label sheet has read it.

**Caveats:**
- It is a different employer, so it measures how the filter transfers, not how it does on the same mix of boards.
- Ashwin saw the board during JS1, before switching boards.
- It is not yet loaded or labeled. Using it would mean drawing a sealed sample with a recorded seed, having Ashwin
  label it blind, and only then running the frozen filter on it.

The other option is a fresh fetch of the same five boards today, keeping only keys outside the 805. That would
match the development mix, but it needs a live fetch and the same blind labeling.

Not chosen yet; this is Ashwin's decision.
