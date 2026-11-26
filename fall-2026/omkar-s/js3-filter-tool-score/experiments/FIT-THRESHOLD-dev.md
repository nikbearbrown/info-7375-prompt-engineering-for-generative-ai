# Threshold fitted on DEV labels (Omkar's audit verdicts) — reported, not adopted

49 labelled cards (cannot_tell left out). The cards over-represent close calls and kept postings, so this is a biased dev set.

| Threshold | Kept | Correct | FP | FN |
|---:|---:|---:|---:|---:|
| 2.0 | 8 | 45 | 4 | 0 |
| 2.5 | 8 | 45 | 4 | 0 |
| 3.0 | 8 | 45 | 4 | 0 |
| 3.5 | 8 | 45 | 4 | 0 |
| 4.0 | 8 | 45 | 4 | 0 |
| 4.5 | 7 | 46 | 3 | 0 |
| 5.0 | 7 | 46 | 3 | 0 |
| 5.5 | 5 | 44 | 3 | 2 |
| 6.0 | 4 | 45 | 2 | 2 |
| 6.5 | 4 | 45 | 2 | 2 |
| 7.0 | 4 | 45 | 2 | 2 |
| 7.5 | 4 | 45 | 2 | 2 |
| 8.0 | 4 | 45 | 2 | 2 |
| 8.5 | 2 | 43 | 2 | 4 |
| 9.0 | 2 | 43 | 2 | 4 |

Best on dev: threshold 4.5 (46 of 49 correct). The filter keeps 5.0 until Omkar decides; a change would be a FILTER.md change-log row and then a held-out run (E2 shows the held-out effect of 4.0).
