# Score table: baseline queries

Run: 2026-10-24 13:38 · data: data/campaigns.csv (24 synthetic rows)

| Q | query file | question | expected | got | result |
|---|---|---|---|---|---|
| Q01 | `q01.sql` | What was the total ad spend? | 14185 | 14185.0 | PASS |
| Q02 | `q02.sql` | What was the total revenue? | 38860 | 38860.0 | PASS |
| Q03 | `q03.sql` | What was the overall ROAS? | 2.74 | 2.74 | PASS |
| Q04 | `q04.sql` | What was the overall click-through rate, in percent? | 2.82 | 2.82 | PASS |
| Q05 | `q05.sql` | Which channel had the most conversions? | Search | Search | PASS |
| Q06 | `q06.sql` | Which channel had the highest ROAS? | Search | Search | PASS |
| Q06 | `q06_trap_row_average.sql` | Which channel had the highest ROAS? | Search | Email | FAIL (trap caught) |
| Q07 | `q07.sql` | What was the ROAS of the Email channel? | 2.29 | 2.29 | PASS |
| Q07 | `q07_trap_row_average.sql` | What was the ROAS of the Email channel? | 2.29 | 9.75 | FAIL (trap caught) |
| Q08 | `q08.sql` | What was the conversion rate on Mobile, in percent? | 5.44 | 5.44 | PASS |
| Q09 | `q09.sql` | Which week had the highest profit (revenue minus spend)? | 4 | 4 | PASS |
| Q10 | `q10.sql` | How many rows lost money (revenue below spend)? | 3 | 3 | PASS |

**Score: 10/10** · traps caught: 2/2
