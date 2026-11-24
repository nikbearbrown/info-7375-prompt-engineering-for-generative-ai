# Evaluation after the brand-name fix — same 25 companies, 2026-11-23

## Executive summary

**What this is:** the same 25 companies from my October evaluation, run again after fixing how the tool looks up brand
names. **Why read it:** in October the tool missed three strong sponsors (Robinhood, SoFi, Chime) because the dataset
stores them under their legal names. **What it found:** all three now appear as candidates for a person to confirm;
none is picked automatically. Three other companies (Plaid, Ramp, Coinbase) now also show candidates, all with no
approvals on record. No company that had an answer before lost it, and no company got a wrong automatic answer.

## Run record

- Script: `eval_rows_after_fix.py` (calls the recipe's own matcher + its alias file) → `eval-after-fix-2026-11-23.json`
- Before: `../../final-project-film/evidence/eval-rows-dataset-2026-10-25.json`. Same CSV (sha256 identical, checked).
- Fix: fork branch `final/arundhatik26-and-fix`, on top of `379252f` (not yet committed at time of run).
- Tests: 18 → 26; 9 failed before the fix (`tests-before-fix-2026-11-23.txt`), 26 pass after (`tests-after-fix-2026-11-23.txt`).
- Predictions written first: `../PREDICTIONS.md`, 2026-11-23 15:32 EST.

## The three brand-name misses

| Company | Before (10-25) | After (11-23) | Right company listed? | Found by |
|---|---|---|---|---|
| Robinhood | not in dataset | needs human check — 2 candidates | **yes** — ROBINHOOD MARKETS INC, 824 | first word |
| Chime | matched CHIME INC (2) → "Possible", no human | needs human check — 2 candidates | **yes** — CHIME FINANCIAL INC, 580 (listed first) | first word |
| SoFi | not in dataset | needs human check — 3 candidates | **yes** — SOCIAL FINANCE INC, 182 | alias list only |

## The other 22 companies

| Change | Companies |
|---|---|
| No change | 19 (PayPal, Visa, Goldman Sachs, Mastercard, BlackRock, LSEG, JPMorgan Chase, Morgan Stanley, Citi, Bank of America, Wells Fargo, Capital One, BNY, State Street, Fidelity, Charles Schwab, Stripe, Affirm, Brex) |
| New candidates, sent to a human | 3 — Plaid (PLAID TECHNOLOGIES INC), Ramp (3 rows), Coinbase (COINBASE GLOBAL INC); every candidate has **blank** approvals |
| Auto-answered wrongly | 0 |

Stripe is still auto-matched (exact name STRIPE INC, 1,250 approvals, Proven) — an exact name is not a guess.

## Totals

| | Before | After |
|---|---|---|
| Strong software sponsor in the dataset that the tool did not show | 3 | **0** |
| Sent to a human check (G2) | 0 | **6 of 25** |
| Wrong automatic answer | 1 (Chime → CHIME INC) | **0** |

## Against my predictions (`../PREDICTIONS.md`)

| # | I predicted | What happened |
|---|---|---|
| 1 | A alone finds 2 of 3: Robinhood and Chime; not SoFi | Right — A found Robinhood and Chime; for SoFi it found only SOFI TECHNOLOGIES INC (blank), not SOCIAL FINANCE INC |
| 2 | SoFi needs the alias list | Right — SOCIAL FINANCE INC appears only through the alias |
| 3 | "a few additional candidates" in the other 22 | 3 companies changed (Plaid, Ramp, Coinbase); all blank, so none would have given a wrong "yes" |
| 4 | all three go through the human check | Right — all three are "ambiguous", none auto-picked |
| 5 | fails if Robinhood/Chime not listed, SoFi not found with alias, or anything auto-selected | None of these happened |

## Not checked

- Whether the Ramp, Plaid and Coinbase candidates are the same companies (a human must still decide; none has approvals).
- The alias list has one entry (SoFi). Other brands with unrelated legal names outside these 25 will still be missed.
- The USCIS hub is not yet joined as a second source.
