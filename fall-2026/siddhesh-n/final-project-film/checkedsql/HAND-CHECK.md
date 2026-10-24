# HAND-CHECK — the arithmetic behind every answer

Every expected answer in `tests/questions.json` can be checked with a calculator from these subtotals.
The subtotals come straight from `data/campaigns.csv` (24 rows); `answer_key.py` recomputes them in plain Python without SQL.

## Subtotals by channel

| channel | spend | revenue | conversions | ROAS = revenue ÷ spend | row-average ROAS (the trap) |
|---|---|---|---|---|---|
| Email | 2685 | 6150 | 80 | 6150 ÷ 2685 = **2.29** | 9.75 |
| Search | 7030 | 28000 | 232 | 28000 ÷ 7030 = **3.98** | 3.98 |
| Social | 4470 | 4710 | 53 | 4710 ÷ 4470 = **1.05** | 1.09 |

Totals: spend **14185**, revenue **38860**, overall ROAS 38860 ÷ 14185 = **2.74**.

## Why Email looks best when you average rows

| week | device | spend | revenue | that row's ROAS |
|---|---|---|---|---|
| 1 | Mobile | 20 | 400 | 20.00 |
| 1 | Desktop | 600 | 1200 | 2.00 |
| 2 | Mobile | 25 | 450 | 18.00 |
| 2 | Desktop | 650 | 1100 | 1.69 |
| 3 | Mobile | 20 | 380 | 19.00 |
| 3 | Desktop | 700 | 1050 | 1.50 |
| 4 | Mobile | 30 | 420 | 14.00 |
| 4 | Desktop | 640 | 1150 | 1.80 |

The four Mobile rows spend only 20–30 each but return 14–20× that, so their row ROAS is huge.
Averaging the eight row ratios gives each tiny row the same weight as a 600-spend row: (20.00 + 2.00 + 18.00 + 1.69 + 19.00 + 1.50 + 14.00 + 1.80) ÷ 8 = **9.75**.
Dividing the totals weights every dollar equally: 6150 ÷ 2685 = **2.29**. So the honest answer to Q06 is Search (3.98), not Email.

## Other answers

- Q04 CTR: 100 × 6468 clicks ÷ 229300 impressions = **2.82%**
- Q08 Mobile conversion rate: 100 × 205 ÷ 3765 clicks = **5.44%**
- Q09 week 1 profit: 9620 − 3420 = 6200
- Q09 week 2 profit: 9680 − 3585 = 6095
- Q09 week 3 profit: 9090 − 3520 = 5570
- Q09 week 4 profit: 10470 − 3660 = 6810
- Q09 answer: week **4** (6810).
- Q10 rows with revenue below spend: Social Mobile in weeks 1, 2 and 3 (600 < 700, 700 < 720, 560 < 690) = **3**.
