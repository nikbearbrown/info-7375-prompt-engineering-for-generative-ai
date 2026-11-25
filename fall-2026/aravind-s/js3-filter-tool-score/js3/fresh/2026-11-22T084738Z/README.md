# A fresh blind set for FILTER.md v1.1, filter run 2026-11-22T084738Z

Made by `tools/fresh_kit.py` (Claude Code, at Aravind's request) on 2026-11-24, before any verdict, from `js3/filter-run/2026-11-22T084738Z/` (v1.1) and `js3/filter-run/2026-11-21T044414Z/` (v1.0, the same saved answers).

## Why this set exists

Aravind made v1.1's three calls (a cutoff of 50, 10 points off for an export-control line, no "build systems") after seeing the held-out results, so the held-out set (`js3/heldout/2026-11-21T044414Z/`) became development data on 2026-11-22 and no longer tests them. This set holds postings he has never been shown, most of them ones whose recommendation v1.1 changes, so his verdicts can say whether the calls hold on new labels. The book, chapter 9: a held-out set is touched once.

## How it was drawn

Seed **2026112401**, a new one (the audit used 20261121 and 20261122, the claims kit 2026112102, the held-out set 2026112103), and the card order shuffled with seed 2026112402. The full rule is in the tool's docstring. "Recommended" means kept with a score at or above the version's cutoff (v1.0: 60, v1.1: 50).

Left out: the 99 postings already shown to Aravind (the audit's and the held-out set's cards, both runs' shortlists, which the claims kit and the reports show, and the two postings the MCP runs scored) and every other posting with the same board and normalized title as one of those.

| Stratum | In the run | Already shown | Same-title copies | Left to draw from | Cards |
|---|---:|---:|---:|---:|---:|
| A: v1.1 adds | 41 | 16 | 1 | 24 | 12 |
| B: the penalty holds back | 8 | 5 | 0 | 3 | 3 |
| C: both recommend | 50 | 25 | 2 | 23 | 3 |
| D: both reject | 308 | 15 | 12 | 281 | 2 |

- A: kept, recommended by v1.1 and not by v1.0 (the cutoff moved from 60 to 50).
- B: kept, below v1.1's cutoff only because of the 10-point export-control penalty (recommended without it).
- C and D are controls: recommended by both versions, and rejected by both for exactly one rule.
- No posting's v1.1 recommendation changes with "build systems" back (it moves only scores and ranks), so no card here can test that call.
- Kept postings that v1.0 recommends and v1.1 does not: 0.

Which card came from which stratum, and every score, is in `sealed/answers.json` (SHA-256 `1be18c40d3ff408c7f79e2089f3153d69833030114069090c66596b42808f27e`). It is opened only after VERDICTS.md is committed; the hash shows it was not changed. What each outcome would mean is in PREDICTIONS.md, written with the kit, and `tools/score_fresh.py` scores it.

## What this set may claim

Small random draws from strata of one day's saved answers of three boards, judged by one person. Each stratum is reported on its own, with its bound where it has one. It is not a rate for all postings, and it says nothing about live postings, other boards or other days. The filter runs' reports list kept postings with their scores and are public in this repo; Aravind has not studied them, but they were not hidden from him.
