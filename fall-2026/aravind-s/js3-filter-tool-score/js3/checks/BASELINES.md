Computed by Claude Code on 2026-11-24 from committed files, after the fact. Not a new measurement. Rebuild: `python3 tools/baselines.py` from the repo root (`--check` compares without writing).

# Baselines, distance from the boundary, and what the held-out draw could detect

A diagnostic. It changes no rule, no verdict and no frozen result, and it opens nothing sealed that was not already open: the audit's answers were opened on 2026-11-22 (`js3/audit/2026-11-21T044414Z/RESULTS.md`), the held-out answers on 2026-11-22 for the one measurement (`js3/heldout/2026-11-21T044414Z/CHANGES.md`).

Read from:

- `js3/audit/2026-11-21T044414Z/sealed/answers.json` (SHA-256 `b812a56034ab763ce429eeef5ff2de40e9d688dc454bcc4a2709709b6b107e86`, the hash `SAMPLE.md` published), `js3/audit/2026-11-21T044414Z/VERDICTS.md`, `js3/audit/2026-11-21T044414Z/AFTER-REVEAL.md`
- `js3/heldout/2026-11-21T044414Z/sealed/answers.json` (SHA-256 `9d9b062acb945d5d847e47f4fa8da804a450ae97c58c849e532ff2f7a397356a`, the hash `README.md` published), `js3/heldout/2026-11-21T044414Z/VERDICTS.md`
- `js3/filter-run/2026-11-21T044414Z/verdicts.json` (FILTER.md v1.0) and the saved board answers it names, checked against their SHA-256
- `js3/score/runs/2026-11-22T083619Z/` (`R0.json`, `X1.json` to `X6.json`, `whole-run.json`), used as cross-checks
- `FILTER.md` Section 7, version 1.0; `persona/jane-doe.json`; the changes as `tools/heldout_experiments.py` builds them

## 1. The audit: the filter against "reject everything" and "keep everything"

On the cards Aravind judged Keep or Reject; a "?" is left out, as `tools/score_audit.py` does. The filter is FILTER.md v1.0 as frozen: the fates in the sealed answers. A constant answer agrees with him wherever his verdict is that answer.

His verdicts as frozen (`VERDICTS.md`, commit `45fc2c0`):

| Group | Cards | Judged | Reject everything | Keep everything | The filter as frozen (v1.0) |
|---|---:|---:|---:|---:|---:|
| random reject | 30 | 30 | 29 of 30 | 1 of 30 | 29 of 30 |
| kept sample | 10 | 9 | 0 of 9 | 9 of 9 | 9 of 9 |
| close call: kept near the cutoff | 8 | 7 | 0 of 7 | 7 of 7 | 7 of 7 |
| close call: failed one rule | 7 | 6 | 6 of 6 | 0 of 6 | 6 of 6 |
| **all** | **55** | **52** | **35 of 52** | **17 of 52** | **51 of 52** |

With the checks asked after the reveal (`AFTER-REVEAL.md`: card 17 from Keep to Reject), reported beside the frozen result, never in place of it, as `RESULTS.md` does:

| Group | Cards | Judged | Reject everything | Keep everything | The filter as frozen (v1.0) |
|---|---:|---:|---:|---:|---:|
| random reject | 30 | 30 | 30 of 30 | 0 of 30 | 30 of 30 |
| kept sample | 10 | 9 | 0 of 9 | 9 of 9 | 9 of 9 |
| close call: kept near the cutoff | 8 | 7 | 0 of 7 | 7 of 7 | 7 of 7 |
| close call: failed one rule | 7 | 6 | 6 of 6 | 0 of 6 | 6 of 6 |
| **all** | **55** | **52** | **36 of 52** | **16 of 52** | **52 of 52** |

What this shows:

- Inside each group the filter gives every card the same answer, because the kit drew each group by the filter's fate. So in each group it equals one of the two constant answers by construction, and a group alone cannot tell the filter from a constant.
- Over all 52 judged cards the filter agrees on 51 and "reject everything" on 35 (after the reveal: 52 and 36). The filter is the only one of the three answers that matches him in every group.
- The totals depend on the kit's mix, which over-draws kept postings on purpose: 18 of the 55 cards are postings the filter kept, against 99 of the 1508 postings the run gave a fate (6.6%). He marked Reject on 29 of the 30 random rejects he judged, so on a uniform sample of the run "reject everything" would agree more often than here, and "keep everything" less often.

## 2. The held-out set (development data since 2026-11-22)

Development data since 2026-11-22: after the one measurement, Aravind's three calls for FILTER.md v1.1 (cutoff 50, an export-control line costs 10 points, "build systems" dropped) used its results, so it has guided a change (`js3/heldout/2026-11-21T044414Z/CHANGES.md`). These numbers describe the set; they are not an independent test of v1.1.

On the cards he judged Keep or Reject, his verdicts as frozen (`VERDICTS.md`, commit `1e2b1e1`); the filter is v1.0 as frozen (the fates in the sealed answers, the same as the saved run `R0.json`):

| Pool | Cards | Judged | Reject everything | Keep everything | The filter as frozen (v1.0) |
|---|---:|---:|---:|---:|---:|
| kept | 15 | 12 | 0 of 12 | 12 of 12 | 12 of 12 |
| rejected | 15 | 15 | 15 of 15 | 0 of 15 | 15 of 15 |
| **all** | **30** | **27** | **15 of 27** | **12 of 27** | **27 of 27** |

The pools were drawn equally (15 kept, 15 rejected), so the constant answers score 15 and 12 of 27 because of that design, and again each pool alone cannot tell the filter from a constant.

## 3. How far the audit's random rejects sit from the boundary

Distance here is the number of hard rules a rejected posting fails (every rule runs on every posting, `verdicts.json`). The v1.0 run gave 1508 postings a fate: 1409 rejected (93.4%) and 99 kept. The audit's 30 random rejects are a uniform sample of the 1409 rejects.

| Hard rules failed | Audit random rejects (30) | All rejects of the run (1409) |
|---:|---:|---:|
| 1 | 6 | 318 |
| 2 | 11 | 490 |
| 3 | 10 | 434 |
| 4 | 3 | 158 |
| 5 | 0 | 9 |

| Rule | Random rejects failing it | All rejects failing it | Random rejects failing only it | All rejects failing only it |
|---|---:|---:|---:|---:|
| R1 employment type | 0 | 75 | 0 | 0 |
| R2 location | 9 | 335 | 1 | 9 |
| R3 job level | 12 | 666 | 0 | 11 |
| R4 job role | 28 | 1214 | 4 | 207 |
| R5 work authorization and sponsorship | 6 | 361 | 0 | 28 |
| R6 start date | 0 | 3 | 0 | 0 |
| R7 years of experience | 15 | 623 | 1 | 63 |
| R8 AI training and data annotation | 0 | 0 | 0 | 0 |

- **28 of the 30 random rejects fail R4** (the title names no software engineering role, or names an excluded one), and **24 fail two or more rules**. Over all 1409 rejects: 1214 fail R4 (86.2%) and 1091 fail two or more (77.4%).
- Near the boundary means an engineering title (it passes R4) that fails exactly one other rule: 111 of the 1409 rejects (7.9%), and 2 of the 30 random rejects.
- So the clean result on the random rejects is mostly a result on easy rejects. The random rejects near the boundary are cards 15 (R7) and 23 (R2): 0 misses in 2 judged, which bounds the miss share among those 111 postings only at 77.6% (the exact one-sided 95% upper bound, `upper_bound()` in `tools/score_audit.py`). The audit's 7 close calls that failed one rule were drawn one per rule, then at random, so they are not a uniform sample and give no rate.
- Rule counts measure distance by the filter's own rules, not by his judgment: card 17 failed 2 rules (R4 and R5), and he kept it from the card he saw.

## 4. What the held-out draw could detect

The held-out kit drew 15 postings from a pool of 69 kept and 15 from a pool of 1350 rejected (the audit's postings, the shortlist and their same-title copies left out, as `tools/heldout_kit.py` does). For each change, the postings of the whole run it moves against v1.0, judged by the filter with the change: its fate, its score, its failed rules, or whether it is recommended (kept and at or above the cutoff). X1 to X4 keep the cutoff, so their recommendation is compared at each of 60, 55 and 50; X5 and X6 are the cutoff, so v1.0 at 60 is compared with the change at its own cutoff (their fates and scores are v1.0's: the tool checks that only the cutoff differs, and `whole-run.json` records 0 and 0 for both).

| Change | Fates | Scores | Failed rules | Recommended at 60 | At 55 | At 50 |
|---|---:|---:|---:|---:|---:|---:|
| X1 | 0 | 0 | 0 | 0 | 0 | 0 |
| X2 | 0 | 0 | 69 | 0 | 0 | 0 |
| X3 | 0 | 7 | 0 | 1 | 4 | 0 |
| X4 | 0 | 9 | 0 | 0 | 3 | 8 |
| X5 | 0 | 0 | 0 | n/a | 22 (v1.0 at 60 against this cutoff) | n/a |
| X6 | 0 | 0 | 0 | n/a | n/a | 49 (v1.0 at 60 against this cutoff) |

Where a change moved anything, how much of it the draw could reach. The chance is exact: C(N - m, n) / C(N, n) for each pool that holds moved postings, multiplied, with N the pool, m the moved postings in it and n the kit's draw from it (15 kept, 15 rejected).

| Change | What moved | In the run | In the kept pool (69) | In the rejected pool (1350) | In the held-out draw | Chance a uniform draw holds none |
|---|---|---:|---:|---:|---|---|
| X2 | failed rules | 69 | 0 | 65 | 2 (cards 03, 11) | C(1285, 15) / C(1350, 15): 47.5% |
| X3 | score | 7 | 4 | 0 | 0 | C(65, 15) / C(69, 15) = 6201/16951: 36.6% |
| X3 | recommended at 60 | 1 | 1 | 0 | 0 | C(68, 15) / C(69, 15) = 18/23: 78.3% |
| X3 | recommended at 55 | 4 | 2 | 0 | 0 | C(67, 15) / C(69, 15) = 477/782: 61.0% |
| X4 | score | 9 | 6 | 0 | 3 (cards 10, 22, 29) | C(63, 15) / C(69, 15) = 116865/542432: 21.5% |
| X4 | recommended at 55 | 3 | 1 | 0 | 1 (card 29) | C(68, 15) / C(69, 15) = 18/23: 78.3% |
| X4 | recommended at 50 | 8 | 6 | 0 | 3 (cards 10, 22, 29) | C(63, 15) / C(69, 15) = 116865/542432: 21.5% |
| X5 | recommended at 55 | 22 | 14 | 0 | 3 (cards 19, 28, 29) | C(55, 15) / C(69, 15) = 1383364395/65900684368: 2.1% |
| X6 | recommended at 50 | 49 | 35 | 0 | 8 (cards 08, 10, 17, 19, 22, 27, 28, 29) | C(34, 15) / C(69, 15) = 15/4581527: 0.0003% |

What each result could show:

- **X1** moved nothing in the whole run by any of these measures, so no draw could show it: "no card changes" is certain, not a sample result.
- **X2:** the draw held some of the postings X2 moved:
  - failed rules: 2 of the 65 moved postings in the pools (cards 03, 11); a draw with none of them was quite possible (47.5%). `EXPERIMENTS.md` reports no card change for X2 because it compares fates and scores only; these cards' failed rules differ between the saved `R0.json` and `X2.json`.
- **X3:** the draw held none of the postings X3 moved, so "none moved here" says little about X3:
  - score: none of the 4 moved postings in the pools; a uniform draw holds none of them 36.6% of the time (quite possible).
  - recommended at 60: not the one moved posting in the pools; a uniform draw misses it 78.3% of the time (more likely than not).
  - recommended at 55: none of the 2 moved postings in the pools; a uniform draw holds none of them 61.0% of the time (more likely than not).
- **X4:** the draw held some of the postings X4 moved:
  - score: 3 of the 6 moved postings in the pools (cards 10, 22, 29); a draw with none of them was quite possible (21.5%).
  - recommended at 55: the one moved posting in the pools (card 29); a draw without it was more likely than not (78.3%).
  - recommended at 50: 3 of the 6 moved postings in the pools (cards 10, 22, 29); a draw with none of them was quite possible (21.5%).
  - recommended at 60, the cutoff it was measured with: no posting moves anywhere in the run, so no draw could show a change in what is recommended there (the prediction: "no fate changes; fewer recommended").
- **X5:** the draw held some of the postings X5 moved:
  - recommended at 55: 3 of the 14 moved postings in the pools (cards 19, 28, 29); a draw with none of them was unlikely (2.1%).
- **X6:** the draw held some of the postings X6 moved:
  - recommended at 50: 8 of the 35 moved postings in the pools (cards 08, 10, 17, 19, 22, 27, 28, 29); a draw with none of them was unlikely (0.0003%).

These chances describe the draw's design (which postings a change moves on the whole run, which is development data), not his verdicts: they say how often a draw of this size would contain no posting a change moves, whatever he would say about it.
