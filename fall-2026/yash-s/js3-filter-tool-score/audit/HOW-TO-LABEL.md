# How to label the audit sample

The sample from the first filter run is in [`sample-filter-v1.1-2026-11-18T212545Z/`](sample-filter-v1.1-2026-11-18T212545Z/):

| File | What it is |
|---|---|
| `labeling-sheet.csv` | One row per posting. The four `MY_` columns were blank when `sample_audit.py` generated the sample. I filled them later, and committed my labels in `e926b963`. |
| `source-text.md` | The full cleaned text of each posting, by row number. The filter's decision is at the end of each entry, so I can decide before reading it. |
| `sample.json` | Seed, method, population sizes and the posting IDs in each group, so the sample can be redrawn exactly. |

## The groups

| Group | Rows | How it was drawn |
|---|---:|---|
| `random_reject` | 30 | Simple random sample of the 2,355 rejected postings (seed 20261118) |
| `borderline_55_to_64` | 10 | Random draw from the postings scoring 55-64. A deliberate selection near the threshold |
| `borderline_65_to_75` | 10 | Random draw from the postings scoring 65-75. A deliberate selection near the threshold |
| `kept_confirmed` | 0 | Every confirmed posting. The first run confirmed none |
| `kept_review_queue` | 10 | Random sample of the review queue |

Only `random_reject` supports an estimate about all rejected postings. The other groups are chosen on purpose and must be reported separately (FILTER.md section 8).

## The columns I fill in

| Column | What to write |
|---|---|
| `MY_VERDICT` | My own judgment. Suggested values, from FILTER.md section 8: for a rejected posting, `correct reject` or `should have been kept for review`; for a kept posting, `correctly in review`, `should have been rejected`, or `should be confirmed`; for either, `cannot tell` |
| `MY_REASON` | One line: why, in my words |
| `FALSE_FRIEND_WORD` | A word that matched without meaning what the filter assumed, if I see one |
| `MY_NOTES` | Anything else |

I do not change any other column. The filter's results stay as they were saved.

## The held-out sample (for measuring one change at a time)

[`heldout-filter-v1.1-2026-11-18T212545Z/`](heldout-filter-v1.1-2026-11-18T212545Z/) holds 20 postings I have not labeled before. They were drawn by `sample_audit.py --heldout` from the postings that the pre-registered changes in [`../experiments/candidates.json`](../experiments/candidates.json) would flip, leaving out my 60 tuning postings. See `sample.json` for the seed and populations.

The sheet is **blind**: it shows no filter decision, score, or group. I judge each posting from `source-text.md` alone, then fill the same four columns:

| Column | What to write |
|---|---|
| `MY_VERDICT` | What the decision should be for Priya: `reject`, `keep for review`, `confirm`, or `cannot tell` |
| `MY_REASON` | One line: why, in my words |
| `FALSE_FRIEND_WORD` | Optional, as before |
| `MY_NOTES` | Optional |

I should not open `sample.json` until I finish, because it records which version decided what. After labeling and committing the sheet, `python3 experiment.py report` measures each change on these labels.
